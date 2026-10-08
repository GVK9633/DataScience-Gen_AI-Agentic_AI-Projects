# weather_server.py
from typing import List
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
# Load .env file from project root
load_dotenv()
mcp = FastMCP("WebSearch")

from langchain_community.tools.tavily_search import TavilySearchResults

web_search_tool = TavilySearchResults(k=2)

@mcp.tool()
async def get_web_search_results(question: str) -> str:
    """Does a web search for recent events"""
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    return web_results

if __name__ == "__main__":
    mcp.run(transport="sse")