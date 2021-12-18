import pygame
import math

from utils.point import Point

# Handles Vehicles types
class VehicleType:
    TRIANGLE = 0
    SQUARE = 1
    CIRCLE = 2
    WEAPONS = (TRIANGLE,)
    TARGETS = (SQUARE, CIRCLE)


# Handles Vehicles
class Vehicle:
    coords = Point(0, 0)
    _speed = Point(2, 4)
    max_speed = 20
    strength = Point(0, 0)
    max_strength = 10
    _seeInFuture = 3

    def __init__(
        self,
        coords=Point(0, 0),
        speed=Point(1, 1),
        force=Point(1, 1),
        vehicle_type=VehicleType.CIRCLE,
        radius=6,
        color=(200, 100, 100),
    ):
        self.coords = coords
        self._speed = speed
        self.strength = force
        self.radius = radius
        self._color = color
        self._colorFg = pygame.Color([int(c / 2) for c in self._color])
        self.vehicle_type = vehicle_type
        self.has_collided = False
        self.age = 0

    def steer_update(self, track):
        self.strength = Point(0, 0)
        self.strength = self.strength + self.steer_path_follow(track)

    def steer_path_follow(self, track):
        (s, p, l) = track.closest_point_to_point(self.coords)
        # TODO: We should first add a force if l is too large
        #  (too far from the middle of the track)

        # This is the future position
        (sf, futurePosition) = track.segment_point_add_length(
            s, p, max(10, abs(self._speed)) * self._seeInFuture
        )
        # We just have to register a force to get to futurePosition !
        force = futurePosition - self.coords
        force = force * (self.max_strength / abs(force))
        return force

    def draw_me(self, screen):
        if self.vehicle_type == VehicleType.CIRCLE:
            pygame.draw.circle(
                screen, self._color, self.coords.to_tuple(), self.radius, 0
            )
            pygame.draw.circle(
                screen, self._colorFg, self.coords.to_tuple(), self.radius, 5
            )
        elif self.vehicle_type == VehicleType.SQUARE:
            pygame.draw.rect(
                screen,
                self._color,
                pygame.Rect(
                    self.coords.x - self.radius,
                    self.coords.y - self.radius,
                    self.radius * 2,
                    self.radius * 2,
                ),
                0,
            )
            pygame.draw.rect(
                screen,
                self._color,
                pygame.Rect(
                    self.coords.x - self.radius,
                    self.coords.y - self.radius,
                    self.radius * 2,
                    self.radius * 2,
                ),
                2,
            )
        elif self.vehicle_type == VehicleType.TRIANGLE:
            coordinates = []
            for i in range(3):
                coordinates.append(
                    [
                        self.coords.x + self.radius * math.cos(2 * math.pi * i / 3),
                        self.coords.y + self.radius * math.sin(2 * math.pi * i / 3),
                    ]
                )
            pygame.draw.polygon(screen, (255, 0, 0), coordinates)


class SetOfVehicles:
    def __init__(self, properties):
        self.vehicles = []
        self.marks = 0
        self.killed_targets = 0
        self.used_weapons = 0
        self.properties = properties

    def handle_collisions(self):
        """
        Simple collision checking. Not a very good one, but may do the job
        for simple simulations
        """
        for i, v1 in enumerate(self.vehicles):
            for v2 in self.vehicles[i + 1 :]:
                offset = v2.coords - v1.coords
                al = abs(offset)
                if al != 0 and al < v1.radius + v2.radius - 1:  # collision
                    if (
                        v1.vehicle_type in VehicleType.WEAPONS
                        and v2.vehicle_type in VehicleType.TARGETS
                    ):
                        self.vehicles.remove(v2)
                        v1.coords = Point(
                            int(v1.coords.x + offset.x / al * (v1.radius + v2.radius)),
                            int(v2.coords.y + offset.y / al * (v1.radius + v2.radius)),
                        )
                        v1.has_collided = True
                        self.marks += 10
                        self.killed_targets += 1
                    elif (
                        v1.vehicle_type in VehicleType.TARGETS
                        and v2.vehicle_type in VehicleType.WEAPONS
                    ):
                        self.vehicles.remove(v1)
                        v2.has_collided = True
                        self.marks += 10
                        self.killed_targets += 1
                    elif (
                        v1.vehicle_type in VehicleType.WEAPONS
                        and v2.vehicle_type in VehicleType.WEAPONS
                    ):
                        self.marks -= 20

    def update_positions(self):
        for v in self.vehicles:
            v.age += 1
            if v.age == 50 and v.vehicle_type in VehicleType.WEAPONS:
                self.vehicles.remove(v)
                self.marks -= 3
                continue
            v._speed = v._speed + v.strength
            speed = abs(v._speed)
            if speed > v.max_speed:
                v._speed = v._speed * (v.max_speed / speed)
            v.coords = Point(v.coords.x + int(v._speed.x), v.coords.y + int(v._speed.y))

    def append(self, item):
        self.vehicles.append(item)

    def draw_me(self):
        screen = self.properties["screen"]
        for v in self.vehicles:
            v.draw_me(screen)
