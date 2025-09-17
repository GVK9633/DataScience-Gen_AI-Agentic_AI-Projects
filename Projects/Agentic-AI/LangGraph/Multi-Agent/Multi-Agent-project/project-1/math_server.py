# math_server.py

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b

if __name__ == "__main__":
    #mcp.run("streamable-http", host="127.0.0.1", port=8000)
    mcp.run(transport="stdio")
   