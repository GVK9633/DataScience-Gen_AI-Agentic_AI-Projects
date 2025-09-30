from config.settings import AGENT_CONFIG
from openai import OpenAI
from langgraph.graph import StateGraph, END
from agents.agent_factory import AgentFactory
import os
import json
from typing_extensions import Annotated

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AgentState(dict):
    query: str
    # query: Annotated[list[str], "aggregate"]
    targets: dict      # e.g., {"weather": "Paris"}
    # Mark 'results' as Annotated to allow concurrent updates
    results: Annotated[dict, "concurrent"]
    
    final: str

# --- LLM classification ---
def classify_query(state: AgentState) -> AgentState:
    prompt = f"""
    Extract which agents to call and their target from this query.
    Available agents: {AGENT_CONFIG['parent']['agents']}
    User query: {state['query']}
    Respond strictly in JSON with no extra text.
    Example: {{"weather": "Paris", "pollution": "Delhi"}}
    """
    resp = client.chat.completions.create(
        model=AGENT_CONFIG["parent"]["llm_model"],
        messages=[{"role": "user", "content": prompt}]
    )
    content = resp.choices[0].message.content.strip()
    try:
        # strip code fences if LLM adds ```json
        if content.startswith("```"):
            content = content.strip("`").split("json")[-1].strip()
        parsed = json.loads(content)
    except Exception as e:
        print("⚠️ JSON parse error:", e, "content:", content)
        parsed = {}
    state["targets"] = parsed
    state["results"] = {}
    return state


# --- Call agent node ---
def call_agent(agent_name: str):
    async def node(state: AgentState) -> AgentState:
        targets = state.get("targets", {})
        if not targets:
            return {}
        target = targets.get(agent_name)
        if target:
            agent = AgentFactory.create_agent(agent_name)
            result = await agent.run(target)
            return {"results": {agent_name: result}}
        return {}
    return node


# --- Merge results ---
def merge_results(state: AgentState) -> AgentState:
    if not state["results"]:
        state["final"] = "❌ No results found."
    else:
        state["final"] = " | ".join(f"{k}: {v}" for k, v in state["results"].items())
    return state

# --- Build graph ---
workflow = StateGraph(AgentState)
workflow.add_node("classify", classify_query)
workflow.set_entry_point("classify")

for agent_name in AGENT_CONFIG["parent"]["agents"]:
    workflow.add_node(agent_name, call_agent(agent_name))
    workflow.add_edge("classify", agent_name)
    workflow.add_edge(agent_name, "merge")

workflow.add_node("merge", merge_results)
workflow.add_edge("merge", END)

app = workflow.compile()