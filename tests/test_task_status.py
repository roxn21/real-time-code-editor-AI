import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test task status endpoint
def test_task_status():
    task_id = "sample-task-id"
    response = client.get(f"/task-status/{task_id}")
    assert response.status_code == 200
    assert "status" in response.json()
