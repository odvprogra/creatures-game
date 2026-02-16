from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from creature import Creature
    from world import World
    from food import Food


class Brain:

    def decide(self, creature: Creature) -> str:
        if creature.hunger > 30:
            return "seek_food"

        elif creature.boredom > 30 and creature.energy > 10:
            return "reproduce"
        else:
            return "wander"

    def find_nearest_food(self, creature: Creature, world: World) -> Optional[Food]:
        best = None
        best_dist = float('inf')
        for f in world.food:
            d = (f.x - creature.x)**2 + (f.y - creature.y)**2
            if d < best_dist and creature.can_see_thing(f.x, f.y):
                best_dist = d
                best = f
        return best

    def find_partner(self, creature: Creature, world: World) -> Optional[Creature]:
        for c in world.creatures:
            if c is not creature and c.is_free_for_reproduce() and creature.can_see_thing(c.x, c.y):
                return c
        return None
