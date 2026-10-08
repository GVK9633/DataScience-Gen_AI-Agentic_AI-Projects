# universal_mcp_client.py
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

async def load_all_mcp_tools(agent_cfg: dict):
    """
    Scan for MCP servers defined in the agent configuration and load all tools dynamically.
    Example: agent_cfg["mcp_servers"] = ["math_server", "pollution-mcp_server"]
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    servers_config = {}

    # ✅ Dynamically build config for each MCP server
    for mcp_name in agent_cfg.get("mcp_servers", []):
        server_file = f"{mcp_name}.py"
        server_path = os.path.join(current_dir, "..", "mcp_servers", server_file)
        server_path = os.path.abspath(server_path)

        if not os.path.exists(server_path):
            print(f"⚠️ Warning: MCP server file not found at {server_path}")
            continue

        servers_config[mcp_name] = {
            "command": "python",
            "args": [server_path],
            "transport": "stdio",
        }

    if not servers_config:
        raise ValueError("❌ No valid MCP servers found in configuration.")

    # ✅ Initialize the MultiServer MCP Client
    client = MultiServerMCPClient(servers_config)

    # ✅ Load all tools from all MCP servers
    all_tools = await client.get_tools()

    print(f"🔧 Loaded {len(all_tools)} tools from servers: {', '.join(servers_config.keys())}")
    return all_tools
