"""Flask application factory for the TaskFlow project."""

from flask import Flask, redirect, url_for

from analytics import analytics_bp
from auth import auth_bp
from config import Config
from models import bcrypt, csrf, db, init_login_manager
from sockets import register_socket_events, socketio
from tasks import tasks_bp


def create_app() -> Flask:
    """Create, configure, and return the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    init_login_manager(app)
    socketio.init_app(
        app,
        async_mode=app.config["SOCKETIO_ASYNC_MODE"],
        cors_allowed_origins="*",
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(analytics_bp)
    register_socket_events()

    @app.get("/")
    def index():
        """Redirect visitors to the dashboard or login page."""
        return redirect(url_for("auth.dashboard"))

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
