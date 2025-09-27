# import asyncio
# from langgraph.graph import StateGraph, START, END
# from agents.agent_factory import AgentFactory
# from agents.parent_agent import llm_router

from agents.parent_agent import app

if __name__ == "__main__":
    print("🤖 Dynamic Tool Framework started!")
    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit"]:
            break
        result = app.invoke({"query": query})
        print("Bot:", result["final"])