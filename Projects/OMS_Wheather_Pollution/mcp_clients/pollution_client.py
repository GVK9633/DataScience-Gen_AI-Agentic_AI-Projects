from fastmcp import MCPClient

async def fetch_pollution(location: str) -> str:
    async with MCPClient("pollution-mcp-1") as client:
        result = await client.call("get_pollution", location=location)
        return result.content