"""Analytics blueprint and Pandas/NumPy task metrics."""

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from models import Task


analytics_bp = Blueprint("analytics", __name__)


def get_analytics(user_id: int) -> dict:
    """Compute task analytics for a single user with Pandas and NumPy."""
    tasks = Task.query.filter_by(user_id=user_id).all()
    records = [task.to_dict() for task in tasks]
    df = pd.DataFrame(records)

    today = datetime.now(timezone.utc).date()
    last_seven_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

    if df.empty:
        tasks_by_date = [{"date": day.isoformat(), "count": 0} for day in last_seven_days]
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_pct": 0.0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "tasks_by_date": tasks_by_date,
            "avg_per_day": 0.0,
        }

    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    df["created_date"] = df["created_at"].dt.date

    total_tasks = max(0, int(df.shape[0]))
    completed_tasks = max(0, int(np.sum(df["status"] == "completed")))
    pending_tasks = max(0, int(np.sum(df["status"] == "pending")))
    completion_pct = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0
    high_priority = max(0, int(np.sum(df["priority"] == "high")))
    medium_priority = max(0, int(np.sum(df["priority"] == "medium")))
    low_priority = max(0, int(np.sum(df["priority"] == "low")))

    recent_counts = (
        df[df["created_date"].isin(last_seven_days)]
        .groupby("created_date")
        .size()
        .to_dict()
    )
    tasks_by_date = [
        {"date": day.isoformat(), "count": int(recent_counts.get(day, 0))}
        for day in last_seven_days
    ]
    avg_per_day = round(float(np.mean([item["count"] for item in tasks_by_date])), 1)

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_pct": max(0.0, completion_pct),
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "tasks_by_date": tasks_by_date,
        "avg_per_day": max(0.0, avg_per_day),
    }


@analytics_bp.get("/api/analytics")
@login_required
def analytics():
    """Return analytics for the authenticated user."""
    try:
        return jsonify({"success": True, "analytics": get_analytics(current_user.id)})
    except Exception:
        return jsonify({"success": False, "message": "Unable to load analytics."}), 500
