from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def place_order(item: str, quantity: int, location: str) -> str:
    """Place an order if weather is favorable, else reroute."""
    weather_check = interrupt(f"Check weather at {location} before placing order for {quantity} {item}?")
    
    if weather_check == "good":
        return f"✅ Order placed: {quantity} {item} to {location}."
    else:
        return f"⚠️ Weather not good at {location}, rerouting order..."
