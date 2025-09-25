import asyncio
from langgraph.graph import StateGraph, START, END
from agents.agent_factory import AgentFactory
from agents.parent_agent import llm_router

def build_graph():
    factory = AgentFactory()
    weather_agent = factory.get_agent("weather")
    pollution_agent = factory.get_agent("pollution")

    builder = StateGraph(dict)

    # builder.add_node("parent_router", lambda state: {"next": llm_router(state["prompt"])})
    # builder.add_node("weather", lambda state: {"result": asyncio.run(weather_agent(state))})
    # builder.add_node("pollution", lambda state: {"result": asyncio.run(pollution_agent(state))})

    # builder.add_edge(START, "parent_router")
    # builder.add_conditional_edges(
    #     "parent_router",
    #     lambda out: out["next"],
    #     {"weather": "weather", "pollution": "pollution", "end": END}
    # )
    # builder.add_edge("weather", END)
    # builder.add_edge("pollution", END)

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

      # === Graph Visualization ===
    drawable = graph.get_graph()

    # Mermaid
    print("\n=== Mermaid =====")
    print(drawable.draw_mermaid())

    # PNG
    try:
        from IPython.display import Image, display
        img = drawable.draw_mermaid_png()
        with open("graph1.png", "wb") as f:
            f.write(img)
        print("Graph saved as graph.png — open it in VS Code Explorer.")
    except Exception as e:
        print("Could not draw PNG:", e)

    # ASCII
    if hasattr(drawable, "draw_ascii"):
        print("\n=== ASCII =====")
        print(drawable.draw_ascii())
    else:
        print("ASCII draw not supported in this version")
        
if __name__ == "__main__":
    main()