import asyncio
from mcp_client.weather_mcp_client import WeatherMCPClient
from langgraph.graph import StateGraph, END
from typing_extensions import Annotated
from langchain_openai import ChatOpenAI
import os
import json
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5,
                 api_key=os.getenv("OPENAI_API_KEY"))

class AgentState(dict):
    query: str
    targets: dict           # {"weather": [{"location": "Paris", "forecast_type": "today"}]}
    results: Annotated[dict, "aggregate"]
    final: str

# --- Node 1: Parent LLM classifies user query ---
async def classify_query(state: AgentState) -> AgentState:
    prompt = f"""
    You are a world-class weather assistant.
    Extract all relevant locations, zip codes, countries, districts, and forecast types (today, tomorrow, 3-day, 7-day)
    from this user query: "{state['query']}".
    Output strictly as JSON like:
    {{
        "weather": [
            {{"location": "Paris", "forecast_type": "today"}}
        ]
    }}
    """
    # content = await llm.invoke(prompt).content.strip()
    response = await llm.ainvoke(prompt)
    content = response.content.strip() 
    if content.startswith("```"):
        content = content.strip("`").split("json")[-1].strip()
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"weather": [{"location": state["query"], "forecast_type": "today"}]}
    state["targets"] = parsed
    state["results"] = {}
    return state

# --- Node 2: Call weather MCP ---
def call_weather_node():
    async def node(state: AgentState) -> AgentState:
        client = WeatherMCPClient()
        weather_targets = state.get("targets", {}).get("weather", [])
        results = {}
        for item in weather_targets:
            loc = item.get("location")
            forecast = item.get("forecast_type", "today")
            res = await client.get_weather(loc, forecast)
            results[f"{loc} ({forecast})"] = res.get("content")
        return {"results": {"weather": results}}
    return node

# --- Node 3: merge results ---
async def merge_results(state: AgentState) -> AgentState:
    state["final"] = state.get("results", {})
    return state

# --- Build workflow ---
workflow = StateGraph(AgentState)
workflow.add_node("classify", classify_query)
workflow.set_entry_point("classify")

workflow.add_node("weather", call_weather_node())
workflow.add_edge("classify", "weather")

workflow.add_node("merge", merge_results)
workflow.add_edge("weather", "merge")
workflow.add_edge("merge", END)

app = workflow.compile()

# --- Run ---
async def main():
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
           break
        result = await app.ainvoke({"query": query})
        print("🌍 Weather Result:\n", result["final"])

if __name__ == "__main__":
    asyncio.run(main())