from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    question: str
    options: List[str]
    answer: str

class OutputMock(BaseModel):
    questions: List[Question]