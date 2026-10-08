from fastmcp.server import FastMCP
from langchain_openai import ChatOpenAI
import requests
import os
import json
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

mcp = FastMCP("weather-mcp")

# MCP internal LLM
mcp_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5,
                     api_key=os.getenv("OPENAI_API_KEY"))

@mcp.tool()
async def get_weather(location: str, forecast_type: str = "today"):
    """
    MCP server tool:
    1. Use internal LLM to validate/adjust location and forecast_type.
    2. Call weather API (wttr.in).
    """
    try:
        # LLM reasoning inside MCP
        reasoning_prompt = f"""
        You are a weather assistant inside MCP server.
        Adjust the following location and forecast request to a standard format.
        Input: location='{location}', forecast_type='{forecast_type}'
        Output strictly as JSON: {{"location": "validated_location", "forecast_type": "validated_forecast_type"}}
        Valid forecast types: today, tomorrow, 3-day, 7-day
        """
        # validated = mcp_llm.invoke(reasoning_prompt).strip()
        response = mcp_llm.invoke(reasoning_prompt)
        validated = response.content.strip()
        # response = await mcp_llm.ainvoke(reasoning_prompt)
        # validated = response.content.strip() 
        if validated.startswith("```"):
            validated = validated.strip("`").split("json")[-1].strip()
        try:
            validated_json = json.loads(validated)
            location = validated_json.get("location", location)
            forecast_type = validated_json.get("forecast_type", forecast_type)
        except Exception:
            pass

        # Call wttr.in
        suffix_map = {"today": "?1", "tomorrow": "?2", "3-day": "?3", "7-day": "?7"}
        suffix = suffix_map.get(forecast_type.lower(), "?1")
        # url = f"https://wttr.in/{location}{suffix}?format=3"
        url = f"https://wttr.in/{location}?format=3"
        weather_resp = requests.get(url, timeout=10).text

        return {
            "location": location,
            "forecast_type": forecast_type,
            "content": weather_resp
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()