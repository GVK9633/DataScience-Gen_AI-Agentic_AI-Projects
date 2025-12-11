
import os
from mcp.server.fastmcp import FastMCP
from adidas_rag.rag_pipeline import load_or_create_db, search_db

# Create MCP Server
mcp = FastMCP("adidas_rag_server")

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(current_dir, "../../adidas-data/adidas.csv")
# csv_file = os.path.join(current_dir, "../../data/adidas.csv")
    
# CSV_PATH = os.path.abspath("data/adidas.csv")
DB_PATH = "db/chroma_db_adidas"

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


# Run the server
if __name__ == "__main__":
    mcp.run()

