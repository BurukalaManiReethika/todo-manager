import calendar
from datetime import date, timedelta

from .task import Priority, Status, Task
from .storage import Storage

class TodoManager:
    def __init__(self, storage=None):
        self.storage = storage or Storage()
        self.tasks = self.storage.load()

    def add_task(self, title, description="", priority="medium", due_date=None, tags=None, recurrence=None):
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        task = Task(title.strip(), description.strip(), Priority(priority.lower()), due_date, tags=tags or [], recurrence=recurrence)
        self.tasks.append(task)
        self._save()
        return task

    def get_all(self): return list(self.tasks)
    def get_by_id(self, task_id): return next((t for t in self.tasks if t.id == task_id), None)
    def get_by_status(self, status): return [t for t in self.tasks if t.status == Status(status)]
    def get_by_priority(self, priority): return [t for t in self.tasks if t.priority == Priority(priority)]
    def get_by_tag(self, tag: str): return [t for t in self.tasks if tag.lower() in [tg.lower() for tg in t.tags]]

    def get_overdue(self):
        today = date.today().isoformat()
        return [
            t for t in self.tasks
            if t.due_date and t.due_date < today and t.status != Status.DONE
        ]

    def get_due_today(self):
        today = date.today().isoformat()
        return [
            t for t in self.tasks
            if t.due_date == today and t.status != Status.DONE
        ]

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

    def complete_task(self, task_id):
        task = self._get_or_raise(task_id)
        task.status = Status.DONE
        self._save()

        if task.recurrence and task.due_date:
            next_due = self._next_due(task.due_date, task.recurrence)
            self.add_task(
                title=task.title,
                description=task.description,
                priority=task.priority.value,
                due_date=next_due,
                tags=task.tags,
                recurrence=task.recurrence,
            )
            return task, next_due
        return task, None

    def _next_due(self, due_date, recurrence):
        d = date.fromisoformat(due_date)
        if recurrence == "daily":
            d += timedelta(days=1)
        elif recurrence == "weekly":
            d += timedelta(weeks=1)
        elif recurrence == "monthly":
            month = d.month % 12 + 1
            year = d.year + (d.month // 12)
            day = min(d.day, calendar.monthrange(year, month)[1])
            d = d.replace(year=year, month=month, day=day)
        else:
            raise ValueError(f"Unsupported recurrence '{recurrence}'.")
        return d.isoformat()

    def escalate_priorities(self) -> list:
        """
        Escalate priorities for active tasks with nearby due dates.

        - Due within 1 day escalates to high.
        - Due within 3 days escalates low-priority tasks to medium.

        Returns a list of ``(task, old_priority)`` tuples for tasks that changed.
        """
        today = date.today()
        escalated = []

        for task in self.tasks:
            if task.status == Status.DONE or not task.due_date:
                continue

            due = date.fromisoformat(task.due_date)
            days = (due - today).days

            old_priority = task.priority
            if days <= 1 and task.priority != Priority.HIGH:
                task.priority = Priority.HIGH
            elif days <= 3 and task.priority == Priority.LOW:
                task.priority = Priority.MEDIUM

            if task.priority != old_priority:
                escalated.append((task, old_priority))

        if escalated:
            self._save()
        return escalated

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
