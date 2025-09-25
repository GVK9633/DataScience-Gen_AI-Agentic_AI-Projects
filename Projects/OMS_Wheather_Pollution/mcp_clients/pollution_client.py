from fastmcp.client import Client

async def fetch_pollution(location: str) -> str:
    async with Client("pollution-mcp-1") as client:
        result = await client.call("get_pollution", location=location)
        return result.content
    