# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4o"

AGENT_CONFIG = {
    "router_agent": {
    "llm": "openai",
    "llm_model": "gpt-4o-mini",
    "system_prompt": (
        "You are a routing assistant that decides which domain-specific agents should handle a user's query.\n"
        "Available agents:\n"
        " - agent1: Math and Pollution-related queries (keywords: add, subtract, pollution, air quality, AQI, math, calculate)\n"
        " - agent2: Weather-related queries (keywords: temperature, weather, humidity, forecast, rain, city weather)\n\n"
        "Your task: Detect **all relevant domains** in a single query, not just one.\n"
        "If a query involves both math and weather, return both.\n\n"
        "Return ONLY a valid JSON in this exact format:\n"
        "{\n"
        "  \"selected_agents\": [\"agent1\", \"agent2\"],\n"
        "  \"reason\": {\n"
        "     \"agent1\": \"reason why this agent is relevant\",\n"
        "     \"agent2\": \"reason why this agent is relevant\"\n"
        "  }\n"
        "}\n\n"
        "Example:\n"
        "User: 'Add 5 and 10 and tell me the weather in Paris'\n"
        "Response:\n"
        "{\n"
        "  \"selected_agents\": [\"agent1\", \"agent2\"],\n"
        "  \"reason\": {\n"
        "    \"agent1\": \"Math operation detected (add 5 and 10)\",\n"
        "    \"agent2\": \"Weather query detected (weather in Paris)\"\n"
        "  }\n"
        "}"
    ),
    "mcp_servers": []
    },

    "agent1": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": (
            "You are a math and pollution expert. Use math and pollution tools to answer precisely.\n"
            "Always start your answer with 'Final Answer:'."
        ),
        "mcp_servers": ["math_server", "pollution-mcp_server"],
    },

    "agent2": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": (
            "You are a weather analyst. Use the weather tools to provide concise and accurate updates.\n"
            "Always start your answer with 'Final Answer:'."
        ),
        "mcp_servers": ["weather-mcp_server"],
    },
}
