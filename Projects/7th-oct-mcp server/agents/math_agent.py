# mcp_agents/math_agent.py

from langchain.agents import Tool

def calculate(expression: str) -> str:
    """Simple safe math evaluator."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"The result of {expression} is {result}"
    except Exception:
        return "Invalid math expression."

def get_tools():
    return [
        Tool(
            name="Math",
            func=calculate,
            description="Useful for performing arithmetic or math operations.",
        )
    ]
