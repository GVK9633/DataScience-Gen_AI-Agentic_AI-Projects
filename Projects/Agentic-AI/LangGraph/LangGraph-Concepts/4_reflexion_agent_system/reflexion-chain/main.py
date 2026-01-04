import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

from schema import AnswerQuestion, ReviseAnswer

load_dotenv()

# -------------------- LLM --------------------
llm = ChatOpenAI(model="gpt-4o")

# -------------------- PROMPT --------------------
actor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert AI researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. After reflection, list 1–3 search queries separately.
"""
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Use the required tool format."),
    ]
).partial(time=datetime.datetime.now().isoformat)

# -------------------- FIRST RESPONDER --------------------
first_responder_prompt = actor_prompt.partial(
    first_instruction="Provide a detailed ~250 word answer"
)

first_chain = (
    first_responder_prompt
    | llm.bind_tools([AnswerQuestion], tool_choice="AnswerQuestion")
    | PydanticToolsParser(tools=[AnswerQuestion])
)

# -------------------- REVISOR --------------------
revise_prompt = actor_prompt.partial(
    first_instruction="""
Revise your previous answer using critique.
- Add missing important info
- Remove weak content
- Max 250 words
- Add numerical citations
- Add References section
"""
)

revisor_chain = (
    revise_prompt
    | llm.bind_tools([ReviseAnswer], tool_choice="ReviseAnswer")
    | PydanticToolsParser(tools=[ReviseAnswer])
)

# -------------------- RUN --------------------
question = "What is Retrieval-Augmented Generation (RAG)?"

first_response = first_chain.invoke(
    {"messages": [HumanMessage(content=question)]}
)

print("\n=== FIRST RESPONSE ===")
print(first_response)

revised_response = revisor_chain.invoke(
    {
        "messages": [
            HumanMessage(content=first_response[0].answer),
            HumanMessage(content=f"Critique: {first_response[0].critique}")
        ]
    }
)

print("\n=== REVISED RESPONSE ===")
print(revised_response)
