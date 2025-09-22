import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# -----------------------------
# Load environment variables
# -----------------------------
dotenv_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../../..", ".env")
)
print("Looking for .env at:", dotenv_path)
print("OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print("⚠️ .env file not found at:", dotenv_path)

# Ensure API key is available
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables!")
else:
    os.environ["OPENAI_API_KEY"] = openai_key
    print("✅ OPENAI_API_KEY loaded")

# -----------------------------
# Define state
# -----------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# -----------------------------
# Define tools
# -----------------------------
@tool
def get_stock_price(symbol: str) -> float:
    """Return the current price of a stock given the stock symbol"""
    return {"MSFT": 200.3, "AAPL": 100.4, "AMZN": 150.0, "RIL": 87.6}.get(symbol, 0.0)

@tool
def buy_stocks(symbol: str, quantity: int, total_price: float) -> str:
    """Buy stocks given the stock symbol and quantity"""
    decision = interrupt(f"Approve buying {quantity} {symbol} stocks for ${total_price:.2f}?")

    if decision == "yes":
        return f"You bought {quantity} shares of {symbol} for a total price of {total_price}"
    else:
        return "Buying declined."

tools = [get_stock_price, buy_stocks]

# -----------------------------
# Setup LLM with tools
# -----------------------------
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

def chatbot_node(state: State):
    msg = llm_with_tools.invoke(state["messages"])
    return {"messages": [msg]}

# -----------------------------
# Build LangGraph
# -----------------------------
memory = MemorySaver()
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "buy_thread"}}

# -----------------------------
# Run conversation
# -----------------------------
# Step 1: user asks price
state = graph.invoke(
    {"messages": [{"role": "user", "content": "What is the current price of 10 MSFT stocks?"}]},
    config=config,
)
print(state["messages"][-1].content)

# Step 2: user asks to buy
state = graph.invoke(
    {"messages": [{"role": "user", "content": "Buy 10 MSFT stocks at current price."}]},
    config=config,
)
print(state.get("__interrupt__"))

decision = input("Approve (yes/no): ")
state = graph.invoke(Command(resume=decision), config=config)
print(state["messages"][-1].content)
