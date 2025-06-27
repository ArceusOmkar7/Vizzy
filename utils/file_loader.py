"""
Data loading and caching utilities.

Handles file uploads, data parsing, and caching for the Streamlit app.
"""

import streamlit as st
import pandas as pd
from typing import Union
import io


@st.cache_data
def load_data(uploaded_file) -> pd.DataFrame:
    """
    Load and cache data from uploaded file.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        pd.DataFrame: Loaded dataframe

    Raises:
        Exception: If file cannot be read or parsed
    """
    try:
        # Get file extension
        file_name = uploaded_file.name.lower()

        if file_name.endswith('.csv'):
            # Try different encodings for CSV files
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(uploaded_file, encoding='latin-1')

        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)

        else:
            raise ValueError(f"Unsupported file format: {file_name}")

        # Basic validation
        if df.empty:
            raise ValueError("The uploaded file is empty")

        if len(df.columns) == 0:
            raise ValueError("No columns found in the file")

        return df

    except Exception as e:
        raise Exception(f"Error loading file: {str(e)}")


def get_file_info(df: pd.DataFrame) -> dict:
    """
    Get basic information about the loaded dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        dict: Dictionary containing file statistics
    """
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'dtypes': df.dtypes.value_counts().to_dict(),
        'null_counts': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum()
    }


def sample_dataframe(df: pd.DataFrame, max_rows: int = 10000) -> pd.DataFrame:
    """
    Sample dataframe if it's too large for visualization.

    Args:
        df (pd.DataFrame): Input dataframe
        max_rows (int): Maximum number of rows to keep

    Returns:
        pd.DataFrame: Sampled dataframe
    """
    if len(df) <= max_rows:
        return df

    # Use random sampling to maintain distribution
    return df.sample(n=max_rows, random_state=42)
