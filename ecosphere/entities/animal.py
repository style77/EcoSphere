import logging
import math
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Type

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position

from ecosphere.common import EnvironmentContext, bus, StatusProperty
from ecosphere.entities.food import Berry, Food, Mushroom, Seaweed, Wheat

from ecosphere.states import (
    DeadState,
    ForagingState,
    IdleState,
    MatingState,
    SeekingWaterState,
    SleepingState,
)
from ecosphere.states.state import AnimalState

from ecosphere.utils import clamp
from ecosphere.world.biome import Biome, BiomeManager

if TYPE_CHECKING:
    from ecosphere.world.overworld import Overworld


@dataclass
class PerceivedEnvironment:
    current_biome: Biome
    potential_mates: List["Animal"]
    nearby_entities: List[Entity]


def get_rand_prop(min_value: int = 50) -> float:
    _rand_val = random.uniform(min_value, 100)
    return min(min_value, _rand_val)


class Animal(Entity):
    """
    Class representing a animal entity in the overworld. This class is inherited by specific animal classes.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the animal's representation in the overworld
    """
    _cant_go_on_land = False
    _can_eat: List[Type[Food]] = []

    def __init__(
        self,
        position: Position,
        representation: str,
        properties: StatusProperty = StatusProperty(),
    ):
        super().__init__(position, representation, dynamic=True)

        self.perception_radius = properties.perception_radius
        self.properties = properties

        self.state = IdleState()
        self.health = get_rand_prop(80)
        self.hunger = get_rand_prop()
        self.thirst = get_rand_prop()
        self.energy = get_rand_prop(80)
        self.mating_urge = 0

    def _calculate_position(
        self, overworld: "Overworld", biome_manager: BiomeManager
    ) -> Position:
        """
        Calculate next position for animal after moving (+1 in every direction),
        it should not be occupied and should be within the biome.
        If There is no space in the biome, return same position.

        Attributes:
            overworld: Overworld object representing the overworld
            biome_manager: BiomeManager object representing the biome manager for the overworld
        """
        _x = [self.position.x + 1, self.position.x - 1, self.position.x]
        _y = [self.position.y + 1, self.position.y - 1, self.position.y]

        random.shuffle(_x)
        random.shuffle(_y)

        current_biome = biome_manager.get_biome_by_coords(
            self.position.x, self.position.y
        )

        for x in _x:
            x = max(0, min(x, overworld.width - 1))

            for y in _y:
                y = max(0, min(y, overworld.height - 1))

                is_new_biome = biome_manager.get_biome_by_coords(x, y) != current_biome
                is_occupied = overworld.is_occupied(Position(x=x, y=y))
                if not is_occupied and not is_new_biome:
                    return Position(x=x, y=y)

        return self.position

    def perceive_environment(
        self, overworld: "Overworld", biome_manager: BiomeManager
    ) -> PerceivedEnvironment:
        nearby_entities = overworld.get_nearby_entities(self, self.perception_radius)
        potential_mates = []

        for entity in nearby_entities:
            if isinstance(entity, type(self)) and entity.mating_urge >= 80:
                potential_mates.append(entity)

        current_biome = biome_manager.get_biome_by_coords(
            self.position.x, self.position.y
        )

        return PerceivedEnvironment(
            current_biome=current_biome,
            potential_mates=potential_mates,
            nearby_entities=nearby_entities,
        )

    async def move_towards(self, position: Position, overworld: "Overworld", biome_manager: BiomeManager):
        dx = 1 if position.x > self.position.x else -1 if position.x < self.position.x else 0
        dy = 1 if position.y > self.position.y else -1 if position.y < self.position.y else 0

        new_position = Position(x=self.position.x + dx, y=self.position.y + dy)
        _old_position = self.position

        if self._cant_go_on_land:
            biome = biome_manager.get_biome_by_coords(new_position.x, new_position.y)
            if biome != Biome.WATER:
                return await self.move_towards(self._calculate_position(overworld, biome_manager), overworld, biome_manager)

        await self._move(new_position.x, new_position.y, overwrite=True)

        biome = biome_manager.get_biome_by_coords(_old_position.x, _old_position.y)
        biome_color = biome_manager.get_biome_color(biome)
        overworld.stdscr.addstr(_old_position.y, _old_position.x, "  ", biome_color)

    def change_state(self, state: AnimalState):
        if not isinstance(self.state, state.__class__):
            logging.debug(f"{self.id} is changing state to {state}.")
            self.state = state

    def update_status(self):
        # Update basic needs
        self.hunger = clamp(self.hunger + self.properties.hunger_increase_rate, 0, 100)
        self.thirst = clamp(self.thirst + self.properties.thirst_increase_rate, 0, 100)
        self.energy = clamp(self.energy - self.properties.energy_decrease_rate, 0, 100)

        # Update mating urge based on hunger, thirst, and energy
        if self.hunger <= 50 and self.thirst <= 50 and self.energy > 50:
            self.mating_urge += self.properties.mating_urge_increase_rate
        else:
            self.mating_urge -= self.properties.mating_urge_decrease_rate
        self.mating_urge = clamp(self.mating_urge, 0, 100)

        # Update health based on extreme hunger or thirst
        if self.hunger >= 90 or self.thirst >= 90:
            self.health -= (
                self.properties.health_decrease_rate * self.properties.health_multiplier
            )
        elif self.hunger >= 80 or self.thirst >= 80:
            self.health -= self.properties.health_decrease_rate
        elif self.hunger <= 20 and self.thirst <= 20 and self.energy > 50:
            self.health += self.properties.health_increase_rate

        self.health = clamp(self.health, 0, 100)

    async def update(self, overworld: "Overworld", biome_manager: BiomeManager):
        if isinstance(self.state, DeadState):
            return

        self.update_status()

        logging.debug(
            f"{self.id} at {self.position} is {self.state} and has {self.health} health, {self.hunger} hunger, {self.thirst} thirst, {self.energy} energy, and {self.mating_urge} mating urge."
        )
        await self.state.handle(self, EnvironmentContext(overworld, biome_manager))


class Crab(Animal):
    frequency = 0.01
    _property = StatusProperty()

    _can_eat = [Seaweed, Mushroom]

    def __init__(self, position: Position, representation: str):
        super().__init__(position, representation, self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return "🦀"


class Fox(Animal):
    frequency = 0.01
    _property = StatusProperty(movement_speed=2)

    _can_eat = [Mushroom, Berry, Wheat]

    def __init__(self, position: Position, representation: str):
        super().__init__(position, representation, self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return "🦊"


class Fish(Animal):
    frequency = 0.03
    _property = StatusProperty()
    _cant_go_on_land = True

    _can_eat = [Seaweed]

    def __init__(self, position: Position, representation: str):
        super().__init__(position, representation, self._property)

    @staticmethod
    def get_representation(biome: Biome):
        return random.choice(["🐟", "🐠", "🐡"])
