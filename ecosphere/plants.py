import random

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.biome import Biome


class Plant(Entity):
    """
    Class representing a plant entity in the overworld. This class is inherited by specific plant classes.

    Attributes:
        id: unique identifier for the entity
        position: Position object representing the entity's location in the overworld
    """

    def __init__(self, position: Position):
        super().__init__(position)

    def move(self, x: int, y: int, overwrite: bool = False):
        raise NotImplementedError("Plants cannot move.")


class Tree(Plant):
    """
    Class representing a tree entity in the overworld.

    Attributes:
        id: unique identifier for the entity
        position: Position object representing the entity's location in the overworld
    """
    frequency = 0.25

    def __init__(self, position: Position):
        super().__init__(position)

    def __repr__(self):
        return f"Tree(id={self.id}, position={self.position})"

    @classmethod
    def create(cls, position):
        return cls(position=position)

    def get_representation(self, biome: Biome):
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
