# from fastmcp.client import Client

# async def fetch_pollution(location: str) -> str:
#     async with Client("pollution-mcp-1") as client:
#         result = await client.call("get_pollution", location=location)
#         return result.content
# mcp_clients/pollution_client.py
import asyncio
from mcp.client.stdio import StdioClient

async def get_pollution(location: str) -> str:
    """Call the Pollution MCP server tool"""
    client = StdioClient(command=["python", "mcp_servers/pollution_server.py"])
    async with client:
        result = await client.call("get_pollution", {"location": location})
        return result.content

if __name__ == "__main__":
    async def main():
        res = await get_pollution("Delhi")
        print("Pollution in Delhi:", res)

    asyncio.run(main())
# async def fetch_pollution(location: str) -> str:
#     return await get_pollution(location)        