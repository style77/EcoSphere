import curses
from dataclasses import dataclass
import sys
from typing import List
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
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)


def setup_stdscr():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    _init_colors()

    return stdscr


@dataclass
class SystemArgs:
    debug: bool = False
    sysinfo: bool = False


def _get_args(argv: List[str]) -> SystemArgs:
    debug = False
    sysinfo = False

    for arg in argv:
        if arg == "--debug" or arg == "-d":
            debug = True
        if arg == "--sysinfo" or arg == "-s":
            sysinfo = True

    return SystemArgs(debug, sysinfo)


if __name__ == "__main__":
    stdscr = setup_stdscr()
    stdscr.refresh()

    win = curses.newwin(0, 0)
    win.refresh()

    width = win.getmaxyx()[1] - 1
    height = win.getmaxyx()[0] - 1

    args = _get_args(sys.argv)

    sysinfo = SystemInfo(win) if args.sysinfo else None

    if sysinfo:
        width = sysinfo.width
        height = sysinfo.height - 2

    ov = Overworld(win, width, height)
    sys = System(ov, sysinfo)
    sys.run()
