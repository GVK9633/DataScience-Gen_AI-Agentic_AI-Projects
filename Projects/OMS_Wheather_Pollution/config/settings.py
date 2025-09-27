import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o"  # change to "gpt-4.1-mini" if you want cheaper


AGENT_CONFIG = {
    "weather": {
        "llm": "openai",
        "tools": ["get_city_weather", "get_country_weather"],
        "mcp_servers": ["weather-mcp-1"]
    },
    "pollution": {
        "llm": "openai",
        "tools": ["get_city_pollution", "get_country_pollution"],
        "mcp_servers": ["pollution-mcp-1"]
    },
    "parent": {
        "agents": ["weather", "pollution"],
        "llm_model": "gpt-4o-mini",
    }
}