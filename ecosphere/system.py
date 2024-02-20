import curses

from ecosphere.overworld import Overworld
from ecosphere.plants import Tree

ENTITIES = {
    Tree: 700,
}
HOUR_LENGTH = 10  # seconds


class System:
    def __init__(self, overworld: Overworld):
        self.overworld = overworld

    def __listen_for_end(self) -> bool:
        key = self.overworld.stdscr.getch()
        if key == ord("q"):
            self.overworld.end()
            return True
        return False

    def spawn_entities(self):
        for key, value in ENTITIES.items():
            for _ in range(value):
                self.overworld.spawn_entity(key)

    def run(self):
        self.spawn_entities()

        while True:
            self.overworld.update()

            self.overworld.draw()

            if self.__listen_for_end():
                return

            curses.napms(HOUR_LENGTH * 1000)
