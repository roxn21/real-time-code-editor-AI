from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    user_data = {
        "username": "new_user",
        "password": "password123",
        "role": "user"
    }

    # Register user
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "new_user"

    # Try to register the same user again (should fail)
    response = client.post("/register/", json=user_data)
    assert response.status_code == 400  # Conflict error for duplicate username
