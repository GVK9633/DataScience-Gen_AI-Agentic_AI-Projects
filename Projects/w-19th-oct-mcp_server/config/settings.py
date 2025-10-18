# config/settings.py
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
        "mcp_servers": ["math_server"]
    },
   
}