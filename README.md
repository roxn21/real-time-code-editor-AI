# Real-Time Code Editor API

## Overview
The Real-Time Code Editor API is a FastAPI-based backend that enables real-time collaborative code editing with AI-powered debugging. It provides authentication, role-based access control, WebSocket support for live editing, and AI-based code analysis.

## Features
- **User Authentication**: JWT-based authentication for secure access.
- **Role-Based Access Control**: Different user roles (admin, editor, viewer) for controlled access.
- **Real-Time Collaboration**: WebSockets for live multi-user code editing.
- **AI-Powered Debugging**: AI-generated code analysis and debugging suggestions.
- **File Management**: Secure storage and retrieval of code files.
- **Database Integration**: Uses SQLAlchemy with SQLite for persistent storage.
- **Redis Caching**: Improves performance by caching AI suggestions.

## Architecture
The application follows a modular architecture:
- `app/main.py`: Entry point for FastAPI.
- `app/database.py`: Database session and connection management.
- `app/models.py`: SQLAlchemy models for users, files, and collaborations.
- `app/schemas.py`: Pydantic schemas for request validation.
- `app/auth/auth_service.py`: JWT authentication logic.
- `app/middleware/rbac.py`: Role-based access control middleware.
- `app/redis_client.py`: Redis integration for caching and real-time updates.

## Data Models
### User
```python
class User(Base):
    id: int (Primary Key)
    username: str (Unique)
    hashed_password: str
    role: str (admin/editor/viewer)
```

### CodeFile
```python
class CodeFile(Base):
    id: int (Primary Key)
    name: str
    owner_id: int (Foreign Key to User)
```

### EditingSession
```python
class EditingSession(Base):
    id: int (Primary Key)
    file_id: int (Foreign Key to CodeFile)
    user_id: int (Foreign Key to User)
```

## API Endpoints
### Authentication
- **POST** `/register/` - Register a new user.
- **POST** `/login/` - Authenticate and retrieve JWT token.

### File Management
- **GET** `/files/` - List all code files.
- **POST** `/files/` - Create a new code file.

### Real-Time Collaboration
- **WebSocket** `/ws/{file_id}` - Connect for live editing.

### AI Debugging
- **POST** `/ai-debug/` - Analyze code and return AI suggestions.

## Setup & Installation
### Prerequisites
- Python 3.10+
- Redis (Docker recommended)
- SQLite (default, can be replaced with PostgreSQL)

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/real-time-code-editor-AI.git
   cd real-time-code-editor-AI
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```sh
   cp .env.example .env
   ```
4. Start Redis (if using Docker):
   ```sh
   docker run -d --name redis -p 6379:6379 redis
   ```
5. Run the application:
   ```sh
   uvicorn app.main:app --reload
   ```

## Running with Docker
1. Build and run the Docker container:
   ```sh
   docker-compose up --build
   ```

## Testing
Run the test suite:
```sh
pytest
```

## API Documentation
Interactive API docs available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Future Improvements
- Implement real-time cursor tracking.
- Enhance AI debugging with LLM-based suggestions.
- Add support for multiple file formats.

