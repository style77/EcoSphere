import asyncio
import curses
import logging
import traceback
from typing import TYPE_CHECKING

from ecosphere.abc.position import Position
from ecosphere.common.event_bus import bus
from ecosphere.common.singleton import SingletonMeta
from ecosphere.config import MINUTE_LENGTH, REFRESH_STATIC_AFTER
from ecosphere.world.overworld import Overworld

if TYPE_CHECKING:
    from ecosphere.abc.entity import Entity
    from ecosphere.system import SystemInfo


class System(metaclass=SingletonMeta):
    def __init__(self, overworld: Overworld, system_info: "SystemInfo" = None):
        self.overworld = overworld
        self.system_info = system_info

        self.info_win = None

        self._running = True

        self._static_update_iter = 0

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
                self.info_win = await self.show_entity_info(
                    self.overworld.stdscr, entity
                )
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

    async def refresh_overworld(self):
        while self._running:
            self.overworld.draw(
                force_static=self._static_update_iter % REFRESH_STATIC_AFTER == 0
            )
            self.overworld.stdscr.refresh()

            await asyncio.sleep(0.1)

    async def update_system_info(self):
        while self._running:
            await self.system_info.draw()
            await asyncio.sleep(0.1)

    async def run(self) -> None:
        tasks = []
        try:
            self.overworld.spawn_entities()
            self.overworld.stdscr.nodelay(True)

            key_listener_task = asyncio.create_task(self.key_listeners())
            tasks.append(key_listener_task)

            if self.system_info:
                mouse_hover_task = asyncio.create_task(self.check_mouse_hover())
                info_task = asyncio.create_task(self.update_system_info())
                tasks.extend([mouse_hover_task, info_task])

            update_task = asyncio.create_task(self.overworld.update())
            refresh_task = asyncio.create_task(self.refresh_overworld())
            tasks.extend([update_task, refresh_task])

            while self._running:
                await asyncio.sleep(0.1)

            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.CancelledError:
            logging.info("Tasks were cancelled.")
        except Exception as e:
            logging.error(f"Unhandled exception: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        self.overworld.end()
        self.overworld.stdscr.nodelay(False)
        self.overworld.stdscr.clear()
        self.overworld.stdscr.refresh()
        curses.endwin()
        bus.emit("system:shutdown")
        logging.info("System shutting down")
