# mcp_client/universal_mcp_client.py
import asyncio
import os
from langchain.tools import Tool
from mcp_clients.mcp_session import MCPSession

async def load_tools_from_mcp(server_script_path: str):
    """Dynamically connect to an MCP server and create LangChain tools for its functions."""
    tools = []
    async with MCPSession(server_script_path) as session:
        for tool_info in session.tools_info:
            tool_name = tool_info.name
            desc = tool_info.description or "No description available"
            server_name = session.server_name

            async def tool_func(**kwargs):
                return await session.call_tool(tool_name, **kwargs)

            # Create synchronous wrapper for LangChain compatibility
            # def sync_tool_func(**kwargs):
            #     return asyncio.run(tool_func(**kwargs))
            
            #working-1
            
            # def sync_tool_func(*args, **kwargs):
            #     # Handle both (a, b) and {"a": a, "b": b} cases
            #     if len(args) == 1 and isinstance(args[0], dict):
            #         kwargs = args[0]
            #     elif len(args) == 2 and not kwargs:
            #     # LangChain sometimes passes (5, 3)
            #         kwargs = {"a": args[0], "b": args[1]}

            #     async def run_tool():
            #         return await tool_func(**kwargs)

            #     try:
            #         # Get the current loop if it exists
            #         loop = asyncio.get_running_loop()
            #         return loop.create_task(run_tool())  # schedule coroutine
            #     except RuntimeError:
            #         # No event loop is running
            #         return asyncio.run(run_tool())
            
            def sync_tool_func(*args, **kwargs):
                # Handle both (a, b) and {"a": a, "b": b} cases
                if len(args) == 1 and isinstance(args[0], dict):
                    kwargs = args[0]
                elif len(args) == 2 and not kwargs:
                    # LangChain sometimes passes (5, 3)
                    kwargs = {"a": args[0], "b": args[1]}

                async def run_tool():
                    return await tool_func(**kwargs)

                # Always run synchronously for LangChain compatibility
                return asyncio.run(run_tool())

            tools.append(Tool(name=tool_name, func=sync_tool_func, description=desc))

    print(f"✅ Created {len(tools)} LangChain tools from {os.path.basename(server_script_path)}")
    return tools


async def load_all_mcp_tools(agent_cfg: dict):
    """Scan a folder for MCP servers and load all tools dynamically."""
    all_tools = []
    for mcp_name in agent_cfg["mcp_servers"]:
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "..", "mcp_servers", "math_server.py")
        server_path = os.path.abspath(server_path)
    
        try:
            tools = await load_tools_from_mcp(server_path)
            all_tools.extend(tools)
        except Exception as e:
                print(f"⚠️ Could not load tools from {os.path.basename(server_path)}: {e}")
        # abs_folder = os.path.abspath(mcp_folder)
        # server_files = [
        # os.path.join(abs_folder, f)
        # for f in os.listdir(abs_folder)
        # if f.endswith("-mcp_server.py")
        # ]

        # all_tools = []
        # for path in server_files:
        #     try:
        #         tools = await load_tools_from_mcp(path)
        #         all_tools.extend(tools)
        #     except Exception as e:
        #         print(f"⚠️ Could not load tools from {os.path.basename(path)}: {e}")

    print(f"🔧 Total MCP tools loaded: {len(all_tools)}")
    return all_tools