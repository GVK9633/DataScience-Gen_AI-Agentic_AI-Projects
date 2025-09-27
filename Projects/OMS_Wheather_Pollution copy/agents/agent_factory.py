# agents/agent_factory.py
from config.settings import AGENT_CONFIG
from tools import weather_tools, pollution_tools

class AgentFactory:
    def __init__(self):
        self.agents = {}

    def build_agent(self, agent_name: str):
        if agent_name not in AGENT_CONFIG:
            raise ValueError(f"Unknown agent: {agent_name}")

        config = AGENT_CONFIG[agent_name]

        if agent_name == "weather":
            async def run(task: dict):
                city = task.get("city")
                if not city:
                    return "Weather agent: no city provided"
                return await weather_tools.get_city_weather(city)

        elif agent_name == "pollution":
            async def run(task: dict):
                city = task.get("city")
                if not city:
                    return "Pollution agent: no city provided"
                return await pollution_tools.get_city_pollution(city)

        else:
            async def run(task: dict):
                return f"{agent_name} agent not implemented"

        self.agents[agent_name] = run
        return run

    def get_agent(self, agent_name: str):
        return self.agents.get(agent_name) or self.build_agent(agent_name)
