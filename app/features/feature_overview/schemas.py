from pydantic import BaseModel
from typing import Dict, List, Optional

class FeatureOverviewRequest(BaseModel):
    bucket_name: str
    object_names: List[str]
    validator_atom_id: str
    file_key: str
    create_hierarchy: Optional[bool] = False
    create_summary: Optional[bool] = False
    combination: Optional[str] = None  # Optional specific combo

class FeatureOverviewResponse(BaseModel):
    status: str
    message: str
