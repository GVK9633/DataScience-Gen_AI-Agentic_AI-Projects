# math_server.py
from fastmcp.server import FastMCP
from langchain.agents import Tool

mcp = FastMCP("math-mcp")

# ----------------------------
# MCP Tools (for MCP runtime)
# ----------------------------
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


# ----------------------------
# LangChain-compatible tools
# ----------------------------
def get_tools():
    """
    Return a list of LangChain Tool objects
    that wrap the same functionality as the MCP tools.
    These can be dynamically imported and used by the agent.
    """
    return [
        Tool(
            name="add",
            func=lambda a, b: add(a, b),
            description="Add two numbers together",
        ),
        Tool(
            name="multiply",
            func=lambda a, b: multiply(a, b),
            description="Multiply two numbers together",
        ),
    ]


if __name__ == "__main__":
    print("Starting Math MCP Server...")
    mcp.run()
