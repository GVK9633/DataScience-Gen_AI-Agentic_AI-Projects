# main.py
import asyncio
from agent_factory.dynamic_agent_factory import DynamicAgentFactory
from config.settings import AGENT_CONFIG

async def main():
    factory = DynamicAgentFactory(AGENT_CONFIG)

    print("\n🤖 Dynamic Agent System Started")
    print("Available agents:", ", ".join(AGENT_CONFIG.keys()))
    print("Type 'switch' to change agent or 'exit' to quit.\n")

    current_agent_name = input("Enter agent name to activate: ").strip()

    while True:
        # Exit or switch logic
        if current_agent_name.lower() in ["exit", "quit"]:
            print("👋 Exiting. Goodbye!")
            break

        try:
            # Create or get agent
            agent = await factory.get_agent(current_agent_name)
            query = input(f"[{current_agent_name}] > ").strip()

            if query.lower() in ["exit", "quit"]:
                print("👋 Exiting. Goodbye!")
                break

            elif query.lower() == "switch":
                print("Available agents:", ", ".join(AGENT_CONFIG.keys()))
                current_agent_name = input("Enter agent name to switch to: ").strip()
                continue

            # Run the query
            print("\n🤔 Thinking...\n")
            result = agent.run(query)
            # result = await agent.invoke(query)
            print(f"🧠 Agent Response:\n{result}\n")

        except ValueError as e:
            print(f"❌ {e}")
            current_agent_name = input("Enter valid agent name: ").strip()
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(main())
