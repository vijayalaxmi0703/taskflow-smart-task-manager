# ⬡ TaskFlow — Smart Task Management System

A full-stack web application built with Flask, PostgreSQL, WebSockets, Pandas/NumPy analytics, and a polished dark-theme frontend.

---

## Features

- **Secure Authentication** — registration, login, logout with bcrypt password hashing
- **REST API** — full CRUD for tasks with proper HTTP status codes and JSON responses
- **PostgreSQL Database** — normalized schema with foreign-key constraints
- **Analytics Module** — Pandas + NumPy powered task statistics
- **Real-Time WebSockets** — live task updates via Flask-SocketIO without page refresh
- **Responsive Frontend** — clean dark-theme UI with modal forms, filters, and toast notifications

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.11+, Flask 3, Blueprints   |
| Database    | PostgreSQL 14+, SQLAlchemy ORM      |
| Analytics   | Pandas, NumPy                       |
| Real-Time   | Flask-SocketIO, eventlet            |
| Auth        | Flask-Login, Flask-Bcrypt           |
| Frontend    | HTML5, CSS3, vanilla JS, Socket.IO  |

---

## Project Structure

```
project/
├── app.py                  # Application factory + entry point
├── config.py               # Config class (env-aware)
├── requirements.txt
├── .env.example
│
├── models/
│   ├── __init__.py         # Shared extensions (db, bcrypt, login_manager)
│   ├── user_model.py       # User ORM model
│   └── task_model.py       # Task ORM model
│
├── routes/
│   ├── auth_routes.py      # /api/auth/* + page routes
│   ├── task_routes.py      # /api/tasks CRUD
│   └── analytics_routes.py # /api/analytics
│
├── websocket/
│   └── socket_events.py    # SocketIO init + event handlers
│
├── static/
│   ├── css/auth.css
│   ├── css/dashboard.css
│   └── js/dashboard.js
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
└── database/
    └── schema.sql
```

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+
- `pip`

### 2. Clone & install dependencies

```bash
git clone https://github.com/your-username/taskflow.git
cd taskflow
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY and DATABASE_URL
```

### 4. Create the database

```bash
psql -U postgres
CREATE DATABASE task_manager;
\q
```

Optionally apply the raw schema (SQLAlchemy will also auto-create tables on first run):

```bash
psql -U postgres -d task_manager -f database/schema.sql
```

### 5. Run the application

```bash
python app.py
```

Visit **http://localhost:5000**

---

## API Endpoints

### Auth

| Method | Endpoint              | Description              | Auth required |
|--------|-----------------------|--------------------------|---------------|
| POST   | /api/auth/register    | Register new user        | No            |
| POST   | /api/auth/login       | Login                    | No            |
| POST   | /api/auth/logout      | Logout                   | Yes           |
| GET    | /api/auth/me          | Get current user profile | Yes           |

### Tasks

| Method | Endpoint              | Description              | Auth required |
|--------|-----------------------|--------------------------|---------------|
| POST   | /api/tasks            | Create task              | Yes           |
| GET    | /api/tasks            | List all tasks           | Yes           |
| PUT    | /api/tasks/\<id\>     | Update task              | Yes           |
| DELETE | /api/tasks/\<id\>     | Delete task              | Yes           |

### Analytics

| Method | Endpoint        | Description             | Auth required |
|--------|-----------------|-------------------------|---------------|
| GET    | /api/analytics  | Task statistics         | Yes           |

### Pages

| Route       | Description       |
|-------------|-------------------|
| /           | Redirect to login |
| /login      | Login page        |
| /register   | Register page     |
| /dashboard  | Main dashboard    |

---

## WebSocket Events

| Event          | Trigger          | Payload               |
|----------------|------------------|-----------------------|
| task_created   | Task created     | Full task object      |
| task_updated   | Task updated     | Full task object      |
| task_deleted   | Task deleted     | `{ id: <task_id> }`  |

Events are scoped to the authenticated user's private room — no cross-user data leaks.

---

## Analytics Response Example

```json
{
  "total_tasks": 10,
  "completed_tasks": 4,
  "pending_tasks": 6,
  "completion_percentage": 40.0,
  "by_priority": {
    "Low": 2,
    "Medium": 5,
    "High": 3
  }
}
```

---

## Security Notes

- Passwords are hashed with bcrypt — plain text is never stored
- Tasks are scoped per user via `user_id` FK — users cannot see each other's data
- All API routes returning user data require an active session
- Input validated before every DB write

---

## License

MIT
