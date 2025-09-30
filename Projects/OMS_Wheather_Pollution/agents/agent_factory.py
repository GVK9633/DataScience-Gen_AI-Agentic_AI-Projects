# agents/agent_factory.py
from config.settings import AGENT_CONFIG
from tools import weather_tools, pollution_tools
import importlib

TOOL_MAP = {
    "get_city_weather": weather_tools.get_city_weather,
    "get_country_weather": weather_tools.get_country_weather,
    "get_city_pollution": pollution_tools.get_city_pollution,
    "get_country_pollution": pollution_tools.get_country_pollution
}

class DynamicAgent:
    def __init__(self, name: str):
        if name not in AGENT_CONFIG:
            raise ValueError(f"Unknown agent: {name}")
        self.name = name
        self.cfg = AGENT_CONFIG[name]
        # self.tools = [TOOL_MAP[t] for t in self.cfg.get("tools", [])]
        self.tools = self._load_tools()
        
    def _load_tools(self):
        """
        Dynamically load tool functions based on AGENT_CONFIG.
        Each tool name must follow <module>.<function> OR
        be registered inside a corresponding <agent>_tools.py file.
        """
        tool_funcs = []
        for tool_name in self.cfg.get("tools", []):
            # Dynamically figure out which module to load from agent name
            module_name = f"tools.{self.name}_tools"
            try:
                module = importlib.import_module(module_name)
                func = getattr(module, tool_name)
                tool_funcs.append(func)
            except (ImportError, AttributeError) as e:
                raise ImportError(f"❌ Tool {tool_name} not found in {module_name}") from e
        return tool_funcs    
        
        
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