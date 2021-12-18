import pygame
import random

from utils.point import Point
from .track import Track
from .vehicle import Vehicle, SetOfVehicles


class Control:
    def __init__(self, properties, vehicles):
        self.properties = properties
        self.vehicles = vehicles
        self._font = pygame.font.SysFont("Arial", 20)

    def draw_text(self, text, position, color=(255, 0, 127)):
        text = self._font.render(text, True, color)
        text_rect = text.get_rect(
            center=(self.properties["screenWidth"] / 2, position[1])
        )
        self.properties["screen"].blit(text, text_rect)

    def draw_me(self):
        margin = 10
        screen = self.properties["screen"]
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(
                margin,
                self.properties["gameHeight"],
                self.properties["screenWidth"] - 2 * margin,
                self.properties["screenHeight"]
                - self.properties["gameHeight"]
                - margin,
            ),
            2,
        )
        self.draw_text(
            "Points : {} \t|\t Killed targets : {} \t|\t Weapons used : {}".format(
                self.vehicles.marks,
                self.vehicles.killed_targets,
                self.vehicles.used_weapons,
            ),
            (
                20,
                (
                    self.properties["gameHeight"]
                    + self.properties["screenHeight"]
                    - margin
                )
                / 2,
            ),
        )


class Scene:
    track = None
    vehicles = None

    _mouseCoords = Point(0, 0)

    def __init__(self, properties):
        self.properties = properties
        self.track = Track(properties)
        self.vehicles = SetOfVehicles(properties)
        self.control = Control(self.properties, self.vehicles)

    def draw_me(self):
        screen = self.properties["screen"]
        screen.fill((0, 0, 0))
        self.track.draw_me()
        self.vehicles.draw_me()
        self.control.draw_me()

        # Illustrate the closest_point_to_point function
        (s, p, l) = self.track.closest_point_to_point(self._mouseCoords)
        pygame.draw.line(
            screen, (128, 255, 128), p.to_tuple(), self._mouseCoords.to_tuple()
        )
        pygame.draw.circle(
            screen,
            (128, 255, 128),
            self.track.segment_point_add_length(s, p, 150)[1].to_tuple(),
            20,
            5,
        )

        pygame.display.flip()

    def update(self):
        for v in self.vehicles.vehicles:
            v.steer_update(self.track)
        self.vehicles.update_positions()
        self.vehicles.handle_collisions()
        self.draw_me()

    def event_click(self, coord, b):
        # TODO: check the value of b
        self.vehicles.append(
            Vehicle(
                Point(coord[0], coord[1]),
                color=random.choices(range(256), k=3),
                radius=random.randint(5, 15),
                vehicle_type=0,
            )
        )
        self.vehicles.used_weapons += 1

    def record_mouse_move(self, coord):
        self._mouseCoords = Point(coord[0], coord[1])
