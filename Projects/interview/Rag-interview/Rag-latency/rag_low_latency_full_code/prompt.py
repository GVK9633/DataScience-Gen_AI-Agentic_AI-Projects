
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""Answer strictly from context.

Context:
{context}

Question:
{question}
"""
)
