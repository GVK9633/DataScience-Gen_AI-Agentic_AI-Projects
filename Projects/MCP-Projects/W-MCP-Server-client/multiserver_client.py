import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient, load_mcp_tools
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load .env file from project root
load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    math_server_path = os.path.join(current_dir, "math_server.py")

    # ✅ Instantiate client normally (no async with)
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": [math_server_path],
                "transport": "stdio",
            },
            "WebSearch": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    )

    # ✅ Load tools from each server session
    tools = []
    async with client.session("math") as session:
        tools.extend(await load_mcp_tools(session))

    async with client.session("WebSearch") as session:
        tools.extend(await load_mcp_tools(session))

    # ✅ Create agent with the collected tools
    agent = create_react_agent(model, tools)

    # Test queries
    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
    web_response = await agent.ainvoke({"messages": "what is the weather in Kolkata?"})

    print("1st Response:", math_response["messages"][-1].content)
    print("2nd Response:", web_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
