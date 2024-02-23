from dataclasses import dataclass
import random
from typing import TYPE_CHECKING, List
from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.biome import BiomeManager, Biome
from ecosphere.common.event_bus import bus
from ecosphere.state import (
    DeadState,
    ForagingState,
    IdleState,
    MatingState,
    SleepingState,
)


if TYPE_CHECKING:
    from ecosphere.overworld import Overworld


@dataclass
class PerceivedEnvironment:
    current_biome: Biome
    potential_mates: List["Animal"]
    nearby_entities: List[Entity]


def get_rand_prop(min_value: int = 50) -> float:
    return min(min_value, round(random.random() * 100, 2))


class Animal(Entity):
    """
    Class representing a animal entity in the overworld. This class is inherited by specific animal classes.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the animal's representation in the overworld
    """

    def __init__(
        self, position: Position, representation: str, perception_radius: int = 5
    ):
        super().__init__(position, representation, dynamic=True)

        self.perception_radius = perception_radius

        self.state = IdleState()
        self.health = get_rand_prop()  # 0-100, 100 being healthy and 0 being dead
        self.hunger = get_rand_prop()  # 0-100, 100 being full and 0 being starving
        self.thirst = get_rand_prop()  # 0-100, 100 being full and 0 being dehydrated
        self.energy = get_rand_prop()  # 0-100, 100 being full of energy and 0 exhausted
        self.mating_urge = 0  # 0-100, 100 being ready to mate and 0 being not ready

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

    def move_towards(self, position: Position):
        dx = (
            1
            if position.x > self.position.x
            else -1
            if position.x < self.position.x
            else 0
        )
        dy = (
            1
            if position.y > self.position.y
            else -1
            if position.y < self.position.y
            else 0
        )
        self._move(dx, dy, overwrite=False)

    def update_state(self):
        if self.health <= 0:
            if self.state != DeadState():
                self.state = DeadState()
                bus.emit("entity:dead", self)
                return

        elif self.state != DeadState():
            # If energy is too low, animal needs to sleep
            if self.energy <= 10:
                self.state = SleepingState()
            # If the animal is very hungry or thirsty, it should forage for food or water
            elif self.hunger >= 80 or self.thirst >= 80:
                self.state = ForagingState()
            # Consider mating urge for changing state to MATING
            elif self.mating_urge >= 80 and self.energy > 50:
                self.state = MatingState()
            # If none of the above, and energy is not full, go to SLEEPING to restore energy
            elif self.energy < 50:
                self.state = SleepingState()

    def update_status(self):
        # Increase hunger and thirst over time
        self.hunger += 0.5
        self.thirst += 0.5

        # Decrease energy slightly over time
        self.energy -= 0.5

        # Cap hunger and thirst at 100
        self.hunger = min(self.hunger, 100)
        self.thirst = min(self.thirst, 100)

        # Increase mating urge if conditions are favorable
        if self.hunger <= 20 and self.thirst <= 20 and self.energy > 50:
            self.mating_urge += 3
        else:
            self.mating_urge = max(
                self.mating_urge - 1, 0
            )  # Decrease if not ideal conditions

        if self.hunger >= 90 or self.thirst >= 90:
            self.health -= 5
        elif self.hunger >= 80 or self.thirst >= 80:
            self.health -= 2

        self.mating_urge = min(self.mating_urge, 100)
        self.health = max(self.health, 0)

    def update(self, overworld: "Overworld", biome_manager: BiomeManager):
        if self.state == DeadState():
            return

        self.update_status()
        self.update_state()

        if self.state == DeadState():  # boilerplate, but necessary
            return

        print(
            f"{self.__class__.__name__} at {self.position} is {self.state} and has {self.health} health, {self.hunger} hunger, {self.thirst} thirst, {self.energy} energy, and {self.mating_urge} mating urge."
        )
        self.state.handle(self, overworld=overworld, biome_manager=biome_manager)


class Crab(Animal):
    frequency = 0.01

    def __init__(self, position: Position, representation: str = "🦀"):
        super().__init__(position, representation)

    @staticmethod
    def get_representation(biome: Biome):
        return "🦀"
