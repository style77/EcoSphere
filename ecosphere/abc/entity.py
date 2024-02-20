from abc import ABC, abstractmethod, abstractclassmethod
from ecosphere.biome import Biome

from ecosphere.utils import generate_id
from ecosphere.abc.position import Position


class Entity(ABC):
    """
    Abstract class representing an entity in the overworld.
    Can be either a plant, tree, animal, or any other entity.
    """

    def __init__(self, position: Position):
        self.id = generate_id(self.__class__.__name__)
        self.position = position

    @abstractmethod
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, position={self.position})"

    @abstractmethod
    def get_representation(self, biome: Biome):
        raise NotImplementedError

    @classmethod
    @abstractclassmethod
    def create(self):
        raise NotImplementedError

    def move(self, x: int, y: int, overwrite: bool = False):
        """
        Move the entity by the specified amount. If overwrite is True, the entity's position is set to the new position.

        Attributes:
            x: int representing the amount to move on the x-axis
            y: int representing the amount to move on the y-axis
            overwrite: bool representing whether to overwrite the entity's position with the new position
        """
        if overwrite:
            self.position = Position(x=x, y=y)
        else:
            self.position.x += x
            self.position.y += y
