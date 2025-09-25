from fastmcp import FastMCP, Response

POLLUTION_DATA = {
    "Delhi": "AQI 320 (Very Poor)",
    "Mumbai": "AQI 160 (Moderate)",
    "Paris": "AQI 70 (Good)"
}

mcp = FastMCP("pollution-mcp-1")

@mcp.tool()
def get_pollution(location: str) -> Response:
    return Response(content=POLLUTION_DATA.get(location, "No data available"))

if __name__ == "__main__":
    mcp.run()