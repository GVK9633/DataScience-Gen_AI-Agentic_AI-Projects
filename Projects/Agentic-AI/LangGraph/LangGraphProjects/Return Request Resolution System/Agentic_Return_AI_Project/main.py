
from langgraph.graph import StateGraph, END
from state import ReturnState

from agents.parent_agent import parent_agent
from agents.policy_agent import policy_agent
from agents.order_agent import order_agent
from agents.decision_agent import decision_agent
from agents.communication_agent import communication_agent
from agents.route_from_parent import route_from_parent  

graph = StateGraph(ReturnState)

graph.add_node("parent", parent_agent)
graph.add_node("policy_agent", policy_agent)
graph.add_node("order_agent", order_agent)
graph.add_node("decision_agent", decision_agent)
graph.add_node("communication_agent", communication_agent)

graph.set_entry_point("parent")

graph.add_conditional_edges(
    "parent",
    route_from_parent,
    {
        "policy_agent": "policy_agent",
        "communication_agent": "communication_agent"
    }
)

graph.add_edge("policy_agent", "order_agent")
graph.add_edge("order_agent", "decision_agent")
graph.add_edge("decision_agent", "communication_agent")
graph.add_edge("communication_agent", END)

app = graph.compile()

result = app.invoke({
    "input": "I want to return my laptop"
    # "input": "I want to cost my laptop"
})

print("Final Response:", result["response"])
