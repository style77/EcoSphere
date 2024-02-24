import random
from typing import TYPE_CHECKING

from ecosphere.abc.position import Position
from ecosphere.world.biome import Biome
from ecosphere.state import AnimalState
from ecosphere.states.idle_state import IdleState

if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal


class SeekingWaterState(AnimalState):
    def handle(self, animal: "Animal", environment_context: "EnvironmentContext"):
        if animal.thirst <= 0:
            animal.state = IdleState()
            return

        nearest_water = self.find_nearest_water_source(
            animal, environment_context
        )

        if nearest_water:
            print(
                f"There is water nearby ({nearest_water}). Moving from {animal.position} towards it (thirst: {animal.thirst})."
            )
            if animal.position.is_next_to(nearest_water):
                animal.thirst -= animal.properties.thirst_decrease_rate
                if animal.thirst < 20:
                    animal.state = IdleState()
            else:
                animal.move_towards(
                    nearest_water,
                    environment_context.overworld,
                    environment_context.biome_manager,
                )
        else:
            fallback_direction = self.decide_fallback_direction(
                animal, environment_context.overworld
            )
            animal.move_towards(
                fallback_direction,
                environment_context.overworld,
                environment_context.biome_manager,
            )

    def find_nearest_water_source(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ):
        perception_range = animal.perception_radius
        current_pos = animal.position
        nearest_water_pos = None
        min_distance = float("inf")

        for x in range(
            max(0, current_pos.x - perception_range),
            min(
                environment_context.overworld.width,
                current_pos.x + perception_range + 1,
            ),
        ):
            for y in range(
                max(0, current_pos.y - perception_range),
                min(
                    environment_context.overworld.height,
                    current_pos.y + perception_range + 1,
                ),
            ):
                # Check if the position (x, y) is within a circular area
                if (x - current_pos.x) ** 2 + (
                    y - current_pos.y
                ) ** 2 <= perception_range**2:
                    if (
                        environment_context.biome_manager.get_biome_by_coords(x, y)
                        is Biome.WATER
                    ):
                        distance = (
                            (x - current_pos.x) ** 2 + (y - current_pos.y) ** 2
                        ) ** 0.5
                        if distance < min_distance:
                            nearest_water_pos = Position(x, y)
                            min_distance = distance

        if nearest_water_pos is not None:
            return nearest_water_pos

    def decide_fallback_direction(self, animal, overworld):
        directions = [Position(1, 0), Position(-1, 0), Position(0, 1), Position(0, -1)]
        fallback_direction = random.choice(directions)

        new_x = max(
            0, min(animal.position.x + fallback_direction.x, overworld.width - 1)
        )
        new_y = max(
            0, min(animal.position.y + fallback_direction.y, overworld.height - 1)
        )

        return Position(new_x, new_y)
