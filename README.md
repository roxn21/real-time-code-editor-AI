# Real-Time Code Editor with AI Debugging

This project is a **Real-Time Code Editor** application powered by **AI-Assisted Debugging** and built with **FastAPI**, **WebSockets**, and **Redis** caching. Users can collaborate on code in real-time, get AI debugging suggestions, and manage user roles with secure authentication.

## Features
- **Real-Time Collaboration**: Multi-user code editing with live cursor tracking.
- **AI-Assisted Debugging**: DeepSeek-Coder integration for real-time code analysis.
- **Role-Based Access Control (RBAC)**: Secure endpoints and file access.
- **Redis Caching**: Optimized AI debugging responses with Redis caching.
- **Authentication**: JWT-based authentication for secure access.
- **Dockerized**: Fully containerized using Docker and Docker Compose for local and cloud deployment.

## Tech Stack
- **Backend**: FastAPI
- **Real-Time Communication**: WebSockets
- **AI Debugging**: DeepSeek-Coder (integrated with Redis caching)
- **Database**: SQLite (for simplicity, can be swapped to PostgreSQL)
- **Containerization**: Docker and Docker Compose
- **Testing**: pytest, httpx

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- **Docker**: [Install Docker](https://www.docker.com/get-started)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

### Cloning the Repository
```bash
git clone https://github.com/your-username/real-time-code-editor-AI.git
cd real-time-code-editor-AI

