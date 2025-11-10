from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import initialize_agent, tool
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
import datetime
import os

load_dotenv()

# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7,api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# search_tool = TavilySearchResults(search_depth="basic",api_key=os.getenv("TAVILY_API_KEY"))
search_tool = TavilySearchResults(search_depth="basic")

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
    """ Returns the current date and time in the specified format """

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime(format)
    return formatted_time


tools = [search_tool,get_system_time]

agent = initialize_agent(tools=tools, llm=llm, agent="zero-shot-react-description", verbose=True)
# agent.invoke("give me funny tweet about weather in bangalore  today")
agent.invoke("When was SpaceX's last launch and how many days ago was that from this instant")

