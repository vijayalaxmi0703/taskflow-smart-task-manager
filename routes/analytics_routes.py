import numpy as np
import pandas as pd
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.task_model import Task

analytics_bp = Blueprint("analytics", __name__)


def build_analytics_payload(tasks):
    """Build a safe analytics payload from task model instances."""
    if not tasks:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_percentage": 0,
            "by_priority": {"Low": 0, "Medium": 0, "High": 0},
        }

    records = [task.to_dict() for task in tasks]
    df = pd.DataFrame(records)

    total = max(0, int(len(df)))
    completed = max(0, int((df["status"] == "Completed").sum()))
    pending = max(0, int((df["status"] == "Pending").sum()))
    completion_pct = int(np.round((completed / total) * 100)) if total > 0 else 0

    priority_counts = df["priority"].value_counts().to_dict()
    by_priority = {
        "Low": max(0, int(priority_counts.get("Low", 0))),
        "Medium": max(0, int(priority_counts.get("Medium", 0))),
        "High": max(0, int(priority_counts.get("High", 0))),
    }

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "completion_percentage": max(0, completion_pct),
        "by_priority": by_priority,
    }


@analytics_bp.route("/api/analytics", methods=["GET"])
@login_required
def get_analytics():
    """
    Return task analytics for the current user.

    Uses Pandas to build a DataFrame from DB records and NumPy for
    percentage calculation so the data pipeline is explicit and extensible.
    """
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify(build_analytics_payload(tasks)), 200
