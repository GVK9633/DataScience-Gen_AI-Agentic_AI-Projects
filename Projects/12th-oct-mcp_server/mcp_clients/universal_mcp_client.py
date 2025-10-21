# mcp_clients/universal_mcp_client.py
import asyncio
from langchain.agents import Tool

async def run_mcp_query(mcp_name: str):
    """
    Universal MCP client that dynamically loads tools from any MCP server.
    Example usage: await run_mcp_query("math_mcp")
    """
    try:
        # Dynamically import the server
        module_path = f"mcp_server.{mcp_name}_server"
        server_module = __import__(module_path, fromlist=["mcp"])
        mcp_instance = getattr(server_module, "mcp", None)

        if not mcp_instance:
            raise ValueError(f"No MCP instance found in {module_path}")

        # Collect all tools defined in the MCP server
        tools = []
        for tool_name, tool_func in mcp_instance.tools.items():
            tools.append(
                Tool(
                    name=tool_name,
                    func=tool_func,
                    description=tool_func.__doc__ or f"Tool {tool_name}",
                )
            )
        print(f"✅ Loaded {len(tools)} tools from {mcp_name}")
        return tools

    except ModuleNotFoundError:
        raise ValueError(f"MCP server not found: {mcp_name}")
    except Exception as e:
        raise RuntimeError(f"Error running MCP query for {mcp_name}: {e}")
