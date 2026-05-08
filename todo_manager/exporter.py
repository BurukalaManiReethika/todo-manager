import csv
from datetime import datetime
from typing import Optional

from .manager import TodoManager


EXPORT_FIELDS = [
    "id",
    "title",
    "description",
    "priority",
    "status",
    "created_at",
    "due_date",
]


def _timestamped_filepath(extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"tasks_export_{timestamp}.{extension}"


def export_csv(mgr: TodoManager, filepath: Optional[str] = None) -> str:
    """Export all tasks from a manager to a CSV file and return its path."""
    filepath = filepath or _timestamped_filepath("csv")
    tasks = mgr.get_all()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for task in tasks:
            task_data = task.to_dict()
            writer.writerow({field: task_data.get(field, "") for field in EXPORT_FIELDS})

    return filepath


def export_markdown(mgr: TodoManager, filepath: Optional[str] = None) -> str:
    """Export all tasks from a manager to a Markdown table and return its path."""
    filepath = filepath or _timestamped_filepath("md")
    tasks = mgr.get_all()
    lines = [
        "# Task Export\n",
        "| ID | Title | Priority | Status | Due Date |",
        "|---|---|---|---|---|",
    ]

    for task in tasks:
        due_date = task.due_date or "—"
        lines.append(
            f"| {task.id} | {task.title} | {task.priority.value} | "
            f"{task.status.value} | {due_date} |"
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
