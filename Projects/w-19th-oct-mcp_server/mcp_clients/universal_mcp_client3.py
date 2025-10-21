import asyncio
import os
import re
from langchain.tools import Tool
from mcp_clients.mcp_session import MCPSession

async def load_tools_from_mcp(server_script_path: str):
    """Dynamically connect to an MCP server and create LangChain tools for its functions."""
    tools = []
    
    # First, connect to get tool info
    async with MCPSession(server_script_path) as session:
        tool_definitions = session.tools_info.copy()
    
    # Create tools with flexible parameter handling
    for tool_info in tool_definitions:
        tool_name = tool_info.name
        desc = tool_info.description or "No description available"
        
        def create_tool_function(tool_name=tool_name, server_path=server_script_path):
            def tool_function(*args, **kwargs):
                print(f"🔧 Tool {tool_name} called with args: {args}, kwargs: {kwargs}")
                
                # Extract numbers from any input format
                numbers = extract_numbers_from_input(args, kwargs)
                
                if not numbers:
                    return "Error: No numbers found in the input. Please provide numbers to calculate."
                
                # Prepare arguments based on tool parameter types
                final_args = {}
                
                # Check if tool expects a list of numbers (from the description)
                if "multiple" in desc.lower() or "list" in desc.lower() or "numbers" in desc.lower():
                    final_args = {"numbers": numbers}
                else:
                    # For tools that expect individual parameters
                    if len(numbers) >= 1:
                        final_args["a"] = numbers[0]
                    if len(numbers) >= 2:
                        final_args["b"] = numbers[1]
                    if len(numbers) >= 3:
                        final_args["c"] = numbers[2]
                    # Add more if needed
                
                print(f"🔧 Final arguments for {tool_name}: {final_args}")
                
                # Create new session and call the tool
                async def call_tool():
                    async with MCPSession(server_path) as session:
                        return await session.call_tool(tool_name, final_args)
                
                # Run the async call
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(lambda: asyncio.run(call_tool()))
                            return future.result()
                    else:
                        return asyncio.run(call_tool())
                except Exception as e:
                    return f"Error calling tool {tool_name}: {e}"
            
            return tool_function
        
        sync_func = create_tool_function(tool_name)
        tools.append(Tool(name=tool_name, func=sync_func, description=desc))

    print(f"✅ Created {len(tools)} LangChain tools from {os.path.basename(server_script_path)}")
    return tools

def extract_numbers_from_input(args, kwargs):
    """Extract numbers from various input formats."""
    numbers = []
    
    # Case 1: Numbers already in kwargs
    if kwargs:
        for key, value in kwargs.items():
            if isinstance(value, (int, float)):
                numbers.append(value)
            elif isinstance(value, str):
                # Extract numbers from string values
                numbers.extend(extract_numbers_from_string(value))
    
    # Case 2: Numbers in args
    for arg in args:
        if isinstance(arg, (int, float)):
            numbers.append(arg)
        elif isinstance(arg, str):
            # Extract numbers from string arguments
            numbers.extend(extract_numbers_from_string(arg))
        elif isinstance(arg, dict):
            # Extract numbers from dictionary values
            for value in arg.values():
                if isinstance(value, (int, float)):
                    numbers.append(value)
                elif isinstance(value, str):
                    numbers.extend(extract_numbers_from_string(value))
    
    # Case 3: If we have a single string with multiple numbers
    if len(args) == 1 and isinstance(args[0], str) and len(numbers) <= 1:
        # Re-parse the string more aggressively
        numbers = extract_numbers_from_string(args[0])
    
    print(f"🔧 Extracted numbers: {numbers}")
    return numbers

def extract_numbers_from_string(text):
    """Extract all numbers from a string using regex."""
    if not isinstance(text, str):
        return []
    
    # Find all numbers (integers and floats)
    number_pattern = r'-?\d+\.?\d*'
    matches = re.findall(number_pattern, text)
    
    # Convert to appropriate numeric types
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(int(match))
        except ValueError:
            continue
    
    return numbers

async def load_all_mcp_tools(agent_cfg: dict):
    """Scan for MCP servers and load all tools dynamically."""
    all_tools = []
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_servers_dir = os.path.join(current_dir, "..", "mcp_servers")
    
    for mcp_name in agent_cfg["mcp_servers"]:
        server_path = os.path.join(mcp_servers_dir, f"{mcp_name}.py")
        server_path = os.path.abspath(server_path)
        
        if not os.path.exists(server_path):
            print(f"⚠️ MCP server not found: {server_path}")
            continue
            
        try:
            tools = await load_tools_from_mcp(server_path)
            all_tools.extend(tools)
        except Exception as e:
            print(f"⚠️ Could not load tools from {os.path.basename(server_path)}: {e}")
    
    print(f"🔧 Total MCP tools loaded: {len(all_tools)}")
    return all_tools