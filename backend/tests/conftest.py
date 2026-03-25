"""Pytest fixtures for Vizzy backend tests."""
import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core import session as session_store


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_df():
    """A small sample DataFrame for testing."""
    return pd.DataFrame({
        "age": [25, 30, 35, 40, 45, None],
        "salary": [50000.0, 60000.0, 70000.0, 80000.0, 90000.0, 100000.0],
        "department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing", "HR"],
        "hire_date": pd.to_datetime([
            "2020-01-01", "2020-06-01", "2021-01-01",
            "2021-06-01", "2022-01-01", "2022-06-01",
        ]),
    })


@pytest.fixture
def session_with_df(sample_df):
    """A pre-created session containing the sample DataFrame. Cleans up after."""
    sid = session_store.create_session(sample_df, "test.csv", 1024)
    yield sid
    session_store.delete_session(sid)


@pytest.fixture
def csv_bytes(sample_df):
    """Sample DataFrame serialized as CSV bytes."""
    buf = io.BytesIO()
    sample_df.to_csv(buf, index=False)
    return buf.getvalue()
