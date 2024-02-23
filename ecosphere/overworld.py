import curses
import random
from typing import Any, List

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.biome import Biome, BiomeManager
from ecosphere.common.singleton import SingletonMeta
from ecosphere.config import ENTITIES, ENTITY_BIOME_SPAWN_RATES
from ecosphere.common.event_bus import bus


class Overworld(metaclass=SingletonMeta):
    def __init__(self, stdscr: Any, width: int, height: int):
        self.stdscr = stdscr

        self.width = width
        self.height = height

        self.entities: List[Entity] = []

        self.biome = BiomeManager(stdscr, self.width, self.height)

        self._static_drawn = False

    def _calculate_entity_cap(self, frequency: float = 0.25):
        return self.width * self.height * frequency

    def _calculate_position(self):  # UNSAFE
        occupied = True
        while occupied:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            position = Position(x=x, y=y)

            if not self.is_occupied(position):
                occupied = False

        return position

    def _get_spawn_rate(self, entity: Entity, biome: Biome):
        for entity_biome_spawn_rate in ENTITY_BIOME_SPAWN_RATES:
            if entity_biome_spawn_rate.entity_name == entity.__name__:
                return getattr(entity_biome_spawn_rate.spawn_rates, biome.name, 0)
        return 0

    def _draw_entity(self, entity: Entity, position: Position):
        biome = self.biome.get_biome_by_coords(position.x, position.y)
        biome_color = self.biome.get_biome_color(biome)

        char = entity.representation

        try:
            self.stdscr.addstr(position.y, position.x, char, biome_color)
        except curses.error:
            pass

    def draw(self):
        """
        Draw all the existing entities on the board.
        """

        if not self._static_drawn:
            self.biome.draw()

            static_entities = [entity for entity in self.entities if not entity.dynamic]
            for entity in static_entities:
                self._draw_entity(entity, entity.position)
            self._static_drawn = True

        dynamic_entities = [entity for entity in self.entities if entity.dynamic]

        for entity in dynamic_entities:
            self._draw_entity(entity, entity.position)

        self.stdscr.refresh()

    def end(self):
        """
        End the overworld 😲.
        """
        self.stdscr.clear()

    def get_nearby_entities(self, entity: Entity, perception_range: int):
        nearby_entities = []
        for other_entity in self.entities:
            if self.is_within_range(entity.position, other_entity.position, perception_range):
                nearby_entities.append(entity)
        return nearby_entities

    def is_occupied(self, position: Position):
        return position in [entity.position for entity in self.entities]

    def is_within_range(self, position: Position, other_position: Position, range: int):
        return (
            abs(position.x - other_position.x) <= range
            and abs(position.y - other_position.y) <= range
        )

    def update(self):
        """
        Update all the entities in the overworld.
        """
        for entity in self.entities:
            if not entity.dynamic:
                continue

            entity.update(self, self.biome)

    def spawn_entities(self):
        """
        Spawn all the entities in the overworld.
        """
        for entity_class in ENTITIES:
            cap = self._calculate_entity_cap(entity_class.frequency)
            for _ in range(round(cap)):
                self.spawn_entity(entity_class)

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

        spawn_rate = self._get_spawn_rate(entity, biome)

        if random.random() < spawn_rate:
            entity = entity.create(position, biome)
            self.entities.append(entity)
            bus.emit("entity:created", entity)
