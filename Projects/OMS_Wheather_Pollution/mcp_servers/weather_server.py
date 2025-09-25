from fastmcp import FastMCP, Response
import requests

mcp = FastMCP("weather-mcp-1")

@mcp.tool()
def get_weather(location: str) -> Response:
    """Fetch weather info from wttr.in"""
    try:
        resp = requests.get(f"https://wttr.in/{location}?format=3", timeout=5)
        return Response(content=resp.text)
    except Exception as e:
        return Response(content=f"Error: {e}")

if __name__ == "__main__":
    mcp.run()