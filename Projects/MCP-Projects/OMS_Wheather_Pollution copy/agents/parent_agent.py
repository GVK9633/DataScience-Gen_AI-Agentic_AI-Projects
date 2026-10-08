from config.settings import AGENT_CONFIG
from openai import OpenAI

def get_llm_client():
    llm_conf = AGENT_CONFIG["parent"]["llm"]
    provider = llm_conf.get("provider", "openai")

    if provider == "openai":
        return OpenAI(), llm_conf["model"]

    # 🔧 Future: extend here for Gemini/Anthropic
    raise ValueError(f"Unsupported LLM provider: {provider}")

def llm_router(prompt: str) -> str:
    """
    Use the configured LLM to decide which agent to call (weather or pollution).
    """
    client, model = get_llm_client()

    routing_prompt = f"""
    You are a router. Decide whether this query is about weather, pollution, or none.

    Query: "{prompt}"

    Respond with only one word: "weather", "pollution", or "end".
    """

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": routing_prompt}],
        max_tokens=1,
    )

    decision = resp.choices[0].message.content.strip().lower()
    if decision not in ["weather", "pollution", "end"]:
        return "end"
    return decision