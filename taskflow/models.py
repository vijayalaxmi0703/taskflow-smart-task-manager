"""Database models and extension instances for TaskFlow."""

from datetime import datetime, timezone

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import Enum


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()


def utc_now():
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def init_login_manager(app):
    """Configure Flask-Login for the application."""
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        """Load and return a user by identifier."""
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """Return JSON for API requests and redirects for browser views."""
        from flask import jsonify, redirect, request, url_for

        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Authentication required."}), 401
        return redirect(url_for("auth.login"))


class User(UserMixin, db.Model):
    """Application user model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    tasks = db.relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self) -> str:
        """Return a readable representation of the user."""
        return f"<User {self.email}>"


class Task(db.Model):
    """Task model belonging to an authenticated user."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(
        Enum("high", "medium", "low", name="priority_enum"),
        nullable=False,
        default="medium",
    )
    status = db.Column(
        Enum("pending", "completed", name="status_enum"),
        nullable=False,
        default="pending",
        index=True,
    )
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user = db.relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        """Return a readable representation of the task."""
        return f"<Task {self.id}: {self.title}>"

    def to_dict(self) -> dict:
        """Serialize the task into a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description or "",
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
