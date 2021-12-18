import pygame
import random

from utils.point import Point


class Track:
    _color_back = pygame.Color(128, 128, 128)
    _color_fore = pygame.Color(10, 10, 10)
    _width = 20
    _screen = None
    _cachedLength = []
    _cachedNormals = []

    def __init__(self, properties):
        self.properties = properties
        self.is_moving = False
        self.initialize()

    def initialize(self):
        circuit = self.properties["circuit"]
        for i in range(0, len(circuit)):
            self._cachedNormals.append(
                circuit[i] - circuit[len(circuit) - 1 if i - 1 < 0 else i - 1]
            )
            self._cachedLength.append(abs(self._cachedNormals[i]))
            self._cachedNormals[i] = Point(
                self._cachedNormals[i].x / self._cachedLength[i],
                self._cachedNormals[i].y / self._cachedLength[i],
            )

    def segment_point_add_length(self, segment, point, length):
        """
        Get the segment and point (on it) after adding length to the
        segment and point (on it), by following the path
        """
        circuit = self.properties["circuit"]
        next_step = point.distance_to(circuit[segment])
        if next_step > length:  # We stay on the same segment
            next_point = point + self._cachedNormals[segment] * length
            return segment, Point(int(next_point.x), int(next_point.y))
        length -= next_step
        segment = segment + 1 if segment + 1 < len(circuit) else 0
        while length > self._cachedLength[segment]:
            length -= self._cachedLength[segment]
            segment = segment + 1 if segment + 1 < len(circuit) else 0
        next_point = (
            circuit[segment - 1 if segment > 0 else len(circuit) - 1]
            + self._cachedNormals[segment] * length
        )
        return segment, Point(int(next_point.x), int(next_point.y))

    def closest_point_to_point(self, point):
        best_length = None
        best_point = None
        best_segment = None
        circuit = self.properties["circuit"]
        for i in range(0, len(circuit)):
            p = self.closest_point_to_segment(i, point)
            distance = p.distance_to(point)
            if best_length is None or distance < best_length:
                best_length = distance
                best_point = p
                best_segment = i
        return best_segment, best_point, best_length

    def closest_point_to_segment(self, numSegment, point):
        """
        Returns the closest point on the circuit segment from point
        """
        circuit = self.properties["circuit"]
        p0 = circuit[len(circuit) - 1 if numSegment - 1 < 0 else numSegment - 1]
        p1 = circuit[numSegment]
        local = point - p0
        projection = local * self._cachedNormals[numSegment]
        if projection < 0:
            return p0
        if projection > self._cachedLength[numSegment]:
            return p1
        return p0 + self._cachedNormals[numSegment] * projection

    def draw_me(self):
        screen = self.properties["screen"]
        circuit = self.properties["circuit"]
        for p in circuit:
            pygame.draw.circle(
                screen, self._color_back, p.to_tuple(), int(self._width / 2), 0
            )
        pygame.draw.lines(
            screen,
            self._color_back,
            True,
            tuple(map(Point.to_tuple, circuit)),
            self._width,
        )

        if self.is_moving:
            to_move = random.randint(0, len(circuit) - 1)
            circuit[to_move] += Point(random.randint(-1, 1), random.randint(-1, 1))
