from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END, add_messages
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()

# -------------------------
# LLM
# -------------------------
llm = ChatGroq(model="llama-3.1-8b-instant")

# -------------------------
# State
# -------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]
    review_decision: str | None

# -------------------------
# Nodes
# -------------------------
def generate_post(state: State):
    """Generate LinkedIn post"""
    ai_message = llm.invoke(state["messages"])
    return {"messages": [ai_message]}


def review_node(state: State):
    """Human reviews the post"""
    post_content = state["messages"][-1].content

    print("\n📢 Generated LinkedIn Post:\n")
    print(post_content)
    print("\n")

    decision = input("Post to LinkedIn? (yes/no): ").strip().lower()
    return {"review_decision": decision}


def collect_feedback(state: State):
    """Collect human feedback"""
    feedback = input("How can I improve this post? ")
    return {
        "messages": [HumanMessage(content=feedback)],
        "review_decision": None
    }


def post_node(state: State):
    """Final post action"""
    final_post = state["messages"][-1].content

    print("\n✅ Final LinkedIn Post:\n")
    print(final_post)
    print("\n🚀 Post approved and published!")
    return {}

# -------------------------
# Router
# -------------------------
def review_router(state: State):
    if state["review_decision"] == "yes":
        return "post"
    return "collect_feedback"

# -------------------------
# Graph
# -------------------------
graph = StateGraph(State)

graph.add_node("generate_post", generate_post)
graph.add_node("review", review_node)
graph.add_node("collect_feedback", collect_feedback)
graph.add_node("post", post_node)

graph.set_entry_point("generate_post")

graph.add_edge("generate_post", "review")

graph.add_conditional_edges(
    "review",
    review_router,
    {
        "post": "post",
        "collect_feedback": "collect_feedback"
    }
)

graph.add_edge("collect_feedback", "generate_post")
graph.add_edge("post", END)

app = graph.compile()

# -------------------------
# Run
# -------------------------
app.invoke({
    "messages": [
        HumanMessage(
            content="Write a LinkedIn post on AI Agents transforming content creation"
        )
    ],
    "review_decision": None
})
