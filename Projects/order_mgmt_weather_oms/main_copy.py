from dotenv import load_dotenv
import os

# Load environment variables
# dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# load_dotenv(dotenv_path=dotenv_path)

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# from config import OPENAI_API_KEY   # now imported cleanly
from mcp import get_memory
from agents import create_order_agent   # cleaner import (renamed from create_agent)
from langgraph.types import Command


if __name__ == "__main__":
    memory = get_memory()
    graph = create_order_agent(memory)   # use the renamed factory
    config = {"configurable": {"thread_id": "weather_oms"}}

    # Step 1: User asks to place order
    state = graph.invoke(
        {"messages": [{"role": "user", "content": "Place an order for 10 umbrellas in Mumbai"}]},
        config=config
    )
    print("Bot:", state["messages"][-1].content)

    # Step 2: Bot interrupts for weather check
    if "__interrupt__" in state:
        print("Interrupt:", state["__interrupt__"])

        # Approve or deny based on weather
        decision = input("Enter weather condition (good/bad): ")
        state = graph.invoke(Command(resume=decision), config=config)

    print("Final Response:", state["messages"][-1].content)
