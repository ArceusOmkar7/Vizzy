"""Tests for insights endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_query_no_api_key(client: TestClient, session_with_df: str):
    """Query endpoint should return graceful error when no API key set."""
    resp = client.post(
        f"/api/query/{session_with_df}",
        json={"question": "What is the average salary?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "question" in data
    assert "answer" in data


def test_insights_stream_no_api_key(client: TestClient, session_with_df: str):
    """SSE stream should return graceful fallback when no API key configured."""
    resp = client.get(f"/api/insights/{session_with_df}")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")


def test_insights_not_found(client: TestClient):
    resp = client.get("/api/insights/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
