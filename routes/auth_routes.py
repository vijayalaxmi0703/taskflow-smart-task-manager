from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user_model import User

auth_bp = Blueprint("auth", __name__)


# ─── Page Routes ──────────────────────────────────────────────────────────────

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("login.html")


@auth_bp.route("/register")
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("register.html")


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


# ─── API Routes ────────────────────────────────────────────────────────────────

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user. Expects JSON: {username, email, password}."""
    data = request.get_json()

    # Input validation
    required = ("username", "email", "password")
    if not data or not all(k in data for k in required):
        return jsonify({"error": "username, email, and password are required"}), 400

    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if "@" not in email:
        return jsonify({"error": "Invalid email address"}), 400

    # Uniqueness checks
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # Create user (password is hashed inside set_password)
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Login. Expects JSON: {email, password}."""
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "email and password are required"}), 400

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Login successful", "user": user.to_dict()}), 200


@auth_bp.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    """Logout the current user and clear session."""
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@login_required
def me():
    """Return the currently authenticated user's profile."""
    return jsonify({"user": current_user.to_dict()}), 200
