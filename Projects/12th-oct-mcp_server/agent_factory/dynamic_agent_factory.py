# agent_factory/dynamic_agent_factory.py
import asyncio
import importlib
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from mcp_clients.universal_mcp_client import run_mcp_query


class DynamicAgentFactory:
    """
    Dynamically creates and manages LangChain agents that can
    interact with MCP servers via universal_mcp_client.run_mcp_clent_query().
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.registry = {}

    async def create_agent(self, name: str):
        """
        Create and register an agent dynamically based on configuration.
        """
        if name not in self.config:
            raise ValueError(f"Agent '{name}' not found in configuration.")

        agent_cfg = self.config[name]
        print(f"🔧 Creating agent: {name}")
        print(f"   ↳ LLM: {agent_cfg['llm_model']}")
        print(f"   ↳ MCP Servers: {agent_cfg['mcp_servers']}")

        # 1️⃣ Load LLM
        llm = ChatOpenAI(model=agent_cfg["llm_model"], temperature=0.5)

        # Load all tools from listed MCP servers
        tools = await self.load_all_mcp_tools(agent_cfg['mcp_servers'])
        

        # 3️⃣ Initialize LangChain agent
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
        """Retrieve an agent from the registry or create it if missing."""
        if name not in self.registry:
            await self.create_agent(name)
        return self.registry[name]["agent"]
    
    async def load_all_mcp_tools(self, mcp_servers):
        """Load tools dynamically from multiple MCP servers using the universal MCP client."""
        tools = []

        for mcp_name in mcp_servers:
            try:
                print(f"🔍 Loading tools from {mcp_name}...")
                mcp_tools = await run_mcp_query(mcp_name)
                if mcp_tools:
                    tools.extend(mcp_tools)
                    print(f"✅ Loaded {len(mcp_tools)} tools from {mcp_name}")
                else:
                    print(f"⚠️ No tools found in {mcp_name}")
            except Exception as e:
                print(f"❌ Failed to load tools from {mcp_name}: {e}")

        return tools