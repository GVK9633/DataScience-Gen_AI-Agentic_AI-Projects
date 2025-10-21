import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPSession:
    """Manage a single MCP session for multiple tool calls"""

    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.session = None
        self.tools_info = []
        self._stdio_ctx = None
        self._client_session_ctx = None
        self._stdio_pair = None

    async def __aenter__(self):
        """Enter async context and initialize the session"""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script_path]
        )

        # Open stdio transport manually
        self._stdio_ctx = stdio_client(server_params)
        self._stdio_pair = await self._stdio_ctx.__aenter__()
        read, write = self._stdio_pair

        # Start client session
        self._client_session_ctx = ClientSession(read, write)
        self.session = await self._client_session_ctx.__aenter__()

        await self.session.initialize()
        list_result = await self.session.list_tools()
        self.tools_info = list_result.tools

        print(f"✅ Connected to MCP server [{os.path.basename(self.server_script_path)}], found {len(self.tools_info)} tools")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up and close resources"""
        if self._client_session_ctx:
            await self._client_session_ctx.__aexit__(exc_type, exc_val, exc_tb)
            self.session = None
        if self._stdio_ctx:
            await self._stdio_ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(self, tool_name: str, **kwargs):
        """Call a tool by name"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        result = await self.session.call_tool(tool_name, kwargs)
        if hasattr(result, "content") and result.content:
            return result.content[0].text
        return str(result)

    def get_tool_names(self):
        """Get list of available tool names"""
        return [tool.name for tool in self.tools_info]


# ===============================
# MULTI-SERVER DEMO
# ===============================
async def demo():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # List of MCP server scripts
    servers = [
        os.path.join(current_dir, "math-mcp_server.py"),
        os.path.join(current_dir, "pollution-mcp_server.py"),
    ]

    # Loop through each MCP server
    for server_path in servers:
        print(f"\n🔹 Connecting to server: {os.path.basename(server_path)}")

        async with MCPSession(server_path) as mcp_session:
            tool_names = mcp_session.get_tool_names()
            print(f"   Available tools: {tool_names}")

            # Dynamically handle based on server type
            if "add" in tool_names:
                result = await mcp_session.call_tool("add", a=5, b=7)
                print(f"   ➕ add(5,7) = {result}")

            if "multiply" in tool_names:
                result = await mcp_session.call_tool("multiply", a=3, b=4)
                print(f"   ✖️ multiply(3,4) = {result}")

            if "get_pollution" in tool_names:
                for city in ["Delhi", "Mumbai", "Paris", "New York"]:
                    result = await mcp_session.call_tool("get_pollution", location=city)
                    print(f"   🌆 Pollution in {city}: {result}")


if __name__ == "__main__":
    asyncio.run(demo())
