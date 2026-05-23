from flask import Flask
from flask_login import LoginManager
from config import config
from models import db, bcrypt, login_manager
from models.user_model import User
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp, set_emit
from routes.analytics_routes import analytics_bp
from websocket.socket_events import init_socketio, broadcast_task_event


def create_app():
    """Application factory — creates and wires up the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config)

    # ── Initialize extensions ──────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"

    # ── User loader for Flask-Login ────────────────────────────────────────────
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify, request
        if request.path.startswith("/api/"):
            return jsonify({"error": "Authentication required"}), 401
        from flask import redirect, url_for
        return redirect(url_for("auth.login_page"))

    # ── Register Blueprints ────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(analytics_bp)

    # ── Initialize WebSocket ───────────────────────────────────────────────────
    socketio = init_socketio(app)

    # Inject broadcast function into task routes (avoids circular imports)
    set_emit(broadcast_task_event)

    # ── Create DB tables ───────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app, socketio


app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
