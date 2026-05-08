import argparse, sys
from datetime import date
from .manager import TodoManager
from .task import Status, Priority

RESET="\033[0m"; BOLD="\033[1m"; RED="\033[91m"; GREEN="\033[92m"
YELLOW="\033[93m"; BLUE="\033[94m"; CYAN="\033[96m"; GRAY="\033[90m"

PRIORITY_COLOR = {"low": GRAY, "medium": YELLOW, "high": RED}
STATUS_COLOR   = {"pending": YELLOW, "in_progress": BLUE, "done": GREEN}
STATUS_ICON    = {"pending": "○", "in_progress": "◑", "done": "●"}

def _fmt(task):
    sc = STATUS_COLOR.get(task.status.value, RESET)
    pc = PRIORITY_COLOR.get(task.priority.value, RESET)
    icon = STATUS_ICON.get(task.status.value, "?")
    due = ""
    if task.due_date:
        today = date.today().isoformat()
        if task.due_date < today:
            due = f"  {RED}⚠ OVERDUE {task.due_date}{RESET}"
        elif task.due_date == today:
            due = f"  {YELLOW}⏰ DUE TODAY{RESET}"
        else:
            due = f"  {GRAY}due {task.due_date}{RESET}"
    desc = f"\n      {GRAY}{task.description}{RESET}" if task.description else ""
    tags_str = f"  {CYAN}#{' #'.join(task.tags)}{RESET}" if task.tags else ""
    recurrence = f"  {CYAN}↻ {task.recurrence}{RESET}" if task.recurrence else ""
    return f"  {sc}{icon}{RESET} {BOLD}[{task.id}]{RESET} {task.title}  {pc}[{task.priority.value}]{RESET}{tags_str}{recurrence}{due}{desc}"

def _header(t): print(f"\n{CYAN}{BOLD}{t}{RESET}\n{CYAN}{'─'*len(t)}{RESET}")

def cmd_add(a, m):
    t = m.add_task(a.title, a.description or "", a.priority, a.due, tags=a.tags, recurrence=a.recur)
    print(f"\n{GREEN}✔ Task added!{RESET}"); print(_fmt(t))

def cmd_list(a, m):
    tasks = m.get_by_tag(a.tag) if a.tag else m.get_all()
    if a.status:   tasks = [t for t in tasks if t.status.value == a.status]
    if a.priority: tasks = [t for t in tasks if t.priority.value == a.priority]
    if a.search:
        kw = a.search.lower()
        tasks = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()]
    if not tasks: print(f"\n{GRAY}No tasks found.{RESET}"); return
    _header(f"Tasks ({len(tasks)})")
    for t in tasks: print(_fmt(t))
    print()

def cmd_done(a, m):
    result = m.complete_task(a.id)
    task, next_due = result if isinstance(result, tuple) else (result, None)
    print(f"\n{GREEN}✔ Done:{RESET} {task.title}")
    if next_due:
        print(f"{CYAN}↻ Next occurrence scheduled: {next_due}{RESET}")
def cmd_status(a, m): t = m.set_status(a.id, a.status); print(f"\n{GREEN}✔ Updated:{RESET} {t.title} → {t.status.value}")
def cmd_update(a, m):
    kw = {k: v for k, v in [("title",a.title),("description",a.description),("priority",a.priority),("due_date",a.due)] if v}
    if not kw: print(f"{YELLOW}Nothing to update.{RESET}"); return
    print(f"\n{GREEN}✔ Updated:{RESET}"); print(_fmt(m.update_task(a.id, **kw)))
def cmd_delete(a, m): t = m.delete_task(a.id); print(f"\n{RED}✖ Deleted:{RESET} {t.title}")
def cmd_clear(a, m):  n = m.clear_done(); print(f"\n{GREEN}✔ Cleared {n} task(s).{RESET}")
def cmd_stats(a, m):
    s = m.stats(); _header("Statistics")
    print(f"  Total: {BOLD}{s['total']}{RESET}\n\n  By Status:")
    for k,v in s["by_status"].items():   print(f"    {STATUS_COLOR.get(k,RESET)}{STATUS_ICON.get(k,'?')} {k:<14}{RESET}{v}")
    print("  By Priority:")
    for k,v in s["by_priority"].items(): print(f"    {PRIORITY_COLOR.get(k,RESET)}■ {k:<14}{RESET}{v}")
    print()

def cmd_export(a, m):
    from .exporter import export_csv, export_markdown

    path = export_csv(m, a.output) if a.format == "csv" else export_markdown(m, a.output)
    print(f"\n{GREEN}✔ Exported to:{RESET} {path}")

def main():
    p = argparse.ArgumentParser(prog="todo", description="📝 Todo Manager")
    s = p.add_subparsers(dest="command", metavar="<command>")
    a = s.add_parser("add");    a.add_argument("title"); a.add_argument("-d","--description",default=""); a.add_argument("-p","--priority",choices=["low","medium","high"],default="medium"); a.add_argument("--due",default=None); a.add_argument("--recur", choices=["daily", "weekly", "monthly"], default=None); a.add_argument("--tags", nargs="+", help="Tags e.g. --tags work urgent")
    l = s.add_parser("list");   l.add_argument("-s","--status",choices=["pending","in_progress","done"]); l.add_argument("-p","--priority",choices=["low","medium","high"]); l.add_argument("-q","--search"); l.add_argument("--tag", help="Filter by tag")
    d = s.add_parser("done");   d.add_argument("id")
    st = s.add_parser("status");st.add_argument("id"); st.add_argument("status",choices=["pending","in_progress","done"])
    u = s.add_parser("update"); u.add_argument("id"); u.add_argument("--title"); u.add_argument("-d","--description"); u.add_argument("-p","--priority",choices=["low","medium","high"]); u.add_argument("--due")
    dl = s.add_parser("delete");dl.add_argument("id")
    ex = s.add_parser("export", help="Export tasks to file"); ex.add_argument("format", choices=["csv","markdown"]); ex.add_argument("--output", help="Output file path", default=None)
    s.add_parser("clear"); s.add_parser("stats")
    args = p.parse_args()
    if not args.command: p.print_help(); sys.exit(0)
    cmds = {"add":cmd_add,"list":cmd_list,"done":cmd_done,"status":cmd_status,"update":cmd_update,"delete":cmd_delete,"clear":cmd_clear,"stats":cmd_stats,"export":cmd_export}
    try: cmds[args.command](args, TodoManager())
    except ValueError as e: print(f"\n{RED}Error:{RESET} {e}"); sys.exit(1)

if __name__ == "__main__": main()
