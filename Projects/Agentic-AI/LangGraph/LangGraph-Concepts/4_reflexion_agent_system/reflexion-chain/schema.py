from pydantic import BaseModel, Field
from typing import List

class AnswerQuestion(BaseModel):
    answer: str = Field(description="Main answer")
    critique: str = Field(description="Self-critique of the answer")
    search_queries: List[str] = Field(description="1-3 search queries")

class ReviseAnswer(BaseModel):
    revised_answer: str = Field(description="Improved answer with citations")
