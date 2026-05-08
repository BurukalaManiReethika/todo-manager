from datetime import date, timedelta

import pytest
from todo_manager.task import Task, Priority, Status
from todo_manager.storage import Storage
from todo_manager.manager import TodoManager

@pytest.fixture
def mgr(tmp_path):
    return TodoManager(storage=Storage(str(tmp_path / "tasks.json")))

def test_add_task(mgr):          assert mgr.add_task("Test").title == "Test"
def test_empty_title(mgr):       
    with pytest.raises(ValueError): mgr.add_task("  ")
def test_complete(mgr):          
    t = mgr.add_task("T"); mgr.complete_task(t.id); assert mgr.get_by_id(t.id).status == Status.DONE
def test_delete(mgr):            
    t = mgr.add_task("T"); mgr.delete_task(t.id); assert mgr.get_by_id(t.id) is None
def test_search(mgr):            
    mgr.add_task("Buy milk"); mgr.add_task("Write code"); assert len(mgr.search("milk")) == 1
def test_stats(mgr):             
    mgr.add_task("T"); s = mgr.stats(); assert s["total"] == 1
def test_persistence(tmp_path):  
    s = Storage(str(tmp_path/"t.json")); TodoManager(s).add_task("X"); assert len(TodoManager(s).get_all()) == 1


def test_due_date_filters(mgr):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    overdue = mgr.add_task("Overdue", due_date=yesterday)
    due_today = mgr.add_task("Due today", due_date=today)
    future = mgr.add_task("Future", due_date=tomorrow)
    done_overdue = mgr.add_task("Done overdue", due_date=yesterday)
    mgr.complete_task(done_overdue.id)

    assert mgr.get_overdue() == [overdue]
    assert mgr.get_due_today() == [due_today]
    assert future not in mgr.get_overdue()


def test_tags_filter_and_persistence(tmp_path):
    storage = Storage(str(tmp_path / "tasks.json"))
    mgr = TodoManager(storage=storage)
    work = mgr.add_task("Team meeting", tags=["work", "meetings"])
    mgr.add_task("Buy milk", tags=["personal"])

    assert work.tags == ["work", "meetings"]
    assert mgr.get_by_tag("WORK") == [work]

    reloaded = TodoManager(storage=storage)
    assert reloaded.get_by_tag("meetings")[0].tags == ["work", "meetings"]


def test_export_csv(mgr, tmp_path):
    from todo_manager.exporter import export_csv

    task = mgr.add_task("Export me", "Details", priority="high", due_date="2026-05-09")
    output = tmp_path / "tasks.csv"

    path = export_csv(mgr, str(output))

    assert path == str(output)
    assert output.read_text(encoding="utf-8").splitlines() == [
        "id,title,description,priority,status,created_at,due_date",
        f"{task.id},Export me,Details,high,pending,{task.created_at},2026-05-09",
    ]


def test_export_markdown(mgr, tmp_path):
    from todo_manager.exporter import export_markdown

    task = mgr.add_task("Export me", priority="low")
    output = tmp_path / "tasks.md"

    path = export_markdown(mgr, str(output))

    assert path == str(output)
    assert output.read_text(encoding="utf-8") == "\n".join([
        "# Task Export\n",
        "| ID | Title | Priority | Status | Due Date |",
        "|---|---|---|---|---|",
        f"| {task.id} | Export me | low | pending | — |",
    ])


def test_recurring_task_completion_creates_next_daily_occurrence(mgr):
    task = mgr.add_task(
        "Team standup",
        description="Daily sync",
        priority="high",
        due_date="2024-12-01",
        tags=["work"],
        recurrence="daily",
    )

    completed, next_due = mgr.complete_task(task.id)

    assert completed == task
    assert completed.status == Status.DONE
    assert next_due == "2024-12-02"
    next_task = [t for t in mgr.get_all() if t.id != task.id][0]
    assert next_task.title == "Team standup"
    assert next_task.description == "Daily sync"
    assert next_task.priority == Priority.HIGH
    assert next_task.due_date == "2024-12-02"
    assert next_task.tags == ["work"]
    assert next_task.recurrence == "daily"
    assert next_task.status == Status.PENDING


def test_recurring_task_monthly_uses_calendar_months(mgr):
    assert mgr._next_due("2024-01-31", "monthly") == "2024-02-29"


def test_task_recurrence_persistence(tmp_path):
    storage = Storage(str(tmp_path / "tasks.json"))
    task = TodoManager(storage).add_task("Pay rent", due_date="2024-12-01", recurrence="monthly")

    reloaded = TodoManager(storage).get_by_id(task.id)

    assert reloaded.recurrence == "monthly"


def test_escalate_priorities_updates_active_tasks_near_due_dates(mgr):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    three_days = (date.today() + timedelta(days=3)).isoformat()
    later = (date.today() + timedelta(days=4)).isoformat()

    urgent = mgr.add_task("Urgent report", priority="low", due_date=tomorrow)
    soon = mgr.add_task("Soon task", priority="low", due_date=three_days)
    already_medium = mgr.add_task("Medium task", priority="medium", due_date=three_days)
    later_task = mgr.add_task("Later task", priority="low", due_date=later)
    no_due = mgr.add_task("No due date", priority="low")
    done = mgr.add_task("Done task", priority="low", due_date=tomorrow)
    mgr.complete_task(done.id)

    escalated = mgr.escalate_priorities()

    assert escalated == [(urgent, Priority.LOW), (soon, Priority.LOW)]
    assert urgent.priority == Priority.HIGH
    assert soon.priority == Priority.MEDIUM
    assert already_medium.priority == Priority.MEDIUM
    assert later_task.priority == Priority.LOW
    assert no_due.priority == Priority.LOW
    assert done.priority == Priority.LOW


def test_escalate_priorities_persists_changes(tmp_path):
    storage = Storage(str(tmp_path / "tasks.json"))
    mgr = TodoManager(storage=storage)
    task = mgr.add_task(
        "Urgent report",
        priority="low",
        due_date=(date.today() + timedelta(days=1)).isoformat(),
    )

    assert mgr.escalate_priorities() == [(task, Priority.LOW)]

    reloaded = TodoManager(storage=storage).get_by_id(task.id)
    assert reloaded.priority == Priority.HIGH


def test_cmd_check_reports_escalated_tasks(mgr, capsys):
    from argparse import Namespace
    from todo_manager.cli import cmd_check

    mgr.add_task(
        "Urgent report",
        priority="low",
        due_date=(date.today() + timedelta(days=1)).isoformat(),
    )

    cmd_check(Namespace(), mgr)

    output = capsys.readouterr().out
    assert "Escalated 1 task(s)" in output
    assert "Urgent report" in output
    assert "low" in output
    assert "high" in output
