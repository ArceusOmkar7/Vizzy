"""Analyze router: GET /api/analyze/{session_id}/{analysis_type}"""
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
from fastapi import APIRouter
from ..core.session import get_session
from ..models.analysis import (
    OverviewResponse, ColumnSummary, NullReport, NullColumn,
    DistributionResponse, DistributionData, CorrelationResponse, CorrelationPair,
    CategoryResponse, CategoryItem, TimeSeriesResponse, TimePoint,
    PreprocessingResponse, PreprocessingSuggestion,
)
from ..utils import data_checks, quality_engine as qe_module, preprocessing_suggestions as ps_module
from ..utils.chart_data import get_correlation_matrix

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.get("/{session_id}/overview", response_model=OverviewResponse)
def get_overview(session_id: str) -> OverviewResponse:
    """Return quality score, column stats, dtype summary, duplicate count."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]

    engine = qe_module.DataQualityEngine(df)
    quality_results = engine.calculate_overall_score()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    column_summaries = [
        ColumnSummary(
            name=col,
            dtype=str(df[col].dtype),
            null_count=int(df[col].isnull().sum()),
            null_pct=round(float(df[col].isnull().mean() * 100), 2),
            unique_count=int(df[col].nunique()),
            sample_values=[str(v) for v in df[col].dropna().head(5).tolist()],
        )
        for col in df.columns
    ]

    return OverviewResponse(
        quality_score=round(float(quality_results["overall_score"]), 1),
        quality_grade=quality_results["grade"],
        total_rows=len(df),
        total_columns=len(df.columns),
        total_nulls=int(df.isnull().sum().sum()),
        duplicate_rows=int(df.duplicated().sum()),
        numeric_columns=len(numeric_cols),
        categorical_columns=len(categorical_cols),
        datetime_columns=len(datetime_cols),
        column_summaries=column_summaries,
    )


@router.get("/{session_id}/nulls", response_model=NullReport)
def get_nulls(session_id: str) -> NullReport:
    """Return null analysis for all columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    null_analysis = data_checks.analyze_null_values(df)

    null_columns = [
        NullColumn(
            column=col,
            null_count=int(null_analysis["null_counts"][col]),
            null_pct=round(float(null_analysis["null_percentages"][col]), 2),
        )
        for col in null_analysis["columns_with_nulls"]
    ]

    return NullReport(
        total_nulls=int(null_analysis["total_nulls"]),
        columns_with_nulls=len(null_analysis["columns_with_nulls"]),
        null_columns=null_columns,
    )


@router.get("/{session_id}/distributions", response_model=DistributionResponse)
def get_distributions(session_id: str) -> DistributionResponse:
    """Return histogram and box plot data for numeric columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    distributions: dict = {}
    for col in numeric_cols[:20]:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        counts_arr, edges = np.histogram(series, bins=20)
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        skewness = float(scipy_stats.skew(series))
        kurtosis = float(scipy_stats.kurtosis(series))
        distributions[col] = DistributionData(
            column=col,
            bins=[round(float(e), 6) for e in edges[:-1]],
            counts=[int(c) for c in counts_arr],
            min=float(series.min()),
            q1=q1,
            median=float(series.median()),
            q3=q3,
            max=float(series.max()),
            mean=float(series.mean()),
            std=float(series.std()),
            skewness=skewness,
            kurtosis=kurtosis,
        )

    return DistributionResponse(columns=list(distributions.keys()), distributions=distributions)


@router.get("/{session_id}/correlations", response_model=CorrelationResponse)
def get_correlations(session_id: str) -> CorrelationResponse:
    """Return correlation matrix and top correlations."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]

    result = get_correlation_matrix(df)
    cols = result["columns"]
    matrix = result["matrix"]

    top_pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = matrix[i][j]
            if val is not None:
                top_pairs.append(CorrelationPair(col1=cols[i], col2=cols[j], correlation=round(val, 4)))
    top_pairs.sort(key=lambda x: abs(x.correlation), reverse=True)

    return CorrelationResponse(
        columns=cols,
        matrix=matrix,
        top_pairs=top_pairs[:20],
    )


@router.get("/{session_id}/categories", response_model=CategoryResponse)
def get_categories(session_id: str) -> CategoryResponse:
    """Return value counts for categorical columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    categories: dict = {}
    for col in cat_cols[:20]:
        total = len(df[col].dropna())
        counts = df[col].value_counts().head(15)
        categories[col] = [
            CategoryItem(
                value=str(k),
                count=int(v),
                pct=round(float(v) / max(total, 1) * 100, 2),
            )
            for k, v in counts.items()
        ]

    return CategoryResponse(columns=list(categories.keys()), categories=categories)


@router.get("/{session_id}/timeseries", response_model=TimeSeriesResponse)
def get_timeseries(session_id: str) -> TimeSeriesResponse:
    """Return time series data for detected datetime columns."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    has_datetime = len(datetime_cols) > 0
    series: dict = {}
    value_columns: list = []

    if has_datetime and numeric_cols:
        dt_col = datetime_cols[0]
        value_columns = numeric_cols[:5]
        ts_df = df[[dt_col] + value_columns].dropna(subset=[dt_col]).sort_values(dt_col)
        if len(ts_df) > 1000:
            step = max(len(ts_df) // 1000, 1)
            ts_df = ts_df.iloc[::step]
        for val_col in value_columns:
            points = []
            for _, row in ts_df.iterrows():
                v = row[val_col]
                if not pd.isna(v):
                    points.append(TimePoint(timestamp=str(row[dt_col]), value=float(v)))
            series[val_col] = points

    return TimeSeriesResponse(
        datetime_columns=datetime_cols,
        has_datetime=has_datetime,
        series=series,
        value_columns=value_columns,
    )


@router.get("/{session_id}/preprocessing", response_model=PreprocessingResponse)
def get_preprocessing(session_id: str) -> PreprocessingResponse:
    """Return preprocessing suggestions as a flat list."""
    session = get_session(session_id)
    df: pd.DataFrame = session["df"]
    engine = ps_module.PreprocessingSuggestionEngine(df)
    raw = engine.generate_all_suggestions()

    section_labels = {
        "missing_values": "Missing Values",
        "outliers": "Outliers",
        "scaling": "Feature Scaling",
        "encoding": "Categorical Encoding",
        "data_types": "Data Types",
        "feature_engineering": "Feature Engineering",
        "duplicates": "Duplicates",
        "validation": "Data Validation",
    }

    suggestions = []
    for key, label in section_labels.items():
        section = raw.get(key, {})
        if not isinstance(section, dict):
            continue
        texts = section.get("suggestions", [])
        snippets = section.get("code_snippets", [])
        score = section.get("priority", 0)
        if isinstance(score, (int, float)):
            if score >= 60:
                prio = "high"
            elif score >= 30:
                prio = "medium"
            else:
                prio = "low"
        else:
            prio = "low"

        for i, text in enumerate(texts):
            if not text:
                continue
            snippet = snippets[i] if i < len(snippets) else ""
            suggestions.append(PreprocessingSuggestion(
                priority=prio,
                category=label,
                description=str(text),
                code_snippet=str(snippet),
            ))

    # Sort by priority (high first)
    order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: order.get(s.priority, 3))

    return PreprocessingResponse(suggestions=suggestions)

