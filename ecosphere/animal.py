from dataclasses import dataclass
import random
from enum import Enum, auto
from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.biome import BiomeManager, Biome

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ecosphere.overworld import Overworld


class AnimalState(Enum):
    IDLE = auto()
    MOVING = auto()
    FORAGING = auto()
    MATING = auto()
    SLEEPING = auto()
    DEAD = auto()


@dataclass
class PerceivedEnvironment:
    current_biome: Biome
    potential_mates: List["Animal"]
    nearby_entities: List[Entity]


def get_rand_prop() -> float:
    return round(random.random() * 100, 2)


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

        self.state = AnimalState.IDLE
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

    def is_next_to(self, position: Position) -> bool:
        return (
            abs(self.position.x - position.x) <= 1
            and abs(self.position.y - position.y) <= 1
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
        self.move(dx, dy, overwrite=True)

    def distance_to(self, position: Position) -> float:
        return (
            (self.position.x - position.x) ** 2 + (self.position.y - position.y) ** 2
        ) ** 0.5

    def calculate_offspring_position(self, mate_position: Position) -> Position:
        return Position(
            (self.position.x + mate_position.x) // 2,
            (self.position.y + mate_position.y) // 2,
        )

    def decide_action(
        self,
        overworld: "Overworld",
        biome_manager: BiomeManager,
        environment: PerceivedEnvironment,
    ):
        print(self.state)
        if self.state == AnimalState.DEAD:
            return

        if self.state == AnimalState.MATING and environment.potential_mates:
            mate = min(
                environment.potential_mates,
                key=lambda mate: self.distance_to(mate.position),
            )
            if self.distance_to(mate.position) <= self.perception_radius:
                if not self.is_next_to(mate.position):
                    self.move_towards(mate.position)
                else:
                    self.reproduce(mate, overworld)

        if self.state == AnimalState.FORAGING:
            # Implement logic to move towards food or water sources if hungry or thirsty
            # This might involve finding the closest food or water source and moving towards it
            return

        # Eating behavior
        # if self.state == AnimalState.EATING:
        #     # Implement logic to consume food if available
        #     # This might involve checking if the animal is on a food source and then consuming it
        #     return

        if self.state == AnimalState.SLEEPING:
            # Implement logic for sleeping
            # This might involve increasing the animal's energy over time
            self.energy += 5  # Example to increase energy
            if self.energy >= 100:
                self.state = AnimalState.IDLE  # Wake up fully energized
            return

        if self.state == AnimalState.MOVING:
            new_position = self._calculate_position(overworld, biome_manager)
            old_position = self.position

            if new_position != old_position:
                self.move(new_position.x, new_position.y, overwrite=True)

                biome = biome_manager.get_biome_by_coords(
                    self.position.x, self.position.y
                )
                biome_color = biome_manager.get_biome_color(biome)

                overworld.stdscr.addstr(
                    old_position.y, old_position.x, "  ", biome_color
                )

        if self.state == AnimalState.IDLE:
            # randomly select a new state, moving, foraging, or sleeping
            self.state = random.choice(
                [AnimalState.MOVING, AnimalState.SLEEPING]  # AnimalState.FORAGING,
            )

    def reproduce(self, mate: "Animal", overworld: "Overworld"):
        offspring_position = self.calculate_offspring_position(mate.position)
        offspring = type(self)
        overworld.spawn_entity(offspring, offspring_position)

        self.mating_urge = 0
        mate.mating_urge = 0

        # Take a break after reproducing
        self.state = AnimalState.IDLE
        mate.state = AnimalState.IDLE

    def update_state(self):
        if self.health <= 0:
            self.state = AnimalState.DEAD
        elif self.state != AnimalState.DEAD:
            # If energy is too low, animal needs to sleep
            if self.energy <= 10:
                self.state = AnimalState.SLEEPING
            # If the animal is very hungry or thirsty, it should forage for food or water
            elif self.hunger >= 80 or self.thirst >= 80:
                self.state = AnimalState.FORAGING
            # Consider mating urge for changing state to MATING
            elif self.mating_urge >= 80 and self.energy > 50:
                self.state = AnimalState.MATING
            # If none of the above, and energy is not full, go to SLEEPING to restore energy
            elif self.energy < 50:
                self.state = AnimalState.SLEEPING

    def update_status(self):
        # Increase hunger and thirst over time
        self.hunger += 1.5
        self.thirst += 1.5

        # Decrease energy slightly over time
        self.energy -= 0.5

        # Cap hunger and thirst at 100
        self.hunger = min(self.hunger, 100)
        self.thirst = min(self.thirst, 100)

        # Increase mating urge if conditions are favorable
        if self.hunger <= 20 and self.thirst <= 20 and self.energy > 50:
            self.mating_urge += 2
        else:
            self.mating_urge = max(
                self.mating_urge - 1, 0
            )  # Decrease if not ideal conditions

        # Decrease health if very hungry or thirsty
        if self.hunger >= 90 or self.thirst >= 90:
            self.health -= 5
        elif self.hunger >= 80 or self.thirst >= 80:
            self.health -= 2

        # Cap mating urge at 100 and health at 0
        self.mating_urge = min(self.mating_urge, 100)
        self.health = max(self.health, 0)

        # Restore some energy if resting
        if self.state == AnimalState.SLEEPING:
            self.energy += 2
            self.energy = min(self.energy, 100)

        # Check if energy is too low and force state to sleeping
        if self.energy <= 10:
            self.state = AnimalState.SLEEPING

    def update(self, overworld: "Overworld", biome_manager: BiomeManager):
        self.update_status()
        self.update_state()

        if self.state == AnimalState.DEAD:
            return

        environment = self.perceive_environment(overworld, biome_manager)
        self.decide_action(overworld, biome_manager, environment)


class Crab(Animal):
    frequency = 0.01

    def __init__(self, position: Position, representation: str = "🦀"):
        super().__init__(position, representation)

    @staticmethod
    def get_representation(biome: Biome):
        return "🦀"
