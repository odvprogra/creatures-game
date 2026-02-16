
import random
from world import World
from creature import Creature

class Simulation:

    def __init__(self, world:World):
        self.world = world

    def step(self, dt: float):
        self.world.set_food()

        alive = []
        for c in self.world.creatures:
            if not c.is_alive():
                continue
            c.decide(self.world, dt)
            alive.append(c)
        self.world.creatures = alive

    



