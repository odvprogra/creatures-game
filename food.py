from dataclasses import dataclass, field
import itertools

_food_id_counter = itertools.count()

@dataclass
class Food:
    x: float
    y: float
    id: int = field(default_factory=lambda: next(_food_id_counter))