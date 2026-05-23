"""REST API endpoints for task CRUD operations."""

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from analytics.analytics import get_analytics
from models import Task, db
from sockets import socketio


tasks_bp = Blueprint("tasks", __name__)


def _emit_analytics():
    """Broadcast refreshed analytics to the current user's socket room."""
    analytics_payload = get_analytics(current_user.id)
    socketio.emit(
        "task_updated",
        analytics_payload,
        to=f"user_{current_user.id}",
    )
    return analytics_payload


@tasks_bp.get("/api/tasks")
@login_required
def list_tasks():
    """Return all tasks for the authenticated user."""
    try:
        tasks = (
            Task.query.filter_by(user_id=current_user.id)
            .order_by(Task.created_at.desc())
            .all()
        )
        return jsonify({"success": True, "tasks": [task.to_dict() for task in tasks]})
    except Exception:
        return jsonify({"success": False, "message": "Unable to load tasks."}), 500


@tasks_bp.post("/api/tasks")
@login_required
def create_task():
    """Create a new task for the authenticated user."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    priority = (data.get("priority") or "medium").lower()

    if not title:
        return jsonify({"success": False, "message": "Title is required."}), 400

    if priority not in {"high", "medium", "low"}:
        return jsonify({"success": False, "message": "Invalid priority value."}), 400

    try:
        task = Task(
            user_id=current_user.id,
            title=title,
            description=description,
            priority=priority,
        )
        db.session.add(task)
        db.session.commit()

        task_payload = task.to_dict()
        analytics_payload = _emit_analytics()
        socketio.emit("task_created", task_payload, to=f"user_{current_user.id}")

        return jsonify(
            {
                "success": True,
                "task": task_payload,
                "analytics": analytics_payload,
            }
        ), 201
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Unable to create task."}), 500


@tasks_bp.put("/api/tasks/<int:task_id>")
@login_required
def update_task(task_id: int):
    """Update a task owned by the authenticated user."""
    data = request.get_json(silent=True) or {}

    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({"success": False, "message": "Task not found."}), 404

        if "title" in data:
            title = (data.get("title") or "").strip()
            if not title:
                return jsonify({"success": False, "message": "Title is required."}), 400
            task.title = title

        if "description" in data:
            task.description = (data.get("description") or "").strip()

        if "priority" in data:
            priority = (data.get("priority") or "").lower()
            if priority not in {"high", "medium", "low"}:
                return jsonify({"success": False, "message": "Invalid priority value."}), 400
            task.priority = priority

        if "status" in data:
            status = (data.get("status") or "").lower()
            if status not in {"pending", "completed"}:
                return jsonify({"success": False, "message": "Invalid status value."}), 400
            task.status = status

        db.session.commit()
        analytics_payload = _emit_analytics()

        return jsonify(
            {
                "success": True,
                "task": task.to_dict(),
                "analytics": analytics_payload,
            }
        )
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Unable to update task."}), 500


@tasks_bp.delete("/api/tasks/<int:task_id>")
@login_required
def delete_task(task_id: int):
    """Delete a task owned by the authenticated user."""
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({"success": False, "message": "Task not found."}), 404

        deleted_id = task.id
        db.session.delete(task)
        db.session.commit()

        analytics_payload = _emit_analytics()
        socketio.emit("task_deleted", {"id": deleted_id}, to=f"user_{current_user.id}")

        return jsonify(
            {
                "success": True,
                "task": {"id": deleted_id},
                "analytics": analytics_payload,
            }
        )
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Unable to delete task."}), 500
