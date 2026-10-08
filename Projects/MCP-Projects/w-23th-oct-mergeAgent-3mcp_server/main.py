# main.py
import asyncio
import json
import re
from agent_factory.dynamic_agent_factory import DynamicAgentFactory
from config.settings import AGENT_CONFIG


async def handle_router(factory, user_input: str):
    """
    Use the router agent to decide which child agents to call.
    Returns a list of agent names.
    """
    router_agent = await factory.get_agent("router_agent")
    response = await router_agent.ainvoke({"input": user_input})

    # Extract text safely
    raw_text = response.get("text", response) if isinstance(response, dict) else str(response)

    # Try to find JSON in router response
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        print("⚠️ Router returned no JSON, defaulting to agent1.")
        return ["agent1"]

    try:
        parsed = json.loads(json_match.group())
        agent_list = parsed.get("selected_agents", [])
        reasons = parsed.get("reason", {})
        print(f"🧭 Routing reasons:\n{json.dumps(reasons, indent=2)}")
        return agent_list or ["agent1"]
    except Exception as e:
        print(f"⚠️ Failed to parse router JSON: {e}")
        return ["agent1"]


async def query_agents(factory, agents, user_input: str):
    """
    Run the selected child agents concurrently and return their results.
    """
    tasks = []
    for name in agents:
        try:
            agent = await factory.get_agent(name)
            tasks.append(agent.ainvoke({"input": user_input}))
        except Exception as e:
            print(f"⚠️ Could not start agent {name}: {e}")
    return await asyncio.gather(*tasks, return_exceptions=True)


async def merge_results(results, agent_list):
    """
    Merge multiple agent outputs into one coherent response.
    """
    merged_output = ""
    for agent_name, res in zip(agent_list, results):
        if isinstance(res, dict):
            text = res.get("output") or res.get("text") or str(res)
        else:
            text = str(res)
        merged_output += f"🧠 {agent_name}: {text}\n"
    return merged_output


async def main():
    factory = DynamicAgentFactory(AGENT_CONFIG)
    print("\n🤖 Multi-Agent System Started\n")

    while True:
        user_input = input("[User] > ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        print("\n🧭 Router deciding which agent(s) to use...\n")
        agent_list = await handle_router(factory, user_input)
        print(f"📡 Router selected agents: {agent_list}\n")

        results = await query_agents(factory, agent_list, user_input)
        merged_output = await merge_results(results, agent_list)

        print(f"\n✅ Combined Result:\n{merged_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
