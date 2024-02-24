from typing import TYPE_CHECKING

from ecosphere.state import AnimalState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class DeadState(AnimalState):
    """
    The animal is dead. It will not do anything anymore.
    """

    def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        return
