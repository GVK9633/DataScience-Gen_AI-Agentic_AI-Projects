# mcp_clients/math-mcp_client.py
from langchain.agents import Tool

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def _parse_and_add(query: str) -> str:
    """Parse '2 + 3' or 'add 2 3' into numbers."""
    import re
    nums = list(map(int, re.findall(r"-?\d+", query)))
    if len(nums) >= 2:
        return str(add(nums[0], nums[1]))
    return "Invalid input format. Example: 'add 2 3'"

def _parse_and_multiply(query: str) -> str:
    """Parse '2 * 3' or 'multiply 2 3' into numbers."""
    import re
    nums = list(map(int, re.findall(r"-?\d+", query)))
    if len(nums) >= 2:
        return str(multiply(nums[0], nums[1]))
    return "Invalid input format. Example: 'multiply 2 3'"

def get_tools():
    return [
        Tool(
            name="add",
            func=_parse_and_add,
            description="Add two numbers. Input example: '2 + 3'"
        ),
        Tool(
            name="multiply",
            func=_parse_and_multiply,
            description="Multiply two numbers. Input example: '2 * 3'"
        ),
    ]
