import asyncio
import curses
import itertools
import logging
import random
from typing import Any, List, Type

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.common.event_bus import bus
from ecosphere.common.onetime_caller import OneTimeCaller
from ecosphere.common.singleton import SingletonMeta
from ecosphere.config import (
    ENTITIES,
    ENTITY_BIOME_SPAWN_RATES,
    MINUTE_LENGTH,
    FOOD_BIOME_SPAWN_RATES,
    SPAWNERS,
)
from ecosphere.entities.food import Food
from ecosphere.entities.food_spawner import FoodSpawner
from ecosphere.states import DeadState
from ecosphere.world.biome import Biome, BiomeManager


class Overworld(metaclass=SingletonMeta):
    def __init__(self, stdscr: Any, width: int, height: int):
        self.stdscr = stdscr

        self.width = width
        self.height = height

        self.entities: List[Entity] = []
        self.spawners: List[FoodSpawner] = []
        self.food: List[Food] = []

        self.biome = BiomeManager(stdscr, self.width, self.height)

        self._static_drawn = False

    def _calculate_entity_cap(self, frequency: float = 0.25):
        return self.width * self.height * frequency

    def _calculate_position(self):  # UNSAFE TODO
        occupied = True
        while occupied:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            position = Position(x=x, y=y)

            if not self.is_occupied(position):
                occupied = False

        return position

    def _get_spawn_rate(self, entity: Entity, biome: Biome, *, spawner: bool = False):
        rates = FOOD_BIOME_SPAWN_RATES if spawner else ENTITY_BIOME_SPAWN_RATES

        for entity_biome_spawn_rate in rates:
            entity_name = (
                entity_biome_spawn_rate.food_name
                if spawner
                else entity_biome_spawn_rate.entity_name
            )
            if entity_name == entity.__name__:
                return getattr(entity_biome_spawn_rate.spawn_rates, biome.name, 0)
        return 0

    async def _draw_entity(self, entity: Entity, position: Position):
        biome = self.biome.get_biome_by_coords(position.x, position.y)
        biome_color = self.biome.get_biome_color(biome)

        char = entity.representation

        try:
            self.stdscr.addstr(position.y, position.x, char, biome_color)
        except curses.error:
            pass

    async def draw(self, force_static: bool = False):
        """
        Draw all the existing entities on the board.
        """
        logging.debug("Drawing entities in the overworld.")
        if not self._static_drawn or force_static:
            await self.biome.draw()

            static_entities = [entity for entity in self.entities if not entity.dynamic]
            for entity in static_entities:
                await self._draw_entity(entity, entity.position)
            self._static_drawn = True

        entities = [entity for entity in self.entities if entity.dynamic]

        dynamic_entities = itertools.chain(entities, self.food)

        for entity in dynamic_entities:
            await self._draw_entity(entity, entity.position)
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

    def get_nearby_entities(
        self, entity: Entity, perception_range: int
    ) -> List[Entity]:
        nearby_entities = []
        for other_entity in itertools.filterfalse(lambda e: e == entity, self.entities):
            if entity.position.is_within_range(other_entity.position, perception_range):
                nearby_entities.append(entity)
        return nearby_entities

    def get_nearby_food(
        self,
        position: Position,
        perception_range: int,
        *,
        food_type: List[Type[Food]] = None,
    ) -> List[Food]:
        nearby_food = []

        if food_type:
            food_list = [
                food for food in self.food if isinstance(food, tuple(food_type))
            ]
        else:
            food_list = self.food

        for food in food_list:
            if position.is_within_range(food.position, perception_range):
                nearby_food.append(food)
        return nearby_food

    def is_occupied(self, position: Position) -> bool:
        return position in [entity.position for entity in self.entities]

    async def update_entity(self, entity: Entity):
        while not isinstance(entity.state, DeadState):
            await entity.update(self, self.biome)
            await asyncio.sleep(MINUTE_LENGTH / entity.properties.movement_speed)

    async def update_spawner(self, spawner: FoodSpawner):
        while True:
            await spawner.update(self, self.biome)
            await asyncio.sleep(MINUTE_LENGTH / spawner.properties.dispersal_speed)

    async def update(self):
        """
        Update overworld.
        """
        logging.info("Updating overworld.")
        update_tasks = [
            asyncio.create_task(self.update_spawner(entity))
            if isinstance(entity, FoodSpawner)
            else asyncio.create_task(self.update_entity(entity))
            for entity in itertools.chain(
                [e for e in self.entities if e.dynamic], self.spawners
            )
        ]

        await asyncio.gather(*update_tasks)

        logging.info("Overworld updated.")

    def _spawn_entities(self):
        for entity_class in ENTITIES:
            cap = self._calculate_entity_cap(entity_class.frequency)
            for _ in range(round(cap)):
                self.spawn_entity(entity_class, spawner=False)

        for spawner_class in SPAWNERS:
            cap = self._calculate_entity_cap(spawner_class.frequency)
            for _ in range(round(cap)):
                self.spawn_entity(spawner_class, spawner=True)

    def spawn_entities(self):
        """
        Spawn all the entities in the overworld.
        """
        logging.debug("Spawning entities in the overworld.")
        oc = OneTimeCaller(self._spawn_entities)
        oc()
        logging.info("Entities spawned.")

    def remove(self, entity: Entity):
        """
        Remove entity from the overworld.
        """
        mapper = None
        if isinstance(entity, Food):
            mapper = self.food
        elif isinstance(entity, FoodSpawner):
            mapper = self.spawners
        else:
            mapper = self.entities

        mapper.remove(entity)
        bus.emit("entity:removed", entity)
        logging.info(f"{entity} removed from the overworld.")

    def spawn_food(self, food: Food, position: Position):
        """
        Spawn food at the given position.
        """
        biome = self.biome.get_biome_by_coords(position.x, position.y)
        food = food.create(position, biome)

        self.food.append(food)
        bus.emit("entity:created", food)
        logging.debug(f"{food} spawned at {position}.")

    def spawn_entity(
        self, entity: Entity, position: Position = None, *, spawner: bool = False
    ):
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

        spawn_rate = self._get_spawn_rate(entity, biome, spawner=spawner)

        if random.random() < spawn_rate:
            entity = entity.create(position, biome)

            if spawner:
                self.spawners.append(entity)
            else:
                self.entities.append(entity)

            bus.emit("entity:created", entity)
            logging.debug(f"{entity} spawned at {position}.")
