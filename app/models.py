from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy.sql import func

# Many-to-Many relationship table between Users and CodeFiles
collaborators_table = Table(
    "collaborators",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("file_id", Integer, ForeignKey("code_files.id", ondelete="CASCADE")),
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="collaborator")  # Possible roles: "owner", "collaborator"

    # Relationships
    files = relationship("CodeFile", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("EditingSession", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("CodeFile", secondary=collaborators_table, back_populates="collaborators")

class CodeFile(Base):
    __tablename__ = "code_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    content = Column(Text, default="")  # Store the code inside the file
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Relationships
    owner = relationship("User", back_populates="files")
    sessions = relationship("EditingSession", back_populates="file", cascade="all, delete-orphan")
    collaborators = relationship("User", secondary=collaborators_table, back_populates="collaborations")

class EditingSession(Base):
    __tablename__ = "editing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("code_files.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())  # Auto-updates on edit

    # Relationships
    file = relationship("CodeFile", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
