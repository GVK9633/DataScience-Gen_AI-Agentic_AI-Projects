# agent_factory/dynamic_agent_factory.py
import importlib
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from mcp_clients.universal_mcp_client import load_all_mcp_tools


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
        llm = ChatOpenAI(model=agent_cfg["llm_model"], temperature=0.2)

        # 2️⃣ Dynamically import tools from MCP clients
        tools = []
        try:
            tools = await load_all_mcp_tools(agent_cfg)
        except ModuleNotFoundError:
            print(f"MCP client not found: {name} agent")
       
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
