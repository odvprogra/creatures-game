from creature import Creature
from world import World
from simulation import Simulation
from renderer import Renderer

creatures = [
    Creature(id=i, x=50, y=50, name=f"Creatura {i}")
    for i in range(10)
]

world = World(width=100, height=100, creatures=creatures)

sim = Simulation(world)
renderer = Renderer(world)

running = True
paused = False
step = 0
sim_speed = 1

while running:
    dt = renderer.tick(60) / 1000.0
    running, toggle_pause, speed_delta = renderer.handle_events()

    if toggle_pause:
        paused = not paused
    sim_speed = max(1, min(sim_speed + speed_delta, 20))

    if not paused:
        for _ in range(sim_speed):
            sim.step(dt)
            step += 1

    renderer.draw(sim, step, paused, sim_speed)

renderer.cleanup()
