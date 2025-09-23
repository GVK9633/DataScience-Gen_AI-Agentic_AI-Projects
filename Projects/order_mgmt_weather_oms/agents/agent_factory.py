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
    
    # Visualize the graph
    # print(builder.get_graph().draw_mermaid())
    # builder.get_graph().print_ascii()
    
    return builder.compile(checkpointer=memory)
