import random
from typing import TYPE_CHECKING

from ecosphere.states.state import AnimalState
from ecosphere.states.moving_state import MovingState
from ecosphere.states.sleeping_state import SleepingState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class IdleState(AnimalState):
    """
    The animal is not doing anything in particular. It will randomly select a new state.
    """

    def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        if animal.energy >= 80:  # Animal is full of energy and can just have some fun
            animal.state = MovingState()
        else:
            animal.state = random.choice([MovingState(), SleepingState()])
