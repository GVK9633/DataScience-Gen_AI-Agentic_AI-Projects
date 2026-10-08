# universal_mcp_client.py
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
async def load_all_mcp_tools(agent_cfg: dict):
    """Scan for MCP servers and load all tools dynamically."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "..", "mcp_servers", "math_server.py")
    server_path = os.path.abspath(server_path)
    client=MultiServerMCPClient(
        {
            "math":{
                "command":"python",
                # "args":["mathserver.py"], ## Ensure correct absolute path
                "args":[server_path],
                "transport":"stdio",
            
            },
            # "weather": {
            #     "url": "http://localhost:8000/mcp",  # Ensure server is running here
            #     "transport": "streamable_http",
            # }
        }
    )
    all_tools = await client.get_tools()
    return all_tools