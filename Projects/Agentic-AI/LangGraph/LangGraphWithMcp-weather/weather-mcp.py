# Import FastMCP to create an MCP-compatible tool server
from fastmcp import FastMCP

# Import httpx for making asynchronous HTTP requests
import httpx

# Initialize the MCP server and give it a name "Weather"
mcp = FastMCP("Weather")

# Define an asynchronous tool that can be invoked by an MCP client or agent
@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get the weather for a given location using wttr.in API.
    
    Args:
        location (str): City name or location to fetch the weather for.
    
    Returns:
        str: A short weather description (e.g., "Karachi: 🌤 +38°C") or error message.
    """
    try:
        # Create the URL for wttr.in with simple 1-line format
        url = f"https://wttr.in/{location}?format=3"
        
        # Use async HTTP client to make the request
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            # Return weather text if successful
            if response.status_code == 200:
                return response.text.strip()
            else:
                return f"Could not fetch weather for {location}. Status: {response.status_code}"
    
    # Handle any unexpected exceptions and return the error message
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
    
@mcp.tool()
def get_currency_value(currency_code: str) -> float:
    '''
    Return the current value of a currency against USD.
    :param currency_code: ISO currency code (e.g., "USD", "INR", "EUR")
    :return: current value of the currency against USD
    '''
    return {
        "USD": 1.0,     # US Dollar
        "INR": 0.012,   # Indian Rupee → 1 INR ≈ 0.012 USD
        "EUR": 1.09,    # Euro → 1 EUR ≈ 1.09 USD
    }.get(currency_code.upper(), 0.0)
# Start the MCP tool server on localhost:8000 using streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
