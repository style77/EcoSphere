from typing import TYPE_CHECKING, Literal

from ecosphere.abc.entity import Entity
from ecosphere.abc.position import Position
from ecosphere.common.property import FoodProperty
from ecosphere.world.biome import Biome

if TYPE_CHECKING:
    from ecosphere.world.biome import BiomeManager
    from ecosphere.world.overworld import Overworld


class Food(Entity):
    """
    Class representing a food entity in the overworld. This class is inherited by specific food classes.

    Attributes:
        position: Position object representing the entity's location in the overworld
        representation: str representing the food's representation in the overworld
    """

    def __init__(
        self,
        position: Position,
        representation: str,
        properties: FoodProperty = FoodProperty(),
    ):
        super().__init__(position, representation, dynamic=False)
        self.properties = properties

    def update(self, overworld: "Overworld", biome_manager: "BiomeManager"):
        raise NotImplementedError("Food cannot update.")


class Berry(Food):
    _property = FoodProperty(nutrition=10)

    def __init__(self, position: Position, representation: Literal["🍇", "🍓"]):
        super().__init__(position, representation, properties=self._property)

    @staticmethod
    def get_representation(biome: "Biome"):
        if biome in [Biome.FOREST, Biome.PLAINS]:
            return "🍇" if biome == Biome.FOREST else "🍓"
        else:
            return " "


class Mushroom(Food):
    _property = FoodProperty(nutrition=20)

    def __init__(self, position: Position, representation: Literal["🍄"]):
        super().__init__(position, representation, properties=self._property)

    @staticmethod
    def get_representation(biome: "Biome"):
        if biome in [Biome.FOREST, Biome.PLAINS]:
            return "🍄"
        else:
            return " "


class Seaweed(Food):
    _property = FoodProperty(nutrition=15)

    def __init__(self, position: Position, representation: Literal["🌿"]):
        super().__init__(position, representation, properties=self._property)

    @staticmethod
    def get_representation(biome: "Biome"):
        if biome in [Biome.WATER]:
            return "🌿"
        else:
            return " "


class Wheat(Food):
    _property = FoodProperty(nutrition=15)

    def __init__(self, position: Position, representation: Literal["🌾"]):
        super().__init__(position, representation, properties=self._property)

    @staticmethod
    def get_representation(biome: "Biome"):
        if biome in [Biome.PLAINS]:
            return "🌾"
        else:
            return " "
