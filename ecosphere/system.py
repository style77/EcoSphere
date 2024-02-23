import asyncio
import curses
from ecosphere.abc.position import Position
from ecosphere.common.singleton import SingletonMeta
from ecosphere.systeminfo import SystemInfo
from ecosphere.config import MINUTE_LENGTH

from ecosphere.overworld import Overworld
from ecosphere.common.event_bus import bus

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecosphere.abc.entity import Entity


class System(metaclass=SingletonMeta):
    def __init__(self, overworld: Overworld, system_info: SystemInfo = None):
        self.overworld = overworld
        self.system_info = system_info

        self.info_win = None

        self._running = True

    async def show_entity_info(self, stdscr, entity: "Entity"):
        info_height = 11
        info_width = 50
        start_y, start_x = 1, 1

        info_win = curses.newwin(info_height, info_width, start_y, start_x)
        info_win.box()

        biome = self.overworld.biome.get_biome_by_coords(
            entity.position.x, entity.position.y
        )

        info_lines = [
            f"Entity Type: {type(entity).__name__} {entity.get_representation(biome)}",
            f"ID: {entity.id}",
            f"Position: ({entity.position.x}, {entity.position.y})",
            f"State: {getattr(entity, 'state', 'N/A')}",
            f"Health: {getattr(entity, 'health', 'N/A')}",
            f"Hunger: {getattr(entity, 'hunger', 'N/A')}",
            f"Thirst: {getattr(entity, 'thirst', 'N/A')}",
            f"Energy: {getattr(entity, 'energy', 'N/A')}",
            f"Mating Urge: {getattr(entity, 'mating_urge', 'N/A')}",
        ]

        for i, line in enumerate(info_lines, start=1):
            info_win.addstr(i, 1, line)

        info_win.refresh()
        stdscr.refresh()

        return info_win

    async def check_mouse_hover(self):
        while True:
            _, mx, my, _, _ = curses.getmouse()
            entity = self.overworld.get_entity_at_position(Position(mx, my))
            if entity:
                if self.info_win:
                    self.info_win.clear()
                self.info_win = await self.show_entity_info(self.overworld.stdscr, entity)
                self.info_win.refresh()
            else:
                if self.info_win:
                    self.info_win.clear()
                    self.info_win.refresh()
                    self.overworld.draw(force_static=True)
                    self.overworld.stdscr.refresh()
                    curses.doupdate()
                    self.info_win = None
            await asyncio.sleep(0.1)

    async def key_listeners(self):
        while True:
            c = self.overworld.stdscr.getch()
            if c:
                if c == ord("q"):
                    self._running = False
                    break
            await asyncio.sleep(0.1)

    async def run(self) -> None:
        self.overworld.spawn_entities()
        self.overworld.stdscr.nodelay(True)

        mouse_hover_task = asyncio.create_task(self.check_mouse_hover())
        key_listener_task = asyncio.create_task(self.key_listeners())

        try:
            while self._running:
                self.overworld.update()
                self.overworld.draw()

                if self.system_info:
                    self.system_info.draw()

                self.overworld.stdscr.refresh()

                await asyncio.sleep(MINUTE_LENGTH)
                bus.emit("minute:passed")
        finally:
            mouse_hover_task.cancel()
            key_listener_task.cancel()
            self.overworld.stdscr.nodelay(False)
            self.overworld.stdscr.clear()
            self.overworld.stdscr.refresh()
            curses.endwin()
            bus.emit("system:shutdown")
            print("System shutting down")
