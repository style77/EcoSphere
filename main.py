import curses
from ecosphere.common.systeminfo import SystemInfo

from ecosphere.overworld import Overworld
from ecosphere.system import System


def _init_colors():
    curses.start_color()
    if curses.COLORS >= 256:
        COLOR_LIGHT_GREEN = curses.COLOR_GREEN
        COLOR_DARK_GREEN = 22
        COLOR_GRAY = 244
    else:
        # Fallback
        COLOR_GRAY = curses.COLOR_WHITE
        COLOR_LIGHT_GREEN = curses.COLOR_GREEN
        COLOR_DARK_GREEN = curses.COLOR_GREEN

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_BLACK, COLOR_LIGHT_GREEN)
    curses.init_pair(4, curses.COLOR_BLACK, COLOR_DARK_GREEN)
    curses.init_pair(5, curses.COLOR_BLACK, COLOR_GRAY)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)


def setup_stdscr():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    _init_colors()

    return stdscr


if __name__ == "__main__":
    stdscr = setup_stdscr()
    stdscr.refresh()

    win = curses.newwin(0, 0)
    win.refresh()

    sysinfo = SystemInfo(win)
    ov = Overworld(win)
    sys = System(ov, sysinfo)
    sys.run()
