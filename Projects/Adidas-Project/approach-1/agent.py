# Initialize the agent
from core import CustomerServiceAgent, CustomerQuery
agent = CustomerServiceAgent()

# Example customer queries
queries = [
    CustomerQuery(
        message="I want to return these shoes. They don't fit properly and are too tight.",
        customer_id="cust_123",
        session_id="sess_001"
    ),
    CustomerQuery(
        message="The box came completely torn and my friends are making fun of me!",
        order_id="order_456", 
        session_id="sess_002"
    ),
    CustomerQuery(
        message="This product is fake! I want my money back immediately!",
        session_id="sess_003"
    )
]

# Process queries
for query in queries:
    result = agent.process_customer_query(query)
    print(f"Query: {query.message}")
    print(f"Response: {result['final_response']}")
    print("-" * 50)