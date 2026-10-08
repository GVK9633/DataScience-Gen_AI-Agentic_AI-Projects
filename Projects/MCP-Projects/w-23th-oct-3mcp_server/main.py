import asyncio
from agent_factory.dynamic_agent_factory import DynamicAgentFactory
from config.settings import AGENT_CONFIG

async def main():
    factory = DynamicAgentFactory(AGENT_CONFIG)
    print("\n🤖 Parent Agent System Initialized\n")

    # ✅ Load router agent (LLM-based)
    router_agent = await factory.get_agent("router_agent")
    print("✅ Router agent loaded.\n")

    while True:
        user_input = input("[User] > ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting system. Goodbye!")
            break

        print("\n🧭 Router deciding which agent to use...\n")

        try:
            route_decision = await router_agent.ainvoke({"input": user_input})

            # ✅ Handle both LLMChain and agent output structures
            selected_agent_name = (
                route_decision.get("output")
                or route_decision.get("text")
                or ""
            ).strip()

            if selected_agent_name not in AGENT_CONFIG:
                print(f"⚠️ Unknown route: '{selected_agent_name}'. Defaulting to 'agent1'.")
                selected_agent_name = "agent1"

            print(f"🤖 Routing to: {selected_agent_name}\n")

            selected_agent = await factory.get_agent(selected_agent_name)
            result = await selected_agent.ainvoke({"input": user_input})

            # ✅ Handle output key variations
            final_answer = result.get("output") or result.get("text") or str(result)
            print(f"🧠 Agent Response:\n{final_answer}\n")

        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
