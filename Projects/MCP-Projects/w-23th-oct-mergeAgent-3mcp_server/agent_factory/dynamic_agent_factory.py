# agent_factory/dynamic_agent_factory.py
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from mcp_clients.universal_mcp_client import load_all_mcp_tools

class DynamicAgentFactory:
    def __init__(self, config):
        self.config = config
        self.registry = {}

    async def create_agent(self, name: str):
        if name not in self.config:
            raise ValueError(f"Agent '{name}' not found in configuration.")
        cfg = self.config[name]

        llm = ChatOpenAI(model=cfg["llm_model"], temperature=0.2)
        tools = []

        # Load MCP tools
        try:
            tools = await load_all_mcp_tools(cfg)
        except Exception as e:
            print(f"⚠️ Tool load failed for {name}: {e}")

        # No tools → router or plain LLM agent
        if not tools:
            prompt = PromptTemplate(
                input_variables=["input"],
                template=cfg["system_prompt"] + "\nUser query: {input}"
            )
            agent = LLMChain(llm=llm, prompt=prompt)
            print(f"✅ Created simple LLM chain for {name} (router or plain agent).")
        else:
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.OPENAI_FUNCTIONS,
                verbose=False,
                handle_parsing_errors=True
            )
            print(f"✅ Created tool-based agent for {name}.")

        self.registry[name] = {"agent": agent}
        return agent

    async def get_agent(self, name: str):
        if name not in self.registry:
            await self.create_agent(name)
        return self.registry[name]["agent"]
