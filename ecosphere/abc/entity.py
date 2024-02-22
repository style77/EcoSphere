from abc import (
    ABC,
    abstractmethod,
    abstractclassmethod,
    abstractstaticmethod,
)
from ecosphere.biome import Biome

from ecosphere.utils import generate_id
from ecosphere.abc.position import Position


class Entity(ABC):
    """
    Abstract class representing an entity in the overworld.
    Can be either a plant, tree, animal, or any other entity.
    """
    dynamic: bool = False

    def __init__(self, position: Position, representation: str):
        self.id = generate_id(self.__class__.__name__)
        self.position = position
        self._representation = representation

    @abstractmethod
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, position={self.position})"

    @classmethod
    @abstractclassmethod
    def create(cls, position: Position, biome: Biome):
        raise NotImplementedError

    @property
    def representation(self):
        return self._representation

    @staticmethod
    @abstractstaticmethod
    def get_representation(biome: Biome):
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

    @abstractmethod
    def update(self):
        raise NotImplementedError
