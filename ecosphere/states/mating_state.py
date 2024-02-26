from typing import TYPE_CHECKING

from ecosphere.abc.position import Position

from ecosphere.states.state import AnimalState
from ecosphere.states.idle_state import IdleState
from ecosphere.states.moving_state import MovingState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal
    from ecosphere.world.overworld import Overworld


class MatingState(AnimalState):
    """
    The animal is looking for a mate. It will look for potential mates in the
    environment and move towards them. If it finds a mate, they will reproduce.
    """

    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        environment = self.perceive_environment(
            environment_context.overworld, environment_context.biome_manager
        )
        if environment.potential_mates:
            mate: Animal = min(
                environment.potential_mates,
                key=lambda mate: animal.distance_to(mate.position),
            )
            if animal.position.distance_to(mate.position) <= animal.perception_radius:
                if not animal.position.is_next_to(mate.position):
                    await animal.move_towards(
                        mate.position,
                        environment_context.overworld,
                        environment_context.biome_manager,
                    )
                else:
                    self.reproduce(mate, animal.overworld)
        else:
            animal.state = MovingState()

    def calculate_offspring_position(self, mate_position: Position) -> Position:
        return Position(
            (self.position.x + mate_position.x) // 2,
            (self.position.y + mate_position.y) // 2,
        )

    def reproduce(self, mate: "Animal", overworld: "Overworld") -> None:
        offspring_position = self.calculate_offspring_position(mate.position)

        offspring = mate.__class__
        overworld.spawn_entity(offspring, offspring_position)

        self.energy -= 50
        mate.energy -= 50

        self.change_state(IdleState())
        mate.change_state(IdleState())
