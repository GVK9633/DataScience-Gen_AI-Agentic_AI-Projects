from config.settings import AGENT_CONFIG
from tools import weather_tools, pollution_tools
import asyncio

class AgentFactory:
    def __init__(self):
        self.agents = {}

    def build_agent(self, agent_name: str):
        if agent_name not in AGENT_CONFIG:
            raise ValueError(f"Unknown agent: {agent_name}")

        config = AGENT_CONFIG[agent_name]
        tool_funcs = []

        for tool in config.get("tools", []):
            if hasattr(weather_tools, tool):
                tool_funcs.append(getattr(weather_tools, tool))
            elif hasattr(pollution_tools, tool):
                tool_funcs.append(getattr(pollution_tools, tool))

        async def run(task: dict):
            city = task.get("city")
            country = task.get("country")
            for tool in tool_funcs:
                if city and "city" in tool.__name__:
                    return await tool(city)
                if country and "country" in tool.__name__:
                    return await tool(country)
            return f"{agent_name} agent: No location provided"

        self.agents[agent_name] = run
        return run

    def get_agent(self, agent_name: str):
        return self.agents.get(agent_name) or self.build_agent(agent_name)