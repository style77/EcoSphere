from dataclasses import dataclass
from typing import Literal
from ecosphere.animals import Crab

from ecosphere.plants import Flower, Tree

Biome = Literal[
    "OCEAN",
    "PLAINS",
    "FOREST",
    "DESERT",
    "FOOTHILLS",
    "MOUNTAINS",
]


@dataclass
class BiomeSpawnRate:
    OCEAN: float = 0.0
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
]


ENTITIES = [Tree, Flower, Crab]