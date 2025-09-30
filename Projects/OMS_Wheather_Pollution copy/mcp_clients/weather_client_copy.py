"""
weather_client.py

Asynchronous client module to fetch weather information from a local MCP weather server.

This module connects to a `weather_server.py` MCP server via stdio, initializes
a client session, lists available tools, and invokes the `get_weather` tool for
a given location. The server response is expected to be in JSON format containing
weather information.

Modules:
    asyncio: Provides support for asynchronous coroutines.
    os: Used to handle file paths.
    json: For parsing server responses.
    re: (Optional, for parsing specific data like temperature).
    mcp.client.stdio: Provides stdio client for MCP communication.
    mcp: Provides ClientSession and StdioServerParameters for MCP sessions.
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json
import re

async def fetch_weather(location: str) -> str:
    """
    Fetch weather information for a given location using the MCP weather server.

    This function:
        1. Locates and runs the local MCP weather server (`weather_server.py`).
        2. Initializes an MCP client session via stdio.
        3. Lists all available tools in the server.
        4. Calls the `get_weather` tool with the specified location.
        5. Parses the server response JSON and returns the weather content.

    Args:
        location (str): Name of the location (e.g., "Paris", "London").

    Returns:
        str | None:
            - Weather information string if the server returns valid content
              (e.g., `"Paris: 🌫 +10°C"`).
            - `None` if no valid response is received from the server.

    Example:
        >>> result = await fetch_weather("Paris")
        >>> print(result)
        Paris: 🌫 +10°C

    Notes:
        - Server responses are expected to be JSON strings like:
          `{"content": "Paris: 🌫 +10°C"}`.
        - If JSON parsing fails, the raw text from the server is returned.
        - Optionally, regex can be used to extract specific details like temperature.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "..", "mcp_servers", "weather_server.py")
    server_path = os.path.abspath(server_path)  
    server_params = StdioServerParameters(
        command="python",
        args=[server_path]

    )
    async with stdio_client(server_params) as streams:
        # Create the client session with the streams
        async with ClientSession(*streams) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            response = await session.list_tools()
            print("Available tools:", [tool.name for tool in response.tools])

            # Call the add tool
            result = await session.call_tool("get_weather", {"location": location})
            print("Weather Server Result", result.content)
            
             # Extract and return the text result
            if result.content:
                # result.content is a list of TextContent objects → extract first one
                text = result.content[0].text  
                try:
                    # Parse JSON string from server response
                    data = json.loads(text)
                    # return data.get("content")
                    return data.get("content").strip()
                except Exception:
                    # Fallback: return raw text
                    # return text
                    return text.strip()
                
                   # Extract temperature with regex (e.g., +10°C, -2°C, 25°C)
                    # match = re.search(r"[-+]?\d+°C", weather_str)
                    # if match:
                    #     return match.group(0)  # just the temperature
                    # return weather_str   # fallback: return whole string
            return None
            
   
if __name__ == "__main__":
    async def main():
        res = await fetch_weather("Paris")  
        # print("🌤️ Weather in Paris:", res)
        print(res)

    asyncio.run(main())
##############################
