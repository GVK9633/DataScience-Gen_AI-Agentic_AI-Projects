from fastmcp.server import FastMCP

mcp = FastMCP("math-mcp")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together. Also responds to queries like 'sum', 'plus', 'total', or 'combine'."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers. Also responds to queries like 'product', 'times', or 'multiply'."""
    return a * b

if __name__ == "__main__":
    print("Starting server")
    mcp.run()
