from pydantic import BaseModel
from typing import List

class OutputSearch(BaseModel):
    response_simu: List[str]
    response_video: List[str]