import asyncio
from langgraph.graph import StateGraph, START, END
from agents.agent_factory import AgentFactory
from agents.parent_agent import llm_router

def build_graph():
    factory = AgentFactory()
    weather_agent = factory.get_agent("weather")
    pollution_agent = factory.get_agent("pollution")

    builder = StateGraph(dict)

    builder.add_node("parent_router", lambda state: {"next": llm_router(state["prompt"])})
    builder.add_node("weather", lambda state: {"result": asyncio.run(weather_agent(state))})
    builder.add_node("pollution", lambda state: {"result": asyncio.run(pollution_agent(state))})

    builder.add_edge(START, "parent_router")
    builder.add_conditional_edges(
        "parent_router",
        lambda out: out["next"],
        {"weather": "weather", "pollution": "pollution", "end": END}
    )
    builder.add_edge("weather", END)
    builder.add_edge("pollution", END)

    return builder.compile()

def main():
    graph = build_graph()

    prompts = [
        {"prompt": "What's the weather in Paris?", "city": "Paris"},
        {"prompt": "Check AQI in Delhi", "city": "Delhi"},
        {"prompt": "Tell me a joke"}
    ]

    for p in prompts:
        print(f"\n📝 Prompt: {p['prompt']}")
        result = graph.invoke(p)
        print("🤖 Response:", result.get("result"))

if __name__ == "__main__":
    main()