from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchainhub import client as hub
# from langchain.agents import create_react_agent, AgentExecutor
from langchain.agents import create_react_agent,AgentExecutor
# from langchain.agents import AgentExecutor
from langchain.tools import tool
import datetime


load_dotenv()

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
    """Return the current date and time in the specified format."""
    current_time = datetime.datetime.now()
    return current_time.strftime(format)

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

query = "What is the current time in London? (You are in India). Just show the current time and not the date"

# Load the React prompt from LangChain Hub
prompt = hub.pull("hwchase17/react")

tools = [get_system_time]

# Create ReAct agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# Run
response = agent_executor.invoke({"input": query})
print(response)
