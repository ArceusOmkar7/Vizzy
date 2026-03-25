"""Pydantic models for analysis endpoint responses."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ColumnStats(BaseModel):
    name: str
    dtype: str
    null_count: int
    null_pct: float
    unique_count: int


class QualityReport(BaseModel):
    overall_score: float
    grade: str
    dimensions: Dict[str, Any]


class OverviewResponse(BaseModel):
    quality: QualityReport
    column_stats: List[ColumnStats]
    dtype_summary: Dict[str, int]
    duplicate_count: int
    total_rows: int
    total_columns: int
    memory_mb: float


class NullReport(BaseModel):
    total_nulls: int
    total_cells: int
    null_percentage: float
    columns_with_nulls: List[str]
    null_counts: Dict[str, int]
    null_percentages: Dict[str, float]


class DistributionResponse(BaseModel):
    histograms: Dict[str, List[Dict[str, Any]]]
    boxplots: Dict[str, Dict[str, Any]]


class CorrelationResponse(BaseModel):
    columns: List[str]
    matrix: List[List[Optional[float]]]
    top_correlations: List[Dict[str, Any]]


class CategoryResponse(BaseModel):
    value_counts: Dict[str, List[Dict[str, Any]]]


class TimeSeriesResponse(BaseModel):
    datetime_columns: List[str]
    data: List[Dict[str, Any]]


class PreprocessingResponse(BaseModel):
    suggestions: Dict[str, Any]
