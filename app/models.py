from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from app.database import Base  # Import `Base` from `database.py`

# Many-to-Many relationship table between Users and CodeFiles
collaborators_table = Table(
    "collaborators",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("file_id", Integer, ForeignKey("code_files.id", ondelete="CASCADE")),
)

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="collaborator")  # Possible roles: "owner", "collaborator"

    # Relationships
    files = relationship("CodeFile", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("EditingSession", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("CodeFile", secondary=collaborators_table, back_populates="collaborators")

# CodeFile Model
class CodeFile(Base):
    __tablename__ = "code_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(100), unique=True, nullable=False)
    content = Column(Text, nullable=False, default="")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="files")
    editing_sessions = relationship("EditingSession", back_populates="file", cascade="all, delete-orphan")
    collaborators = relationship("User", secondary=collaborators_table, back_populates="collaborations")

# EditingSession Model
class EditingSession(Base):
    __tablename__ = "editing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("code_files.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
    file = relationship("CodeFile", back_populates="editing_sessions")
