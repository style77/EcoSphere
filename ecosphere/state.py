import random
from abc import ABC, abstractmethod
from ecosphere.abc.position import Position
from typing import TYPE_CHECKING

from ecosphere.biome import Biome

if TYPE_CHECKING:
    from ecosphere.animal import Animal
    from ecosphere.overworld import Overworld
    from ecosphere.biome import BiomeManager


class AnimalState(ABC):
    @abstractmethod
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ) -> None:
        pass

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__.replace("State", "")


class IdleState(AnimalState):
    """
    The animal is not doing anything in particular. It will randomly select a new state.
    """

    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ) -> None:
        if animal.energy >= 80:  # Animal is full of energy and can just have some fun
            animal.state = MovingState()
        else:
            animal.state = random.choice([MovingState(), SleepingState()])


class MovingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        new_position = animal._calculate_position(overworld, biome_manager)
        animal.move_towards(new_position, overworld, biome_manager)


class ForagingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        ...


class SeekingWaterState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        if animal.thirst < 20:
            animal.state = IdleState()
            return

        nearest_water = self.find_nearest_water_source(animal, overworld, biome_manager)

        if nearest_water:
            print(f"There is water nearby ({nearest_water}). Moving from {animal.position} towards it (thirst: {animal.thirst}).")
            if animal.position.is_next_to(nearest_water):
                animal.thirst -= 5
                if animal.thirst < 20:
                    animal.state = IdleState()
            else:
                animal.move_towards(nearest_water, overworld, biome_manager)
        else:
            fallback_direction = self.decide_fallback_direction(animal, overworld)
            animal.move_towards(fallback_direction, overworld, biome_manager)

    def find_nearest_water_source(self, animal: "Animal", overworld: "Overworld", biome_manager: "BiomeManager"):
        perception_range = animal.perception_radius
        current_pos = animal.position
        nearest_water_pos = None
        min_distance = float('inf')

        for x in range(max(0, current_pos.x - perception_range), min(overworld.width, current_pos.x + perception_range + 1)):
            for y in range(max(0, current_pos.y - perception_range), min(overworld.height, current_pos.y + perception_range + 1)):
                # Check if the position (x, y) is within a circular area
                if (x - current_pos.x) ** 2 + (y - current_pos.y) ** 2 <= perception_range ** 2:
                    if biome_manager.get_biome_by_coords(x, y) is Biome.WATER:
                        distance = ((x - current_pos.x) ** 2 + (y - current_pos.y) ** 2) ** 0.5
                        if distance < min_distance:
                            nearest_water_pos = Position(x, y)
                            min_distance = distance

        if nearest_water_pos is not None:
            return nearest_water_pos

    def decide_fallback_direction(self, animal, overworld):
        directions = [Position(1, 0), Position(-1, 0), Position(0, 1), Position(0, -1)]
        fallback_direction = random.choice(directions)

        new_x = max(0, min(animal.position.x + fallback_direction.x, overworld.width - 1))
        new_y = max(0, min(animal.position.y + fallback_direction.y, overworld.height - 1))

        return Position(new_x, new_y)


class EatingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        ...


class SleepingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        animal.energy += 10
        if animal.energy >= 100:
            animal.state = IdleState()


class MatingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ) -> None:
        environment = self.perceive_environment(overworld, biome_manager)
        if environment.potential_mates:
            mate: Animal = min(
                environment.potential_mates,
                key=lambda mate: animal.distance_to(mate.position),
            )
            if animal.position.distance_to(mate.position) <= animal.perception_radius:
                if not animal.position.is_next_to(mate.position):
                    animal.move_towards(mate.position, overworld, biome_manager)
                else:
                    self.reproduce(mate, animal.overworld)
        else:
            animal.state = MovingState()

    def calculate_offspring_position(self, mate_position: Position) -> Position:
        return Position(
            (self.position.x + mate_position.x) // 2,
            (self.position.y + mate_position.y) // 2,
        )

    def reproduce(self, mate: "Animal", overworld: "Overworld") -> None:
        offspring_position = self.calculate_offspring_position(mate.position)

        offspring = mate.__class__
        overworld.spawn_entity(offspring, offspring_position)

        self.energy -= 50
        mate.energy -= 50

        self.state = IdleState()
        mate.state = IdleState()


class DeadState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ) -> None:
        return
