from .task import Priority, Status, Task
from .storage import Storage

class TodoManager:
    def __init__(self, storage=None):
        self.storage = storage or Storage()
        self.tasks = self.storage.load()

    def add_task(self, title, description="", priority="medium", due_date=None):
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        task = Task(title.strip(), description.strip(), Priority(priority.lower()), due_date)
        self.tasks.append(task)
        self._save()
        return task

    def get_all(self): return list(self.tasks)
    def get_by_id(self, task_id): return next((t for t in self.tasks if t.id == task_id), None)
    def get_by_status(self, status): return [t for t in self.tasks if t.status == Status(status)]
    def get_by_priority(self, priority): return [t for t in self.tasks if t.priority == Priority(priority)]
    def search(self, keyword):
        kw = keyword.lower()
        return [t for t in self.tasks if kw in t.title.lower() or kw in t.description.lower()]

    def update_task(self, task_id, **kwargs):
        task = self._get_or_raise(task_id)
        for key, value in kwargs.items():
            if key not in {"title", "description", "priority", "due_date"}:
                raise ValueError(f"Cannot update field '{key}'.")
            setattr(task, key, Priority(value.lower()) if key == "priority" else value)
        self._save()
        return task

    def set_status(self, task_id, status):
        task = self._get_or_raise(task_id)
        task.status = Status(status.lower())
        self._save()
        return task

    def complete_task(self, task_id): return self.set_status(task_id, "done")

    def delete_task(self, task_id):
        task = self._get_or_raise(task_id)
        self.tasks.remove(task)
        self._save()
        return task

    def clear_done(self):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.status != Status.DONE]
        self._save()
        return before - len(self.tasks)

    def stats(self):
        return {
            "total": len(self.tasks),
            "by_status": {s.value: sum(1 for t in self.tasks if t.status == s) for s in Status},
            "by_priority": {p.value: sum(1 for t in self.tasks if t.priority == p) for p in Priority},
        }

    def _get_or_raise(self, task_id):
        task = self.get_by_id(task_id)
        if not task: raise ValueError(f"No task found with id '{task_id}'.")
        return task

    def _save(self): self.storage.save(self.tasks)
