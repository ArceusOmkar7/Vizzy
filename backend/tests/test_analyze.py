"""Tests for analyze endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_overview(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "quality_score" in data
    assert "quality_grade" in data
    assert "column_summaries" in data
    assert "total_nulls" in data
    assert "duplicate_rows" in data
    assert "numeric_columns" in data
    assert "categorical_columns" in data
    assert "datetime_columns" in data
    assert data["total_rows"] > 0
    # Verify column summaries have expected fields including sample_values
    if data["column_summaries"]:
        summary = data["column_summaries"][0]
        assert "name" in summary
        assert "dtype" in summary
        assert "null_count" in summary
        assert "null_pct" in summary
        assert "unique_count" in summary
        assert "sample_values" in summary


def test_nulls(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/nulls")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_nulls" in data
    assert "columns_with_nulls" in data
    assert isinstance(data["columns_with_nulls"], int)
    assert "null_columns" in data
    assert isinstance(data["null_columns"], list)
    if data["null_columns"]:
        col = data["null_columns"][0]
        assert "column" in col
        assert "null_count" in col
        assert "null_pct" in col


def test_distributions(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/distributions")
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "distributions" in data
    assert isinstance(data["columns"], list)
    if data["columns"]:
        col_name = data["columns"][0]
        dist = data["distributions"][col_name]
        assert "bins" in dist
        assert "counts" in dist
        assert "mean" in dist
        assert "std" in dist
        assert "skewness" in dist
        assert "kurtosis" in dist


def test_correlations(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/correlations")
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "matrix" in data
    assert "top_pairs" in data


def test_categories(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "categories" in data
    assert isinstance(data["columns"], list)
    if data["columns"]:
        col_name = data["columns"][0]
        items = data["categories"][col_name]
        assert isinstance(items, list)
        if items:
            assert "value" in items[0]
            assert "count" in items[0]
            assert "pct" in items[0]


def test_timeseries(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/timeseries")
    assert resp.status_code == 200
    data = resp.json()
    assert "datetime_columns" in data
    assert "has_datetime" in data
    assert "series" in data
    assert "value_columns" in data


def test_preprocessing(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/preprocessing")
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    if data["suggestions"]:
        s = data["suggestions"][0]
        assert "priority" in s
        assert "category" in s
        assert "description" in s
        assert "code_snippet" in s


def test_analyze_not_found(client: TestClient):
    resp = client.get("/api/analyze/00000000-0000-0000-0000-000000000000/overview")
    assert resp.status_code == 404
