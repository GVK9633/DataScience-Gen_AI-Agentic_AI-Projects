# agents/agent_factory.py
from config.settings import AGENT_CONFIG
from tools import weather_tools, pollution_tools

TOOL_MAP = {
    "get_city_weather": weather_tools.get_city_weather,
    "get_country_weather": weather_tools.get_country_weather,
    "get_city_pollution": pollution_tools.get_city_pollution,
    "get_country_pollution": pollution_tools.get_country_pollution
}

class DynamicAgent:
    def __init__(self, name: str):
        self.cfg = AGENT_CONFIG[name]
        self.tools = [TOOL_MAP[t] for t in self.cfg.get("tools", [])]

    # Make run async
    async def run(self, target: str):
        results = []
        # Run each tool asynchronously
        for tool in self.tools:
            res = await tool(target)  # <- await coroutine
            results.append(res)
        return " | ".join(results)

class AgentFactory:
    @staticmethod
    def create_agent(name: str):
        if name in AGENT_CONFIG:
            return DynamicAgent(name)
        raise ValueError(f"Unknown agent: {name}")