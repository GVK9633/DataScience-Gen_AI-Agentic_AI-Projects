# weather-mcp_server.py
from fastmcp import FastMCP

# Mock weather data
WEATHER_DATA = {
    "Delhi": "☀️ 35°C, Clear Sky",
    "Mumbai": "🌧️ 29°C, Light Rain",
    "Paris": "⛅ 22°C, Partly Cloudy",
    "New York": "🌤️ 18°C, Breezy",
    "Tokyo": "🌧️ 24°C, Showers"
}

# Create MCP server
mcp = FastMCP("weather-mcp")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather information for a given city."""
    result = WEATHER_DATA.get(city.title(), "No weather data available for this city.")
    return f"Weather in {city.title()}: {result}"

@mcp.tool()
def list_weather_cities() -> str:
    """List all available cities for weather information."""
    return "Available weather cities: " + ", ".join(WEATHER_DATA.keys())

if __name__ == "__main__":
    print("🌦️ Starting Weather MCP Server...")
    mcp.run()
