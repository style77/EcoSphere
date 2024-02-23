import random
from abc import ABC, abstractmethod
from ecosphere.abc.position import Position
from typing import TYPE_CHECKING

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
        animal.state = random.choice([MovingState(), SleepingState()])


class MovingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        new_position = animal._calculate_position(overworld, biome_manager)
        _old_position = animal.position

        if new_position != _old_position:
            animal._move(new_position.x, new_position.y, overwrite=True)
            biome = biome_manager.get_biome_by_coords(animal.position.x, animal.position.y)

            biome_color = biome_manager.get_biome_color(biome)

            overworld.stdscr.addstr(_old_position.y, _old_position.x, "  ", biome_color)


class ForagingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        ...


class SeekingWaterState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        ...


class EatingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        ...


class SleepingState(AnimalState):
    def handle(
        self, animal: "Animal", *, overworld: "Overworld", biome_manager: "BiomeManager"
    ):
        animal.energy += 5
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
                    animal.move_towards(mate.position)
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
