"""
pollution_client.py

This module provides an asynchronous client to interact with the Pollution MCP server
using the MCP stdio client. It can call the `get_pollution` tool to fetch pollution
information for a specified location.

Modules:
    asyncio: Provides async support for coroutines.
    os: For file path operations.
    json: For parsing server responses.
    re: (Imported but unused; can be removed if not needed)
    mcp.client.stdio: For MCP stdio client connection.
    mcp: Provides ClientSession and StdioServerParameters.

Functions:
    get_pollution(location: str) -> str:
        Asynchronously calls the Pollution MCP server's `get_pollution` tool and
        returns the pollution info for the given location.
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import json
import re

async def get_pollution(location: str) -> str:
    """
    Call the Pollution MCP server's `get_pollution` tool and return pollution info.

    Args:
        location (str): Name of the city or location to fetch pollution info for.

    Returns:
        str: The pollution information returned by the server.
             Returns None if no content is available.

    Raises:
        Exception: If there is an error parsing the server's response.

    Example:
        >>> import asyncio
        >>> asyncio.run(get_pollution("Delhi"))
        'AQI 320 (Very Poor)'
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "..", "mcp_servers", "pollution_server.py")
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
            result = await session.call_tool("get_pollution", {"location": location})
            print("pollution Server Result", result.content)
            
             # Extract and return the text result
            if result.content:
                # result.content is a list of TextContent objects → extract first one
                text = result.content[0].text  
                try:
                    # Parse JSON string from server response
                    data = json.loads(text)
                    return data.get("content").strip()
                except Exception:
                    # Fallback: return raw text
                    return text.strip()
            return None

if __name__ == "__main__":
    async def main():
        res = await get_pollution("Paris")
        print("Pollution in Delhi:", res)
        print(res)
    asyncio.run(main())
   