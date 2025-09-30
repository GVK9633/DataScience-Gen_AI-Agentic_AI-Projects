
"""
Weather MCP Server for Real-time Weather Information.

This module provides a Model Context Protocol (MCP) server that exposes
a weather lookup tool using the public wttr.in service. It's built with
FastMCP to create a standardized interface for weather data retrieval.

Key Features:
- Real-time weather data for any location worldwide
- Simple text-based weather summaries
- Error handling and timeout management
- MCP-standard compliant response format

Usage:
    This server is designed to be used with MCP clients that can connect
    to FastMCP servers. The primary tool `get_weather` can be invoked
    through MCP protocol calls.

Example MCP Client Integration:
    Once running, clients can call:
    {"method": "tools/call", "params": {"name": "get_weather", "arguments": {"location": "Tokyo"}}}

Dependencies:
    - fastmcp: For MCP server functionality
    - requests: For HTTP API calls to wttr.in

Service Information:
    - Data Source: wttr.in (public weather service)
    - Response Format: Concise one-line text summary
    - Timeout: 5 seconds per request
"""
from fastmcp.server import FastMCP
import requests
# Initialize the MCP server with a descriptive name
mcp = FastMCP("weather-mcp-1")

@mcp.tool()
def get_weather(location: str):
    """
    Fetch the current weather information for a given location using wttr.in.

    This function queries the public `wttr.in` weather service and returns
    a simple text-based weather summary (location, condition, temperature).
    The result is wrapped in a dictionary with a `content` key, which is
    compatible with MCP client expectations.

    Args:
        location (str): Name of the location (e.g., "Paris", "London", "New York").
                       Supports city names, airport codes, and geographic coordinates.

    Returns:
        dict: A dictionary containing:
            - "content" (str): Weather summary string or an error message.
              Format: "Location: [emoji] [temperature]"

    Raises:
        This function catches all exceptions and returns error messages in the
        response dictionary rather than raising exceptions.

    Example:
        >>> get_weather("Paris")
        {"content": "Paris: 🌫  +10°C"}
        
        >>> get_weather("london")
        {"content": "London: ☁️  +15°C"}
        
        >>> get_weather("invalid_location_123")
        {"content": "Error: ..."}

    Notes:
        - Uses `wttr.in` with format `?format=3` for a concise one-line response
        - Falls back to an error message if the request fails
        - Supports worldwide locations including cities, countries, and coordinates
        - Response includes weather emoji for visual representation
        - Timeout set to 5 seconds to prevent hanging requests
    """
    try:
        resp = requests.get(f"https://wttr.in/{location}?format=3", timeout=5)
        return {"content": resp.text}  # return a dict instead of Response
    except Exception as e:
        return {"content": f"Error: {e}"}

if __name__ == "__main__":
    """
    Entry point for running the weather MCP server.
    
    Starts a FastMCP server named "weather-mcp-1" that exposes the
    `get_weather` tool for fetching real-time weather information.
    
    The server will run and listen for MCP client connections, providing
    weather lookup capabilities through the standardized MCP protocol.
    
    Expected Output:
        - Server startup message
        - Logs of incoming requests when clients connect
        - Error logs if any issues occur during operation
    """
    print("Starting weather-mcp-1")
    mcp.run()
################################
