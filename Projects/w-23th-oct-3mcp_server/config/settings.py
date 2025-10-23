import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4o"

AGENT_CONFIG = {
    # Math + Pollution Agent
    "agent_math_env": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": (
            "You are a helpful assistant specializing in mathematics and environmental analysis. "
            "Use the available math and pollution MCP tools effectively. "
            "Always provide the final answer clearly, starting with 'Final Answer:'."
        ),
        "mcp_servers": ["math_server", "pollution-mcp_server"],
    },

    # Weather Agent
    "agent_weather": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": (
            "You are a friendly assistant specializing in weather and environmental insights. "
            "Use the weather MCP tools to provide accurate and concise information. "
            "Always start your main conclusion with 'Final Answer:'."
        ),
        "mcp_servers": ["weather-mcp_server"],
    },

    # Router Agent
    "router_agent": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": (
            "You are a routing assistant. Based on the user query, decide which specialized agent to use.\n\n"
            "Routing Rules:\n"
            "- If the query involves numbers, calculations, or math → use 'agent_math_env'\n"
            "- If it involves AQI, pollution, or air quality → use 'agent_math_env'\n"
            "- If it involves weather, temperature, or forecast → use 'agent_weather'\n"
            "Return only the agent name (e.g., 'agent_math_env' or 'agent_weather')."
        ),
        "mcp_servers": []
    },
}
