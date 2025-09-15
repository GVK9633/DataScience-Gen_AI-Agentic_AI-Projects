from fastmcp import FastMCP
import httpx

mcp = FastMCP("Weather")

@mcp.tool()
async def get_city_weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text.strip() if response.status_code == 200 else f"Error: {response.status_code}"

@mcp.tool()
async def get_country_weather(country: str) -> str:
    return f"Weather data for {country} (mocked)"

if __name__ == "__main__":
    mcp.run("streamable-http", host="127.0.0.1", port=8000)
