# agent_factory/dynamic_agent_factory.py
import asyncio
import importlib
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from mcp_clients.universal_mcp_client import run_mcp_clent_query


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

        # 2️⃣ Create dynamic MCP-based tools
        tools = []
        for mcp_name in agent_cfg["mcp_servers"]:
            server_filename = f"{mcp_name}_server.py"
            try:
                module = importlib.import_module(f"mcp_server.math_server")
                if hasattr(module, "get_tools"):
                    math_tools = module.get_tools()
                    tools.extend(math_tools)
                    print(f"Loaded {len(math_tools)} tools from math-mcp")     
            except ModuleNotFoundError:
                print(f"MCP client not found: {mcp_name}_client")
            # server_filename = f"{mcp_name}_server.py"

            # async def run_query(query: str, server_file=server_filename):
            #     """Call MCP server dynamically."""
            #     return await run_mcp_clent_query(query, server_file)

            # # Create a generic tool for that MCP
            # tools.append(
            #     Tool(
            #         name=f"{mcp_name}-query",
            #         func=lambda q, sf=server_filename: asyncio.run(run_query(q, sf)),
            #         description=f"Run dynamic queries for {mcp_name} MCP server",
            #     )
            # )
            # print(f"🧩 Added tool for {mcp_name}")

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
