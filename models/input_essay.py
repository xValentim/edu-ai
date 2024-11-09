from pydantic import BaseModel

class InputEssay(BaseModel):
    path_essay: str
    id_essay: str 
    subject: str