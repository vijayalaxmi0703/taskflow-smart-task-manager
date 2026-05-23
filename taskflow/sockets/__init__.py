"""Socket.IO extension exports."""

from flask_socketio import SocketIO

socketio = SocketIO()

from .events import register_socket_events  # noqa: E402

__all__ = ["socketio", "register_socket_events"]
