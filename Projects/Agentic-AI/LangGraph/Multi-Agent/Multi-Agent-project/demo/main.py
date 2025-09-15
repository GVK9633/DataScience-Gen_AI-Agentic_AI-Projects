import asyncio
from agent_factory import load_config, build_agent
from rag.vectorstore import setup_vectorstore

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

if __name__ == "__main__":
    asyncio.run(main())
