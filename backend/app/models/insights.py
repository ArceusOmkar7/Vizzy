"""Pydantic models for insights endpoints."""
from pydantic import BaseModel
from typing import Optional, List


class InsightResponse(BaseModel):
    insights: List[str]


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    error: Optional[str] = None
