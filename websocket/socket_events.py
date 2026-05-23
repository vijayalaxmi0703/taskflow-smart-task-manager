from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user

socketio = SocketIO()


def init_socketio(app):
    """Bind SocketIO to the Flask app."""
    socketio.init_app(
        app,
        async_mode="threading",
        cors_allowed_origins="*",
        logger=False,
        engineio_logger=False,
    )
    return socketio


# ─── Connection Events ─────────────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    """Client connected — join a user-specific room for targeted broadcasts."""
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        emit("connected", {"message": f"Welcome {current_user.username}!"})


@socketio.on("disconnect")
def on_disconnect():
    """Client disconnected."""
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")


# ─── Broadcast helpers (called from task_routes) ────────────────────────────

def broadcast_task_event(event: str, data: dict):
    """
    Emit a task event to the user's private room.
    Called by task_routes after DB changes.
    """
    if current_user.is_authenticated:
        socketio.emit(event, data, room=f"user_{current_user.id}")
