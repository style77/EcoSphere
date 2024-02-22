import random
from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.biome import BiomeManager, Biome

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecosphere.overworld import Overworld


class Animal(Entity):
    """
    Class representing a animal entity in the overworld. This class is inherited by specific animal classes.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the animal's representation in the overworld
    """

    dynamic: bool = True

    def __init__(self, position: Position, representation: str):
        super().__init__(position, representation)

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

    def update(self, overworld: "Overworld", biome_manager: BiomeManager):
        new_position = self._calculate_position(overworld, biome_manager)
        old_position = self.position

        if new_position != old_position:
            self.move(new_position.x, new_position.y, overwrite=True)

            biome = biome_manager.get_biome_by_coords(self.position.x, self.position.y)
            biome_color = biome_manager.get_biome_color(biome)

            overworld.stdscr.addstr(old_position.y, old_position.x, "  ", biome_color)


class Crab(Animal):
    frequency = 0.01

    def __init__(self, position: Position, representation: str = "🦀"):
        super().__init__(position, representation)

    def __repr__(self):
        return f"Crab(id={self.id}, position={self.position})"

    @classmethod
    def create(cls, position: Position, biome: Biome) -> "Crab":
        return cls(position=position, representation=cls.get_representation(biome))

    @classmethod
    def get_representation(cls, biome: Biome):
        return "🦀"
