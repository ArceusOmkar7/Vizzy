"""Pydantic models for analysis endpoint responses."""
from pydantic import BaseModel
from typing import List, Dict, Optional


class ColumnSummary(BaseModel):
    name: str
    dtype: str
    null_count: int
    null_pct: float
    unique_count: int
    sample_values: List[str]


class OverviewResponse(BaseModel):
    quality_score: float
    quality_grade: str
    total_rows: int
    total_columns: int
    total_nulls: int
    duplicate_rows: int
    numeric_columns: int
    categorical_columns: int
    datetime_columns: int
    column_summaries: List[ColumnSummary]


class NullColumn(BaseModel):
    column: str
    null_count: int
    null_pct: float


class NullReport(BaseModel):
    total_nulls: int
    columns_with_nulls: int
    null_columns: List[NullColumn]


class DistributionData(BaseModel):
    column: str
    bins: List[float]
    counts: List[int]
    min: float
    q1: float
    median: float
    q3: float
    max: float
    mean: float
    std: float
    skewness: float
    kurtosis: float


class DistributionResponse(BaseModel):
    columns: List[str]
    distributions: Dict[str, DistributionData]


class CorrelationPair(BaseModel):
    col1: str
    col2: str
    correlation: float


class CorrelationResponse(BaseModel):
    columns: List[str]
    matrix: List[List[Optional[float]]]
    top_pairs: List[CorrelationPair]


class CategoryItem(BaseModel):
    value: str
    count: int
    pct: float


class CategoryResponse(BaseModel):
    columns: List[str]
    categories: Dict[str, List[CategoryItem]]


class TimePoint(BaseModel):
    timestamp: str
    value: float


class TimeSeriesResponse(BaseModel):
    datetime_columns: List[str]
    has_datetime: bool
    series: Dict[str, List[TimePoint]]
    value_columns: List[str]


class PreprocessingSuggestion(BaseModel):
    priority: str
    category: str
    description: str
    code_snippet: str


class PreprocessingResponse(BaseModel):
    suggestions: List[PreprocessingSuggestion]
