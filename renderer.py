from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import pygame
from camera import Camera
from food import Food
from world import World
from simulation import Simulation

if TYPE_CHECKING:
    from creature import Creature


class Renderer:

    BG_COLOR = (20, 20, 30)
    HUD_COLOR = (220, 220, 220)
    DEAD_COLOR = (80, 80, 80)

    def __init__(self, world: World, scale: int = 8, screen_size: int = 800):
        self.world = world
        self.width = screen_size
        self.height = screen_size
        self.camera = Camera(base_scale=scale, screen_w=self.width, screen_h=self.height,
                             world_w=world.width, world_h=world.height)

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Criaturas")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)

        self.dragging_creature: Optional[Creature] = None
        self.panning: bool = False
        self.pan_start: tuple[int, int] = (0, 0)

    def handle_events(self):
        """Retorna (running, toggle_pause, speed_delta)."""
        toggle_pause = False
        speed_delta = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, False, 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, False, 0
                if event.key == pygame.K_SPACE:
                    toggle_pause = True
                if event.key == pygame.K_UP:
                    speed_delta = 1
                if event.key == pygame.K_DOWN:
                    speed_delta = -1

            # Zoom with scroll
            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if event.y > 0:
                    self.camera.zoom_at(mx, my, 1.15)
                elif event.y < 0:
                    self.camera.zoom_at(mx, my, 1 / 1.15)

            # Right-click: place food
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                wx, wy = self.camera.screen_to_world(*event.pos)
                self.world.food.append(Food(wx, wy))

            # Left-click down: drag creature or pan
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                wx, wy = self.camera.screen_to_world(*event.pos)
                creature = self._find_creature_at(wx, wy)
                if creature:
                    self.dragging_creature = creature
                else:
                    self.panning = True
                    self.pan_start = event.pos

            # Middle-click: always pan
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                self.panning = True
                self.pan_start = event.pos

            # Mouse motion
            if event.type == pygame.MOUSEMOTION:
                if self.dragging_creature:
                    wx, wy = self.camera.screen_to_world(*event.pos)
                    self.dragging_creature.x = max(0, min(wx, self.world.width))
                    self.dragging_creature.y = max(0, min(wy, self.world.height))
                elif self.panning:
                    dx = event.pos[0] - self.pan_start[0]
                    dy = event.pos[1] - self.pan_start[1]
                    self.camera.pan(dx, dy)
                    self.pan_start = event.pos

            # Mouse button up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_creature = None
                    self.panning = False
                if event.button == 2:
                    self.panning = False

        return True, toggle_pause, speed_delta

    def _on_screen(self, sx: int, sy: int, margin: int = 10) -> bool:
        return -margin <= sx <= self.width + margin and -margin <= sy <= self.height + margin

    def draw(self, simulation: Simulation, step: int, paused: bool, sim_speed: int = 1):
        self.screen.fill(self.BG_COLOR)

        for c in simulation.world.creatures:
            sx, sy = self.camera.world_to_screen(c.x, c.y)
            if not self._on_screen(sx, sy):
                continue

            color = self._energy_color(c.energy)
            r = max(2, int(6 * self.camera.zoom))
            pygame.draw.circle(self.screen, color, (sx, sy), r)

        for f in simulation.world.food:
            sx, sy = self.camera.world_to_screen(f.x, f.y)
            if not self._on_screen(sx, sy):
                continue
            r = max(1, int(2 * self.camera.zoom))
            pygame.draw.circle(self.screen, (255, 0, 0), (sx, sy), r)

        self._draw_hud(simulation, step, paused, sim_speed)
        pygame.display.flip()

    def tick(self, fps: int = 60) -> int:
        return self.clock.tick(fps)

    def cleanup(self):
        pygame.quit()

    def _find_creature_at(self, wx: float, wy: float, radius: float = 3.0) -> Optional[Creature]:
        best = None
        best_dist = radius
        for c in self.world.creatures:
            if c.is_death:
                continue
            d = ((c.x - wx)**2 + (c.y - wy)**2) ** 0.5
            if d < best_dist:
                best_dist = d
                best = c
        return best

    def _energy_color(self, energy: float):
        t = max(0.0, min(energy / 100.0, 1.0))
        r = int(255 * (1 - t))
        g = int(255 * t)
        return (r, g, 0)

    def _draw_hud(self, simulation: Simulation, step: int, paused: bool, sim_speed: int = 1):
        alive = sum(1 for c in simulation.world.creatures if not c.is_death)
        total = len(simulation.world.creatures)

        lines = [
            f"Step: {step}  |  Vivas: {alive}/{total}  |  Speed: {sim_speed}x",
            "PAUSA" if paused else "ESPACIO=pausa  ESC=salir  Flechas=velocidad",
        ]

        y = 6
        for line in lines:
            surf = self.font.render(line, True, self.HUD_COLOR)
            self.screen.blit(surf, (8, y))
            y += 20
