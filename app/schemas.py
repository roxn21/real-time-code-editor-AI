from pydantic import BaseModel

# User Creation Schema
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "collaborator"  # Default role

# User Response Schema
class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True  # Ensure compatibility with SQLAlchemy models

# File Creation Schema
class FileCreate(BaseModel):
    filename: str  # Fixed: Ensure consistency with `models.py`
    content: str  # Include file content
    owner_id: int  # Specify the file owner

# File Response Schema
class FileOut(BaseModel):
    id: int
    filename: str
    content: str  # Added: Ensure response includes file content
    owner_id: int

    class Config:
        from_attributes = True  # Ensure compatibility with SQLAlchemy models

# Editing Session Schema
class EditingSessionCreate(BaseModel):
    user_id: int
    file_id: int

#  Editing Session Response Schema
class EditingSessionOut(BaseModel):
    id: int
    user_id: int
    file_id: int

    class Config:
        from_attributes = True  # Ensure compatibility with SQLAlchemy models
