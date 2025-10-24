import os
from langchain_mcp_adapters.client import MultiServerMCPClient

async def load_all_mcp_tools(agent_cfg: dict):
    """Dynamically load all MCP tools based on config."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    servers_config = {}

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
        return []

    client = MultiServerMCPClient(servers_config)
    all_tools = await client.get_tools()

    print(f"🔧 Loaded {len(all_tools)} tools from: {', '.join(servers_config.keys())}")
    return all_tools
