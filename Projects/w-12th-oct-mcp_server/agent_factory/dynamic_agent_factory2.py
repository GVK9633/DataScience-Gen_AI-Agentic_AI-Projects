# agent_factory/dynamic_agent_factory.py

import importlib
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.llms import OpenAI
from mcp_clients.universal_mcp_client import run_mcp_query


class DynamicAgentFactory:
    """
    Dynamically loads tools from multiple MCP servers and creates
    a ZeroShot agent that can handle various domains (e.g., math, pollution).
    """

    def __init__(self, agent_cfg):
        self.agent_cfg = agent_cfg
        self.agents = {}

    async def get_agent(self, agent_name: str):
        """Create or fetch an existing agent based on the config."""
        if agent_name in self.agents:
            print(f"🔁 Using cached agent: {agent_name}")
            return self.agents[agent_name]

        # Validate configuration
        if agent_name not in self.agent_cfg:
            raise ValueError(f"❌ Agent '{agent_name}' not found in configuration.")

        agent_cfg = self.config[agent_name]
        print(f"🔧 Creating agent: {agent_name}")
        print(f"   ↳ LLM: {agent_cfg['llm_model']}")
        print(f"   ↳ MCP Servers: {agent_cfg['mcp_servers']}")
        
     
        # llm_model = agent_info.get("llm", "gpt-4o-mini")
        llm_model = agent_cfg['llm_model']
        # mcp_servers = agent_info.get("mcp_servers", [])
        mcp_servers = agent_cfg['mcp_servers']

        print(f"🔧 Creating agent: {agent_name}")
        print(f"   ↳ LLM: {llm_model}")
        print(f"   ↳ MCP Servers: {mcp_servers}")

        # Load all tools from listed MCP servers
        tools = await self.load_all_mcp_tools(mcp_servers)

        if not tools:
            raise ValueError("❌ Got no tools for ZeroShotAgent. At least one tool must be provided.")

        # Initialize the LLM
        llm = OpenAI(model=llm_model, temperature=0)

        # Create LangChain agent
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        self.agents[agent_name] = agent
        return agent

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
