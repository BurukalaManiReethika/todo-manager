<div align="center">

```
████████╗ ██████╗ ██████╗  ██████╗
╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗
   ██║   ██║   ██║██║  ██║██║   ██║
   ██║   ██║   ██║██║  ██║██║   ██║
   ██║   ╚██████╔╝██████╔╝╚██████╔╝
   ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝
```

### **Python CLI Task Manager**
*Simple. Fast. No nonsense.*

<br>

[![Python](https://img.shields.io/badge/Python-3.8%2B-FFD43B?style=for-the-badge&logo=python&logoColor=black)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-4ade80?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-20%20Passing-4ade80?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-f472b6?style=for-the-badge)](setup.py)
[![Storage](https://img.shields.io/badge/Storage-JSON-60a5fa?style=for-the-badge&logo=json&logoColor=white)](tasks.json)

</div>

---

## What is this?

A dead-simple task manager that lives in your terminal. No Electron app. No cloud account. No bloat. Just tasks, stored locally as JSON, managed with clean Python commands.

You add tasks. You complete them. You ship things.

---

## Install in 30 seconds

```bash
# Clone
git clone https://github.com/yourusername/todo-manager.git
cd todo-manager

# Install (makes `todo` available globally)
pip install -e .
```

> **Don't want to install?** Use `python -m todo_manager` instead of `todo` — same thing.

---

## Commands

### Add a task
```bash
todo add "Deploy to production"
todo add "Review PR #42" --priority high
todo add "Write docs" -d "Update API reference" --due 2024-12-31
```

### See your tasks
```bash
todo list                         # everything
todo list --status pending        # only pending
todo list --priority high         # only high priority
todo list --search "deploy"       # search by keyword
```

### Move tasks forward
```bash
todo status <id> in_progress      # start working
todo done <id>                    # mark complete
```

### Edit & clean up
```bash
todo update <id> --title "New title" --priority low
todo delete <id>                  # remove one task
todo clear                        # remove all done tasks
```

### Check your progress
```bash
todo stats
```

---

## What it looks like

```
Tasks (4)
─────────
  ● [a1b2c3d4] Deploy to production   [high]   due 2024-12-01
  ◑ [e5f6g7h8] Review PR #42          [medium]
  ○ [i9j0k1l2] Write docs             [low]    due 2024-12-31
  ○ [m3n4o5p6] Fix login bug          [high]
```

| Icon | Meaning     |
|------|-------------|
| `○`  | Pending     |
| `◑`  | In Progress |
| `●`  | Done        |

Priority colors in terminal: 🔴 high · 🟡 medium · ⚫ low

---

## Use as a library

```python
from todo_manager import TodoManager

mgr = TodoManager()

# Create
task = mgr.add_task("Ship feature X", priority="high", due_date="2024-12-01")

# Read
all_tasks   = mgr.get_all()
high_prio   = mgr.get_by_priority("high")
in_progress = mgr.get_by_status("in_progress")
results     = mgr.search("feature")

# Update
mgr.set_status(task.id, "in_progress")
mgr.update_task(task.id, title="Ship feature X (v2)", priority="medium")
mgr.complete_task(task.id)

# Delete
mgr.delete_task(task.id)
mgr.clear_done()          # remove all completed tasks

# Stats
print(mgr.stats())
# {'total': 5, 'by_status': {'pending': 3, 'in_progress': 1, 'done': 1}, ...}
```

---

## Project structure

```
todo-manager/
│
├── todo_manager/
│   ├── __init__.py       ← package exports
│   ├── __main__.py       ← enables python -m todo_manager
│   ├── task.py           ← Task model, Priority & Status enums
│   ├── storage.py        ← read/write JSON
│   ├── manager.py        ← all CRUD operations
│   └── cli.py            ← argparse CLI with color output
│
├── tests/
│   └── test_todo.py      ← 20 pytest tests
│
├── setup.py
├── requirements-dev.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Run the tests

```bash
pip install pytest
pytest tests/ -v
```

```
20 passed in 0.06s ✔
```

---

## How data is stored

Tasks are saved to `tasks.json` in your working directory. No database, no server, no account.

```json
[
  {
    "id": "a1b2c3d4",
    "title": "Deploy to production",
    "description": "",
    "priority": "high",
    "status": "pending",
    "created_at": "2024-11-20 09:00",
    "due_date": "2024-12-01"
  }
]
```

Move or copy `tasks.json` anywhere — your tasks follow.

---

## Requirements

- Python 3.8 or higher
- No third-party packages required
- `pytest` only for running tests

---

## License

MIT — do whatever you want with it.

---

<div align="center">

Built with Python · Stored as JSON · No cloud required

</div>
