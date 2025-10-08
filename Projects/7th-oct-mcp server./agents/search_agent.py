# mcp_agents/search_agent.py

from langchain.agents import Tool

def search(query: str) -> str:
    """Mock search results (replace with real API like Tavily or SerpAPI)."""
    return f"Fake search results for: {query}"

def get_tools():
    return [
        Tool(
            name="Search",
            func=search,
            description="Useful for looking up factual or general knowledge information.",
        )
    ]
