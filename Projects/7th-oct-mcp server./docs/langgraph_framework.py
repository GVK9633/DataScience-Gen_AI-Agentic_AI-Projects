"""
langgraph_framework.py
A simple, extensible langgraph pattern:
- ParentAgent uses OpenAI LLM to choose an MCP client
- MCP Server (simulated) uses LLM to choose a tool and executes it
- New MCP servers can be registered dynamically

Requirements:
- pip install openai
- Set environment variable OPENAI_API_KEY or replace in code.

Note: This example uses synchronous calls for clarity.
"""

import os
import json
import time
from typing import Any, Dict, Callable, Optional

import openai  # pip install openai
from dotenv import load_dotenv

load_dotenv()

# ------------------------------
# Config / OpenAI helper
# ------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
if OPENAI_API_KEY is None:
    raise RuntimeError("Set OPENAI_API_KEY environment variable")

openai.api_key = OPENAI_API_KEY

def call_llm_chat(system: str, user_prompt: str, model: str = "gpt-4o", max_tokens: int = 400) -> str:
    """
    Call the OpenAI chat completions endpoint and return text.
    (Adjust for your openai SDK version if required.)
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt}
    ]
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens
    )
    # Note: SDK shape may differ by version; this uses the classic response layout.
    return resp.choices[0].message.content.strip()

# ------------------------------
# Plugin registry for MCP clients
# ------------------------------
MCP_REGISTRY: Dict[str, Callable] = {}

def register_mcp(name: str):
    """Decorator to register an MCP client factory"""
    def decorator(factory):
        MCP_REGISTRY[name] = factory
        return factory
    return decorator

# ------------------------------
# Parent Agent
# ------------------------------
class ParentAgent:
    def __init__(self, system_prompt: str = "You are a routing agent."):
        self.system_prompt = system_prompt

    def route(self, user_input: str) -> Dict[str, Any]:
        """
        1) Ask LLM to reason about the user's input and select an MCP server (one of MCP_REGISTRY keys)
        2) If an MCP is selected, call its client with the original input.
        3) Return final result (structured)
        """

        # Ask LLM to return JSON with fields: { "mcp": "<name or none>", "reasoning": "...", "mcp_payload": {...} }
        router_prompt = (
            "Given the user input, decide which MCP server should handle it. "
            "Return a JSON object exactly with keys: mcp (string or null), reasoning (string), mcp_payload (object).\n\n"
            "Available MCP options: " + ", ".join(MCP_REGISTRY.keys()) + "\n\n"
            f"User input: '''{user_input}'''"
        )

        llm_resp = call_llm_chat(self.system_prompt, router_prompt)
        # try to parse JSON from LLM; tolerant parse using heuristics
        parsed = self._parse_json_from_text(llm_resp)

        mcp_name = parsed.get("mcp")
        reasoning = parsed.get("reasoning", "")
        payload = parsed.get("mcp_payload", {})

        result = {"decision": {"mcp": mcp_name, "reasoning": reasoning, "payload": payload}}

        if mcp_name and mcp_name in MCP_REGISTRY:
            client_factory = MCP_REGISTRY[mcp_name]
            client = client_factory()
            mcp_response = client.call(payload.get("text", user_input), meta=payload)
            result["mcp_response"] = mcp_response
        else:
            # No MCP: include LLM's direct answer (if any)
            direct_answer = parsed.get("direct_answer")
            if not direct_answer:
                # fallback: ask LLM for a short answer
                direct_answer = call_llm_chat("You are a helpful assistant.", user_input, max_tokens=200)
            result["direct_answer"] = direct_answer

        return result

    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON-like structure from LLM output.
        If the LLM returns text plus JSON, try to find first {...}.
        """
        text = text.strip()
        # naive search for JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                j = json.loads(text[start:end+1])
                return j
            except Exception:
                pass
        # fallback: try to interpret a simpler pattern
        return {"mcp": None, "reasoning": text, "mcp_payload": {}}


# ------------------------------
# Example MCP servers (simulated)
# ------------------------------
class BaseMCPServer:
    """
    Base MCP Server - real implementation would be a network service.
    Server may itself call LLM to decide which tool to use.
    """

    def call(self, text: str, meta: Optional[Dict] = None) -> Dict[str, Any]:
        raise NotImplementedError()

# Weather MCP
@register_mcp("weather_mcp")
class WeatherMCPClient:
    def __init__(self):
        # in a real system this might hold endpoint URL/config
        self.server = WeatherMCPServer()

    def call(self, text: str, meta: Optional[Dict] = None) -> Dict[str, Any]:
        return self.server.handle(text, meta or {})

class WeatherMCPServer(BaseMCPServer):
    def handle(self, text: str, meta: Dict) -> Dict[str, Any]:
        # Ask LLM: from the user text, what city/date to use; return JSON {tool: "openweather", params: {...}}
        prompt = (
            "You are the weather MCP. Parse the user's request, decide which tool to call and return JSON with keys:\n"
            '{"tool": "<tool_name or none>", "params": {...}, "reasoning": "..."}\n\n'
            f"User text: '''{text}'''"
        )
        resp = call_llm_chat("Weather MCP reasoning agent.", prompt)
        parsed = self._parse_json(resp)
        tool = parsed.get("tool")
        params = parsed.get("params", {})
        reasoning = parsed.get("reasoning", "")

        if tool == "mock_weather_api":
            # Simulate calling an external weather API using the params
            city = params.get("city", "Unknown")
            date = params.get("date", "today")
            # Simulated result:
            weather_result = {"city": city, "date": date, "forecast": "Sunny, 28C"}
            return {"tool": tool, "params": params, "reasoning": reasoning, "result": weather_result}
        else:
            return {"tool": None, "reasoning": reasoning, "result": f"No tool selected. Raw: {text}"}

    def _parse_json(self, text: str) -> Dict[str, Any]:
        # naive parse similar to ParentAgent
        s = text.strip()
        start = s.find("{"); end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                pass
        # fallback: return no tool
        return {"tool": None, "params": {}, "reasoning": s}

# Math MCP
@register_mcp("math_mcp")
class MathMCPClient:
    def __init__(self):
        self.server = MathMCPServer()

    def call(self, text: str, meta: Optional[Dict] = None) -> Dict[str, Any]:
        return self.server.handle(text, meta or {})

class MathMCPServer(BaseMCPServer):
    def handle(self, text: str, meta: Dict) -> Dict[str, Any]:
        # Ask LLM which operation (calc/eval) and then execute safely
        prompt = (
            "You are the math MCP. Inspect the user text and return JSON: {\"tool\":\"python_eval\" or \"none\", \"expr\":\"<python expression>\", \"reasoning\":\"...\"}\n\n"
            f"User text: '''{text}'''"
        )
        resp = call_llm_chat("Math MCP reasoning agent.", prompt)
        parsed = self._parse_json(resp)
        tool = parsed.get("tool")
        expr = parsed.get("expr")
        reasoning = parsed.get("reasoning", "")

        if tool == "python_eval" and expr:
            # Very restricted eval — do NOT eval arbitrary input in production.
            safe_result = self._safe_eval(expr)
            return {"tool": tool, "expr": expr, "reasoning": reasoning, "result": safe_result}
        return {"tool": None, "reasoning": reasoning, "result": "No operation"}

    def _safe_eval(self, expr: str):
        # super simplistic: allow only numbers and operators
        allowed_chars = "0123456789+-*/().e "
        if not all(c in allowed_chars for c in expr):
            return "Unsafe expression"
        try:
            return eval(expr, {"__builtins__": {}}, {})
        except Exception as e:
            return f"Error: {e}"

    def _parse_json(self, text: str) -> Dict[str, Any]:
        s = text.strip()
        start = s.find("{"); end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                pass
        return {"tool": None, "expr": None, "reasoning": s}

# ------------------------------
# Example usage
# ------------------------------
def example_run():
    parent = ParentAgent(system_prompt="You are a router that returns JSON decisions.")
    tests = [
        "What's the weather in Bengaluru tomorrow morning?",
        "Compute 12345 * 6789",
        "Who won the world cup?"
    ]
    for t in tests:
        print("\n=== USER INPUT ===")
        print(t)
        result = parent.route(t)
        print("=== RESULT ===")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    example_run()