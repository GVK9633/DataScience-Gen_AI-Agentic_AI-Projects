import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()


# --- LOAD CSV AND TURN ROWS INTO DOCUMENTS ---
def load_csv_as_documents(csv_path: str):
    df = pd.read_csv(csv_path)

    documents = []
    for idx, row in df.iterrows():
        # Convert row to readable text
        text = " | ".join([f"{col}: {str(row[col])}" for col in df.columns])

        doc = Document(
            page_content=text,
            metadata={
                "row_index": idx,
                "product_name": row["name"],
                "category": row["category"],
                "color": row["color"]
            }
        )
        documents.append(doc)

    return documents


# --- BUILD VECTOR DB (Chroma + OpenAI Embeddings) ---
def build_vector_db(documents, persist_dir="db/adidas_products"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )

    return vectordb


# --- SEARCH VECTOR DB ---
def search_db(query, vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    return docs


# --- MAIN PIPELINE ---
def main():
    print("=== Adidas Product RAG Search ===\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    csv_file = os.path.join(current_dir, "../../data/adidas.csv")


    # csv_file = "/mnt/data/adidas.csv"
    persistent_dir = "db/chroma_db_adidas"

    # Load or create DB
    if os.path.exists(persistent_dir):
        print(f"Loading existing vector DB from {persistent_dir} ...\n")
        vectordb = Chroma(
            persist_directory=persistent_dir,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
    else:
        print("Creating new vector DB...")

        documents = load_csv_as_documents(csv_file)
        print(f"Loaded {len(documents)} product records.\n")

        vectordb = build_vector_db(documents, persist_dir=persistent_dir)
        print("Vector DB created successfully.\n")

    # Sample Query
    query = "Which Adidas products are black in color and available in stock?"
    print(f"Query: {query}\n")

    results = search_db(query, vectordb)

    print("=== Top Matching Products ===\n")
    for doc in results:
        print(doc.page_content)
        print("-" * 80)
   


    print("\n=== Search Completed ===")


if __name__ == "__main__":
    main()
