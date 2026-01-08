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

def setup_database():
    """Setup database with correct schema directly in Python"""
    try:
        # Connect to PostgreSQL
        conn = psycopg.connect(
            "postgresql://postgres:admin@localhost:5432/langgraph_checkpoint"
        )
        print("✅ Connected to PostgreSQL successfully")
        
        # SQL schema definition - CORRECTED based on official LangGraph requirements
        sql_schema = """
        -- Drop tables if they exist
        DROP TABLE IF EXISTS checkpoints CASCADE;
        DROP TABLE IF EXISTS checkpoint_blobs CASCADE;

        -- Create checkpoint_blobs table with thread_id column
        CREATE TABLE checkpoint_blobs (
            id TEXT PRIMARY KEY,
            thread_id TEXT NOT NULL,  -- Added this column
            checkpoint_ns TEXT NOT NULL,  -- Added this column
            blob BYTEA NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Create checkpoints table
        CREATE TABLE checkpoints (
            id TEXT PRIMARY KEY,
            thread_id TEXT NOT NULL,
            checkpoint_ns TEXT NOT NULL,
            checkpoint_id TEXT NOT NULL,
            parent_checkpoint_id TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            metadata JSONB,
            checkpoint JSONB NOT NULL,
            FOREIGN KEY (checkpoint_id, thread_id, checkpoint_ns) 
                REFERENCES checkpoint_blobs(id, thread_id, checkpoint_ns) ON DELETE CASCADE
        );

        -- Create indexes for better performance
        CREATE INDEX idx_checkpoints_thread_ns 
        ON checkpoints(thread_id, checkpoint_ns);

        CREATE INDEX idx_checkpoints_created 
        ON checkpoints(created_at DESC);

        CREATE INDEX idx_checkpoints_parent 
        ON checkpoints(parent_checkpoint_id);

        CREATE INDEX idx_checkpoint_blobs_thread_ns 
        ON checkpoint_blobs(thread_id, checkpoint_ns);

        CREATE INDEX idx_checkpoint_blobs_id 
        ON checkpoint_blobs(id);
        """
        
        with conn.cursor() as cur:
            cur.execute(sql_schema)
            conn.commit()
        
        print("✅ Database tables created successfully")
        return conn
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        traceback.print_exc()
        # Try to reconnect if table creation failed
        try:
            conn = psycopg.connect(
                "postgresql://postgres:admin@localhost:5432/langgraph_checkpoint"
            )
            return conn
        except:
            raise

def main():
    # Setup database with correct schema
    conn = setup_database()
    
    # Create checkpointer
    checkpointer = PostgresSaver(conn)
    print("✅ PostgresSaver initialized")
    
    # ---------------- LLM ----------------
    llm = ChatGroq(model="llama-3.1-8b-instant")
    print("✅ LLM initialized")
    
    # ---------------- STATE ----------------
    class BasicChatState(TypedDict):
        messages: Annotated[list, add_messages]
    
    # ---------------- NODE ----------------
    def chatbot(state: BasicChatState):
        try:
            print(f"🤖 Processing message...")
            response = llm.invoke(state["messages"])
            return {"messages": [response]}
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return {"messages": [HumanMessage(content="Sorry, I encountered an error.")]}
    
    # ---------------- GRAPH ----------------
    print("🔧 Building graph...")
    graph = StateGraph(BasicChatState)
    
    graph.add_node("chatbot", chatbot)
    graph.set_entry_point("chatbot")
    graph.add_edge("chatbot", END)
    
    # Compile with Postgres checkpointer
    app = graph.compile(checkpointer=checkpointer)
    print("✅ Graph compiled successfully")
    
    # ---------------- CONFIG ----------------
    config = {
        "configurable": {
            "thread_id": "chat-user-1",
            "checkpoint_ns": "default"
        }
    }
    
    # ---------------- CHAT LOOP ----------------
    print("\n" + "="*50)
    print("🤖 Chatbot is ready! Type 'exit' to quit.")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("👤 User: ").strip()
            
            if user_input.lower() in ["exit", "quit", "end", "bye"]:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                print("⚠️  Please enter a message.")
                continue
            
            print("🔄 Processing...")
            
            # Invoke the chatbot
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            print(f"🤖 AI: {result['messages'][-1].content}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            traceback.print_exc()
            continue
    
    # Cleanup
    conn.close()
    print("✅ Connection closed")

if __name__ == "__main__":
    main()