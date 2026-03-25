"""Tests for analyze endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_overview(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "quality" in data
    assert "column_stats" in data
    assert data["total_rows"] > 0


def test_nulls(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/nulls")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_nulls" in data
    assert "null_counts" in data


def test_distributions(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/distributions")
    assert resp.status_code == 200
    data = resp.json()
    assert "histograms" in data
    assert "boxplots" in data


def test_correlations(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/correlations")
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "matrix" in data


def test_categories(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert "value_counts" in data


def test_timeseries(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/timeseries")
    assert resp.status_code == 200
    data = resp.json()
    assert "datetime_columns" in data


def test_preprocessing(client: TestClient, session_with_df: str):
    resp = client.get(f"/api/analyze/{session_with_df}/preprocessing")
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data


def test_analyze_not_found(client: TestClient):
    resp = client.get("/api/analyze/00000000-0000-0000-0000-000000000000/overview")
    assert resp.status_code == 404
