# import asyncio
# from langgraph.graph import StateGraph, START, END
# from agents.agent_factory import AgentFactory
# from agents.parent_agent import llm_router

import asyncio
from agents.parent_agent import app

if __name__ == "__main__":
    print("🤖 Dynamic Tool Framework started!")

    async def main():
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit"]:
                break
            result = await app.ainvoke({"query": query})  # <-- async API
            print("Bot:", result["final"])

    asyncio.run(main())
    print("👋 Exiting...")