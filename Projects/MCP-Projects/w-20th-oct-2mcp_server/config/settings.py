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
        "system_prompt": (
                "You are a helpful assistant that uses tools to solve math problems. and You are an environment analyst. Use pollution data tools. "
                "Always provide the final answer clearly, starting with 'Final Answer:'."
                ),
        # "mcp_servers": ["math_server"]
        "mcp_servers": ["math_server","pollution-mcp_server"]
    },
   
}