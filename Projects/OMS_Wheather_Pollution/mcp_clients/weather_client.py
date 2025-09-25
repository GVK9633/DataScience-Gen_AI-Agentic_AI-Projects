# from fastmcp.client.client import MCPClient

# async def fetch_weather(location: str) -> str:
#     async with MCPClient("weather-mcp-1") as client:
#         result = await client.call("get_weather", location=location)
#         return result.content

import asyncio
from fastmcp.client import Client  # fastmcp client

async def fetch_weather(location: str):
    async with Client("weather-mcp-1") as client:
        result = await client.call("get_weather", location=location)
        return result["content"]

# if __name__ == "__main__":
#     asyncio.run(fetch_weather("London"))

