# calendar-mcp_server.py
from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("calendar-mcp")

@mcp.tool()
def get_day_of_week(date_str: str) -> str:
    """
    Get the day of the week for a given date (format: YYYY-MM-DD).
    Example: get_day_of_week("2025-10-21") -> Tuesday
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_str} falls on a {date_obj.strftime('%A')}."
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

@mcp.tool()
def days_between(date1: str, date2: str) -> str:
    """
    Calculate the number of days between two dates (YYYY-MM-DD).
    """
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        diff = abs((d2 - d1).days)
        return f"There are {diff} days between {date1} and {date2}."
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

if __name__ == "__main__":
    print("📅 Starting Calendar MCP Server...")
    mcp.run()
