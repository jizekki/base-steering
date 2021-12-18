import sys
import pygame
import pygame.draw
import random

from point import Point
from scene import Scene
from vehicle import Vehicle


gameWidth = 640
gameHeight = 480
screenWidth = gameWidth
screenHeight = gameHeight + 60
screenSize = Point(screenWidth, screenHeight)

circuit = [
    Point(0.1 * gameWidth, 0.1 * gameHeight),
    Point(0.9 * gameWidth, 0.1 * gameHeight),
    Point(0.8 * gameWidth, 0.3 * gameHeight),
    Point(0.8 * gameWidth, 0.7 * gameHeight),
    Point(0.9 * gameWidth, 0.9 * gameHeight),
    Point(0.1 * gameWidth, 0.9 * gameHeight),
    Point(0.2 * gameWidth, 0.7 * gameHeight),
    Point(0.2 * gameWidth, 0.3 * gameHeight),
]


def main():
    pygame.init()
    clock = pygame.time.Clock()
    properties = {
        "screenWidth": screenWidth,
        "screenHeight": screenHeight,
        "gameWidth": gameWidth,
        "gameHeight": gameHeight,
        "screen": pygame.display.set_mode((screenWidth, screenHeight)),
        "circuit": circuit.copy(),
    }
    scene = Scene(properties=properties)
    done = False
    ticks = 0
    while not done:
        if ticks % 40 == 0:
            scene.vehicles.append(
                Vehicle(
                    Point(
                        random.randint(0, gameWidth - 1),
                        random.randint(0, gameHeight - 1),
                    ),
                    color=random.choices(range(256), k=3),
                    radius=random.randint(5, 15),
                    vehicle_type=random.randint(1, 2),
                )
            )
        ticks += 1
        clock.tick(20)
        scene.update()
        scene.draw_me()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    scene.track.is_moving = not scene.track.is_moving
                if event.key == pygame.K_r:
                    properties["circuit"] = circuit.copy()

            if event.type == pygame.MOUSEBUTTONDOWN:
                scene.event_click(event.dict["pos"], event.dict["button"])
            elif event.type == pygame.MOUSEMOTION:
                scene.record_mouse_move(event.dict["pos"])

    pygame.quit()


if not sys.flags.interactive:
    main()
