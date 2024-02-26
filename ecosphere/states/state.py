from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ecosphere.abc.state import State

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class AnimalState(State, ABC):
    @abstractmethod
    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        pass

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__.replace("State", "")
