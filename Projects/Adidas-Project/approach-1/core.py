from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import chromadb
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langgraph.graph import Graph
from langchain.chat_models import ChatOpenAI  # or your preferred LLM
import json
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
# Data Models
class CustomerQuery(BaseModel):
    message: str
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    session_id: str

class ReturnRequest(BaseModel):
    customer_id: str
    order_id: str
    reason: str
    sentiment: str
    severity: float
    product_details: Dict[str, Any]

class ResolutionOffer(BaseModel):
    action: str  # "refund", "exchange", "discount", "replacement"
    amount: Optional[float] = None
    discount_code: Optional[str] = None
    message: str

class CustomerServiceAgent:
    def __init__(self):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.vector_store = Chroma(
            client=self.chroma_client,
            embedding_function=self.embeddings,
            collection_name="product_catalog"
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")
        
        # Build the agentic workflow
        self.workflow = self._build_workflow()
        
        # Initialize product catalog
        self._initialize_product_catalog()
    
    def _initialize_product_catalog(self):
        """Initialize ChromaDB with product data from CSV"""
        # Convert CSV data to documents
        documents = []
        metadatas = []
        ids = []
        
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct relative path to the CSV
        csv_path = os.path.join(current_dir, "../data/adidas.csv")
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        for index, row in df.iterrows():  # Assuming df is your pandas DataFrame
            doc_text = f"""
            Product: {row['name']}
            SKU: {row['sku']}
            Category: {row['category']}
            Price: ${row['selling_price']}
            Color: {row['color']}
            Description: {row['description']}
            Rating: {row['average_rating']}
            Reviews: {row['reviews_count']}
            """
            
            documents.append(doc_text)
            metadatas.append({
                'sku': row['sku'],
                'name': row['name'],
                'category': row['category'],
                'price': row['selling_price'],
                'color': row['color'],
                'rating': row['average_rating']
            })
            ids.append(str(row['sku']))
        
        # Add to vector store
        self.vector_store.add_texts(
            texts=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def _build_workflow(self) -> Graph:
        """Build the LangGraph workflow for customer service"""
        workflow = Graph()
        
        # Define nodes
        workflow.add_node("authenticate_customer", self.authenticate_customer)
        workflow.add_node("analyze_sentiment", self.analyze_sentiment)
        workflow.add_node("extract_return_reason", self.extract_return_reason)
        workflow.add_node("fetch_order_details", self.fetch_order_details)
        workflow.add_node("classify_issue_severity", self.classify_issue_severity)
        workflow.add_node("generate_resolution", self.generate_resolution)
        workflow.add_node("suggest_alternatives", self.suggest_alternatives)
        workflow.add_node("final_response", self.final_response)
        
        # Define edges
        workflow.set_entry_point("authenticate_customer")
        workflow.add_edge("authenticate_customer", "analyze_sentiment")
        workflow.add_edge("analyze_sentiment", "extract_return_reason")
        workflow.add_edge("extract_return_reason", "fetch_order_details")
        workflow.add_edge("fetch_order_details", "classify_issue_severity")
        workflow.add_edge("classify_issue_severity", "generate_resolution")
        workflow.add_conditional_edges(
            "generate_resolution",
            self.should_suggest_alternatives,
            {
                "suggest": "suggest_alternatives",
                "skip": "final_response"
            }
        )
        workflow.add_edge("suggest_alternatives", "final_response")
        
        return workflow.compile()
    
    # Node implementations
    def authenticate_customer(self, state: Dict) -> Dict:
        """Authenticate customer and retrieve basic info"""
        query = state["query"]
        
        # Check if customer is logged in or provides credentials
        if query.customer_id:
            # Fetch customer profile
            customer_profile = self._get_customer_profile(query.customer_id)
            return {"customer_profile": customer_profile, "authenticated": True}
        elif query.order_id:
            # Try to authenticate via order ID
            order_details = self._get_order_details(query.order_id)
            if order_details:
                return {
                    "customer_profile": {"order_details": order_details},
                    "authenticated": True
                }
        
        return {"authenticated": False, "next_action": "request_authentication"}
    
    def analyze_sentiment(self, state: Dict) -> Dict:
        """Analyze customer sentiment from message"""
        from transformers import pipeline
        
        sentiment_analyzer = pipeline("sentiment-analysis")
        result = sentiment_analyzer(state["query"].message)[0]
        
        return {
            "sentiment": result['label'],
            "sentiment_score": result['score'],
            "urgency": "high" if result['label'] == 'NEGATIVE' and result['score'] > 0.8 else "medium"
        }
    
    def extract_return_reason(self, state: Dict) -> Dict:
        """Extract and classify return reason"""
        reason_categories = {
            "fit_issue": ["fit", "size", "tight", "loose", "small", "big"],
            "color_issue": ["color", "shade", "different", "not matching"],
            "quality_issue": ["quality", "torn", "broken", "defective", "fake"],
            "shipping_issue": ["box", "packaging", "delivery", "late", "damaged"],
            "expectation_mismatch": ["expect", "picture", "look", "appearance"]
        }
        
        message = state["query"].message.lower()
        detected_reasons = []
        
        for category, keywords in reason_categories.items():
            if any(keyword in message for keyword in keywords):
                detected_reasons.append(category)
        
        # Use LLM for more nuanced reason extraction
        prompt = f"""
        Analyze this customer complaint and extract the main reason for return:
        Complaint: {state["query"].message}
        
        Return reasons:
        - fit_issue: Problems with size or fitting
        - color_issue: Color doesn't match expectations
        - quality_issue: Product is defective or poor quality
        - shipping_issue: Problems with packaging or delivery
        - expectation_mismatch: Product doesn't match description/pictures
        - other: Any other reason
        
        Respond with ONLY the reason category.
        """
        
        llm_response = self.llm.predict(prompt)
        primary_reason = llm_response.strip().lower()
        
        return {
            "detected_reasons": detected_reasons,
            "primary_reason": primary_reason,
            "reason_description": state["query"].message
        }
    
    def fetch_order_details(self, state: Dict) -> Dict:
        """Fetch order and product details"""
        if state.get("customer_profile") and state["customer_profile"].get("order_details"):
            order_details = state["customer_profile"]["order_details"]
            
            # Search for product in catalog
            product_results = self.vector_store.similarity_search(
                order_details["product_name"], k=1
            )
            
            if product_results:
                product_info = product_results[0].metadata
                return {
                    "order_details": order_details,
                    "product_info": product_info
                }
        
        return {"order_details": None, "product_info": None}
    
    def classify_issue_severity(self, state: Dict) -> Dict:
        """Classify issue severity and determine resolution strategy"""
        sentiment = state.get("sentiment", "NEUTRAL")
        sentiment_score = state.get("sentiment_score", 0.5)
        primary_reason = state.get("primary_reason", "other")
        
        severity_mapping = {
            "quality_issue": "high",
            "fit_issue": "medium", 
            "color_issue": "low",
            "shipping_issue": "medium",
            "expectation_mismatch": "low",
            "other": "medium"
        }
        
        base_severity = severity_mapping.get(primary_reason, "medium")
        
        # Adjust based on sentiment
        if sentiment == "NEGATIVE" and sentiment_score > 0.8:
            severity = "high"
        elif sentiment == "NEGATIVE" and sentiment_score > 0.6:
            severity = "medium"
        else:
            severity = base_severity
        
        return {"issue_severity": severity, "requires_escalation": severity == "high"}
    
    def generate_resolution(self, state: Dict) -> Dict:
        """Generate resolution offer based on issue analysis"""
        severity = state.get("issue_severity", "medium")
        primary_reason = state.get("primary_reason", "other")
        product_info = state.get("product_info", {})
        
        resolution_strategies = {
            "high": {
                "action": "refund",
                "message": "We sincerely apologize for the inconvenience. We'll process a full refund immediately."
            },
            "medium": {
                "action": "exchange_or_discount",
                "discount_range": (15, 30),
                "message": "We're sorry for the trouble. We can offer you an exchange or {discount}% discount."
            },
            "low": {
                "action": "discount",
                "discount_range": (10, 20),
                "message": "We appreciate your feedback. Here's a {discount}% discount on your next purchase."
            }
        }
        
        strategy = resolution_strategies[severity]
        resolution = ResolutionOffer(
            action=strategy["action"],
            message=strategy["message"]
        )
        
        if "discount_range" in strategy:
            discount = sum(strategy["discount_range"]) // 2  # Average discount
            resolution.discount_code = f"APOLOGY{discount}"
            resolution.message = resolution.message.format(discount=discount)
        
        return {"resolution_offer": resolution}
    
    def should_suggest_alternatives(self, state: Dict) -> str:
        """Determine if we should suggest alternative products"""
        primary_reason = state.get("primary_reason", "")
        resolution_action = state.get("resolution_offer", {}).get("action", "")
        
        # Suggest alternatives for fit issues or when customer might be interested in exchange
        if primary_reason in ["fit_issue", "color_issue"] and resolution_action != "refund":
            return "suggest"
        return "skip"
    
    def suggest_alternatives(self, state: Dict) -> Dict:
        """Suggest alternative products based on original purchase"""
        product_info = state.get("product_info", {})
        primary_reason = state.get("primary_reason", "")
        
        if not product_info:
            return {"alternative_products": []}
        
        # Search for similar products
        query_filters = {}
        
        if primary_reason == "fit_issue":
            # Suggest different sizes or similar fit products
            query_text = f"{product_info.get('category', '')} comfortable fit"
        elif primary_reason == "color_issue":
            # Suggest different colors
            query_text = f"{product_info.get('category', '')} {product_info.get('name', '')}"
        else:
            query_text = product_info.get('name', product_info.get('category', ''))
        
        similar_products = self.vector_store.similarity_search(
            query_text, 
            k=3,
            filter={"sku": {"$ne": product_info.get('sku')}}  # Exclude original product
        )
        
        alternatives = []
        for product in similar_products:
            alternatives.append({
                "name": product.metadata.get('name'),
                "sku": product.metadata.get('sku'),
                "price": product.metadata.get('price'),
                "color": product.metadata.get('color'),
                "rating": product.metadata.get('rating')
            })
        
        return {"alternative_products": alternatives}
    
    def final_response(self, state: Dict) -> Dict:
        """Generate final response to customer"""
        resolution = state.get("resolution_offer", {})
        alternatives = state.get("alternative_products", [])
        authenticated = state.get("authenticated", False)
        
        response_parts = []
        
        # Add apology and resolution
        response_parts.append(resolution.get("message", "We appreciate your feedback."))
        
        # Add alternative suggestions if available
        if alternatives:
            response_parts.append("\nBased on your preferences, you might like:")
            for alt in alternatives:
                response_parts.append(
                    f"- {alt['name']} (${alt['price']}, Rating: {alt['rating']}/5)"
                )
        
        # Add next steps
        if authenticated:
            if resolution.get("action") == "refund":
                response_parts.append("\nWe've initiated the refund process. It will reflect in 5-7 business days.")
            elif resolution.get("discount_code"):
                response_parts.append(f"\nUse code {resolution['discount_code']} on your next purchase.")
        else:
            response_parts.append("\nPlease provide your order ID or phone number to proceed with the return.")
        
        return {
            "final_response": "\n".join(response_parts),
            "resolution_details": resolution,
            "suggested_alternatives": alternatives
        }
    
    def process_customer_query(self, query: CustomerQuery) -> Dict[str, Any]:
        """Main method to process customer queries"""
        initial_state = {
            "query": query,
            "session_id": query.session_id
        }
        
        # Execute the workflow
        result = self.workflow.invoke(initial_state)
        
        return result

# Utility functions
def _get_customer_profile(customer_id: str) -> Dict:
    """Mock function to get customer profile"""
    # In real implementation, connect to your CRM/database
    return {
        "customer_id": customer_id,
        "order_history": [],
        "loyalty_tier": "standard"
    }

def _get_order_details(order_id: str) -> Dict:
    """Mock function to get order details"""
    # In real implementation, connect to your order management system
    return {
        "order_id": order_id,
        "product_name": "Sample Product",
        "order_date": "2024-01-01",
        "amount": 99.99
    }