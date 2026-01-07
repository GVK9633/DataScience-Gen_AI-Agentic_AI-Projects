from typing import TypedDict,Annotated
from langgraph.graph import add_messages,StateGraph,END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,AIMessage
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant")

class BasicChatstate(TypedDict):
    message : Annotated[list,add_messages]
    
def chatbot(state: BasicChatstate):    
    return{
        "message":[llm.invoke(state["message"])]
    }
graph = StateGraph(BasicChatstate)
graph.add_node("chatbot",chatbot)
graph.set_entry_point("chatbot")
graph.add_edge("chatbot",END)
app = graph.compile()

while True:
    user_input = input("User: ")
    if(user_input in["Exit","end"]):
        break
    else:
        result = app.invoke({
            "message":[HumanMessage(content = user_input)]
        })
        print("AI:",result["message"][-1].content)