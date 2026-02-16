from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import TYPE_CHECKING

from food import Food

if TYPE_CHECKING:
    from creature import Creature


@dataclass
class World:
    width: int
    height: int
    creatures: list[Creature]
    food: list[Food] = field(default_factory=list)
    
    def set_food(self):
        if len(self.food) >= 200:
            return
        if not random.randint(1, 10) == 1:
            return

        x = random.randint(1, self.width)
        y = random.randint(1, self.height)

        self.food.append(Food(x,y))