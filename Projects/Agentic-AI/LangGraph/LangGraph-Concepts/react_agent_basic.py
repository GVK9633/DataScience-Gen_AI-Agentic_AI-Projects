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

# usecsae-1

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in {"exit", "quit"}:
#         print("Bot: Goodbye! 👋")
#         break

#     response = llm([HumanMessage(content=user_input)])
#     print("Bot:", response.content)

# usecase-2
search_tool = TavilySearchResults()
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)