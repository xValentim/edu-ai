from pydantic import BaseModel

class InputQuery(BaseModel):
    query: str
    k: int