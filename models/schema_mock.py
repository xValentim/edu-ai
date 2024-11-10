from pydantic import BaseModel

class Question(BaseModel):
    question: str
    options: list
    answer: str

class OutputMock(BaseModel):
    questions: list[Question]