"""WebSocket event handlers for TaskFlow."""

from flask_login import current_user
from flask_socketio import disconnect, emit, join_room

from analytics.analytics import get_analytics
from . import socketio


def register_socket_events():
    """Register all socket event handlers."""

    @socketio.on("connect")
    def handle_connect():
        """Join the authenticated user to a personal realtime room."""
        if not current_user.is_authenticated:
            disconnect()
            return

        room = f"user_{current_user.id}"
        join_room(room)
        emit(
            "task_updated",
            get_analytics(current_user.id),
            to=room,
        )
