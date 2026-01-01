from typing import List, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

from chains import generation_chain, reflection_chain

load_dotenv()

# --------------------
# Constants
# --------------------
GENERATE = "generate"
REFLECT = "reflect"

# --------------------
# State Definition
# --------------------
class GraphState(TypedDict):
    messages: List[BaseMessage]

# --------------------
# Create Graph
# --------------------
graph = StateGraph(GraphState)

# --------------------
# Nodes
# --------------------
def generate_node(state: GraphState) -> GraphState:
    response = generation_chain.invoke({
        "messages": state["messages"]
    })
    return {
        "messages": state["messages"] + [response]
    }

def reflect_node(state: GraphState) -> GraphState:
    response = reflection_chain.invoke({
        "messages": state["messages"]
    })
    return {
        "messages": state["messages"] + [
            HumanMessage(content=response.content)
        ]
    }

# --------------------
# Conditional Logic
# --------------------
def should_continue(state: GraphState):
    if len(state["messages"]) > 4:
        return END
    return REFLECT

# --------------------
# Build Graph
# --------------------
graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)

graph.set_entry_point(GENERATE)

graph.add_conditional_edges(GENERATE, should_continue)
graph.add_edge(REFLECT, GENERATE)

# --------------------
# Compile
# --------------------
app = graph.compile()

# --------------------
# Debug / Visualization
# --------------------
print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

# --------------------
# Invoke
# --------------------
response = app.invoke({
    "messages": [
        HumanMessage(content="AI Agents taking over content creation")
    ]
})

print(response)
