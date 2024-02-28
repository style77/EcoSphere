import logging
import random
from typing import TYPE_CHECKING, Literal, Type

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.common.property import SpawnerProperty
from ecosphere.entities.food import Berry, Food, Mushroom, Seaweed, Wheat
from ecosphere.world.biome import Biome, BiomeManager

if TYPE_CHECKING:
    from ecosphere.world.overworld import Overworld


class FoodSpawner(Entity):
    def __init__(
        self,
        position: Position,
        representation: str,
        food: Type[Food],
        properties: SpawnerProperty = SpawnerProperty(),
    ):
        super().__init__(position, representation, dynamic=False)
        self.properties = properties
        self.food = food

    def move(self, x: int, y: int, overwrite: bool = False):
        raise NotImplementedError("Spawners cannot move.")

    async def update(self, overworld: "Overworld", biome_manager: BiomeManager):
        if (
            len(
                overworld.get_nearby_food(self.position, self.properties.range_capacity)
            )
            > self.properties.range_capacity
        ):
            print("Spawner is full", self.position, self.properties.range_capacity)
            return

        for _ in range(self.properties.range_capacity):
            position = Position.get_random_position_in_radius(
                self.position, self.properties.dispersal_radius
            )
            if not overworld.is_occupied(position):
                overworld.spawn_food(self.food, position)


class Berries(FoodSpawner):
    frequency = 0.01
    _property = SpawnerProperty()

    def __init__(self, position: Position, representation: Literal["🍇", "🍓"]):
        super().__init__(position, representation, Berry, properties=self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return " "


class Mushrooms(FoodSpawner):
    frequency = 0.01
    _property = SpawnerProperty()

    def __init__(self, position: Position, representation: Literal["🍄"]):
        super().__init__(position, representation, Mushroom, properties=self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return " "


class Seaweeds(FoodSpawner):
    frequency = 0.01
    _property = SpawnerProperty()

    def __init__(self, position: Position, representation: Literal["🌿"]):
        super().__init__(position, representation, Seaweed, properties=self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return " "


class Wheats(FoodSpawner):
    frequency = 0.01
    _property = SpawnerProperty()

    def __init__(self, position: Position, representation: Literal["🌾", "🌱"]):
        super().__init__(position, representation, Wheat, properties=self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return " "
