# mcp_clients/universal_mcp_client.py
import asyncio
import os
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_mcp_query(user_query: str, server_filename: str):
    """
    Dynamically connect to an MCP server, list tools,
    and call the right one based on user query.
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

                # Decide which tool to call based on user query
                selected_tool, tool_args = decide_tool(user_query, available_tools.keys())
                if not selected_tool:
                    print("❌ Could not determine which tool to use from query.")
                    return None

                print(f"🤖 Selected tool: {selected_tool} | Args: {tool_args}")

                # Call the tool
                result = await session.call_tool(selected_tool, tool_args)
                print("🔍 Raw result:", result.content)

                if result.content:
                    try:
                        text = result.content[0].text.strip()

                        # Try to parse as JSON if it looks like JSON
                        if text.startswith("{") or text.startswith("["):
                            data = json.loads(text)
                            if isinstance(data, dict) and "content" in data:
                                return data["content"].strip()
                            return data  # return JSON directly if it's structured

                        # Otherwise, just return raw text
                        return text
                    except Exception as e:
                        print(f"⚠️ Error while parsing result: {e}")
                        return str(result.content)
        return None

    except Exception as e:
        print(f"❌ MCP client error: {e}")
        return None


def decide_tool(user_query: str, available_tool_names):
    """
    Simple NLP-like logic to decide which tool to call based on keywords.
    """
    query = user_query.lower()

    # --- Math tools ---
    if "add" in query or "sum" in query or "plus" in query:
        nums = re.findall(r"\d+", query)
        if len(nums) >= 2:
            return "add", {"a": int(nums[0]), "b": int(nums[1])}

    if "multiply" in query or "times" in query:
        nums = re.findall(r"\d+", query)
        if len(nums) >= 2:
            return "multiply", {"a": int(nums[0]), "b": int(nums[1])}


    return None, {}
