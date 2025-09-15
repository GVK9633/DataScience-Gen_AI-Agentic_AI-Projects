from fastmcp import FastMCP

mcp = FastMCP("Pollution")

@mcp.tool()
def get_city_pollution(city: str) -> str:
    return f"Pollution level in {city}: Moderate (mocked)"

@mcp.tool()
def get_country_pollution(country: str) -> str:
    return f"Pollution level in {country}: High (mocked)"

if __name__ == "__main__":
    mcp.run("streamable-http", host="127.0.0.1", port=8002)
