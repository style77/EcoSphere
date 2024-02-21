import curses
from ecosphere.common.singleton import SingletonMeta
from ecosphere.common.systeminfo import SystemInfo

from ecosphere.overworld import Overworld
from ecosphere.plants import Tree

ENTITIES = {
    Tree: 800,
}
HOUR_LENGTH = 10  # seconds


class System(metaclass=SingletonMeta):
    def __init__(self, overworld: Overworld, system_info: SystemInfo = None):
        self.overworld = overworld
        self.system_info = system_info

    def __listen_for_end(self) -> bool:
        key = self.overworld.stdscr.getch()
        if key == ord("q"):
            self.overworld.end()
            return True
        return False

    def run(self):
        self.overworld.spawn_entities()

        while True:
            self.overworld.update()
            self.overworld.draw()

            if self.system_info:
                self.system_info.draw()

            if self.__listen_for_end():
                return

            curses.napms(HOUR_LENGTH * 1000)
