from mcp_clients.pollution_client import fetch_pollution

async def get_city_pollution(city: str) -> str:
    return await fetch_pollution(city)

async def get_country_pollution(country: str) -> str:
    return await fetch_pollution(country)