import asyncio
import curses
import logging
import sys
from dataclasses import dataclass
from typing import List, Literal

from ecosphere.common.event_bus import bus
from ecosphere.logging import set_logging_level
from ecosphere.system import System, SystemInfo
from ecosphere.world.overworld import Overworld


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
    curses.mousemask(1)
    curses.curs_set(0)

    _init_colors()

    return stdscr


@dataclass
class SystemArgs:
    loglevel: Literal["debug", "info", "warning", "error", "critical"] = "info"
    sysinfo: bool = False


def _get_args(argv: List[str]) -> SystemArgs:
    sysinfo = False
    loglevel = "info"

    for arg in argv:
        if arg == "--sysinfo" or arg == "-s":
            sysinfo = True

        if arg == "--info" or arg == "-i":
            loglevel = "info"
        if arg == "--debug" or arg == "-d":
            loglevel = "debug"

    return SystemArgs(loglevel, sysinfo)


def register_listeners(sysinfo: SystemInfo):
    bus.listener("minute:passed")(sysinfo.minute_passed)
    bus.listener("entity:dead")(sysinfo.entity_dead)
    bus.listener("entity:created")(sysinfo.entity_created)


def main(stdscr) -> None:
    win = stdscr

    width = win.getmaxyx()[1]
    height = win.getmaxyx()[0]

    args = _get_args(sys.argv)

    sysinfo = None
    if args.sysinfo:
        sysinfo = SystemInfo(win)
        register_listeners(sysinfo)

    set_logging_level(args.loglevel)

    if sysinfo is not None:
        width = width
        height = height - 3

    ov = Overworld(win, width, height)
    system = System(ov, sysinfo)

    logging.info("Starting system")
    return asyncio.run(system.run())


if __name__ == "__main__":
    stdscr = setup_stdscr()
    main(stdscr)
