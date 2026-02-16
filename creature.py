from __future__ import annotations
from dataclasses import dataclass, field
import random
from typing import Optional

from brain import Brain
from food import Food
from world import World
import math

import itertools

_creature_id_counter = itertools.count()

SPEED = 10
WANDER_SPEED = 20
HUNGER_RATE = 10
BOREDOM_RATE = 5
ENERGY_RATE = 2
AGE_RATE = 10
VISION_RATE = 60

@dataclass
class Creature:
    name: str
    x: float
    y: float
    id: int = field(default_factory=lambda: next(_creature_id_counter))
    energy: float = 100
    hunger: float = 0
    boredom: float = 0
    age: float = 0
    is_death:bool = False
    brain:Brain = Brain()
    current_action:str = "wander"
    is_ocuped: bool = False
    partner:Optional[Creature] = None

    def is_alive(self) -> bool:
        is_alive = self.energy > 0 and not self.is_death and self.age < 500
        if not is_alive and not self.is_death:
            self.is_death = True
            print(f"{self.name} ha muerto con {int(self.age)} anios en posicion x:{self.x:.2f} y:{self.y:.2f}")

        return is_alive

    def decide(self, world:World, dt:float):
        self.current_action = self.brain.decide(self)
        self.act(world, dt)

    def act(self, world, dt:float):
        if self.current_action == "wander":
            self.wander(world, dt)

        elif self.current_action == "seek_food":
            self.seek_food(world, dt)

        elif self.current_action == "reproduce":
            self.look_for_reproduction(world, dt)

        self.update_needs(dt)


    def look_for_reproduction(self, world:World, dt:float):
        if self.is_ocuped and self.partner:
            dist = self.go_to_thing(self.partner.x, self.partner.y, dt)
            if dist < 1:
                self.reproduce(world)
            return

        c = self.brain.find_partner(self, world)
        if c:
            self.compromise_with(c)
            self.go_to_thing(c.x, c.y, dt)
        else:
            self.wander(world, dt)

    def reproduce(self, world:World):
        partner = self.partner
        if not partner:
            self.is_ocuped = False
            return
        partner.partner = None
        partner.is_ocuped = False
        partner.boredom = 0
        self.partner = None
        self.is_ocuped = False
        self.boredom = 0
        world.creatures.append(Creature(f"Creature {self.id}.1", self.x, self.y))

    def compromise_with(self, c:Creature):
        self.is_ocuped = True
        c.is_ocuped = True
        self.partner = c
        c.partner = self


    def is_free_for_reproduce(self) -> bool:
        return self.boredom > 40 and not self.is_ocuped and not self.is_death

    def update_needs(self, dt:float):
        self.hunger += HUNGER_RATE * dt
        self.boredom += BOREDOM_RATE * dt
        self.energy -= ENERGY_RATE * dt
        self.age += AGE_RATE * dt

    def wander(self, world:World, dt:float):
        x = random.uniform(-1, 1) * WANDER_SPEED * dt
        y = random.uniform(-1, 1) * WANDER_SPEED * dt
        self.x = max(0, min(self.x + x, world.width))
        self.y = max(0, min(self.y + y, world.height))

    def seek_food(self, world, dt:float):

        nerby_food = self.brain.find_nearest_food(self, world)

        if nerby_food:
            dist = self.go_to_thing(nerby_food.x, nerby_food.y, dt)
            if dist < 1:
                self.eat(nerby_food, world)
        else:
            self.wander(world, dt)

    def eat(self, food: Food, world: World):
        self.energy += 30
        self.hunger = 0
        world.food.remove(food)


    def can_see_thing(self, x, y) -> bool:
        d = ((x - self.x)**2 + (y - self.y)**2) ** 0.5
        return d < VISION_RATE

    def go_to_thing(self, x, y, dt:float) -> float:
        dx = x - self.x
        dy = y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += dx/dist * SPEED * dt
            self.y += dy/dist * SPEED * dt
        return dist
