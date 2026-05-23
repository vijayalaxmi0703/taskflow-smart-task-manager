from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.task_model import Task

task_bp = Blueprint("tasks", __name__)

# WebSocket emit function is injected at app init to avoid circular imports
_emit_event = None

def set_emit(fn):
    """Inject the SocketIO emit callable after app creation."""
    global _emit_event
    _emit_event = fn


def _broadcast(event: str, data: dict):
    """Safely emit a SocketIO event if available."""
    if _emit_event:
        _emit_event(event, data)


# ─── Helper ────────────────────────────────────────────────────────────────────

def _get_task_or_404(task_id: int):
    """Fetch a task that belongs to the logged-in user, or return 404."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return None, jsonify({"error": "Task not found"}), 404
    return task, None, None


# ─── API Routes ────────────────────────────────────────────────────────────────

@task_bp.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    """Create a new task for the current user."""
    data = request.get_json()

    if not data or not data.get("title", "").strip():
        return jsonify({"error": "title is required"}), 400

    priority = data.get("priority", "Medium")
    if priority not in Task.PRIORITY_CHOICES:
        return jsonify({"error": f"priority must be one of {Task.PRIORITY_CHOICES}"}), 400
    mutation_id = (data.get("mutation_id") or "").strip() or None

    try:
        task = Task(
            user_id=current_user.id,
            title=data["title"].strip(),
            description=data.get("description", "").strip(),
            priority=priority,
            status="Pending",
        )
        db.session.add(task)
        db.session.commit()

        task_dict = task.to_dict()
        _broadcast("task_created", {"task": task_dict, "meta": {"mutation_id": mutation_id}})

        return jsonify({"message": "Task created", "task": task_dict}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create task"}), 500


@task_bp.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    """Return all tasks for the current user, optional ?status= filter."""
    status_filter = request.args.get("status")
    query = Task.query.filter_by(user_id=current_user.id)

    if status_filter in Task.STATUS_CHOICES:
        query = query.filter_by(status=status_filter)

    try:
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200
    except Exception:
        return jsonify({"error": "Failed to load tasks"}), 500


@task_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id: int):
    """Update a task's title, description, priority, or status."""
    task, err, code = _get_task_or_404(task_id)
    if err:
        return err, code

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    mutation_id = (data.get("mutation_id") or "").strip() or None

    try:
        # Apply allowed updates
        if "title" in data:
            title = data["title"].strip()
            if not title:
                return jsonify({"error": "title cannot be empty"}), 400
            task.title = title

        if "description" in data:
            task.description = data["description"].strip()

        if "priority" in data:
            if data["priority"] not in Task.PRIORITY_CHOICES:
                return jsonify({"error": f"priority must be one of {Task.PRIORITY_CHOICES}"}), 400
            task.priority = data["priority"]

        if "status" in data:
            if data["status"] not in Task.STATUS_CHOICES:
                return jsonify({"error": f"status must be one of {Task.STATUS_CHOICES}"}), 400
            task.status = data["status"]

        db.session.commit()

        task_dict = task.to_dict()
        _broadcast("task_updated", {"task": task_dict, "meta": {"mutation_id": mutation_id}})

        return jsonify({"message": "Task updated", "task": task_dict}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update task"}), 500


@task_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: int):
    """Delete a task owned by the current user."""
    task, err, code = _get_task_or_404(task_id)
    if err:
        return err, code

    mutation_id = (request.get_json(silent=True) or {}).get("mutation_id")

    try:
        task_dict = task.to_dict()
        db.session.delete(task)
        db.session.commit()

        _broadcast("task_deleted", {"id": task_id, "meta": {"mutation_id": mutation_id}})

        return jsonify({"message": "Task deleted", "task": task_dict}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete task"}), 500
