import yaml
import importlib
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model

def load_config(path="config/agents.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

async def build_agent(agent_name, config):
    agent_cfg = config["agents"][agent_name]

    llm_name = agent_cfg.get("llm", "openai")
    if llm_name == "openai":
        llm = init_chat_model("gpt-3.5-turbo", model_provider="openai", temperature=0)
    elif llm_name == "gemini":
        llm = init_chat_model("gemini-pro", model_provider="google", temperature=0)
    else:
        raise ValueError(f"Unknown LLM: {llm_name}")

    mcp_client = None
    if "mcp_servers" in agent_cfg:
        mcp_client = MultiServerMCPClient({
            f"{agent_name}_mcp": {"url": url, "transport": "streamable_http"}
            for url in agent_cfg["mcp_servers"]
        })
        tools = await mcp_client.get_tools()
    else:
        tools = []

    for tool_path in agent_cfg.get("tools", []):
        module, func = tool_path.split(":")
        mod = importlib.import_module(module)
        tools.append(getattr(mod, func))

    return create_react_agent(llm, tools)
