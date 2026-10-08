"""
pollution_mcp.py

This module creates a FastMCP server that provides pollution information for specified locations.

Modules:
    fastmcp.server: Provides FastMCP server and tool decorators.

Global Variables:
    POLLUTION_DATA (dict): Mock pollution data for some cities.

Functions:
    get_pollution(location: str) -> dict:
        Returns pollution information for a given location.

Usage:
    Run this script to start the MCP server:
        python pollution_mcp.py
    Then, other clients can call the `get_pollution` tool to fetch pollution info.
"""

from fastmcp.server import FastMCP

# Mock pollution data
POLLUTION_DATA = {
    "Delhi": "AQI 320 (Very Poor)",
    "Mumbai": "AQI 160 (Moderate)",
    "Paris": "AQI 70 (Good)"
}

# Create MCP server
mcp = FastMCP("pollution-mcp-1")

@mcp.tool()
def get_pollution(location: str):
    """
    Return pollution info for a given location.

    Args:
        location (str): Name of the city or location.

    Returns:
        dict: A dictionary containing the pollution info with the key 'content'.
              If the location is not found, returns "No data available".
    
    Example:
        >>> get_pollution("Delhi")
        {'content': 'AQI 320 (Very Poor)'}
    """
    return {"content": POLLUTION_DATA.get(location, "No data available")}

if __name__ == "__main__":
    print("Starting pollution-mcp-1")
    mcp.run()
