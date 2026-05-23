# 🏗️ TaskFlow Architecture

## Complete System Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                          WEB BROWSER                                │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                     FRONTEND (HTML/CSS/JS)               │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │                                                            │   │
│  │  /login.html                 /dashboard.html            │   │
│  │  ├── Login form              ├── Sidebar (nav)          │   │
│  │  ├── Register link           ├── Analytics bar (7 cards)│   │
│  │  └── Validation              ├── Task list              │   │
│  │                              ├── Add task modal         │   │
│  │  /register.html              ├── Edit task modal        │   │
│  │  ├── Register form           └── Real-time updates (WS) │   │
│  │  ├── Login link              ┌─────────────────────────┐│   │
│  │  └── Validation              │ Socket.IO Events        ││   │
│  │                              ├─────────────────────────┤│   │
│  │                              │ task_created            ││   │
│  │                              │ task_updated            ││   │
│  │  Styling:                    │ task_deleted            ││   │
│  │  • auth.css (470 lines)      │ connected               ││   │
│  │  • dashboard.css (450 lines) │ disconnect              ││   │
│  │                              └─────────────────────────┘│   │
│  │  Logic:                                                  │   │
│  │  • dashboard.js (250 lines)                             │   │
│  │    - Fetch API calls                                    │   │
│  │    - DOM manipulation                                   │   │
│  │    - WebSocket handlers                                 │   │
│  │    - Modal & form management                            │   │
│  │                                                          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│                    HTTP & WebSocket Requests                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ REST API & WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND (Python)                         │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  app.py (56 lines)                                         │   │
│  │  • Application factory                                     │   │
│  │  • Extensions initialization                              │   │
│  │  • Blueprint registration                                 │   │
│  │  • Database table creation                                │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ROUTING LAYER (Blueprints)                               │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │                                                            │   │
│  │  auth_routes.py (80 lines)      task_routes.py (100 ln)  │   │
│  │  ├── /api/auth/register        ├── /api/tasks (POST)     │   │
│  │  ├── /api/auth/login           ├── /api/tasks (GET)      │   │
│  │  ├── /api/auth/logout          ├── /api/tasks/<id> (PUT) │   │
│  │  ├── /api/auth/me              └── /api/tasks/<id> (DEL) │   │
│  │  ├── /login (page)                                       │   │
│  │  ├── /register (page)          analytics_routes (50 ln)  │   │
│  │  └── /dashboard (page)         ├── /api/analytics        │   │
│  │                                └── Pandas/NumPy calc     │   │
│  │  Utilities:                                              │   │
│  │  ├── Password hashing (bcrypt)                           │   │
│  │  ├── Session validation                                  │   │
│  │  ├── Input validation                                    │   │
│  │  └── Error handling                                      │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ORM MODELS (SQLAlchemy)                                   │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │                                                            │   │
│  │  User (35 lines)              Task (20 lines)           │   │
│  │  ├── id (PK)                  ├── id (PK)              │   │
│  │  ├── username (UNIQUE)        ├── user_id (FK)         │   │
│  │  ├── email (UNIQUE)           ├── title                │   │
│  │  ├── password_hash            ├── description          │   │
│  │  ├── created_at               ├── priority             │   │
│  │  ├── tasks (relationship)     ├── status               │   │
│  │  ├── set_password()           ├── created_at           │   │
│  │  ├── check_password()         ├── to_dict()            │   │
│  │  └── to_dict()                └── owner (relationship) │   │
│  │                                                          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  WEBSOCKET LAYER (Socket.IO)                              │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  socket_events.py (40 lines)                              │   │
│  │  ├── init_socketio(app)                                   │   │
│  │  ├── @socketio.on("connect")                              │   │
│  │  ├── @socketio.on("disconnect")                           │   │
│  │  ├── broadcast_task_event()                               │   │
│  │  └── User-specific rooms (no cross-user leaks)            │   │
│  │                                                            │   │
│  │  Events (emitted from routes):                           │   │
│  │  ├── task_created → broadcast                            │   │
│  │  ├── task_updated → broadcast                            │   │
│  │  └── task_deleted → broadcast                            │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  EXTENSIONS & MIDDLEWARE                                  │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  • db (SQLAlchemy)         → Database ORM               │   │
│  │  • bcrypt (Flask-Bcrypt)   → Password hashing           │   │
│  │  • login_manager           → Session management         │   │
│  │  • socketio (Flask-SocketIO) → Real-time                │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  config.py (28 lines)                                              │
│  ├── SECRET_KEY (for sessions)                                    │
│  ├── DATABASE_URL (PostgreSQL connection)                         │
│  ├── SQLALCHEMY_TRACK_MODIFICATIONS = False                       │
│  ├── SOCKETIO_ASYNC_MODE = "threading" (Windows compatible)       │
│  └── Development & Production configs                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ SQL Queries
                                │ Connection Pool
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      POSTGRESQL DATABASE                            │
│                                                                     │
│  ┌─ USERS TABLE ──────────────┐    ┌─ TASKS TABLE ──────────────┐ │
│  │                            │    │                            │ │
│  │ id (PK)              ════════════╗ id (PK)                  │ │
│  │ username (UNIQUE)          │    │ user_id (FK) ━━━━━━━━┫   │ │
│  │ email (UNIQUE)             │    │ title (VARCHAR 200)    │   │
│  │ password_hash              │    │ description (TEXT)     │   │
│  │ created_at (TIMESTAMP)     │    │ priority (Low/Med/High)│   │
│  │                            │    │ status (Pending/Done)  │   │
│  │                            │    │ created_at (TIMESTAMP) │   │
│  │                            │    │                        │   │
│  └────────────────────────────┘    └────────────────────────┘   │
│                                                                   │
│  INDEXES:                                                         │
│  • idx_tasks_user_id → Fast user task queries                    │
│  • idx_tasks_status  → Fast status filtering                     │
│                                                                   │
│  CONSTRAINTS:                                                     │
│  • user_id CASCADE DELETE → Remove user = remove tasks           │
│  • Priority CHECK constraint                                     │
│  • Status CHECK constraint                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagrams

### User Registration Flow
```
[Browser] 
    │
    ▼
[Register Form] → /api/auth/register (POST)
    │
    ▼
[validation] (username, email, password)
    │
    ▼
[bcrypt.generate_password_hash(password)]
    │
    ▼
[db.session.add(User)] → PostgreSQL
    │
    ▼
[Response 201] → Dashboard redirect
```

### Task Creation Flow
```
[Dashboard] 
    │
    ▼
[Create Task Modal] → /api/tasks (POST)
    │
    ▼
[validation] (title required, priority valid)
    │
    ▼
[db.session.add(Task)]
    │
    ▼
[_broadcast("task_created", task_dict)]
    │
    ▼ WebSocket
[socket.emit(event)] → All connected clients
    │
    ▼
[Frontend] Updates task list + analytics
```

### Analytics Calculation Flow
```
[/api/analytics GET]
    │
    ▼
[Task.query.filter_by(user_id=current_user.id).all()]
    │
    ▼ PostgreSQL
[db records] → Python dict list
    │
    ▼
[pd.DataFrame(records)] → Convert to Pandas DF
    │
    ▼
[(df["status"] == "Completed").sum()]
[(completed / total) * 100] → NumPy calculation
    │
    ▼
[JSON response] with statistics
    │
    ▼
[Frontend] Displays in analytics bar
```

### Real-time Update Flow
```
[User A] → Creates Task
    │
    ▼
[Task Route] → Saves to DB
    │
    ▼
[_broadcast("task_created", task_dict)]
    │
    ▼ WebSocket Room: user_A_1
[socketio.emit(event)]
    │
    ▼
[Frontend JS] on "task_created" event
    │
    ▼
[tasks.unshift(data)] → Update state
    │
    ▼
[renderTasks()] → Re-render UI
    │
    ▼
[User A sees task immediately]

Same flow for [User A] on another tab → [Sees instant update]
```

---

## 🔄 Request/Response Cycle

### Example: Create Task
```
1. Frontend (POST /api/tasks)
   {
     "title": "Buy groceries",
     "description": "Milk, bread, eggs",
     "priority": "High"
   }

2. Backend (task_routes.py)
   ├── Validate input
   ├── Create Task object
   ├── db.session.add(task)
   ├── db.session.commit()
   ├── Broadcast via WebSocket
   └── Return 201 Created

3. Response
   {
     "message": "Task created",
     "task": {
       "id": 1,
       "user_id": 42,
       "title": "Buy groceries",
       "description": "Milk, bread, eggs",
       "priority": "High",
       "status": "Pending",
       "created_at": "2024-05-23T10:30:00"
     }
   }

4. Frontend
   ├── Parse response
   ├── Add to tasks array
   ├── Re-render list
   ├── Update analytics
   ├── Show success toast
   └── Close modal

5. WebSocket (All connected clients)
   emit("task_created", {task_object})
   ├── Listeners update task list
   ├── Re-render
   ├── Update analytics
   └── Show "Real-time update" toast
```

---

## 🔐 Security Layers

```
┌─ Request ─────────────────────────────────────┐
│  ↓                                             │
│  CORS Check ✓ (allowed from same origin)       │
│  ↓                                             │
│  Route Permission ✓ (@login_required)          │
│  ↓                                             │
│  Input Validation ✓ (type, length, format)     │
│  ↓                                             │
│  Session Verification ✓ (Flask-Login)          │
│  ↓                                             │
│  Database Query ✓ (Parameterized, no SQL inj)  │
│  ↓                                             │
│  Response ✓ (JSON, proper status codes)        │
│  ↓                                             │
│  ✅ Secure                                    │
└─────────────────────────────────────────────────┘
```

---

## 📦 Dependency Graph

```
Flask 3.0.3
├── Werkzeug (WSGI)
├── Jinja2 (templating)
└── Click (CLI)

Flask-SocketIO 5.3.6
├── python-socketio 5.10.0
├── python-engineio
└── Greenlet 0.4.17

Flask-SQLAlchemy 3.1.1
├── SQLAlchemy 2.0.30
└── (provides ORM)

Flask-Login 0.6.3
└── (session management)

Flask-Bcrypt 1.0.1
└── bcrypt (password hashing)

Pandas 2.2.2
├── NumPy 1.26.4
├── Scipy
└── (data analysis)

psycopg2-binary 2.9.9
└── (PostgreSQL driver)

python-dotenv 1.0.1
└── (environment variables)
```

---

## 🏃 Runtime Architecture

```
┌─────────────────────────────────────────────┐
│  Python Process (app.py)                    │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  Thread 1: WSGI Server              │  │
│  │  ├── Listen on 0.0.0.0:5000        │  │
│  │  ├── Handle HTTP requests           │  │
│  │  ├── Route to Flask Blueprints      │  │
│  │  └── Return HTTP responses          │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  Thread 2: WebSocket Server         │  │
│  │  ├── Listen for Socket.IO connect   │  │
│  │  ├── Manage rooms (user-specific)   │  │
│  │  ├── Broadcast events               │  │
│  │  └── Handle disconnects             │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  Thread 3: Debugger (dev mode)      │  │
│  │  ├── Monitor for code changes       │  │
│  │  ├── Auto-restart on change         │  │
│  │  └── Provide debugging info         │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  DB Connection Pool (SQLAlchemy)    │  │
│  │  ├── PostgreSQL connections         │  │
│  │  ├── Query execution                │  │
│  │  └── Transaction management         │  │
│  └─────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
        │ Multi-threaded
        ├─ HTTP requests
        ├─ WebSocket events
        └─ Database queries
```

---

## 📈 Performance Considerations

```
Query Optimization:
├── Indexes on user_id (fast user queries)
├── Indexes on status (fast filtering)
├── Connection pooling (reduce DB overhead)
└── Result caching (session-based)

Analytics Optimization:
├── Single DB query (not n+1)
├── Vectorized Pandas operations
├── NumPy numerical calculations
└── Results cached per session

WebSocket Optimization:
├── User-specific rooms (not global broadcast)
├── Threading async mode (efficient)
├── Client-side event deduplication
└── Minimal payload size

Frontend Optimization:
├── Vanilla JS (no framework overhead)
├── CSS animations (GPU accelerated)
├── Lazy rendering (only visible tasks)
└── Toast notifications (single instance)
```

---

## 🔄 Scalability Path

```
Current (Single Server):
├── Flask + WebSocket on localhost:5000
├── PostgreSQL on localhost
└── Performance: Great for 1-100 concurrent users

Scale Step 1 (Multiple Flask instances):
├── Load balancer (nginx)
├── 3-5 Flask instances
├── Sticky sessions (for WebSocket)
└── Shared PostgreSQL
└── Performance: 100-1000 concurrent users

Scale Step 2 (Distributed):
├── Load balancer (nginx/AWS LB)
├── Flask instances (auto-scaling)
├── Redis (session store + pub/sub for WebSocket)
├── PostgreSQL (with replication/read replicas)
└── CDN (static files)
└── Performance: 1000-10000+ concurrent users

Scale Step 3 (Enterprise):
├── Kubernetes (container orchestration)
├── Microservices (separate auth, tasks, analytics)
├── Message queue (Celery/Kafka)
├── Data warehouse (analytics isolation)
├── Multi-region deployment
└── Performance: 10000+ concurrent users
```

---

This is the complete architecture of **TaskFlow**!

All components are integrated and working together seamlessly.

