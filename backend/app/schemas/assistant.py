from typing import List, Optional
from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    source_title: str = Field(..., description="Title of the official government guideline or document")
    source_url: Optional[str] = Field(None, description="Official government portal URL")
    section_title: Optional[str] = Field(None, description="Section or paragraph reference")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    excerpt: str = Field(..., description="Exact verified clause excerpt from official source")


class AssistantQueryRequest(BaseModel):
    scheme_id: Optional[str] = Field(None, description="Slug or ID of the scheme being queried (e.g. national-scholarship-post-matric)")
    question: str = Field(..., min_length=2, max_length=500, description="Citizen's question in natural language")
    conversation_id: Optional[str] = Field(None, description="Optional conversation session ID")


class AssistantQueryResponse(BaseModel):
    answer: str = Field(..., description="Factually grounded answer synthesized strictly from official documents")
    citations: List[SourceCitation] = Field(default=[], description="Verifiable citations pointing to official government sources")
    insufficient_evidence: bool = Field(False, description="True if official documents do not contain adequate facts to answer")
    conversation_id: Optional[str] = None
    disclaimer: str = "Grounded in official Government of India guidelines. Independent civic information, not legal advice."
    verification_status: Optional[str] = Field("verified", description="LLM-as-a-judge verification status: verified, revised, or insufficient_evidence")
    confidence_score: Optional[float] = Field(1.0, description="Factuality and grounding score from 0.0 to 1.0")
    key_facts: List[str] = Field(default=[], description="Structured key facts, caps, or requirements")
    matched_scheme_name: Optional[str] = Field(None, description="Resolved scheme name from query context")
    detected_intent: Optional[str] = Field(None, description="Categorized user intent, e.g. Income Ceiling, Documents Required")
