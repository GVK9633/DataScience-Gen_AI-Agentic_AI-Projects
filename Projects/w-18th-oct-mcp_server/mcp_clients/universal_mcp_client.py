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
            def sync_tool_func(*args, **kwargs):
                if len(args) == 1 and isinstance(args[0], dict):
                    kwargs = args[0]

                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        # No running loop → safe to call asyncio.run()
                        return asyncio.run(tool_func(**kwargs))
                else:
                    # Already inside an event loop → schedule async task
                    return loop.run_until_complete(tool_func(**kwargs))

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