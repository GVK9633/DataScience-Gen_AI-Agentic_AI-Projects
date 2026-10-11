#### tools, google search -> 
from dotenv import load_dotenv
load_dotenv()

from langchain_aws import ChatBedrockConverse
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_nimble import NimbleSearchTool

#### prompt + tools + llm
NIMBLE_API_KEY = "<YOUR_NIMBLE_API_KEY>"
MODEL = "us.anthropic.claude-sonnet-4-6"
REGION = "us-east-1"

llm = ChatBedrockConverse(
    model=MODEL,
    region_name=REGION
)

@tool
def google_search(query:str):
    """
        Search anything on google for real time data and news.
        Args:
            query - user asked query
    """
    nimble_search = NimbleSearchTool(
        k=5,
        deep_search=True,
        api_key=NIMBLE_API_KEY
    )
    
    res = nimble_search.invoke(query)
    return res
    
    
    

agent = create_agent(
    model=llm,
    tools=[google_search],
    system_prompt="""
        You are a search agent, for real time details you always call 'google_search' tool,
        And provide the correct answer.
        """
)
