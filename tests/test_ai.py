import pytest
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

# Test AI code debugging
def test_ai_debugging():
    code_data = {
        "code": "def foo():\n    print('Hello World')"
    }
    response = client.post("/ai-debug/", json=code_data)
    assert response.status_code == 200
    assert "debug_info" in response.json()

# Test analyze code API
def test_analyze_code():
    code_data = {
        "code": "def foo():\n    print('Hello World')"
    }
    response = client.post("/analyze/", json=code_data)
    assert response.status_code == 200
    assert "analysis_results" in response.json()
