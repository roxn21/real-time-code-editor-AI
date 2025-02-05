from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table
from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

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
    username = Column(String(100), unique=True, index=True, nullable=False)  # Updated to 100 characters
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="collaborator")  # Possible roles: "owner", "collaborator"

    # Relationships
    files = relationship("CodeFile", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("EditingSession", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("CodeFile", secondary=collaborators_table, back_populates="collaborators")

class CodeFile(Base):
    __tablename__ = "code_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(100), unique=True, nullable=False)  # Updated to 100 characters
    content = Column(Text, default="")  # Store the code inside the file
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Relationships
    owner = relationship("User", back_populates="files")
    sessions = relationship("EditingSession", back_populates="file", cascade="all, delete-orphan")
    collaborators = relationship("User", secondary=collaborators_table, back_populates="collaborations")

class EditingSession(Base):
    __tablename__ = "editing_sessions"

    id = Column(Integer, primary_key=True)  # Define a primary key column 'id'
    user_id = Column(Integer, ForeignKey('users.id'))
    code_file_id = Column(Integer, ForeignKey('code_files.id'))

    user = relationship("User", backref="editingsessions")
    codefile = relationship("CodeFile", backref="editingsessions")