"""
Data loading utilities for the Vizzy FastAPI backend.

Handles file parsing from raw bytes for CSV and Excel formats.
"""
import io
import pandas as pd


def load_data_from_bytes(content: bytes, filename: str) -> pd.DataFrame:
    """Load a DataFrame from raw file bytes.

    Args:
        content: Raw file bytes.
        filename: Original filename used to detect format.

    Returns:
        Parsed DataFrame.

    Raises:
        ValueError: If the file format is unsupported, empty, or has no columns.
    """
    file_lower = filename.lower()
    try:
        if file_lower.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(content), encoding="latin-1")
        elif file_lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file format: {filename}")

        if df.empty:
            raise ValueError("The uploaded file is empty")
        if len(df.columns) == 0:
            raise ValueError("No columns found in the file")

        return df
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Error loading file: {str(e)}") from e


def get_file_info(df: pd.DataFrame) -> dict:
    """Return basic file/DataFrame metadata."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "memory_usage": df.memory_usage(deep=True).sum(),
        "dtypes": df.dtypes.value_counts().to_dict(),
        "null_counts": df.isnull().sum().sum(),
        "duplicate_rows": df.duplicated().sum(),
    }


def sample_dataframe(df: pd.DataFrame, max_rows: int = 10000) -> pd.DataFrame:
    """Return a sampled DataFrame if it exceeds max_rows."""
    if len(df) <= max_rows:
        return df
    return df.sample(n=max_rows, random_state=42)
