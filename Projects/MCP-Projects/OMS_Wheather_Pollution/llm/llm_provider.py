from openai import OpenAI

def get_llm_client(provider: str, model: str):
    if provider == "openai":
        return OpenAI(), model
    # 🔧 Add support for Gemini/Anthropic here
    raise ValueError(f"Unsupported LLM provider: {provider}")