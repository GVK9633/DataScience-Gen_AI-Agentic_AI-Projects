import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json

async def fetch_weather(location: str) -> str | None:
    """
    Fetch weather information for a given location using the MCP weather server.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "..", "mcp_servers", "weather_server.py")
    server_path = os.path.abspath(server_path)

    server_params = StdioServerParameters(
        command="python",
        args=[server_path]
    )

    try:
        async with stdio_client(server_params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()

                # List available tools
                response = await session.list_tools()
                print("Available tools:", [tool.name for tool in response.tools])

                # Call the MCP tool
                result = await session.call_tool("get_weather", {"location": location})
                print("Weather Server Result", result.content)

                if result.content:
                    text = result.content[0].text
                    try:
                        data = json.loads(text)
                        return data.get("content", "").strip()
                    except json.JSONDecodeError:
                        return text.strip()
        return None

    except asyncio.CancelledError:
        # Prevent RuntimeError: cancel scope exit in different task
        print("⚠️ Weather fetch was cancelled.")
        return None

    except Exception as e:
        print(f"❌ MCP weather client error: {e}")
        return None


# Manual test
# if __name__ == "__main__":
#     async def main():
#         res = await fetch_weather("Paris")
#         print("🌤️ Weather in Paris:", res)

#     asyncio.run(main())
