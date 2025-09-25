
##############################
from fastmcp.server import FastMCP
import requests

mcp = FastMCP("weather-mcp-1")

@mcp.tool()
def get_weather(location: str):
    """Fetch weather info from wttr.in"""
    try:
        resp = requests.get(f"https://wttr.in/{location}?format=3", timeout=5)
        return {"content": resp.text}  # return a dict instead of Response
    except Exception as e:
        return {"content": f"Error: {e}"}

if __name__ == "__main__":
    mcp.run()
################################
