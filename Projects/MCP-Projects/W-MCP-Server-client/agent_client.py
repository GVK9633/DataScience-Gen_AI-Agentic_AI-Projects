# stdio_client_agentic.py
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

#required for agents
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
# Load .env file from project root
load_dotenv()

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")

async def main():
    # Get the server script path (same directory as this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "math_server.py")

    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[server_path]
    )

    # Create the connection via stdio transport
    async with stdio_client(server_params) as streams:
        # Create the client session with the streams
        async with ClientSession(*streams) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            response = await session.list_tools()
            print("Available tools:", [tool.name for tool in response.tools])

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            print("Agent response:", agent_response['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())