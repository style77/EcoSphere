from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int

    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def is_next_to(self, other: "Position") -> bool:
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1

    def is_within_range(self, other: "Position", range: int) -> bool:
        return abs(self.x - other.x) <= range and abs(self.y - other.y) <= range
