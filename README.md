# Event Search Assignment

A Django + React application that uploads a compressed event archive and searches indexed records by fields such as serial number, protocol, source/destination address, and timestamps.

## Features
- Upload `.tgz` event archives
- Parse and index records from archive members
- Search by multiple filters
- Responsive UI for review and debugging

## Tech Stack
- Backend: Django, Django REST Framework
- Frontend: React + Vite
- Database: SQLite

## Local Setup

### 1. Create a virtual environment
```bash
python -m venv .venv
```

### 2. Install dependencies
```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Run backend
```bash
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

### 4. Run frontend
```bash
cd frontend
npm install
npm run start -- --host 0.0.0.0
```

### 5. Open app
Visit:
```text
http://localhost:5173/
```

## Notes
- Event archives and the local SQLite database are excluded from Git; upload an archive through the UI to index its records.

## Deploy to Render

The `render.yaml` blueprint creates a static frontend and a Django API service. In Render, choose **New > Blueprint** and connect this repository. The API uses SQLite on Render's temporary filesystem, so uploaded records can be lost when the service restarts or redeploys. For persistent production data, configure a persistent database before deploying.
