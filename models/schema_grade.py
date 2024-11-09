from pydantic import BaseModel, Field

class GetSchema(BaseModel):
    """Extrai metadados da correção da redação."""
    
    competencia_1_feedback: str = Field(description="Feedback em texto da competência 1")
    competencia_1_grade: int = Field(description="Nota da competência 1")
    
    competencia_2_feedback: str = Field(description="Feedback em texto da competência 2")
    competencia_2_grade: int = Field(description="Nota da competência 2")
    
    competencia_3_feedback: str = Field(description="Feedback em texto da competência 3")
    competencia_3_grade: int = Field(description="Nota da competência 3")
    
    competencia_4_feedback: str = Field(description="Feedback em texto da competência 4")
    competencia_4_grade: int = Field(description="Nota da competência 4")
    
    competencia_5_feedback: str = Field(description="Feedback em texto da competência 5")
    competencia_5_grade: int = Field(description="Nota da competência 5")