from pydantic import BaseModel
from typing import List, Optional

class TransformInitRequest(BaseModel):
    bucket: str
    file1: str
    file2: str

class TransformSelectionRequest(BaseModel):
    join_columns: List[str]
    join_method: str  
    transform_id: Optional[str] = "default"
