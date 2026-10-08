import asyncio
import os
import nest_asyncio
from langchain.tools import Tool
from mcp_clients.mcp_session import MCPSession

nest_asyncio.apply()  # allow nested async calls safely


async def load_tools_from_mcp(server_script_path: str):
    """Dynamically connect to an MCP server and create LangChain tools for its functions."""
    tools = []

    async with MCPSession(server_script_path) as session:
        for tool_info in session.tools_info:
            tool_name = tool_info.name
            desc = tool_info.description or "No description available"

            async def async_tool_func(**kwargs):
                """Async version of MCP tool call."""
                result = await session.call_tool(tool_name, **kwargs)
                print(f"✅ MCP tool '{tool_name}' result: {result}")
                return result

            def sync_tool_func(*args, **kwargs):
                """Safe sync wrapper (works inside and outside event loops)."""
                # Normalize args to kwargs
                if len(args) == 1 and isinstance(args[0], dict):
                    kwargs = args[0]
                elif len(args) == 2 and not kwargs:
                    kwargs = {"a": args[0], "b": args[1]}

                async def run_tool():
                    return await async_tool_func(**kwargs)

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # Already in event loop — run safely
                    future = asyncio.run_coroutine_threadsafe(run_tool(), loop)
                    result = future.result()
                    print(f"🔹 sync_tool_func returning: {result}")
                    return result
                else:
                    # Normal execution path
                    result = asyncio.run(run_tool())
                    print(f"🔹 sync_tool_func returning: {result}")
                    return result

            # Register this tool for LangChain
            tools.append(Tool(name=tool_name, func=sync_tool_func, description=desc))

    print(f"✅ Loaded {len(tools)} tools from {os.path.basename(server_script_path)}")
    return tools


async def load_all_mcp_tools(agent_cfg: dict):
    """Load all MCP tools dynamically for each configured server."""
    all_tools = []

    for mcp_name in agent_cfg["mcp_servers"]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "..", "mcp_servers", "math_server.py")
        server_path = os.path.abspath(server_path)

        try:
            tools = await load_tools_from_mcp(server_path)
            all_tools.extend(tools)
        except Exception as e:
            print(f"⚠️ Failed to load tools from {os.path.basename(server_path)}: {e}")

    print(f"🔧 Total MCP tools loaded: {len(all_tools)}")
    return all_tools
