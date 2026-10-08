import importlib
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.tools.render import render_text_description
from langchain import hub
from mcp_clients.universal_mcp_client import load_all_mcp_tools


class DynamicAgentFactory:
    """
    Dynamically creates and manages LangChain/LangGraph agents
    based on a provided configuration.
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
        print(f"   ↳ MCP Servers: {agent_cfg.get('mcp_servers', [])}")

        # 1️⃣ Load LLM
        llm = ChatOpenAI(
            model=agent_cfg["llm_model"], 
            temperature=agent_cfg.get("temperature", 0.2)
        )

        # 2️⃣ Dynamically import tools from MCP clients
        tools = []
        try:
            tools = await load_all_mcp_tools(agent_cfg)
            print(f"   ↳ Loaded {len(tools)} tools")
        except Exception as e:
            print(f"⚠️ Error loading MCP tools for {name}: {e}")

        # 3️⃣ Use STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION for JSON tools
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # CHANGED THIS
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=False
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