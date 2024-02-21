import curses
from collections import Counter
from typing import Any
from ecosphere.abc.entity import Entity
from ecosphere.common.singleton import SingletonMeta
from ecosphere.common.event_bus import bus


class SystemInfo(metaclass=SingletonMeta):
    def __init__(self, stdscr: Any):
        self.stdscr = stdscr

        self.width = self.stdscr.getmaxyx()[1]
        self.height = self.stdscr.getmaxyx()[0]

        self.entities = Counter()  # Class determined count of entities

    @staticmethod
    @bus.listener("entity:created")
    def add_entity(entity: Entity):
        """
        Add entity to the system info.

        Attributes:
            entity: the entity to add to the system info counter
        """
        sysinfo = (
            SystemInfo()
        )  # Singleton, that might not be the best approach, but it works for now

        entity_name = entity.__class__.__name__

        if entity_name not in sysinfo.entities:
            sysinfo.entities[entity_name] = 1
        else:
            sysinfo.entities[entity_name] += 1

    def draw(self):
        """
        Draw system info to the screen.
        """
        text = "🌎 | System Info: "

        if self.entities:
            _temp_vals = []
            for entity, count in self.entities.items():
                _temp_vals.append(f"{entity} ({count})")
            text += "Entities: " + ", ".join(_temp_vals)

        self.stdscr.addstr(self.height - 1, 4, text, curses.COLOR_WHITE)
