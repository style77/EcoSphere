from abc import ABC, abstractmethod
import random
from typing import TYPE_CHECKING
from ecosphere.abc.position import Position

from ecosphere.abc.state import State

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal
    from ecosphere.world.overworld import Overworld


class AnimalState(State, ABC):
    def __init__(self):
        self.__fallback_direction = None

    @abstractmethod
    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        pass

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__.replace("State", "")

    def decide_fallback_direction(self, animal: "Animal", overworld: "Overworld"):
        if self.__fallback_direction is None:
            directions = [
                Position(1, 0),
                Position(-1, 0),
                Position(0, 1),
                Position(0, -1),
            ]
            self.__fallback_direction = random.choice(directions)

        new_x = max(
            0, min(animal.position.x + self.__fallback_direction.x, overworld.width - 1)
        )
        new_y = max(
            0,
            min(animal.position.y + self.__fallback_direction.y, overworld.height - 1),
        )

        # If we hit the edge of the map, change direction
        if new_y == overworld.height - 1 or new_y == 0:
            self.__fallback_direction.y *= -1
        if new_x == overworld.width - 1 or new_x == 0:
            self.__fallback_direction.x *= -1

        return Position(new_x, new_y)
