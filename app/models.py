from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="collaborator")  # possible roles: "owner", "collaborator"

    files = relationship("CodeFile", back_populates="owner")
    sessions = relationship("EditingSession", back_populates="user")

class CodeFile(Base):
    __tablename__ = "code_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    content = Column(String, default="")  # Store the code inside the file
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="files")
    sessions = relationship("EditingSession", back_populates="file")

class EditingSession(Base):
    __tablename__ = "editing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("code_files.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())  # Automatically updates on change

    file = relationship("CodeFile", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
