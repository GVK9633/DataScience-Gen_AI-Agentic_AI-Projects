"""
client.py

This is the controller script that connects to multiple MCP tool servers
(weather and email), loads them into a LangGraph AI agent, and performs
automated tool calling using natural language instructions.

"""

# Import the MCP client adapter to connect with multiple MCP tool servers
from langchain_mcp_adapters.client import MultiServerMCPClient

# Import a pre-built LangGraph agent (ReAct logic) for tool reasoning
from langgraph.prebuilt import create_react_agent

# Import ChatGroq model wrapper for using Groq's LLMs (e.g., Qwen)
from langchain_groq import ChatGroq

# Used to load environment variables (e.g., GROQ_API_KEY)
from dotenv import load_dotenv
load_dotenv()  # Load .env file values into the environment

# Import asyncio to run the asynchronous workflow
import asyncio
from langchain.chat_models import init_chat_model
# Main asynchronous function that executes the AI agent logic
async def main():
    # Define the MCP tool servers and their configuration
    client = MultiServerMCPClient(
        {
            "weather": {
                "url": "http://localhost:8000/mcp",  # Weather tool server URL
                "transport": "streamable_http",      # Transport protocol
            },
            # "email": {
            #     "url": "http://localhost:8001/mcp",  # Email tool server URL
            #     "transport": "streamable_http",      # Transport protocol
            # }
        }
    )

    # Load GROQ API key into environment for use by ChatGroq
    
    # os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    # Discover available tools from both MCP servers
    tools = await client.get_tools()

    # Load the Qwen model from Groq
    # model = ChatGroq(model="qwen-qwq-32b")
    import os
    os.environ["OPENAI_API_KEY"] = ""  # <-- paste your real key here

    # Initialize OpenAI GPT model
    model = init_chat_model(
    "gpt-3.5-turbo",
    model_provider="openai",
    temperature=0
    )
    # Create the LangGraph ReAct agent with tools and model
    agent = create_react_agent(model, tools)

    # Step 1: Ask the agent for current weather in Karachi
    weather_response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "what is the current weather in Hyderabad?"}
        ]
    })
    print("Weather response:", weather_response['messages'][-1].content)
    
    response1 = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "Who is the pm of indian in one line?"}
        ]
    })
    print("Who is the pm of indian:", response1['messages'][-1].content)
    
    response2 = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "What is the value of USD?"}
        ]
    })
    print("USD Value:", response2['messages'][-1].content)
    
    response3 = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "What is the value of INR"}
        ]
    })
    print("INR Value:", response3['messages'][-1].content)

    # Extract weather result for use in the email body
    weather_text = weather_response['messages'][-1].content

    # # Step 2: Ask the agent to send an email with the weather update
    # email_response = await agent.ainvoke({
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": (
    #                 f"Send an email to recipient_email@gmail.com with weather update " # addd recipient email
    #                 f"and subject 'Weather Update' and body '{weather_text}'"
    #             )
    #         }
    #     ]
    # })
    # print("Email response:", email_response['messages'][-1].content)

# Run the async workflow
asyncio.run(main())
