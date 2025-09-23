from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agents.state import State
from tools.weather_tools import get_weather
from tools.order_tools import place_order
from config import OPENAI_API_KEY, DEFAULT_MODEL

def create_agent(memory):
    tools = [get_weather, place_order]
    
    llm = ChatOpenAI(model=DEFAULT_MODEL).bind_tools(tools)

    def chatbot_node(state: State):
        msg = llm.invoke(state["messages"])
        return {"messages": [msg]}
    
    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot_node)
    builder.add_node("tools", ToolNode(tools))
    
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    builder.add_edge("chatbot", END)
    
    # # Visualize the graph
    # print("\n=== ASCII Graph ===")
    # builder.print_ascii()

    # print("\n=== Mermaid Graph ===")
    # print(builder.draw_mermaid())
    
    # return builder.compile(checkpointer=memory)
    graph = builder.compile(checkpointer=memory)

   # get the drawable graph object
    drawable = graph.get_graph()

    # Mermaid text
    print("\n=== Mermaid =====")
    print(drawable.draw_mermaid())

    # PNG image (if dependencies exist)
    try:
        from IPython.display import Image, display
        img = drawable.draw_mermaid_png()
        # display(Image(img))
        with open("graph.png", "wb") as f:
            f.write(img)
        print("Graph saved as graph.png — open it in VS Code Explorer.")
    except Exception as e:
        print("Could not draw PNG:", e)

    # ASCII (if supported)
    if hasattr(drawable, "draw_ascii"):
        print("\n=== ASCII =====")
        print(drawable.draw_ascii())
    else:
        print("ASCII draw not supported in this version")

    return graph
