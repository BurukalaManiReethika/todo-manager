import curses

from .manager import TodoManager

STATUS_ICONS = {"pending": "○", "in_progress": "◑", "done": "●"}


def _safe_addstr(window, y, x, text, width=None):
    """Draw text without overflowing narrow terminal windows."""
    if width is not None:
        text = text[: max(width - 1, 0)]
    if text:
        window.addstr(y, x, text)


def run_tui(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

    mgr = TodoManager()
    selected = 0

    while True:
        stdscr.clear()
        tasks = mgr.get_all()
        h, w = stdscr.getmaxyx()

        if tasks:
            selected = max(0, min(selected, len(tasks) - 1))
        else:
            selected = 0

        header = " 📝 TODO MANAGER  [↑↓] Navigate  [D] Done  [X] Delete  [Q] Quit "
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        _safe_addstr(stdscr, 0, 0, header.center(w), w)
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)

        if not tasks and h > 2:
            stdscr.attron(curses.A_DIM)
            _safe_addstr(stdscr, 2, 0, " No tasks yet. Press Q to quit.", w)
            stdscr.attroff(curses.A_DIM)

        for i, task in enumerate(tasks):
            y = i + 2
            if y >= h - 1:
                break

            icon = STATUS_ICONS.get(task.status.value, "?")
            title_width = max(w - 28, 1)
            line = f" {icon} [{task.id}] {task.title[:title_width]:<30} [{task.priority.value}]"
            color = {
                "done": curses.color_pair(1),
                "in_progress": curses.color_pair(2),
                "pending": curses.color_pair(3),
            }.get(task.status.value, 0)

            attrs = color | (curses.A_REVERSE if i == selected else 0)
            stdscr.attron(attrs)
            _safe_addstr(stdscr, y, 0, line, w)
            stdscr.attroff(attrs)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(tasks) - 1:
            selected += 1
        elif key in (ord("d"), ord("D")) and tasks:
            mgr.complete_task(tasks[selected].id)
            selected = min(selected, max(len(mgr.get_all()) - 1, 0))
        elif key in (ord("x"), ord("X")) and tasks:
            mgr.delete_task(tasks[selected].id)
            selected = min(selected, max(len(mgr.get_all()) - 1, 0))
        elif key in (ord("q"), ord("Q")):
            break


def launch():
    curses.wrapper(run_tui)
