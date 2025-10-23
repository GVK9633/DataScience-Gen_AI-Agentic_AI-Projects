import importlib
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from mcp_clients.universal_mcp_client import load_all_mcp_tools

class DynamicAgentFactory:
    """
    Dynamically creates and manages LangChain agents
    based on configuration in AGENT_CONFIG.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.registry = {}

    async def create_agent(self, name: str):
        if name not in self.config:
            raise ValueError(f"Agent '{name}' not found in configuration.")

        agent_cfg = self.config[name]
        print(f"🔧 Creating agent: {name}")
        print(f"   ↳ LLM: {agent_cfg['llm_model']}")
        print(f"   ↳ MCP Servers: {agent_cfg.get('mcp_servers', [])}")

        llm = ChatOpenAI(model=agent_cfg["llm_model"], temperature=0.2)
        tools = []

        try:
            tools = await load_all_mcp_tools(agent_cfg)
        except Exception as e:
            print(f"⚠️ Error loading MCP tools for {name}: {e}")

        # 🧠 Case 1: Router agent (no tools → plain LLM chain)
        if not tools:
            prompt = PromptTemplate(
                input_variables=["input"],
                template=agent_cfg["system_prompt"] + "\n\nUser query: {input}\n\nYour response:"
            )
            agent = LLMChain(llm=llm, prompt=prompt)
            print(f"✅ Created simple LLM chain for {name} (no tools).")

        # 🧩 Case 2: Normal agent with tools
        else:
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                handle_parsing_errors=True
            )
            print(f"✅ Created tool-based agent for {name} with {len(tools)} tools.")

        self.registry[name] = {
            "llm": llm,
            "tools": tools,
            "agent": agent,
        }

        return agent

    async def get_agent(self, name: str):
        if name not in self.registry:
            await self.create_agent(name)
        return self.registry[name]["agent"]
