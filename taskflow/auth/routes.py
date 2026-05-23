"""Authentication and dashboard routes for TaskFlow."""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from models import bcrypt, db, User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login():
    """Render the login page for anonymous users."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("login.html")


@auth_bp.post("/login")
def login_post():
    """Authenticate a user and start a logged-in session."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    try:
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Welcome back to TaskFlow.", "success")
        return redirect(url_for("auth.dashboard"))
    except Exception:
        flash("We could not sign you in right now. Please try again.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.get("/register")
def register():
    """Render the registration page for anonymous users."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("register.html")


@auth_bp.post("/register")
def register_post():
    """Create a new user account with a hashed password."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not email or not password:
        flash("Username, email, and password are required.", "danger")
        return redirect(url_for("auth.register"))

    try:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with that email already exists.", "warning")
            return redirect(url_for("auth.register"))

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created successfully.", "success")
        return redirect(url_for("auth.dashboard"))
    except Exception:
        db.session.rollback()
        flash("Registration failed. Please try again.", "danger")
        return redirect(url_for("auth.register"))


@auth_bp.get("/logout")
@login_required
def logout():
    """Log out the current user and return to the login page."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.get("/dashboard")
@login_required
def dashboard():
    """Render the main authenticated dashboard."""
    return render_template("dashboard.html")
