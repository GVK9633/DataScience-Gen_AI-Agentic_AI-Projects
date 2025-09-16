import asyncio
from agent_factory import load_config, build_agent
from rag.vectorstore import setup_vectorstore
import os
from dotenv import load_dotenv
import nest_asyncio

# Load API keys and other environment variables
load_dotenv()

# Allow nested event loops (fixes RuntimeError in Jupyter/interactive environments)
nest_asyncio.apply()

async def main():
    config = load_config()

    vectordb = setup_vectorstore()
    print("✅ Vectorstore ready with documents.")

    weather_agent = await build_agent("weather", config)
    pollution_agent = await build_agent("pollution", config)

    print("🤖 Agents loaded:", list(config["agents"].keys()))

    query = "What is the weather in London and pollution in Delhi?"
    response_weather = await weather_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    response_pollution = await pollution_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    
    print("🌦 Weather Agent:", response_weather["messages"][-1].content)
    print("🏭 Pollution Agent:", response_pollution["messages"][-1].content)

# if __name__ == "__main__":
#     asyncio.run(main())
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # fallback for already running event loop
        print("⚠️ asyncio.run() failed, using alternative loop:", e)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
