# agent_factory/dynamic_agent_factory.py
import importlib
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool


class DynamicAgentFactory:
    """
    Dynamically creates and manages LangChain/LangGraph agents
    based on a provided configuration.

    Each agent can be linked to different MCP servers, LLM models,
    and system prompts dynamically.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.registry = {}

    async def create_agent(self, name: str):
        """
        Create and register an agent dynamically based on config.
        """
        if name not in self.config:
            raise ValueError(f"Agent '{name}' not found in configuration.")

        agent_cfg = self.config[name]
        print(f"🔧 Creating agent: {name}")
        print(f"   ↳ LLM: {agent_cfg['llm_model']}")
        print(f"   ↳ MCP Servers: {agent_cfg['mcp_servers']}")

        # 1️⃣ Load LLM
        llm = ChatOpenAI(model=agent_cfg["llm_model"], temperature=0.5)

        # 2️⃣ Dynamically import tools from MCP clients
        tools = []
        for mcp_name in agent_cfg["mcp_servers"]:
            try:
                module = importlib.import_module(f"mcp_clients.{mcp_name}_client")
                if hasattr(module, "get_tools"):
                    mcp_tools = module.get_tools()
                    tools.extend(mcp_tools)
                    print(f"Loaded {len(mcp_tools)} tools from {mcp_name}")
                else:
                    print(f"No get_tools() function found in {mcp_name}_client")
            except ModuleNotFoundError:
                print(f"MCP client not found: {mcp_name}_client")

        # 3️⃣ Initialize agent
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True,
        )

        # 4️⃣ Store in registry
        self.registry[name] = {
            "llm": llm,
            "tools": tools,
            "agent": agent,
            "system_prompt": agent_cfg.get("system_prompt", ""),
        }

        return agent

    async def get_agent(self, name: str):
        """
        Retrieve an agent from the registry or create it if missing.
        """
        if name not in self.registry:
            await self.create_agent(name)
        return self.registry[name]["agent"]
