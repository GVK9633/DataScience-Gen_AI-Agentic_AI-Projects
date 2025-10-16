from fastmcp.server import FastMCP

# Mock pollution data
POLLUTION_DATA = {
    "Delhi": "AQI 320 (Very Poor)",
    "Mumbai": "AQI 160 (Moderate)",
    "Paris": "AQI 70 (Good)"
}

# Create MCP server
mcp = FastMCP("pollution-mcp")

@mcp.tool()
def get_pollution(location: str):
    """Return pollution info for a given location"""
    return {"content": POLLUTION_DATA.get(location, "No data available")}

if __name__ == "__main__":
    mcp.run()
