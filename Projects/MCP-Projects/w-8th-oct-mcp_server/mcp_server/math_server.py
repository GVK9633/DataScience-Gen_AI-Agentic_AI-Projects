# math_server.py
# from mcp.server.fastmcp import FastMCP
from fastmcp.server import FastMCP

mcp = FastMCP("math-mcp")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    print("Starting server")
    mcp.run()