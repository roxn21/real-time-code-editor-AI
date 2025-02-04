from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Register an admin user
admin_data = {
    "username": "admin_user",
    "password": "admin_password",
    "role": "owner"
}
response = client.post("/register/", json=admin_data)
admin_token = response.json()["access_token"]

# Register a regular user
user_data = {
    "username": "regular_user",
    "password": "user_password",
    "role": "user"
}
response = client.post("/register/", json=user_data)
user_token = response.json()["access_token"]

def test_create_file_by_owner():
    file_data = {
        "filename": "test_file.py"
    }
    
    # Create a file as owner
    response = client.post("/create-file/", json=file_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["filename"] == "test_file.py"

def test_create_file_by_non_owner():
    file_data = {
        "filename": "test_file.py"
    }
    
    # Try to create a file as non-owner (should fail)
    response = client.post("/create-file/", json=file_data, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403  # Forbidden

def test_add_collaborator_by_owner():
    # Assuming the file is already created by admin and file ID is 1
    response = client.post("/files/1/add-collaborator/2", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "User 2 added as collaborator to file 1"

def test_add_collaborator_by_non_owner():
    # Try to add collaborator as non-owner
    response = client.post("/files/1/add-collaborator/2", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403  # Forbidden
