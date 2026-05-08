import json
import os
from .task import Task

class Storage:
    def __init__(self, filepath="tasks.json"):
        self.filepath = filepath

    def load(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, "r", encoding="utf-8") as f:
            try:
                return [Task.from_dict(item) for item in json.load(f)]
            except (json.JSONDecodeError, KeyError):
                return []

    def save(self, tasks):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)
