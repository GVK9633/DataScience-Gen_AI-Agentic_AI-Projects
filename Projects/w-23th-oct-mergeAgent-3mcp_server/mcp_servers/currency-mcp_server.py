# currency-mcp_server.py
from fastmcp import FastMCP

# Mock exchange rates (base: USD)
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "INR": 83.1,
    "GBP": 0.78,
    "JPY": 150.3
}

mcp = FastMCP("currency-mcp")

@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another (mock rates)."""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency not in EXCHANGE_RATES or to_currency not in EXCHANGE_RATES:
        return "Unsupported currency."

    usd_amount = amount / EXCHANGE_RATES[from_currency]
    converted = usd_amount * EXCHANGE_RATES[to_currency]
    return f"{amount} {from_currency} = {converted:.2f} {to_currency}"

@mcp.tool()
def list_supported_currencies() -> str:
    """List all supported currency codes."""
    return "Supported currencies: " + ", ".join(EXCHANGE_RATES.keys())

if __name__ == "__main__":
    print("💱 Starting Currency MCP Server...")
    mcp.run()
