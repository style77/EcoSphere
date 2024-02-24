from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecosphere.world.biome import BiomeManager
    from ecosphere.world.overworld import Overworld


@dataclass
class EnvironmentContext:
    overworld: "Overworld"
    biome_manager: "BiomeManager"
