from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

memory = MemorySaver()

llm = ChatGroq(model="llama-3.1-8b-instant")

class BasicChatState(TypedDict): 
    messages: Annotated[list, add_messages]

def chatbot(state: BasicChatState): 
    return {
       "messages": [llm.invoke(state["messages"])]
    }

graph = StateGraph(BasicChatState)

graph.add_node("chatbot", chatbot)

graph.add_edge("chatbot", END)

graph.set_entry_point("chatbot")

app = graph.compile(checkpointer=memory)

config = {"configurable": {
    "thread_id": 1
}}

result = app.invoke({
            "messages": [HumanMessage(content="Hi, I am vijay")]
        },config=config)
result1 = app.invoke({
            "messages": [HumanMessage(content="What is my name")]
        },config=config)

# print(result)
# print(result1)
print("AI: " + result["messages"][-1].content)
print("AI-1: " + result1["messages"][-1].content)
# print(app.get_state(config=config))
