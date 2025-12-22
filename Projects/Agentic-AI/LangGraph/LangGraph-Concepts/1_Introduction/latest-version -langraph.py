from dotenv import load_dotenv
import datetime

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

load_dotenv()

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Returns the current date and time"""
    return datetime.datetime.now().strftime(format)

tools = [get_system_time]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

agent = create_agent(
    model="gpt-5",
    # llm=llm,
    tools=tools
)

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="When was SpaceX's last launch and how many days ago was that from now?"
            )
        ]
    }
)
for event in agent.stream(
    {
        "messages": [
            HumanMessage(content="What time is it now?")
        ]
    }
):
    print(event)

# print(result["messages"][-1].content)
