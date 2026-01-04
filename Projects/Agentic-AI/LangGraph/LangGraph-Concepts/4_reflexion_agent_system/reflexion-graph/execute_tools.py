from typing import Dict
from langchain_core.messages import ToolMessage

def execute_tools(state: Dict):
    messages = state["messages"]
    last_message = messages[-1]

    tool_messages = []

    if hasattr(last_message, "tool_calls"):
        for tool_call in last_message.tool_calls:
            tool_messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=str(tool_call["args"])
                )
            )

    return {
        "messages": messages + tool_messages
    }
