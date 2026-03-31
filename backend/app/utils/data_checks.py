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


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of numeric columns from dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        List[str]: List of numeric column names
    """
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of categorical columns from dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        List[str]: List of categorical column names
    """
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def get_datetime_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of datetime columns from dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        List[str]: List of datetime column names
    """
    return df.select_dtypes(include=['datetime64']).columns.tolist()


def detect_datetime_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect and analyze datetime columns in the dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        dict: Dictionary containing datetime column analysis
    """
    datetime_info = {}
    potential_datetime_cols = []

    for col in df.columns:
        # Check if column is already datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_info[col] = {
                'type': 'datetime',
                'min_date': df[col].min(),
                'max_date': df[col].max(),
                'date_range_days': (df[col].max() - df[col].min()).days if pd.notna(df[col].min()) and pd.notna(df[col].max()) else None,
                'null_count': df[col].isnull().sum(),
                'frequency_hint': _infer_frequency(df[col].dropna())
            }
        else:
            # Try to detect potential datetime columns
            sample_data = df[col].dropna().head(100)
            if len(sample_data) > 0:
                datetime_score = _calculate_datetime_score(sample_data)
                if datetime_score > 0.7:  # 70% confidence threshold
                    potential_datetime_cols.append({
                        'column': col,
                        'score': datetime_score,
                        'sample_values': sample_data.head(5).tolist()
                    })

    return {
        'datetime_columns': datetime_info,
        'potential_datetime_columns': potential_datetime_cols,
        'has_time_series': len(datetime_info) > 0
    }


def _calculate_datetime_score(series: pd.Series) -> float:
    """
    Calculate the likelihood that a series contains datetime data.

    Args:
        series (pd.Series): Series to analyze

    Returns:
        float: Score between 0 and 1 indicating datetime likelihood
    """
    if len(series) == 0:
        return 0.0

    score = 0.0
    total_checks = 0

    # Check if values can be parsed as dates
    parseable_count = 0
    for value in series.head(20):  # Sample first 20 values
        try:
            pd.to_datetime(str(value))
            parseable_count += 1
        except:
            pass
        total_checks += 1

    if total_checks > 0:
        score += (parseable_count / total_checks) * 0.6

    # Check for common date patterns
    str_series = series.astype(str)
    pattern_score = 0

    # Date patterns to check
    patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
    ]

    for pattern in patterns:
        matches = str_series.str.contains(pattern, na=False).sum()
        pattern_score = max(pattern_score, matches / len(series))

    score += pattern_score * 0.4

    return min(score, 1.0)


def _infer_frequency(datetime_series: pd.Series) -> str:
    """
    Infer the frequency of a datetime series.

    Args:
        datetime_series (pd.Series): Datetime series

    Returns:
        str: Inferred frequency or 'irregular'
    """
    if len(datetime_series) < 2:
        return 'insufficient_data'

    try:
        # Sort the series
        sorted_series = datetime_series.sort_values()

        # Calculate differences
        diffs = sorted_series.diff().dropna()

        if len(diffs) == 0:
            return 'insufficient_data'

        # Get the most common difference
        mode_diff = diffs.mode()

        if len(mode_diff) == 0:
            return 'irregular'

        mode_diff = mode_diff.iloc[0]

        # Check if most differences match the mode (within tolerance)
        tolerance = pd.Timedelta(hours=1)  # 1 hour tolerance
        consistent_count = ((diffs - mode_diff).abs() <= tolerance).sum()
        consistency_ratio = consistent_count / len(diffs)

        if consistency_ratio < 0.8:  # Less than 80% consistent
            return 'irregular'

        # Determine frequency based on mode difference
        days = mode_diff.total_seconds() / (24 * 3600)

        if abs(days - 1) < 0.1:
            return 'daily'
        elif abs(days - 7) < 0.5:
            return 'weekly'
        elif abs(days - 30.44) < 2:  # Average month length
            return 'monthly'
        elif abs(days - 365.25) < 30:  # Year with leap year consideration
            return 'yearly'
        elif mode_diff.total_seconds() < 3600:  # Less than 1 hour
            return 'intraday'
        else:
            return f'every_{int(days)}_days'

    except Exception:
        return 'irregular'


def prepare_time_series_data(df: pd.DataFrame, datetime_col: str, value_cols: List[str] = None) -> pd.DataFrame:
    """
    Prepare data for time series analysis.

    Args:
        df (pd.DataFrame): Input dataframe
        datetime_col (str): Name of the datetime column
        value_cols (List[str], optional): List of value columns to include

    Returns:
        pd.DataFrame: Prepared time series dataframe
    """
    # Create a copy to avoid modifying original
    ts_df = df.copy()

    # Convert datetime column if needed
    if not pd.api.types.is_datetime64_any_dtype(ts_df[datetime_col]):
        ts_df[datetime_col] = pd.to_datetime(
            ts_df[datetime_col], errors='coerce')

    # Remove rows where datetime conversion failed
    ts_df = ts_df.dropna(subset=[datetime_col])

    # Sort by datetime
    ts_df = ts_df.sort_values(datetime_col)

    # Set datetime as index
    ts_df = ts_df.set_index(datetime_col)

    # Select value columns if specified
    if value_cols:
        # Filter to only include numeric columns that exist
        valid_cols = [col for col in value_cols if col in ts_df.columns
                      and pd.api.types.is_numeric_dtype(ts_df[col])]
        if valid_cols:
            ts_df = ts_df[valid_cols]
    else:
        # Select all numeric columns
        ts_df = ts_df.select_dtypes(include=[np.number])

    return ts_df
