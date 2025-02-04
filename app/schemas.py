from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "collaborator"  # Default role

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True 

class FileCreate(BaseModel):
    filename: str

class FileOut(BaseModel):
    id: int
    filename: str
    owner_id: int

    class Config:
        from_attributes = True  