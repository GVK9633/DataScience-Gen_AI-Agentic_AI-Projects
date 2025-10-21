import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o"  # change to "gpt-4.1-mini" if you want cheaper


AGENT_CONFIG = {
    "agent1": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": "You are a math expert. Use math tools wisely.",
        "mcp_servers": ["math-mcp"]
    },
    # "agent2": {
    #     "llm": "openai",
    #     "llm_model": "gpt-4o-mini",
    #     "system_prompt": "You are a weather expert. Answer using real-time data.",
    #     "mcp_servers": ["weather-mcp"]
    # },
    "agent3": {
        "llm": "openai",
        "llm_model": "gpt-4o-mini",
        "system_prompt": "You are an environment analyst. Use pollution data tools.",
        "mcp_servers": ["pollution-mcp"]
    }
}