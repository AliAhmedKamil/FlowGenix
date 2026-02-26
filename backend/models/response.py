# backend/models/response.py

from typing import List, Dict, Any
from pydantic import BaseModel


class ReportResponse(BaseModel):
    metrics: Dict[str, Any]
    summary: str
    recommendations: List[str]
