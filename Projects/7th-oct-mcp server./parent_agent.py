# parent_agent.py
"""
Parent Agent Module:
- Initializes the LLM (OpenAI)
- Registers tools
- Creates the ReAct-style agent
"""

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
import os
import importlib
import pkgutil

# -----------------------------------
# Load environment variables
# -----------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ Please set OPENAI_API_KEY in your .env file.")

# -----------------------------------
# Initialize the LLM (OpenAI)
# -----------------------------------
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# -----------------------------------
# Define Tools
# -----------------------------------
def search(query: str) -> str:
    """Mock search function (can be replaced with real API call)."""
    return f"Fake search results for: {query}"

# Option 1: Fake search tool
search_tool = Tool(
    name="Search",
    func=search,
    description="Useful for finding factual information from the web."
)

# Option 2 (real): uncomment below if you have Tavily API key
Tavily_search_tool = TavilySearchResults(
    search_depth="basic",
    api_key=os.getenv("TAVILY_API_KEY")
)
# -------------------------------
# Dynamically load MCP agent modules
# -------------------------------
def load_mcp_agents():
    """Auto-discovers all agents in the agents/ folder."""
    gents_list = {}
    package = "agents"
    for _, name, _ in pkgutil.iter_modules([package]):
        module = importlib.import_module(f"{package}.{name}")
        if hasattr(module, "get_tools"):
            gents_list[name] = module.get_tools()
    return gents_list

# -----------------------------------
# Parent reasoning agent
# -----------------------------------
def create_parent_agent(user_input:str, verbose: bool = True):
    """
    Creates and returns the main reasoning agent.
    """
    mcp_agents = load_mcp_agents()
    # Flatten all tools from all MCPs
    tools = [tool for group in mcp_agents.values() for tool in group]
    agent = initialize_agent(
        tools=[search_tool,Tavily_search_tool],
        llm=llm,
        max_iterations=100,
        agent="zero-shot-react-description",  # ReAct-style reasoning
        verbose=verbose,
    )
    response = agent.run(user_input)
    return response
