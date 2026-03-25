"""Analyze router: GET /api/analyze/{session_id}/{analysis_type}"""
import pandas as pd
import numpy as np
from fastapi import APIRouter
from ..core.session import get_session
from ..models.analysis import (
    OverviewResponse, QualityReport, ColumnStats, NullReport,
    DistributionResponse, CorrelationResponse, CategoryResponse,
    TimeSeriesResponse, PreprocessingResponse,
)
from ..utils import data_checks, quality_engine as qe_module, preprocessing_suggestions as ps_module
from ..utils.chart_data import (
    get_histogram_data, get_correlation_matrix, get_value_counts_data,
    get_boxplot_stats, get_time_series_data,
)

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.get("/{session_id}/overview", response_model=OverviewResponse)
def get_overview(session_id: str) -> OverviewResponse:
    """Return quality score, column stats, dtype summary, duplicate count."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]

    engine = qe_module.DataQualityEngine(df)
    quality_results = engine.calculate_overall_score()

    column_stats = [
        ColumnStats(
            name=col,
            dtype=str(df[col].dtype),
            null_count=int(df[col].isnull().sum()),
            null_pct=round(float(df[col].isnull().mean() * 100), 2),
            unique_count=int(df[col].nunique()),
        )
        for col in df.columns
    ]

    dtype_summary = {str(k): int(v) for k, v in df.dtypes.value_counts().items()}

    def _to_serializable(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_to_serializable(i) for i in obj]
        return obj

    dimensions = {
        k: _to_serializable(v)
        for k, v in quality_results["dimensions"].items()
    }

    return OverviewResponse(
        quality=QualityReport(
            overall_score=quality_results["overall_score"],
            grade=quality_results["grade"],
            dimensions=dimensions,
        ),
        column_stats=column_stats,
        dtype_summary=dtype_summary,
        duplicate_count=int(df.duplicated().sum()),
        total_rows=len(df),
        total_columns=len(df.columns),
        memory_mb=round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3),
    )


@router.get("/{session_id}/nulls", response_model=NullReport)
def get_nulls(session_id: str) -> NullReport:
    """Return null analysis for all columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    null_analysis = data_checks.analyze_null_values(df)
    total_cells = len(df) * len(df.columns)

    return NullReport(
        total_nulls=int(null_analysis["total_nulls"]),
        total_cells=total_cells,
        null_percentage=round(float(null_analysis["total_nulls"]) / max(total_cells, 1) * 100, 2),
        columns_with_nulls=null_analysis["columns_with_nulls"],
        null_counts={col: int(v) for col, v in null_analysis["null_counts"].to_dict().items()},
        null_percentages={
            col: round(float(v), 2)
            for col, v in null_analysis["null_percentages"].to_dict().items()
        },
    )


@router.get("/{session_id}/distributions", response_model=DistributionResponse)
def get_distributions(session_id: str) -> DistributionResponse:
    """Return histogram and box plot data for numeric columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    histograms = {}
    boxplots = {}
    for col in numeric_cols[:20]:
        series = df[col].dropna()
        if len(series) > 0:
            histograms[col] = get_histogram_data(series)
            boxplots[col] = get_boxplot_stats(series)

    return DistributionResponse(histograms=histograms, boxplots=boxplots)


@router.get("/{session_id}/correlations", response_model=CorrelationResponse)
def get_correlations(session_id: str) -> CorrelationResponse:
    """Return correlation matrix and top correlations."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]

    result = get_correlation_matrix(df)
    cols = result["columns"]
    matrix = result["matrix"]

    top_corr = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = matrix[i][j]
            if val is not None:
                top_corr.append({"col1": cols[i], "col2": cols[j], "correlation": round(val, 4)})
    top_corr.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    return CorrelationResponse(
        columns=cols,
        matrix=matrix,
        top_correlations=top_corr[:20],
    )


@router.get("/{session_id}/categories", response_model=CategoryResponse)
def get_categories(session_id: str) -> CategoryResponse:
    """Return value counts for categorical columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    value_counts = {col: get_value_counts_data(df[col]) for col in cat_cols[:20]}
    return CategoryResponse(value_counts=value_counts)


@router.get("/{session_id}/timeseries", response_model=TimeSeriesResponse)
def get_timeseries(session_id: str) -> TimeSeriesResponse:
    """Return time series data for detected datetime columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    ts_data: list = []
    if datetime_cols:
        ts_data = get_time_series_data(df, datetime_cols[0], numeric_cols[:5])

    return TimeSeriesResponse(datetime_columns=datetime_cols, data=ts_data)


@router.get("/{session_id}/preprocessing", response_model=PreprocessingResponse)
def get_preprocessing(session_id: str) -> PreprocessingResponse:
    """Return preprocessing suggestions."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    engine = ps_module.PreprocessingSuggestionEngine(df)
    suggestions = engine.generate_all_suggestions()

    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(i) for i in obj]
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        return obj

    return PreprocessingResponse(suggestions=make_serializable(suggestions))
