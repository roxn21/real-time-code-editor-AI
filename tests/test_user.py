import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

# Test user login
def test_login():
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = client.post("/login/", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

# Test user registration
def test_register():
    register_data = {
        "username": "newuser",
        "password": "newpassword123",
        "email": "newuser@example.com"
    }
    response = client.post("/register/", json=register_data)
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
