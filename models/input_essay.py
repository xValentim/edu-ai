from pydantic import BaseModel

class InputEssay(BaseModel):
    path_essay: str
    id_essay: int
    subject: str