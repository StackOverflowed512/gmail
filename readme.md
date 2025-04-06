# MailAI Project Documentation

## Overview
MailAI is a project designed to provide AI-powered solutions for email management. The project consists of a **frontend** built with React and a **backend** powered by FastAPI.

---

## Prerequisites
Before setting up the project, ensure the following tools are installed on your system:
- **Python 3.8+**
- **Node.js 16+**
- **npm** (comes with Node.js)
- **Virtual Environment Tool** (e.g., `venv` or `virtualenv`)
- **Olama CLI** (for managing AI models)

---

## Backend Setup (FastAPI)

### 1. Create a Virtual Environment
```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
Ensure you have a `requirements.txt` file in the root directory. Install the dependencies:
```bash
pip install -r ../requirements.txt
```

### 3. Install the Alama Model
Install the Olama CLI from the [official site](https://alama.ai) and pull the required model:
```bash
olama pull mistral
```

### 4. Run the FastAPI Server
Start the FastAPI development server:
```bash
uvicorn main:app --reload
```
- Replace `main:app` with the actual entry point of your FastAPI application.

---

## Frontend Setup (React)

### 1. Install Node.js
Download and install Node.js from the [official website](https://nodejs.org/).

### 2. Install Dependencies
Navigate to the frontend directory and install the required packages:
```bash
cd frontend
npm install
```

### 3. Start the React Development Server
Run the following command to start the React app:
```bash
npm start
```

---

## Project Structure
```
/project-root
│
├── backend/          # FastAPI backend
│   ├── main.py       # Entry point for FastAPI
│   └── ...
│
├── frontend/         # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
│
├── requirements.txt  # Backend dependencies
│
└── README.md         # Project documentation
```

---

## Additional Notes
- Ensure the backend and frontend servers are running on different ports (e.g., 8000 for FastAPI and 3000 for React).
- Use a tool like **Postman** or **cURL** to test API endpoints.
- For production, consider using tools like **Docker** or **NGINX** for deployment.

---

## License
This project is licensed under [MIT License](LICENSE).
