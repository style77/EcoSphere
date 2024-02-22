from abc import (
    ABC,
    abstractmethod,
    abstractstaticmethod,
)
from ecosphere.biome import Biome

from ecosphere.utils import generate_id
from ecosphere.abc.position import Position

from typing import NoReturn


class Entity(ABC):
    """
    Abstract class representing an entity in the overworld.
    Can be either a plant, tree, animal, or any other entity.
    """
    def __init__(self, position: Position, representation: str, dynamic: bool):
        self.id = generate_id(self.__class__.__name__)
        self.position = position
        self._representation = representation
        self.dynamic = dynamic

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, position={self.position})"

    @classmethod
    def create(cls, position: Position, biome: Biome) -> "Entity":
        return cls(position=position, representation=cls.get_representation(biome))

    @property
    def representation(self) -> str:
        return self._representation

    @staticmethod
    @abstractstaticmethod
    def get_representation(biome: Biome) -> str:
        """
        Return the representation of the entity based on the biome. This method should be implemented by the specific entity class.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self):
        raise NotImplementedError

    def move(self, x: int, y: int, overwrite: bool = False) -> NoReturn:
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
