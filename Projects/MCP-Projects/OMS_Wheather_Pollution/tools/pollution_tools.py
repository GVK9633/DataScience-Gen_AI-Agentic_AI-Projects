from mcp_clients.pollution_client import get_pollution

async def get_city_pollution(city: str) -> str:
    return await get_pollution(city)

async def get_country_pollution(country: str) -> str:
    return await get_pollution(country)