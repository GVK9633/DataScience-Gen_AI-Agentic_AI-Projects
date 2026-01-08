from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# PostgreSQL imports
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

load_dotenv()

def main():
    # Connect to PostgreSQL
    conn = psycopg.connect(
        "postgresql://postgres:admin@localhost:5432/langgraph_checkpoint"
    )
    
    # Create checkpointer - it will automatically create tables if they don't exist
    checkpointer = PostgresSaver.from_conn(conn, table_name="checkpoints")
    
    # ---------------- LLM ----------------
    llm = ChatGroq(model="llama-3.1-8b-instant")
    
    # ---------------- STATE ----------------
    class BasicChatState(TypedDict):
        messages: Annotated[list, add_messages]
    
    # ---------------- NODE ----------------
    def chatbot(state: BasicChatState):
        response = llm.invoke(state["messages"])
        return {"messages": [response]}
    
    # ---------------- GRAPH ----------------
    graph = StateGraph(BasicChatState)
    
    graph.add_node("chatbot", chatbot)
    graph.set_entry_point("chatbot")
    graph.add_edge("chatbot", END)
    
    # Compile with Postgres checkpointer
    app = graph.compile(checkpointer=checkpointer)
    
    # ---------------- CONFIG ----------------
    config = {
        "configurable": {
            "thread_id": "chat-user-1",
            "checkpoint_ns": "default"
        }
    }
    
    # ---------------- TEST ----------------
    print("Testing chatbot...")
    
    result = app.invoke(
        {"messages": [HumanMessage(content="Hello!")]},
        config=config
    )
    
    print(f"AI: {result['messages'][-1].content}")
    
    # Cleanup
    conn.close()

if __name__ == "__main__":
    main()