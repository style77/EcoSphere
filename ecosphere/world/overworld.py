import asyncio
import curses
import logging
import random
from typing import Any, List

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.common.event_bus import bus
from ecosphere.common.onetime_caller import OneTimeCaller
from ecosphere.common.singleton import SingletonMeta
from ecosphere.config import ENTITIES, ENTITY_BIOME_SPAWN_RATES, MINUTE_LENGTH
from ecosphere.states.dead_state import DeadState
from ecosphere.world.biome import Biome, BiomeManager


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

    def draw(self, force_static: bool = False):
        """
        Draw all the existing entities on the board.
        """
        logging.debug("Drawing entities in the overworld.")
        if not self._static_drawn or force_static:
            self.biome.draw()

            static_entities = [entity for entity in self.entities if not entity.dynamic]
            for entity in static_entities:
                self._draw_entity(entity, entity.position)
            self._static_drawn = True

        dynamic_entities = [entity for entity in self.entities if entity.dynamic]

        for entity in dynamic_entities:
            self._draw_entity(entity, entity.position)
        logging.debug("Entities drawn.")

    def end(self):
        """
        End the overworld 😲.
        """
        logging.debug("Ending the overworld. Clearing screen.")
        self.stdscr.clear()

    def get_entity_at_position(
        self, position: Position, dynamic_only: bool = True, range: int = 2
    ):
        entities = [
            entity for entity in self.entities if not dynamic_only or entity.dynamic
        ]
        for entity in entities:
            if entity.position.is_within_range(position, range):
                return entity
        return None

    def get_nearby_entities(self, entity: Entity, perception_range: int):
        nearby_entities = []
        for other_entity in self.entities:
            if entity.position.is_within_range(other_entity.position, perception_range):
                nearby_entities.append(entity)
        return nearby_entities

    def is_occupied(self, position: Position):
        return position in [entity.position for entity in self.entities]

    async def update_entity(self, entity):
        while not isinstance(entity.state, DeadState):
            await entity.update(self, self.biome)
            await asyncio.sleep(MINUTE_LENGTH / entity.properties.movement_speed)

    async def update(self):
        """
        Update all the entities in the overworld.
        """
        logging.debug("Updating entities in the overworld.")
        update_tasks = [
            asyncio.create_task(self.update_entity(entity))
            for entity in self.entities
            if entity.dynamic
        ]

        await asyncio.gather(*update_tasks)

        logging.info("Entities updated.")

    def _spawn_entities(self):
        for entity_class in ENTITIES:
            cap = self._calculate_entity_cap(entity_class.frequency)
            for _ in range(round(cap)):
                self.spawn_entity(entity_class)

    def spawn_entities(self):
        """
        Spawn all the entities in the overworld.
        """
        logging.debug("Spawning entities in the overworld.")
        oc = OneTimeCaller(self._spawn_entities)
        oc()
        logging.info("Entities spawned.")

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
            logging.debug(f"{entity} spawned at {position}.")
