from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# ✅ PostgreSQL imports
# pip install langgraph-checkpoint-postgres
from langgraph.checkpoint.postgres import PostgresSaver

# pip install psycopg
import psycopg

load_dotenv()

# ---------------- POSTGRES CONNECTION ----------------
# conn = psycopg.connect(
#     host="localhost",
#     port=5432,
#     dbname="langgraph_checkpoint",
#     user="postgres",
#     password="admin"  # change as per your setup
# )
conn = psycopg.connect(
    "postgresql://postgres:admin@localhost:5432/langgraph_checkpoint"
)


checkpointer = PostgresSaver(conn)

# ---------------- LLM ----------------
llm = ChatGroq(model="llama-3.1-8b-instant")

# ---------------- STATE ----------------
class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]

# ---------------- NODE ----------------
def chatbot(state: BasicChatState):
    return {
        "messages": [llm.invoke(state["messages"])]
    }

# ---------------- GRAPH ----------------
graph = StateGraph(BasicChatState)

graph.add_node("chatbot", chatbot)
graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)

# ✅ Compile with Postgres checkpointer
app = graph.compile(checkpointer=checkpointer)

# ---------------- CONFIG ----------------
config = {
    "configurable": {
        "thread_id": "chat-user-1" , # important for persistence
        "checkpoint_ns": "default"
    }
}

# ---------------- CHAT LOOP ----------------
while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "end"]:
        break

    result = app.invoke(
        {
            "messages": [HumanMessage(content=user_input)]
        },
        config=config
    )

    print("AI:", result["messages"][-1].content)


# DROP TABLE IF EXISTS checkpoint_blobs CASCADE;

# CREATE TABLE checkpoint_blobs (
#     id TEXT PRIMARY KEY,
#     blob BYTEA NOT NULL
# );

# DROP TABLE IF EXISTS checkpoints CASCADE;

# CREATE TABLE checkpoints (
#     id TEXT PRIMARY KEY,
#     thread_id TEXT NOT NULL,
#     checkpoint_ns TEXT NOT NULL,
#     checkpoint_id TEXT NOT NULL,
#     parent_id TEXT,
#     created_at TIMESTAMPTZ DEFAULT NOW(),
#     metadata JSONB,
#     FOREIGN KEY (checkpoint_id) REFERENCES checkpoint_blobs(id)
# );

# CREATE INDEX idx_checkpoints_thread
# ON checkpoints(thread_id, checkpoint_ns, created_at DESC);

