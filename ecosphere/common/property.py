from dataclasses import dataclass


@dataclass
class StatusProperty:
    """
    Class representing the status properties of an entity in the overworld.
    """

    hunger_increase_rate: float = 0.5
    hunger_decrease_rate: float = 10

    thirst_increase_rate: float = 0.5
    thirst_decrease_rate: float = 10

    energy_increase_rate: float = 10
    energy_decrease_rate: float = 0.5

    mating_urge_increase_rate: float = 5
    mating_urge_decrease_rate: float = 1

    health_increase_rate: float = 2
    health_multiplier: float = 2.5
    health_decrease_rate: float = 2

    perception_radius: int = 30
    movement_speed: float = 1


@dataclass
class SpawnerProperty:
    """
    Class representing the properties of a spawner in the overworld.
    """

    dispersal_speed: float = 0.05
    dispersal_radius: int = 1
    range_capacity: int = 4


@dataclass
class FoodProperty:
    """
    Class representing the properties of a food entity in the overworld.
    """

    nutrition: float = 10
