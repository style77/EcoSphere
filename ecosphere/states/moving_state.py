from typing import TYPE_CHECKING

from ecosphere.states.state import AnimalState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class MovingState(AnimalState):
    """
    The animal is moving. It will move to a new position in the environment.
    """

    async def handle(self, animal: "Animal", environment_context: "EnvironmentContext"):
        new_position = animal._calculate_position(
            environment_context.overworld, environment_context.biome_manager
        )
        await animal.move_towards(
            new_position,
            environment_context.overworld,
            environment_context.biome_manager,
        )
