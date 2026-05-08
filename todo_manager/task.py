import uuid
from datetime import datetime
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task:
    def __init__(self, title, description="", priority=Priority.MEDIUM, due_date=None, tags=None, recurrence=None):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.priority = priority
        self.status = Status.PENDING
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.due_date = due_date
        self.tags = tags if tags else []
        self.recurrence = recurrence

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "priority": self.priority.value, "status": self.status.value,
            "created_at": self.created_at, "due_date": self.due_date,
            "tags": self.tags, "recurrence": self.recurrence,
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(title=data["title"], description=data.get("description", ""),
                   priority=Priority(data.get("priority", "medium")), due_date=data.get("due_date"),
                   tags=data.get("tags", []), recurrence=data.get("recurrence"))
        task.id = data["id"]
        task.status = Status(data.get("status", "pending"))
        task.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
        return task
