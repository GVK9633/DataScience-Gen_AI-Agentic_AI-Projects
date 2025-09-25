from fastmcp import MCPClient

async def fetch_weather(location: str) -> str:
    async with MCPClient("weather-mcp-1") as client:
        result = await client.call("get_weather", location=location)
        return result.content