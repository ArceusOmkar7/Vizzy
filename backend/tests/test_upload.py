"""Tests for upload endpoints."""
import io
import pytest
from fastapi.testclient import TestClient


def test_upload_csv(client: TestClient, csv_bytes: bytes):
    """CSV upload should return a valid UploadResponse."""
    resp = client.post(
        "/api/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["filename"] == "data.csv"
    assert data["rows"] > 0
    assert data["columns"] > 0


def test_upload_invalid_type(client: TestClient):
    """Uploading a .txt file should return 415."""
    resp = client.post(
        "/api/upload",
        files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 415


def test_get_session(client: TestClient, csv_bytes: bytes):
    """Getting a session after upload should return SessionInfo."""
    upload_resp = client.post(
        "/api/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    session_id = upload_resp.json()["session_id"]
    resp = client.get(f"/api/session/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == session_id


def test_delete_session(client: TestClient, csv_bytes: bytes):
    """Deleting a session should cause subsequent GET to return 404."""
    upload_resp = client.post(
        "/api/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    session_id = upload_resp.json()["session_id"]
    client.delete(f"/api/session/{session_id}")
    resp = client.get(f"/api/session/{session_id}")
    assert resp.status_code == 404


def test_session_not_found(client: TestClient):
    """Getting a non-existent session should return 404."""
    resp = client.get("/api/session/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
