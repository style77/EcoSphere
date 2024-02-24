from typing import TYPE_CHECKING

from ecosphere.state import AnimalState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class ForagingState(AnimalState):
    """
    The animal is foraging for food. It will look for food in the environment and eat it.
    """

    def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        ...
