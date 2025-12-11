import asyncio

from mcp.client import Client

async def main():
    client = Client("adidas_client")

    await client.connect("localhost", 8765)

    response = await client.call_tool(
        "search_adidas_products",
        {"query": "Which shoes have rating above 4.5?"}
    )

    print("\n=== RAG Search Results ===")
    for item in response.content:
        print(item)
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())