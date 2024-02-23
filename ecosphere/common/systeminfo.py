import curses
import psutil
from collections import Counter
from typing import Any, Counter as CounterType
from ecosphere.abc.entity import Entity
from ecosphere.common.singleton import SingletonMeta


class SystemInfo(metaclass=SingletonMeta):
    def __init__(self, stdscr: Any):
        self.stdscr = stdscr

        self.width: int = self.stdscr.getmaxyx()[1]
        self.height: int = self.stdscr.getmaxyx()[0]

        self.entities: CounterType[Entity] = Counter()
        self._dead_entities: CounterType[Entity] = Counter()

        self._time = 0  # Minutes counter

    @staticmethod
    def entity_created(entity: Entity):
        """
        Add entity to the system info.

        Attributes:
            entity: the entity to add to the system info counter
        """
        sysinfo = SystemInfo()

        entity_name = entity.__class__.__name__

        if entity_name not in sysinfo.entities:
            sysinfo.entities[entity_name] = 1
        else:
            sysinfo.entities[entity_name] += 1

    @staticmethod
    def entity_dead(entity: Entity):
        """
        Remove entity from the system info.

        Attributes:
            entity: the entity to remove from the system info counter
        """
        sysinfo = SystemInfo()

        entity_name = entity.__class__.__name__

        if entity_name not in sysinfo._dead_entities:
            sysinfo._dead_entities[entity_name] = 1
        else:
            sysinfo._dead_entities[entity_name] += 1

    @staticmethod
    def minute_passed():
        """
        Increment the day counter.
        """
        sysinfo = SystemInfo()

        sysinfo._time += 1

    def _get_overworld_info(self):
        """
        Get overworld info.
        """
        overworld_info = "🌎 | System Info: "

        if self.entities:
            _temp_vals = []
            for entity, count in self.entities.items():
                dead_count = self._dead_entities.get(entity, 0)
                alive = count - dead_count

                message = f"{entity} ({alive} alive, {self._dead_entities.get(entity, 0)} dead)"

                _temp_vals.append(message)

            overworld_info += "Entities: " + ", ".join(_temp_vals)

        if self._time is not None:
            days = self._time // 1440
            hours = (self._time % 1440) // 60
            minutes = self._time % 60
            overworld_info += f" | Time: {days}d {hours}h {minutes}m"

        return overworld_info

    def _get_machine_info(self):
        """
        Get machine info.
        """
        machine_info = "🕹️ | Machine Info: "

        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent

        if cpu_percent is not None and cpu_percent > 0.0 and cpu_percent < 100.0:
            machine_info += f"CPU: {int(cpu_percent)}% | MEM: {int(memory_percent)}%"
        return machine_info

    def draw(self):
        """
        Draw system info to the screen.
        """
        overworld_info = self._get_overworld_info()
        machine_info = self._get_machine_info()

        self.stdscr.addstr(self.height - 2, 0, overworld_info, curses.color_pair(7))
        self.stdscr.addstr(self.height - 1, 0, machine_info, curses.color_pair(7))
