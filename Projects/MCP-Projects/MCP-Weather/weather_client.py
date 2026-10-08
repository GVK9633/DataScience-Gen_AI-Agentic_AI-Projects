#!/usr/bin/env python3
"""
Simple MCP Weather Client
"""

import asyncio
from mcp.client.stdio import stdio_client
from mcp.client import ClientSession
from mcp import StdioServerParameters

async def get_weather(location: str) -> str:
    """Get weather for a location"""
    # Configure server to run our weather_server.py
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"]
    )
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # Call the weather tool
                result = await session.call_tool("get_weather", {"location": location})
                
                # Extract the text content
                if result.content:
                    return result.content[0].text
                else:
                    return "No weather data received"
                    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test the client
    async def test():
        weather = await get_weather("London")
        print(weather)
    
    asyncio.run(test())