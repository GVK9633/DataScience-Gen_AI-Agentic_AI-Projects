
import os
from mcp.server.fastmcp import FastMCP
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()


# Create MCP Server
mcp = FastMCP("adidas_rag_server")

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(current_dir, "../../adidas-data/adidas.csv")
    
# CSV_PATH = os.path.abspath("data/adidas.csv")
DB_PATH = "db/chroma_db_adidas"

def load_or_create_db(csv_file, persistent_dir):
    if os.path.exists(persistent_dir):
        vectordb = Chroma(
            persist_directory=persistent_dir,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
    else:
        documents = load_csv_as_documents(csv_file)
        vectordb = build_vector_db(documents, persist_dir=persistent_dir)
    return vectordb

# Load Vector Database
vectordb = load_or_create_db(CSV_PATH, DB_PATH)


# Define Tool in NEW MCP Format
@mcp.tool()
def search_adidas_products(query: str):
    """
    Search Adidas products using vector similarity.
    """
    results = search_db(query, vectordb)

    output = []
    for doc in results:
        row = doc.page_content.split(" | ")
        kv = {}

        for item in row:
            if ": " in item:
                k, v = item.split(": ", 1)
                kv[k] = v

        output.append(kv)

    return {"results": output}

def load_csv_as_documents(csv_path: str):
    df = pd.read_csv(csv_path)

    documents = []
    for idx, row in df.iterrows():
        text = " | ".join([f"{col}: {str(row[col])}" for col in df.columns])

        doc = Document(
            page_content=text,
            metadata={col: row[col] for col in df.columns}
        )
        documents.append(doc)

    return documents


def build_vector_db(documents, persist_dir="db/adidas_products"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectordb



def search_db(query, vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    return retriever.invoke(query)

# Run the server
if __name__ == "__main__":
    mcp.run()

