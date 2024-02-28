import random
from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int

    def __eq__(self, __value: "Position") -> bool:
        return self.x == __value.x and self.y == __value.y

    def __hash__(self):
        return hash((self.x, self.y))

    @classmethod
    def get_random_position_in_radius(
        cls, position: "Position", radius: int
    ) -> "Position":
        return cls(
            position.x + random.randint(-radius, radius),
            position.y + random.randint(-radius, radius),
        )

    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def is_next_to(self, other: "Position") -> bool:
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1

    def is_within_range(self, other: "Position", range: int) -> bool:
        return abs(self.x - other.x) <= range and abs(self.y - other.y) <= range
