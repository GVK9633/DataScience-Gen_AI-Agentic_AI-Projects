import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class WeatherMCPClient:
    """
    Client wrapper for communicating with the MCP weather server.
    """

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_path = os.path.abspath(
            os.path.join(current_dir, "..", "mcp_server", "weather_mcp_server.py")
        )

    async def get_weather(self, location: str, forecast_type: str = "today") -> dict:
        """
        Call MCP weather server and return weather info.
        """
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path]
        )

        try:
            async with stdio_client(server_params) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()

                    # Call MCP tool
                    result = await session.call_tool(
                        "get_weather",
                        {"location": location, "forecast_type": forecast_type}
                    )

                    if result.content:
                        text = result.content[0].text
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            return {"content": text.strip()}
            return {"content": None}

        except asyncio.CancelledError:
            return {"content": "⚠️ Request cancelled"}
        except Exception as e:
            return {"content": f"❌ Error: {e}"}


# Manual test
# if __name__ == "__main__":
#     async def main():
#         client = WeatherMCPClient()   # ✅ create client instance
#         res = await client.get_weather("Paris")
#         print("🌤️ Weather in Paris:", res)

#     asyncio.run(main())
