# Real-Time Code Editor with AI Debugging

## 🚀 Project Overview
This is a **FastAPI-based real-time collaborative code editor** with **AI-assisted debugging**. It enables multiple users to **edit code together**, while an **AI model analyzes and suggests improvements** in real-time.

---

## 🛠️ Tech Stack
- **Backend:** FastAPI, SQLAlchemy, Celery
- **AI Model:** DeepSeek-Coder 6.7B via Ollama
- **Database:** SQLite (or PostgreSQL in production)
- **Real-Time Collaboration:** WebSockets + Redis Pub/Sub
- **Authentication:** JWT-based authentication & role-based access control
- **Deployment:** Docker, CI/CD (GitHub Actions)
- **Testing:** Pytest

---

## 🔧 Installation & Setup
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/real-time-code-editor-AI.git
cd real-time-code-editor-AI
```

### **2️⃣ Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables**
Create a `.env` file:
```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite+aiosqlite:///./test.db
REDIS_HOST=localhost
REDIS_PORT=6379
```

### **4️⃣ Start the Services with Docker**
```bash
docker-compose up --build
```

---

## 🛠️ API Documentation
### **🔹 Swagger UI (Interactive API Docs)**
Once the app is running, open **Swagger UI**:
- **URL:** `http://localhost:8000/docs`

### **🔹 Postman Collection**
A Postman collection is provided for testing all API endpoints.

---

## ⚡ Usage
### **User Authentication**
- **Register:** `POST /register/`
- **Login:** `POST /login/`

### **File Management**
- **Create File:** `POST /files/`
- **List Files:** `GET /files/`
- **Edit File:** `PUT /files/{file_id}`
- **Delete File:** `DELETE /files/{file_id}`

### **Collaboration**
- **Add Collaborator:** `POST /collaboration/add/{file_id}/{user_id}`
- **Remove Collaborator:** `DELETE /collaboration/remove/{file_id}/{user_id}`

### **Real-Time Editing (WebSockets)**
Connect using WebSockets:
```ws://localhost:8000/ws/{file_id}?token=your_token_here```

### **AI Debugging**
- **Analyze Code:** `POST /ai-debug/`
- **Asynchronous Analysis:** `POST /analyze/`
- **Check Task Status:** `GET /task-status/{task_id}`

---

## 🔒 Security
- **JWT Authentication** (Token-based access)
- **Role-Based Access Control (RBAC)** (Owners vs. Collaborators)
- **Input Validation & Security Measures**

---

## ✅ Testing
Run all tests using:
```bash
pytest -v
```

---

## 🚀 Deployment
1️⃣ **Build and push Docker image:**
```bash
docker build -t your-dockerhub-username/real-time-code-editor-ai .
docker push your-dockerhub-username/real-time-code-editor-ai
```

2️⃣ **Deploy using CI/CD Pipeline** (GitHub Actions triggers deployment on push to `dev` branch).

---