import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test list code files
def test_list_code_files():
    response = client.get("/files/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
