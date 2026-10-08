#!/usr/bin/env python3
"""
Main application to demonstrate the weather client
"""

import asyncio
from weather_client import get_weather

async def main():
    print("🌤️ Simple MCP Weather App")
    print("=" * 30)
    
    # Test with a few locations
    locations = ["London", "Paris", "New York", "Tokyo", "Berlin"]
    
    for location in locations:
        print(f"\n📍 Getting weather for {location}...")
        try:
            result = await get_weather(location)
            print(f"✅ {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print("\n" + "=" * 30)
    print("🏁 All requests completed!")

if __name__ == "__main__":
    asyncio.run(main())