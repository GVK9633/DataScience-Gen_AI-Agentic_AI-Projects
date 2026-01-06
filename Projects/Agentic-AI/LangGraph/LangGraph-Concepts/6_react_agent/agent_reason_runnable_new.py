# Name: langchain
# Version: 1.1.0
# Name: langgraph
# Version: 1.0.3

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
import datetime
from langchain_tavily import TavilySearch
from langchain_classic import hub
import warnings
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings(
    "ignore",
    message="Field name .* shadows an attribute in parent .*"
)

# ---------------- LLM ----------------
llm = ChatOpenAI(model="gpt-4")

# ---------------- TOOL ----------------
@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
    """Returns the current date and time in the specified format"""
    current_time = datetime.datetime.now()
    return current_time.strftime(format)

# ---------------- SEARCH TOOL ----------------
search_tool = TavilySearch(search_depth="basic")

# ---------------- PROMPT ----------------
react_prompt = hub.pull("hwchase17/react")

# ---------------- TOOLS ----------------
tools = [get_system_time, search_tool]

# ---------------- REACT AGENT ----------------
react_agent_runnable = create_agent(
    model="gpt-5",
    # llm=llm,
    tools=tools,
    # prompt=react_prompt
)
# react_agent_runnable = create_react_agent(
#     llm=llm,
#     tools=tools,
#     prompt=react_prompt
# )
