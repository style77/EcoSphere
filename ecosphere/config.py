from dataclasses import dataclass
from typing import Literal

from ecosphere.entities.animal import Crab, Fish, Fox
from ecosphere.entities.food_spawner import Berries, Mushrooms, Seaweeds, Wheats
from ecosphere.entities.plant import Flower, Tree

Biome = Literal[
    "WATER",
    "PLAINS",
    "FOREST",
    "DESERT",
    "FOOTHILLS",
    "MOUNTAINS",
]


@dataclass
class BiomeSpawnRate:
    WATER: float = 0.0
    PLAINS: float = 0.0
    FOREST: float = 0.0
    DESERT: float = 0.0
    FOOTHILLS: float = 0.0
    MOUNTAINS: float = 0.0


@dataclass
class EntityBiomeSpawnRates:
    entity_name: str
    spawn_rates: BiomeSpawnRate


ENTITY_BIOME_SPAWN_RATES = [
    EntityBiomeSpawnRates(
        entity_name="Tree",
        spawn_rates=BiomeSpawnRate(
            PLAINS=0.10,
            FOREST=0.8,
            DESERT=0.15,
        ),
    ),
    EntityBiomeSpawnRates(
        entity_name="Flower",
        spawn_rates=BiomeSpawnRate(
            PLAINS=0.75,
            FOREST=0.1,
        ),
    ),
    EntityBiomeSpawnRates(
        entity_name="Crab",
        spawn_rates=BiomeSpawnRate(
            DESERT=0.4,
        ),
    ),
    EntityBiomeSpawnRates(
        entity_name="Fox",
        spawn_rates=BiomeSpawnRate(
            FOREST=0.6,
        ),
    ),
    EntityBiomeSpawnRates(
        entity_name="Fish",
        spawn_rates=BiomeSpawnRate(
            WATER=0.8,
        ),
    ),
]


@dataclass
class FoodBiomeSpawnRates:
    food_name: str
    spawn_rates: BiomeSpawnRate


FOOD_BIOME_SPAWN_RATES = [
    FoodBiomeSpawnRates(
        food_name="Berries",
        spawn_rates=BiomeSpawnRate(PLAINS=0.05, FOREST=0.85),
    ),
    FoodBiomeSpawnRates(
        food_name="Mushrooms",
        spawn_rates=BiomeSpawnRate(
            FOREST=0.7,
        ),
    ),
    FoodBiomeSpawnRates(
        food_name="Seaweeds",
        spawn_rates=BiomeSpawnRate(
            WATER=0.85,
        ),
    ),
    FoodBiomeSpawnRates(
        food_name="Wheats",
        spawn_rates=BiomeSpawnRate(
            PLAINS=0.6,
        ),
    ),
]


ENTITIES = [Tree, Flower, Crab, Fox, Fish]
SPAWNERS = [Berries, Mushrooms, Seaweeds, Wheats]

MINUTE_LENGTH = 1  # seconds

REFRESH_STATIC_AFTER = 1  # iterations = MINUTE_LENGTH * REFRESH_STATIC_AFTER
