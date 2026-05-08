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
