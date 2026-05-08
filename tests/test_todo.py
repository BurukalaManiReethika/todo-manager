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
