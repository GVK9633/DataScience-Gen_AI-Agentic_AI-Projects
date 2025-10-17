# agent_factory/dynamic_agent_factory.py
import asyncio
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from mcp_client.universal_mcp_client import load_all_mcp_tools

class DynamicAgentFactory:
    """
    Dynamically creates and manages LangChain agents
    that connect to real MCP servers and tools.
    """

    def __init__(self, config: Dict[str, Any], mcp_folder: str):
        self.config = config
        self.registry = {}
        self.mcp_folder = mcp_folder

    async def create_agent(self, name: str):
        if name not in self.config:
            raise ValueError(f"Agent '{name}' not found in configuration.")

        agent_cfg = self.config[name]
        print(f"🔧 Creating agent: {name}")
        print(f"   ↳ LLM: {agent_cfg['llm_model']}")
        print(f"   ↳ MCP Servers: {agent_cfg['mcp_servers']}")

        llm = ChatOpenAI(model=agent_cfg["llm_model"], temperature=0.5)

        # 1️⃣ Dynamically load tools (filter only relevant servers)
        all_tools = await load_all_mcp_tools(self.mcp_folder)
        # selected_tools = [
        #     t for t in all_tools
        #     if any(mcp in t.name or mcp in t.description for mcp in agent_cfg["mcp_servers"])
        # ] or all_tools  # fallback if no name match
        has_mcp_servers = agent_cfg["mcp_servers"]
        selected_tools = [
            t for t in all_tools
            if any(mcp in t.name or mcp in t.description  for mcp in has_mcp_servers)
        ]

        if not selected_tools:  # If no tools matched the filter
            selected_tools = all_tools
        print(f"   ✅ Loaded {len(selected_tools)} tools for agent '{name}'")

        # 2️⃣ Initialize agent
        agent = initialize_agent(
            tools=selected_tools,
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True,
        )

        self.registry[name] = {
            "llm": llm,
            "tools": selected_tools,
            "agent": agent,
            "system_prompt": agent_cfg.get("system_prompt", ""),
        }

        return agent

    async def get_agent(self, name: str):
        if name not in self.registry:
            await self.create_agent(name)
        return self.registry[name]["agent"]