# mcp_clients/pollution-mcp_client.py
from langchain.agents import Tool
import random
import re

# --- Core data and logic ---

POLLUTION_DATA = {
    "Delhi": {"PM2.5": 185, "AQI": "Poor", "CO2": 410, "NO2": 45},
    "Bangalore": {"PM2.5": 78, "AQI": "Moderate", "CO2": 390, "NO2": 30},
    "Mumbai": {"PM2.5": 122, "AQI": "Unhealthy", "CO2": 400, "NO2": 38},
    "Tokyo": {"PM2.5": 42, "AQI": "Good", "CO2": 370, "NO2": 22},
    "New York": {"PM2.5": 60, "AQI": "Moderate", "CO2": 380, "NO2": 28},
}

# --- Functions for pollution tools ---

def get_pollution(city: str) -> str:
    """Get pollution data for a city."""
    data = POLLUTION_DATA.get(city.title())
    if data:
        return (
            f"Pollution in {city.title()} — PM2.5: {data['PM2.5']} µg/m³, "
            f"AQI: {data['AQI']}, CO₂: {data['CO2']} ppm, NO₂: {data['NO2']} µg/m³"
        )
    return f"No pollution data found for {city}."

def compare_pollution(city1: str, city2: str) -> str:
    """Compare pollution between two cities."""
    d1, d2 = POLLUTION_DATA.get(city1.title()), POLLUTION_DATA.get(city2.title())
    if not d1 or not d2:
        return f"Data missing for one of the cities: {city1}, {city2}."
    worse = city1 if d1["PM2.5"] > d2["PM2.5"] else city2
    return (
        f"{worse.title()} has higher PM2.5 levels — "
        f"{POLLUTION_DATA[worse.title()]['PM2.5']} µg/m³ vs "
        f"{POLLUTION_DATA[city1.title()]['PM2.5']} µg/m³ in {city1.title()} and "
        f"{POLLUTION_DATA[city2.title()]['PM2.5']} µg/m³ in {city2.title()}."
    )

# --- Helper parser functions ---

def _parse_and_get_pollution(query: str) -> str:
    match = re.search(r"pollution in ([A-Za-z\s]+)", query,re.IGNORECASE)
    if match:
        return get_pollution(match.group(1).strip())
    return "Please specify a city. Example: 'Pollution in Delhi'."

def _parse_and_compare(query: str) -> str:
    cities = re.findall(r"[A-Za-z]+", query,re.IGNORECASE)
    if len(cities) >= 2:
        return compare_pollution(cities[0], cities[1])
    return "Please specify two cities. Example: 'Compare Delhi and Bangalore pollution'."

# --- LangChain Tool registration (only two tools) ---

def get_pollution_tools():
    """Return only two pollution-related tools."""
    return [
        Tool(
            name="get_pollution",
            func=_parse_and_get_pollution,
            description="Get pollution data for a city. Example: 'Pollution in Delhi'"
        ),
        Tool(
            name="compare_pollution",
            func=_parse_and_compare,
            description="Compare pollution between two cities. Example: 'Compare Delhi and Bangalore pollution'"
        ),
    ]
