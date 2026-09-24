from dotenv import load_dotenv
load_dotenv()

from langchain_core import __version__ as langchain_core_version
print("langchain_core version:", langchain_core_version)
# from langgraph import __version__ as langgraph_version
# print("langgraph version:", langgraph_version)
from importlib.metadata import version

print("langgraph version:", version("langgraph"))
from langchain_openai import __version__ as langchain_openai_version
print("langchain_openai version:", langchain_openai_version)

from langchain_openai import ChatOpenAI

def main():
    llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.7)
    response = llm.invoke("Hello, how are you?")
    print("Response:", response)
    
    print ("completed successfully")


if __name__ == "__main__":
    main()
