# TaskFlow

## 1. Project Overview
TaskFlow is a Flask-based Smart Task Management System built as a college assignment project. It combines secure authentication, PostgreSQL persistence, realtime Socket.IO updates, and Pandas/NumPy analytics inside a dark glassmorphism dashboard.

## 2. Tech Stack
- Backend: Python, Flask, Flask Blueprints
- Database: PostgreSQL, SQLAlchemy ORM
- Authentication: Flask-Login, Flask-Bcrypt, Flask-WTF CSRF protection
- Realtime: Flask-SocketIO
- Analytics: Pandas, NumPy
- Frontend: HTML5, CSS3, Vanilla JavaScript

## 3. Features List
- User registration, login, and logout
- Secure password hashing with bcrypt
- CSRF-protected forms and API actions
- Task CRUD for authenticated users only
- Priority and status filtering
- Realtime task create/update/delete events
- Live analytics counters for each user
- Responsive dark glassmorphism UI

## 4. Prerequisites
- Python 3.10+
- PostgreSQL 13+
- `pip`

## 5. Installation & Setup
1. Clone or download the project.
2. Open a terminal in the `taskflow` folder.
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate it:
   ```bash
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Create a `.env` file in the `taskflow` folder:
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/taskflow_db
   SECRET_KEY=your-secret-key
   FLASK_ENV=development
   SOCKETIO_ASYNC_MODE=eventlet
   ```

## 6. Database Setup
1. Create a PostgreSQL database named `taskflow_db`.
2. Update the `DATABASE_URL` value in `.env`.
3. Run the SQL in `schema.sql` if you want the raw schema version for submission.
4. Alternatively, start the app and let SQLAlchemy create the tables automatically.

## 7. Running the App
```bash
python app.py
```

Then open `http://127.0.0.1:5000`.

## 8. API Endpoints
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/tasks` | List all tasks for the current user | Yes |
| POST | `/api/tasks` | Create a new task | Yes |
| PUT | `/api/tasks/<id>` | Update title, description, priority, or status | Yes |
| DELETE | `/api/tasks/<id>` | Delete a task | Yes |
| GET | `/api/analytics` | Fetch analytics summary for the current user | Yes |

## 9. WebSocket Events
| Event | Direction | Description |
|---|---|---|
| `task_updated` | Server to client | Sends the full analytics payload after task changes |
| `task_created` | Server to client | Sends the new task object for live card insertion |
| `task_deleted` | Server to client | Sends the deleted task id for live removal |

## 10. Project Structure
```text
taskflow/
├── app.py
├── config.py
├── models.py
├── auth/
│   ├── __init__.py
│   └── routes.py
├── tasks/
│   ├── __init__.py
│   └── routes.py
├── analytics/
│   ├── __init__.py
│   └── analytics.py
├── sockets/
│   ├── __init__.py
│   └── events.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/
│   └── style.css
├── requirements.txt
├── schema.sql
└── README.md
```

## 11. Screenshots
- Login page screenshot placeholder
- Register page screenshot placeholder
- Dashboard screenshot placeholder
- Realtime updates screenshot placeholder
