from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import traceback

# PostgreSQL imports
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

load_dotenv()

def create_connection():
    """Create PostgreSQL connection with proper error handling"""
    try:
        conn = psycopg.connect(
            "postgresql://postgres:admin@localhost:5432/langgraph_checkpoint"
        )
        print("✅ Connected to PostgreSQL successfully")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        raise

def setup_database():
    """Setup database tables if they don't exist"""
    conn = None
    try:
        conn = create_connection()
        with conn.cursor() as cur:
            # Check if tables exist
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'checkpoints'
                );
            """)
            tables_exist = cur.fetchone()[0]
            
            if not tables_exist:
                print("🔧 Creating database tables...")
                with open("setup_postgres.sql", "r") as f:
                    sql_script = f.read()
                cur.execute(sql_script)
                conn.commit()
                print("✅ Database tables created successfully")
            else:
                print("✅ Database tables already exist")
        
        return conn
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        if conn:
            conn.close()
        raise

def main():
    # Setup database
    conn = setup_database()
    
    # Create checkpointer
    checkpointer = PostgresSaver(conn)
    
    # ---------------- LLM ----------------
    llm = ChatGroq(model="llama-3.1-8b-instant")
    
    # ---------------- STATE ----------------
    class BasicChatState(TypedDict):
        messages: Annotated[list, add_messages]
    
    # ---------------- NODE ----------------
    def chatbot(state: BasicChatState):
        try:
            response = llm.invoke(state["messages"])
            return {"messages": [response]}
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return {"messages": [HumanMessage(content="Sorry, I encountered an error.")]}
    
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
    
    # ---------------- CHAT LOOP ----------------
    print("\n🤖 Chatbot is ready! Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("👤 User: ").strip()
            
            if user_input.lower() in ["exit", "quit", "end"]:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                print("⚠️  Please enter a message.")
                continue
            
            # Invoke the chatbot
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            print(f"🤖 AI: {result['messages'][-1].content}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            continue
    
    # Cleanup
    conn.close()
    print("✅ Connection closed")

if __name__ == "__main__":
    main()
    
    
#     -- Create the required tables for langgraph PostgresSaver
# DROP TABLE IF EXISTS checkpoints CASCADE;
# DROP TABLE IF EXISTS checkpoint_blobs CASCADE;

# -- Table for storing the actual checkpoint data as binary
# CREATE TABLE checkpoint_blobs (
#     id TEXT PRIMARY KEY,
#     blob BYTEA NOT NULL
# );

# -- Table for storing checkpoint metadata and relationships
# CREATE TABLE checkpoints (
#     id TEXT PRIMARY KEY,
#     thread_id TEXT NOT NULL,
#     checkpoint_ns TEXT NOT NULL,
#     checkpoint_id TEXT NOT NULL,
#     parent_id TEXT,
#     created_at TIMESTAMPTZ DEFAULT NOW(),
#     metadata JSONB,
#     checkpoint JSONB NOT NULL,  -- This was missing!
#     FOREIGN KEY (checkpoint_id) REFERENCES checkpoint_blobs(id) ON DELETE CASCADE
# );

# -- Index for efficient querying by thread and namespace
# CREATE INDEX idx_checkpoints_thread_ns 
# ON checkpoints(thread_id, checkpoint_ns);

# -- Index for querying checkpoints in chronological order
# CREATE INDEX idx_checkpoints_created 
# ON checkpoints(created_at DESC);

# -- Index for parent-child relationships
# CREATE INDEX idx_checkpoints_parent 
# ON checkpoints(parent_id);

# -- Index for blob lookups
# CREATE INDEX idx_checkpoint_blobs_id 
# ON checkpoint_blobs(id);