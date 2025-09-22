from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Fetch weather condition for a location (mocked)."""
    weather_data = {
        "New York": "rainy",
        "Mumbai": "sunny",
        "London": "cloudy", 
    }
    return weather_data.get(location, "unknown")        
    return f"The weather in {location} is {weather_data.get(location, 'unknown')}."
