from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain_community.tools import TavilySearchResults

load_dotenv()  # Load environment variables from .env file
import os
os.environ["OPENAI_API_KEY"] = "" 
print(os.environ.get("OPENAI_API_KEY"))
# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Define a simple tool
def search(query: str) -> str:
    return f"Fake search results for: {query}"

search_tool = Tool(
    name="Search",
    func=search,
    description="Useful for when you need to find information"
)

# Define the LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Initialize agent
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Run query
response = agent.run("What is the capital of France?")
print("Agent Response:", response)