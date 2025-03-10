# src/models/tender_models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class HealthCheck(BaseModel):
    status: str = "healthy"

class TenderAnalysisRequest(BaseModel):
    text: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class TenderMeta(BaseModel):
    title: Optional[str] = None
    reference_number: Optional[str] = None
    issuing_organization: Optional[str] = None
    submission_deadline: Optional[str] = None
    estimated_budget: Optional[str] = None

class TenderAnalysisResponse(BaseModel):
    document_id: str
    summary: str
    basic_info: Dict[str, Any]
    key_requirements: List[str]
    eligibility_criteria: List[str]
    evaluation_criteria: List[str]
    required_documents: List[str]
    compliance_checklist: List[str]
    winning_strategy: str
    risks_and_mitigations: List[Dict[str, str]]
    metadata: TenderMeta
    full_analysis: Optional[str] = None

class SearchResult(BaseModel):
    document_id: str
    score: float
    title: Optional[str] = None
    summary: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]