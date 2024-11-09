
from typing import List, Dict

def format_schemas_output(response_essay: str, 
                          response_schema_essay: Dict, 
                          id_essay: int) -> List[Dict]:
    """Formata a saída dos schemas."""
    schemas_competencias = [x['args'] for x in response_schema_essay.tool_calls]
    raw_feedback_dict = {'raw_feedback': response_essay}
    id_essay_dict = {'id_essay': id_essay}
    
    schemas_competencias.append(id_essay_dict)
    schemas_competencias.append(raw_feedback_dict)
    return schemas_competencias