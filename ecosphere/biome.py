import curses
from enum import Enum, auto
from functools import lru_cache
from typing import List, Any, Literal, Dict
from noise import pnoise2


class Biome(Enum):
    OCEAN = auto()
    PLAINS = auto()
    FOREST = auto()
    DESERT = auto()
    FOOTHILLS = auto()
    MOUNTAINS = auto()


class BiomeColorPair(Enum):
    """
    Biome with their curses color pair mapping.
    """

    OCEAN = 1
    DESERT = 2
    PLAINS = 3
    FOREST = 4
    FOOTHILLS = 5
    MOUNTAINS = 6


class BiomeManager:
    ENTITY_BIOME_SPAWN_RATES: Dict[
        str,
        Dict[
            Literal[
                Biome.OCEAN,
                Biome.PLAINS,
                Biome.FOREST,
                Biome.DESERT,
                Biome.FOOTHILLS,
                Biome.MOUNTAINS,
            ],
            str,
        ],
    ] = {
        "Tree": {
            Biome.OCEAN: 0,
            Biome.PLAINS: 0.2,
            Biome.FOREST: 0.5,
            Biome.DESERT: 0.1,
            Biome.FOOTHILLS: 0.0,
            Biome.MOUNTAINS: 0.0,
        },
        "Animal": {
            Biome.OCEAN: 0,
            Biome.PLAINS: 0.8,
            Biome.FOREST: 0.6,
            Biome.DESERT: 0.2,
            Biome.FOOTHILLS: 0.3,
            Biome.MOUNTAINS: 0.1,
        },
    }

    def __init__(self, stdscr: Any, width: int, height: int):
        self.stdscr = stdscr
        self.width = width
        self.height = height

        self.map: List[List[float]] = self._generate_biome_map()

    def _generate_biome_map(self, scale: int = 0.05):
        """
        Generate a biome map using Perlin noise.
        """
        biome_map = [
            [pnoise2(x * scale, y * scale) for x in range(self.width)]
            for y in range(self.height)
        ]
        return biome_map

    def draw(self):
        """
        Color the screen according to the biome map.
        """
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                biome = self.get_biome(self.map[y][x])
                color = BiomeColorPair[biome.name]

                self.stdscr.addstr(
                    y,
                    x,
                    " ",
                    curses.color_pair(color.value),
                )
        self.stdscr.refresh()

    @lru_cache
    def get_biome_color(self, biome: Biome) -> int:
        """
        Get the color pair for a given biome.
        """
        color = BiomeColorPair[biome.name]
        return curses.color_pair(color.value)

    @lru_cache
    def get_biome_by_coords(self, x: int, y: int) -> str:
        """
        Get the biome for a given set of coordinates.
        """
        value = self.map[y][x]
        return self.get_biome(value)

    @lru_cache
    def get_biome(self, value: float) -> str:
        """
        Get the biome for a given value.
        """
        if value < -0.4:
            return Biome.OCEAN
        elif value < -0.2:
            return Biome.DESERT
        elif value < 0.2:
            return Biome.PLAINS
        elif value < 0.5:
            return Biome.FOREST
        elif value < 0.65:
            return Biome.FOOTHILLS
        else:
            return Biome.MOUNTAINS
