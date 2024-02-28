import random
from typing import TYPE_CHECKING
from ecosphere.abc.position import Position

from ecosphere.states.state import AnimalState

import logging

from ecosphere.world.biome import Biome


if TYPE_CHECKING:
    from ecosphere.common.environment_context import EnvironmentContext
    from ecosphere.entities.animal import Animal
    from ecosphere.world.overworld import Overworld
    from ecosphere.entities.food import Food


class DeadState(AnimalState):
    """
    The animal is dead. It will not do anything anymore.
    """

    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        return


class IdleState(AnimalState):
    """
    The animal is not doing anything in particular. It will decide what to do next based on its current status.
    """

    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        if animal.health <= 0:
            if not isinstance(animal.state, DeadState):
                logging.debug(f"{animal.id} has died.")
                animal.change_state(DeadState())
                # bus.emit("entity:dead", self)
                return

        if animal.energy <= 10:
            logging.debug(f"{animal.id} is very tired and needs to rest.")
            animal.change_state(SleepingState())
        elif animal.thirst >= 50:
            logging.debug(f"{animal.id} is thirsty and needs water.")
            animal.change_state(SeekingWaterState())
        elif animal.hunger >= 50:
            logging.debug(f"{animal.id} is hungry and needs to eat.")
            animal.change_state(ForagingState())
        elif animal.mating_urge >= 80 and animal.energy > 50:
            logging.debug(f"{animal.id} is in mood and needs to mate.")
            animal.change_state(MatingState())
        elif animal.energy < 50:
            logging.debug(f"{animal.id} is tired and needs to rest.")
            animal.change_state(SleepingState())
        else:
            animal.change_state(MovingState())


class ForagingState(AnimalState):
    """
    The animal is foraging for food. It will look for food in the environment and eat it.
    """

    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        if animal.hunger <= 0:
            logging.debug(f"{animal} is no longer hungry.")
            animal.change_state(IdleState())
            return

        nearest_food = self.find_nearest_food_source(animal, environment_context)

        if nearest_food:
            logging.debug(
                f"{animal} found that there is food nearby ({nearest_food}). Moving from {animal.position} towards it (hunger: {animal.hunger})."
            )
            if animal.position.is_next_to(nearest_food.position):
                logging.debug(f"{animal} is eating food.")
                self.eat(animal, nearest_food, environment_context.overworld)
            else:
                logging.debug(f"{animal} is moving towards food.")
                await animal.move_towards(
                    nearest_food.position,
                    environment_context.overworld,
                    environment_context.biome_manager,
                )
        else:
            logging.debug(
                f"{animal} couldn't find any water nearby. Moving in a random direction."
            )
            fallback_direction = self.decide_fallback_direction(
                animal, environment_context.overworld
            )
            await animal.move_towards(
                fallback_direction,
                environment_context.overworld,
                environment_context.biome_manager,
            )

    def eat(self, animal: "Animal", food: "Food", overworld: "Overworld"):
        animal.hunger -= food.properties.nutrition
        overworld.remove(food)

    def find_nearest_food_source(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        perception_range = animal.perception_radius
        current_pos = animal.position
        nearest_food = None
        min_distance = float("inf")

        nearest_food = environment_context.overworld.get_nearby_food(
            current_pos, perception_range, food_type=animal._can_eat
        )

        for food in nearest_food:
            distance = current_pos.distance_to(food.position)
            if distance < min_distance:
                min_distance = distance
                nearest_food = food

        return nearest_food


class MatingState(AnimalState):
    """
    The animal is looking for a mate. It will look for potential mates in the
    environment and move towards them. If it finds a mate, they will reproduce.
    """

    async def handle(
        self, animal: "Animal", environment_context: "EnvironmentContext"
    ) -> None:
        environment = animal.perceive_environment(
            environment_context.overworld, environment_context.biome_manager
        )
        if environment.potential_mates:
            mate: Animal = min(
                environment.potential_mates,
                key=lambda mate: animal.position.distance_to(mate.position),
            )
            if animal.position.distance_to(mate.position) <= animal.perception_radius:
                if not animal.position.is_next_to(mate.position):
                    await animal.move_towards(
                        mate.position,
                        environment_context.overworld,
                        environment_context.biome_manager,
                    )
                else:
                    self.reproduce(animal, mate, environment_context.overworld)
            else:
                logging.debug(f"{animal} is moving towards a potential mate.")
                await animal.move_towards(
                    mate.position,
                    environment_context.overworld,
                    environment_context.biome_manager,
                )
        else:
            fallback_direction = self.decide_fallback_direction(
                animal, environment_context.overworld
            )
            await animal.move_towards(
                fallback_direction,
                environment_context.overworld,
                environment_context.biome_manager,
            )

    def calculate_offspring_position(self, animal_position: Position, mate_position: Position) -> Position:
        return Position(
            (animal_position.x + mate_position.x) // 2,
            (animal_position.y + mate_position.y) // 2,
        )

    def reproduce(self, animal: "Animal", mate: "Animal", overworld: "Overworld") -> None:
        offspring_position = self.calculate_offspring_position(animal.position, mate.position)

        offspring = animal.__class__
        overworld.spawn_entity(offspring, offspring_position)

        animal.energy -= 50
        mate.energy -= 50

        animal.change_state(IdleState())
        mate.change_state(IdleState())


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


class SeekingWaterState(AnimalState):
    async def handle(self, animal: "Animal", environment_context: "EnvironmentContext"):
        if animal.thirst <= 0:
            logging.debug(f"{animal} is no longer thirsty.")
            animal.change_state(IdleState())
            return

        nearest_water = self.find_nearest_water_source(animal, environment_context)

        if nearest_water:
            logging.debug(
                f"{animal} found that there is water nearby ({nearest_water}). Moving from {animal.position} towards it (thirst: {animal.thirst})."
            )
            if animal.position.is_next_to(nearest_water):
                logging.debug(f"{animal} is drinking water.")
                self.drink(animal)
            else:
                logging.debug(f"{animal} is moving towards water.")
                await animal.move_towards(
                    nearest_water,
                    environment_context.overworld,
                    environment_context.biome_manager,
                )
        else:
            logging.debug(
                f"{animal} couldn't find any water nearby. Moving in a random direction."
            )
            fallback_direction = self.decide_fallback_direction(
                animal, environment_context.overworld
            )
            await animal.move_towards(
                fallback_direction,
                environment_context.overworld,
                environment_context.biome_manager,
            )

    def drink(self, animal: "Animal"):
        animal.thirst -= animal.properties.thirst_decrease_rate
        if animal.thirst < 20:
            animal.change_state(IdleState())

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


class SleepingState(AnimalState):
    async def handle(self, animal: "Animal", environment_context: "EnvironmentContext"):
        animal.energy += animal.properties.energy_increase_rate
        if animal.energy >= 100:
            animal.state = MovingState()
