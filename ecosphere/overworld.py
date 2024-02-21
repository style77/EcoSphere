import curses
import random
from typing import Any

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.biome import BiomeManager
from ecosphere.common.singleton import SingletonMeta
from ecosphere.plants import Tree


class Overworld(metaclass=SingletonMeta):
    def __init__(self, stdscr: Any):
        self.stdscr = stdscr

        self.width = self.stdscr.getmaxyx()[1]
        self.height = self.stdscr.getmaxyx()[0]

        self.entities = []

        self.biome = BiomeManager(stdscr, self.width, self.height)

    def _calculate_entity_cap(self, frequency: float = 0.25):
        return self.width * self.height * frequency

    def _calculate_position(self):  # UNSAFE
        occupied = True
        while occupied:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            position = Position(x=x, y=y)

            if position not in [entity.position for entity in self.entities]:
                occupied = False

        return position

    def _draw_entity(self, entity: Entity, position: Position):
        biome = self.biome.get_biome_by_coords(position.x, position.y)
        biome_color = self.biome.get_biome_color(biome)

        char = entity.get_representation(biome)

        try:
            self.stdscr.addstr(position.y, position.x, char, biome_color)
        except curses.error:
            pass
        self.stdscr.refresh()

    def spawn_entity(self, entity: Entity, position: Position = None):
        """
        Create new entity and add it to the overworld.

        Attributes:
            entity: the entity to add to the overworld
            position: the position to add the entity to
        """
        if not position:
            position = self._calculate_position()
            biome = self.biome.get_biome_by_coords(position.x, position.y)
        else:
            biome = self.biome.get_biome_by_coords(position.x, position.y)

        spawn_rate = self.biome.ENTITY_BIOME_SPAWN_RATES.get(entity.__name__, {}).get(
            biome, 0
        )

        if random.random() < spawn_rate:
            entity = entity.create(position)
            self.entities.append(entity)

    def spawn_entities(self):
        """
        Spawn all the entities in the overworld.
        """
        for entity_class in [Tree]:
            cap = self._calculate_entity_cap(entity_class.frequency)
            for _ in range(round(cap)):
                self.spawn_entity(entity_class)

    def draw(self):
        """
        Draw all the existing entities on the board.
        """
        self.stdscr.clear()

        self.biome.draw()

        for entity in self.entities:
            self._draw_entity(entity, entity.position)

    def end(self):
        """
        End the overworld 😲.
        """
        self.stdscr.clear()

    def update(self):
        """
        Update all the entities in the overworld.
        """
        self.stdscr.clear()
