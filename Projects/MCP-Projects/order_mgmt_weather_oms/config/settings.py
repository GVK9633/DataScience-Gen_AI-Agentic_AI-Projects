import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o"  # change to "gpt-4.1-mini" if you want cheaper

# Optional helper if you want dict-style access
def load_settings():
    return {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "DEFAULT_MODEL": DEFAULT_MODEL,
    }
