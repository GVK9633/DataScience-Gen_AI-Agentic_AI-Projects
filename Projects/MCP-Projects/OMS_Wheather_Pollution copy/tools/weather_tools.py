from mcp_clients.weather_client import fetch_weather

async def get_city_weather(city: str) -> str:
    return await fetch_weather(city)

async def get_country_weather(country: str) -> str:
    return await fetch_weather(country)