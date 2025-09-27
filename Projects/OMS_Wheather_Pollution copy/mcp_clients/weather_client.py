# from fastmcp.client.client import MCPClient

# async def fetch_weather(location: str) -> str:
#     async with MCPClient("weather-mcp-1") as client:
#         result = await client.call("get_weather", location=location)
#         return result.content

# import asyncio
# from fastmcp.client import Client  # fastmcp client

# async def fetch_weather(location: str):
#     async with Client("weather-mcp-1") as client:
#         result = await client.call("get_weather", location=location)
#         return result["content"]

# if __name__ == "__main__":
#     asyncio.run(fetch_weather("London"))

# tools/weather_tools.py
# mcp_clients/weather_client.py
#########################################
# import asyncio
# from mcp.client.stdio import stdio_client
# from mcp.server import FastMCP

# # define the server object
# weather_mcp = FastMCP(name="weather-mcp-1", command=["python", "mcp_servers/weather_server.py"])

# async def fetch_weather(location: str) -> str:
#     """Call the Weather MCP server tool"""
#     async with stdio_client(weather_mcp) as (client, reader, writer):
#         await client.start()
#         result = await client.call_tool("get_weather", {"location": location})
#         return result.content

# if __name__ == "__main__":
#     async def main():
#         res = await fetch_weather("Paris")
#         print("🌤️ Weather in Paris:", res)

#     asyncio.run(main())

##########################################

# import asyncio
# from mcp.client.stdio import stdio_client, StdioServerParameters

# async def fetch_weather(location: str) -> str:
#     # Create a server parameters object
#     server_params = StdioServerParameters(
#         command="python",                     # Python executable
#         # args=["mcp_servers/weather_server.py"] 
#         args=["../mcp_servers/weather_server.py"]  # server script
#     )
#     # Use stdio_client to manage the server process
#     async with stdio_client(server_params) as client:
#         await client.start()
#         result = await client.call_tool("get_weather", {"location": location})
#         return result["content"]
    
# if __name__ == "__main__":
#     async def main():
#         res = await fetch_weather("Paris")
#         print("🌤️ Weather in Paris:", res)

#     asyncio.run(main())
###################################
# import asyncio
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# async def fetch_weather(location: str) -> str:
#     server_params = StdioServerParameters(
#         command="python",
#         args=["../mcp_servers/weather_server.py"]
#         # args=["/Users/gvijaykumarachary/Desktop/MyComputer/E-Drive/DataScience/Repos/datascience-projects/DataScience-Gen_AI-Agentic_AI-Projects/Projects/OMS_Wheather_Pollution/mcp_servers/weather_server.py"]
#     )
    
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#             result = await session.call_tool("get_weather", {"location": location})
#             return result.content

# if __name__ == "__main__":
#     async def main():
#         res = await fetch_weather("Paris")
#         print("🌤️ Weather in Paris:", res)

#     asyncio.run(main())
##############################


# weather_client.py
import asyncio
from fastmcp import FastMCP

async def fetch_weather(location: str) -> str:
    # Connect to the FastMCP server
    mcp = FastMCP("weather-mcp-1")
    
    # FastMCP typically uses HTTP transport, not stdio
    # You'll need to configure the connection based on how your server runs
    try:
        result = await mcp.call_tool("get_weather", {"location": location})
        return result
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    async def main():
        res = await fetch_weather("Paris")
        print("🌤️ Weather in Paris:", res)

    asyncio.run(main())