#!/usr/bin/env python3
"""
Simple MCP Weather Server using wttr.in
"""

import asyncio
import sys
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Create server instance
server = Server("simple-weather-server")

@server.list_tools()
async def list_tools():
    """Return available tools"""
    return [{
        "name": "get_weather",
        "description": "Get simple weather information for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Handle tool calls"""
    if name == "get_weather":
        location = arguments.get("location", "").strip()
        if not location:
            return [{"type": "text", "text": "Please provide a location"}]
        
        try:
            # Call wttr.in with simple format
            url = f"https://wttr.in/{location}?format=3"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            weather_text = response.text.strip()
            result = f"Weather in {location}: {weather_text}"
            
            return [{"type": "text", "text": result}]
            
        except Exception as e:
            return [{"type": "text", "text": f"Error getting weather: {str(e)}"}]
    
    return [{"type": "text", "text": f"Unknown tool: {name}"}]

async def main():
    """Start the server"""
    # Use stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())