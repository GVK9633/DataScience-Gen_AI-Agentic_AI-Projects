# from langchain.agents import create_agent
# import datetime
# from langchain.tools import tool
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# load_dotenv()

# @tool
# def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
#     """ Returns the current date and time in the specified format """

#     current_time = datetime.datetime.now()
#     formatted_time = current_time.strftime(format)
#     return formatted_time
# tools = [get_system_time]
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
# agent = create_agent("gpt-5", tools=tools)
# agent.invoke("When was SpaceX's last launch and how many days ago was that from this instant")

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

print(result["messages"][-1].content)
