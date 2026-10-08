import asyncio
from langgraph.graph import StateGraph, START, END
from agents.agent_factory import AgentFactory
from agents.parent_agent import llm_router

def run_async(coro):
    """Run async coroutines safely"""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Already in an event loop
        return asyncio.get_event_loop().run_until_complete(coro)

def build_graph():
    factory = AgentFactory()
    weather_agent = factory.get_agent("weather")
    pollution_agent = factory.get_agent("pollution")

    builder = StateGraph(dict)

    # Parent router node (LLM-based)
    builder.add_node(
        "parent_router",
        lambda state: {"next_agent": llm_router(state["prompt"])}
    )

    # Weather node
    builder.add_node(
        "weather",
        lambda state: {"weather_result": run_async(weather_agent(state))}
    )

    # Pollution node
    builder.add_node(
        "pollution",
        lambda state: {"pollution_result": run_async(pollution_agent(state))}
    )

    # Connect START
    builder.add_edge(START, "parent_router")

    # Conditional routing based on LLM output
    builder.add_conditional_edges(
        "parent_router",
        lambda out: out["next_agent"],
        {"weather": "weather", "pollution": "pollution", "end": END}
    )

    # Connect to END
    builder.add_edge("weather", END)
    builder.add_edge("pollution", END)

    return builder.compile()

def main():
    graph = build_graph()

    prompts = [
        {"prompt": "What's the weather in Paris?", "city": "Paris"},
        {"prompt": "Check AQI in Delhi", "city": "Delhi"},
        {"prompt": "Tell me a joke"}  # Should route to 'end'
    ]

    for p in prompts:
        print(f"\n📝 Prompt: {p['prompt']}")
        result = graph.invoke(p)
        # Merge possible keys
        if "weather_result" in result:
            print("🤖 Weather:", result["weather_result"])
        elif "pollution_result" in result:
            print("🤖 Pollution:", result["pollution_result"])
        else:
            print("🤖 Response: End of graph / No agent matched.")

    # === Graph Visualization ===
    drawable = graph.get_graph()

    print("\n=== Mermaid =====")
    print(drawable.draw_mermaid())

    try:
        from IPython.display import Image, display
        img = drawable.draw_mermaid_png()
        with open("graph1.png", "wb") as f:
            f.write(img)
        print("Graph saved as graph1.png")
    except Exception as e:
        print("Could not draw PNG:", e)

    if hasattr(drawable, "draw_ascii"):
        print("\n=== ASCII =====")
        print(drawable.draw_ascii())
    else:
        print("ASCII draw not supported in this version")

if __name__ == "__main__":
    main()
