"""
Chart data utilities for converting DataFrames to JSON-serializable
structures compatible with Recharts frontend components.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional


def get_histogram_data(series: pd.Series, bins: int = 20) -> List[Dict[str, Any]]:
    """
    Compute histogram data for a numeric series.
    Returns list of {"bin": "0-10", "count": 5} dicts.
    """
    counts, edges = np.histogram(series.dropna(), bins=bins)
    return [
        {"bin": f"{edges[i]:.2f}-{edges[i+1]:.2f}", "count": int(count)}
        for i, count in enumerate(counts)
    ]


def get_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute correlation matrix for numeric columns.
    Returns {"columns": [...], "matrix": [[...]]}.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return {"columns": [], "matrix": []}

    corr = numeric_df.corr()
    cols = corr.columns.tolist()
    matrix = [
        [None if np.isnan(corr.iloc[i, j]) else round(float(corr.iloc[i, j]), 4) for j in range(len(cols))]
        for i in range(len(cols))
    ]
    return {"columns": cols, "matrix": matrix}


def get_value_counts_data(series: pd.Series, top_n: int = 15) -> List[Dict[str, Any]]:
    """
    Compute value counts for a categorical series.
    Returns list of {"category": "A", "count": 10} dicts.
    """
    counts = series.value_counts().head(top_n)
    return [{"category": str(k), "count": int(v)} for k, v in counts.items()]


def get_null_heatmap_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute null pattern data for a heatmap visualization.
    Returns {"columns": [...], "null_counts": {...}, "null_percentages": {...}}.
    """
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / len(df) * 100).round(2)
    return {
        "columns": df.columns.tolist(),
        "null_counts": {col: int(v) for col, v in null_counts.items()},
        "null_percentages": {col: float(v) for col, v in null_percentages.items()},
    }


def get_boxplot_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Compute box plot statistics for a numeric series.
    Returns {min, q1, median, q3, max, outliers}.
    """
    clean = series.dropna()
    if clean.empty:
        return {"min": None, "q1": None, "median": None, "q3": None, "max": None, "outliers": []}

    q1 = float(clean.quantile(0.25))
    q3 = float(clean.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = clean[(clean < lower) | (clean > upper)].tolist()

    return {
        "min": float(clean.min()),
        "q1": q1,
        "median": float(clean.median()),
        "q3": q3,
        "max": float(clean.max()),
        "outliers": [float(x) for x in outliers[:100]],
    }


def get_time_series_data(
    df: pd.DataFrame, datetime_col: str, value_cols: List[str]
) -> List[Dict[str, Any]]:
    """
    Build time series data for Recharts.
    Returns list of {"date": "2023-01-01", "col1": 10.5, ...} dicts.
    """
    if datetime_col not in df.columns:
        return []

    valid_cols = [c for c in value_cols if c in df.columns]
    ts_df = df[[datetime_col] + valid_cols].dropna(subset=[datetime_col]).sort_values(datetime_col)

    if len(ts_df) > 1000:
        ts_df = ts_df.iloc[:: len(ts_df) // 1000]

    result = []
    for _, row in ts_df.iterrows():
        entry: Dict[str, Any] = {"date": str(row[datetime_col])}
        for col in valid_cols:
            val = row[col]
            entry[col] = None if pd.isna(val) else float(val)
        result.append(entry)
    return result
