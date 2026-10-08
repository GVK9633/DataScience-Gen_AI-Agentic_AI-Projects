# mcp_clients/universal_mcp_client.py
import asyncio
import os
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_mcp_clent_query(user_query: str, server_filename: str):
    """
    Dynamically connect to an MCP server, list tools,
    and call the correct one based on user query.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "..", "mcp_server", server_filename)
    server_path = os.path.abspath(server_path)

    server_params = StdioServerParameters(command="python", args=[server_path])

    try:
        async with stdio_client(server_params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()

                # List available tools
                response = await session.list_tools()
                available_tools = {tool.name: tool for tool in response.tools}
                print(f"🧰 Available tools: {list(available_tools.keys())}")

                # Decide which tool to call
                selected_tool, tool_args = decide_tool(user_query, available_tools.keys())
                if not selected_tool:
                    print("❌ Could not determine which tool to use from query.")
                    return None

                print(f"🤖 Selected tool: {selected_tool} | Args: {tool_args}")

                # Call the selected MCP tool
                result = await session.call_tool(selected_tool, tool_args)
                print("🔍 Raw result:", result.content)

                if result.content:
                    try:
                        text = result.content[0].text.strip()
                        # Try JSON parse if looks like JSON
                        if text.startswith("{") or text.startswith("["):
                            data = json.loads(text)
                            if isinstance(data, dict) and "content" in data:
                                return data["content"].strip()
                            return data
                        return text
                    except Exception as e:
                        print(f"⚠️ Error while parsing result: {e}")
                        return str(result.content)
                return None

    except Exception as e:
        print(f"❌ MCP client error: {e}")
        return None


# -------------------------------------------------------------------------
# 🧠 Intelligent Tool Selector
# -------------------------------------------------------------------------
def decide_tool(user_query: str, available_tool_names):
    """
    Decide which MCP tool to use and extract arguments from the query.
    Uses keyword matching and regex extraction.
    """
    query = user_query.lower().strip()
    nums = re.findall(r"-?\d+(?:\.\d+)?", query)
    a, b = (int(nums[0]), int(nums[1])) if len(nums) >= 2 else (None, None)

    # Normalize available tool names (e.g., ["add", "multiply"])
    available = [t.lower() for t in available_tool_names]

    # 1️⃣ Exact keyword logic for math MCP
    if any(k in query for k in ["add", "sum", "plus"]) and "add" in available:
        return "add", {"a": a, "b": b} if a is not None and b is not None else {}

    if any(k in query for k in ["multiply", "product", "times"]) and "multiply" in available:
        return "multiply", {"a": a, "b": b} if a is not None and b is not None else {}

    # 2️⃣ Fallback: fuzzy match (e.g., if tool name appears in query)
    for tool in available:
        if tool in query:
            return tool, {"a": a, "b": b} if a is not None and b is not None else {}

    # 3️⃣ No match found
    print(f"⚠️ No matching tool found for query: '{user_query}'")
    return None, {}
