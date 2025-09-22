from config import OPENAI_API_KEY, DEFAULT_MODEL
from mcp import get_memory
from agents.agent_factory import create_agent
from langgraph.types import Command

print("API Key:", OPENAI_API_KEY)
print("Model:", DEFAULT_MODEL)

if __name__ == "__main__":
    memory = get_memory()
    graph = create_agent(memory)
    config = {"configurable": {"thread_id": "weather_oms"}}

    # Step 1: User asks to place order
    state = graph.invoke(
        {"messages": [{"role": "user", "content": "Place an order for 10 umbrellas in Mumbai"}]},
        config=config
    )
    print("Bot:", state["messages"][-1].content)

    # Step 2: Bot interrupts for weather check
    print("Interrupt:", state.get("__interrupt__"))

    # Approve or deny based on weather
    decision = input("Enter weather condition (good/bad): ")
    state = graph.invoke(Command(resume=decision), config=config)

    print("Final Response:", state["messages"][-1].content)
