# main.py
"""
Entry point for interactive user-agent chat.
Imports and uses the parent agent dynamically.
"""

# from parent_agent import create_parent_agent
from agents import parent_agent

def main():
    print("🤖 Dynamic Parent Agent (type 'exit' to quit)\n")

    # Create the parent agent
    # agent = parent_agent.create_parent_agent(verbose=True)

    # Interactive loop
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        try:
            response = parent_agent.create_parent_agent(user_input,verbose=True)
            # response = agent.run(user_input)
            print("\nAgent Response:", response, "\n")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
