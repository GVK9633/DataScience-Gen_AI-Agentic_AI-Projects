from typing import List, TypedDict

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)

from langgraph.graph import StateGraph, END

from nodes import draft_node, revisor_node
from execute_tools import execute_tools

# ---------------- STATE ----------------
class GraphState(TypedDict):
    messages: List[BaseMessage]

# ---------------- GRAPH ----------------
graph = StateGraph(GraphState)

MAX_ITERATIONS = 2

graph.add_node("draft", draft_node)
graph.add_node("execute_tools", execute_tools)
graph.add_node("revisor", revisor_node)

graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "revisor")

def event_loop(state: GraphState):
    tool_calls = sum(isinstance(m, ToolMessage) for m in state["messages"])
    if tool_calls > MAX_ITERATIONS:
        return END
    return "execute_tools"

graph.add_conditional_edges("revisor", event_loop)
graph.set_entry_point("draft")

app = graph.compile()

# ---------------- RUN ----------------
print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

response = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="Write about how small businesses can leverage AI to grow"
            )
        ]
    }
)

# ---------------- OUTPUT ----------------
final_ai_message = response["messages"][-1]

print("\nFINAL REVISED ANSWER:\n")
print(final_ai_message.tool_calls[0]["args"]["revised_answer"])
print("\nCITATIONS & REFERENCES:\n")