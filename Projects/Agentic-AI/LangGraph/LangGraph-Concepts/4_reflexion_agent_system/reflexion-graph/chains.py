import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

from schema import AnswerQuestion, ReviseAnswer
from dotenv import load_dotenv  
load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

# ---------------- PROMPT ----------------
actor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert AI researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer.
3. List 1–3 search queries.
"""
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Use the required tool format."),
    ]
).partial(time=datetime.datetime.now().isoformat)

# ---------------- FIRST RESPONDER ----------------
first_prompt = actor_prompt.partial(
    first_instruction="Provide a detailed ~50 word answer"
)

first_responder_chain = (
    first_prompt
    | llm.bind_tools([AnswerQuestion], tool_choice="AnswerQuestion")
    | PydanticToolsParser(tools=[AnswerQuestion])
)

# ---------------- REVISOR ----------------
revise_prompt = actor_prompt.partial(
    first_instruction="""
Revise the answer using critique.
- Improve clarity
- Max 50 words
- Add citations & references
"""
)

revisor_chain = (
    revise_prompt
    | llm.bind_tools([ReviseAnswer], tool_choice="ReviseAnswer")
    | PydanticToolsParser(tools=[ReviseAnswer])
)
