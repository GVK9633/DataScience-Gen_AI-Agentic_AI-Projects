# main.py
import asyncio
import os
from config.settings import AGENT_CONFIG
from agent_factory.dynamic_agent_factory import DynamicAgentFactory

async def main():
    mcp_folder = os.path.join(os.path.dirname(__file__), "mcp_servers")
    factory = DynamicAgentFactory(AGENT_CONFIG, mcp_folder)

    # Create math agent
    math_agent = await factory.get_agent("agent1")
    #result = math_agent.run("add", {"a": 5, "b": 7})
    result = math_agent.run("Add 5 and 10.")
    print("🧮 Math Agent Result:", result)

    # Create pollution agent
    pollution_agent = await factory.get_agent("agent3")
    result = pollution_agent.run("Get pollution for Delhi.")
    print("🌆 Pollution Agent Result:", result)

if __name__ == "__main__":
    asyncio.run(main())