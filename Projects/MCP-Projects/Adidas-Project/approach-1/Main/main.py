import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()
def load_csv_as_documents(csv_path: str):
    df = pd.read_csv(csv_path)

    documents = []
    for idx, row in df.iterrows():
        text = " | ".join(f"{col}: {row[col]}" for col in df.columns)

        doc = Document(
            page_content=text,
            # metadata={"row_index": idx, "columns": list(df.columns)}
            metadata={"row_index": idx,"columns": ",".join(df.columns)}

        )
        documents.append(doc)

    return documents

def build_vector_db(documents, persist_dir="db/adidas"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectordb

def search_db(query, vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    return docs

def main():
    """Main ingestion pipeline"""
    print("=== RAG Document Ingestion Pipeline ===\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    docs_path = os.path.join(current_dir, "../../data/adidas.csv")
    persistent_directory = "db/chroma_db_addidas"
    
    # Check if vector store already exists
    if os.path.exists(persistent_directory):
        print(f"Vector store already exists at {persistent_directory}. Skipping ingestion.")
        return
    
    # Load documents
    csv_docs = load_csv_as_documents(docs_path)
    print(f"Loaded {len(csv_docs)} documents from CSV files.\n")
    
    vectordb = build_vector_db(csv_docs)
    print(f"Vector store created and saved to {persistent_directory}\n")
    
    results = search_db(
    "What are the different colours for shoes available?",
    vectordb
    )

    for doc in results:
        print(doc.page_content)
    
    print("\n=== Ingestion Pipeline Completed ===")
if __name__ == "__main__":
    main()