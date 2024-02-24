from typing import TYPE_CHECKING

from ecosphere.states.state import AnimalState
from ecosphere.states.moving_state import MovingState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class SleepingState(AnimalState):
    def handle(self, animal: "Animal", environment_context: "EnvironmentContext"):
        animal.energy += animal.properties.energy_increase_rate
        if animal.energy >= 100:
            animal.state = MovingState()
