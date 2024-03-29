import random
from typing import TYPE_CHECKING, Literal

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.world.biome import Biome, BiomeManager

if TYPE_CHECKING:
    from ecosphere.world.overworld import Overworld


class Plant(Entity):
    """
    Class representing a plant entity in the overworld. This class is inherited by specific plant classes.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the plant's representation in the overworld
    """

    def __init__(self, position: Position, representation: str):
        super().__init__(position, representation, dynamic=False)

    def move(self, x: int, y: int, overwrite: bool = False):
        raise NotImplementedError("Plants cannot move.")

    def update(self, overworld: "Overworld", biome_manager: BiomeManager):
        raise NotImplementedError("Plants cannot update.")


class Tree(Plant):
    """
    Class representing a tree entity in the overworld.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the tree's representation in the overworld
    """

    frequency = 0.25

    def __init__(
        self, position: Position, representation: Literal["🌲", "🌳", "🌴", "🌵"] = "🌲"
    ):
        super().__init__(position, representation)

    def __repr__(self):
        return f"Tree(id={self.id}, position={self.position})"

    @classmethod
    def create(cls, position: Position, biome: Biome) -> "Tree":
        return cls(position=position, representation=cls.get_representation(biome))

    @staticmethod
    def get_representation(biome: Biome):
        """
        Return the representation of the tree based on the biome.

        Attributes:
            biome: Biome object representing the biome the tree is in (e.g. forest, plains, desert)
        """
        if biome in [Biome.FOREST, Biome.PLAINS]:
            return random.choice(["🌲", "🌳"])
        elif biome == Biome.DESERT:
            return random.choice(["🌴", "🌵"])
        else:
            return " "


class Flower(Plant):
    """
    Class representing a flower entity in the overworld.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the flower's representation in the overworld
    """

    frequency = 0.03

    def __init__(
        self, position: Position, representation: Literal["🌸", "🌼", "🌷", "🌻"] = "🌸"
    ):
        super().__init__(position, representation)

    @staticmethod
    def get_representation(biome: Biome):
        if biome in [Biome.FOREST, Biome.PLAINS]:
            return random.choice(["🌸", "🌼", "🌷", "🌻"])
        else:
            return " "
