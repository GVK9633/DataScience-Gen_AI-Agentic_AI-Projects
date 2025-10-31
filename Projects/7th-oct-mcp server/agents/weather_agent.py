# mcp_agents/weather_agent.py

from langchain.agents import Tool
import random

def get_weather(location: str) -> str:
    """Mock weather report (replace with API later)."""
    temps = [28, 30, 32, 35, 29]
    return f"The weather in {location} is {random.choice(temps)}°C and sunny."

def get_tools():
    return [
        Tool(
            name="Weather",
            func=get_weather,
            description="Useful for checking weather of a given location. Input should be a city name.",
        )
    ]
