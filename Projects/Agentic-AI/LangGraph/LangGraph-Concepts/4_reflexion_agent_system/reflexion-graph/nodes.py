from typing import Dict
from langchain_core.messages import AIMessage

from chains import first_responder_chain, revisor_chain

# ---------------- DRAFT NODE ----------------
def draft_node(state: Dict):
    result = first_responder_chain.invoke(state)
    tool_output = result[0]

    ai_message = AIMessage(
        content="",
        tool_calls=[
            {
                "id": "answer_question",
                "name": "AnswerQuestion",
                "args": tool_output.dict()
            }
        ]
    )

    return {
        "messages": state["messages"] + [ai_message]
    }

# ---------------- REVISOR NODE ----------------
def revisor_node(state: Dict):
    result = revisor_chain.invoke(state)
    tool_output = result[0]

    ai_message = AIMessage(
        content="",
        tool_calls=[
            {
                "id": "revise_answer",
                "name": "ReviseAnswer",
                "args": tool_output.dict()
            }
        ]
    )

    return {
        "messages": state["messages"] + [ai_message]
    }
