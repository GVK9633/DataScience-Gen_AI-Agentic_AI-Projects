# main.py
import asyncio
from mcp_clients.universal_mcp_client import run_mcp_query

async def main():
    print("🤖 MCP Client Interface")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        prompt = input("Enter your query (e.g., 'add 4 and 6'): ").strip()

        # Exit or switch logic
        if prompt.lower() in ["exit", "quit"]:
            print("👋 Exiting. Goodbye!")
            break

        try:
            # Auto-detect which server to call
            if any(word in prompt.lower() for word in ["add", "multiply"]):
                server_file = "math_server.py"
            elif "pollution" in prompt.lower():
                server_file = "pollution_server.py"
            elif "weather" in prompt.lower():
                server_file = "weather_server.py"
            else:
                print("⚠️ Could not determine the right MCP server for your query.")
                continue

            # Run query
            result = await run_mcp_query(prompt, server_file)
            print(f"✅ Result from {server_file}:", result)

        except ValueError as e:
            print(f"❌ Input Error: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
