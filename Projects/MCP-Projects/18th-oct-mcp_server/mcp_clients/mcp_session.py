# mcp_clients/mcp_session.py
import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPSession:
    """Manage a single MCP session for multiple tool calls"""

    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.server_name = None
        self.session = None
        self.tools_info = []
        self._stdio_ctx = None
        self._client_session_ctx = None
        self._stdio_pair = None

    async def __aenter__(self):
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script_path]
        )

        self._stdio_ctx = stdio_client(server_params)
        self._stdio_pair = await self._stdio_ctx.__aenter__()
        read, write = self._stdio_pair

        self._client_session_ctx = ClientSession(read, write)
        self.session = await self._client_session_ctx.__aenter__()

        init_result = await self.session.initialize()
        list_result = await self.session.list_tools()
        self.tools_info = list_result.tools
        self.server_name  = getattr(getattr(init_result, "serverInfo", {}), "name", None)
        print(f"✅ Connected to MCP server [{os.path.basename(self.server_script_path)}], found {len(self.tools_info)} tools")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client_session_ctx:
            await self._client_session_ctx.__aexit__(exc_type, exc_val, exc_tb)
            self.session = None
        if self._stdio_ctx:
            await self._stdio_ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(self, tool_name: str, **kwargs):
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        result = await self.session.call_tool(tool_name, kwargs)
        if hasattr(result, "content") and result.content:
            return result.content[0].text
        return str(result)

    def get_tool_names(self):
        return [tool.name for tool in self.tools_info]