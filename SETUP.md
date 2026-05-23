# Setup & Installation Guide

## Quick Setup

### Step 1: Prerequisites
Ensure you have:
- Python 3.8+ (`python --version`)
- PostgreSQL 12+ running (`psql --version`)
- pip (comes with Python)

### Step 2: Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE taskdb;

-- Verify
\l
```

### Step 3: Clone Dependencies
```bash
cd /path/to/project
pip install -r requirements.txt
```

### Step 4: Configure Environment
Edit `.env`:
```
SECRET_KEY=your-secret-key-123
DATABASE_URL=postgresql://postgres:Vijayalaxmi@localhost:5432/taskdb
FLASK_ENV=development
FLASK_DEBUG=True
```

### Step 5: Initialize Database
Option A - Flask (Recommended):
```bash
python -c "
from app import app
with app.app_context():
    from models import db
    db.create_all()
    print('✓ Database initialized')
"
```

Option B - Direct SQL:
```bash
psql -U postgres -d taskdb -f database/schema.sql
```

### Step 6: Run Application
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Troubleshooting

### PostgreSQL Connection Error
```
psycopg2.OperationalError: could not connect to server
```
**Solution**: 
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env
- Test connection: `psql -U postgres -d taskdb`

### Port 5000 Already in Use
```
OSError: [WinError 10048] Only one usage of each socket address
```
**Solution**:
- Kill the process: `lsof -i :5000` (macOS/Linux) or `netstat -ano | findstr :5000` (Windows)
- Change port in app.py: `socketio.run(app, port=5001)`

### Module Not Found Error
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**:
- Reinstall: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version` (should be 3.8+)

### WebSocket Connection Failed
```
[WS] Failed to connect
```
**Solution**:
- Hard refresh: Ctrl+Shift+R
- Check browser console for errors (F12)
- Verify server is running and accessible

---

## API Quick Test

### 1. Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Create Task (need session cookie)
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "High"
  }'
```

### 4. Get Analytics
```bash
curl -X GET http://localhost:5000/api/analytics \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## Database Schema

### users table
```sql
id (PK)
username (UNIQUE)
email (UNIQUE)
password_hash
created_at
```

### tasks table
```sql
id (PK)
user_id (FK → users.id)
title
description
priority (Low|Medium|High)
status (Pending|Completed)
created_at
```

---

## Project Files

| File | Purpose |
|------|---------|
| `app.py` | Flask app factory & entry point |
| `config.py` | Config classes (development/production) |
| `models/` | SQLAlchemy ORM models |
| `routes/` | API endpoints (auth, tasks, analytics) |
| `websocket/` | WebSocket event handlers |
| `static/` | Frontend (CSS, JS, images) |
| `templates/` | HTML pages (login, register, dashboard) |
| `database/` | SQL schema |

---

## Development Notes

- **Debug mode** is enabled in development (`FLASK_DEBUG=True`)
- **Hot reload** is active — code changes auto-restart the server
- **Database auto-creation** happens on first run
- **WebSocket** uses threading (not eventlet) for Windows compatibility

---

## Performance Tips

- Use indexes on frequently queried columns ✓ (user_id, status)
- Batch analytics queries ✓ (single DB query → Pandas)
- Session caching ✓ (Flask-Login handles it)
- Limit WebSocket broadcasts to user-specific rooms ✓

---

## What to Do Next

1. **Create an account** at /register
2. **Login** at /login
3. **Add some tasks** using the "+ New Task" button
4. **Check analytics** in the header bar
5. **Try real-time updates** — open dashboard in 2 tabs and add a task
6. **Read the code** — understand the architecture
7. **Extend it** — add due dates, tags, sharing, etc.

---

Happy coding! 🚀
