"""
Data quality checks and analysis utilities.

Functions for detecting nulls, data types, outliers, and other data quality issues.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any


def analyze_null_values(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive analysis of null values in the dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        dict: Dictionary containing null analysis results
    """
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / len(df)) * 100

    return {
        'null_counts': null_counts,
        'null_percentages': null_percentages,
        'total_nulls': null_counts.sum(),
        'columns_with_nulls': null_counts[null_counts > 0].index.tolist(),
        'completely_null_columns': null_counts[null_counts == len(df)].index.tolist(),
        'mostly_null_columns': null_percentages[null_percentages > 50].index.tolist()
    }


def analyze_data_types(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze data types and provide insights about the dataframe structure.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        dict: Dictionary containing data type analysis
    """
    dtypes_summary = df.dtypes.value_counts()

    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(
        include=['object', 'category']).columns.tolist()
    datetime_columns = df.select_dtypes(
        include=['datetime64']).columns.tolist()
    boolean_columns = df.select_dtypes(include=['bool']).columns.tolist()

    # Analyze uniqueness
    unique_counts = df.nunique()

    return {
        'dtypes_summary': dtypes_summary,
        'numeric_columns': numeric_columns,
        'categorical_columns': categorical_columns,
        'datetime_columns': datetime_columns,
        'boolean_columns': boolean_columns,
        'unique_counts': unique_counts,
        'high_cardinality_columns': unique_counts[unique_counts > len(df) * 0.8].index.tolist(),
        'low_cardinality_columns': unique_counts[unique_counts <= 10].index.tolist()
    }


def detect_outliers_iqr(series: pd.Series) -> Tuple[pd.Series, Dict[str, float]]:
    """
    Detect outliers using the Interquartile Range (IQR) method.

    Args:
        series (pd.Series): Numeric series to analyze

    Returns:
        tuple: (outlier_mask, outlier_stats)
    """
    if not pd.api.types.is_numeric_dtype(series):
        return pd.Series([False] * len(series), index=series.index), {}

    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outlier_mask = (series < lower_bound) | (series > upper_bound)

    stats = {
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'outlier_count': outlier_mask.sum(),
        'outlier_percentage': (outlier_mask.sum() / len(series)) * 100
    }

    return outlier_mask, stats


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> Tuple[pd.Series, Dict[str, float]]:
    """
    Detect outliers using the Z-score method.

    Args:
        series (pd.Series): Numeric series to analyze
        threshold (float): Z-score threshold for outlier detection

    Returns:
        tuple: (outlier_mask, outlier_stats)
    """
    if not pd.api.types.is_numeric_dtype(series):
        return pd.Series([False] * len(series), index=series.index), {}

    z_scores = np.abs((series - series.mean()) / series.std())
    outlier_mask = z_scores > threshold

    stats = {
        'mean': series.mean(),
        'std': series.std(),
        'threshold': threshold,
        'max_zscore': z_scores.max(),
        'outlier_count': outlier_mask.sum(),
        'outlier_percentage': (outlier_mask.sum() / len(series)) * 100
    }

    return outlier_mask, stats


def get_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a comprehensive summary of all columns in the dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        pd.DataFrame: Summary dataframe with column statistics
    """
    summary_data = []

    for col in df.columns:
        col_data = {
            'Column': col,
            'Data_Type': str(df[col].dtype),
            'Non_Null_Count': df[col].count(),
            'Null_Count': df[col].isnull().sum(),
            'Null_Percentage': (df[col].isnull().sum() / len(df)) * 100,
            'Unique_Count': df[col].nunique(),
            'Unique_Percentage': (df[col].nunique() / len(df)) * 100
        }

        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(df[col]):
            col_data.update({
                'Mean': df[col].mean(),
                'Std': df[col].std(),
                'Min': df[col].min(),
                'Max': df[col].max(),
                'Q1': df[col].quantile(0.25),
                'Q3': df[col].quantile(0.75)
            })
        else:
            col_data.update({
                'Most_Frequent': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                'Most_Frequent_Count': df[col].value_counts().iloc[0] if not df[col].empty else 0
            })

        summary_data.append(col_data)

    return pd.DataFrame(summary_data)
