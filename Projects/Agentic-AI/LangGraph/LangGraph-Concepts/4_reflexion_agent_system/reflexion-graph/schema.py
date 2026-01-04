from pydantic import BaseModel, Field
from typing import List

class AnswerQuestion(BaseModel):
    answer: str = Field(description="Main answer")
    critique: str = Field(description="Self critique")
    search_queries: List[str] = Field(description="Search queries")

class ReviseAnswer(BaseModel):
    revised_answer: str = Field(description="Improved answer with citations")
