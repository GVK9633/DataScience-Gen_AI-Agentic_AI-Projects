# mcp_clients/test_mcp_client.py
import asyncio
from universal_mcp_client import run_mcp_query

if __name__ == "__main__":
    async def main():
        # Try a math query
        result = await run_mcp_query("add 4 and 6", "math_server.py")
        print("✅ Math Result:", result)

        # Try a pollution query (if pollution_server.py exists)
        # result = await run_mcp_query("pollution in Delhi", "pollution_server.py")
        # print("✅ Pollution Result:", result)

    asyncio.run(main())
