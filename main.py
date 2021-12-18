import sys
import pygame

import pygame.draw
import random
from point import Point
import math

__gameWidth__ = 640
__gameHeight__ = 480
__screenWidth__ = __gameWidth__
__screenheight__ = __gameHeight__ + 60
__screenSize__ = Point(__screenWidth__, __screenheight__)

__circuit__ = [
    Point(0.1 * __gameWidth__, 0.1 * __gameHeight__),
    Point(0.9 * __gameWidth__, 0.1 * __gameHeight__),
    Point(0.8 * __gameWidth__, 0.3 * __gameHeight__),
    Point(0.8 * __gameWidth__, 0.7 * __gameHeight__),
    Point(0.9 * __gameWidth__, 0.9 * __gameHeight__),
    Point(0.1 * __gameWidth__, 0.9 * __gameHeight__),
    Point(0.2 * __gameWidth__, 0.7 * __gameHeight__),
    Point(0.2 * __gameWidth__, 0.3 * __gameHeight__),
]


# Handles Vehicles types

class VehicleType:
    TRIANGLE = 0
    SQUARE = 1
    CIRCLE = 2
    WEAPONS = (TRIANGLE,)
    TARGETS = (SQUARE, CIRCLE)

# Handles Vehicles


class Vehicle:
    _coords = Point(0, 0)   # vector
    _speed = Point(2, 4)    # vector
    _maxSpeed = 20
    _Strength = Point(0, 0)  # accelerating force
    _maxStrength = 10
    _seeInFuture = 3

    def __init__(self, coords=Point(0, 0), speed=Point(1, 1), force=Point(1, 1), type=VehicleType.CIRCLE, radius=6, color=(200, 100, 100)):
        self._coords = coords
        self._speed = speed
        self._Strength = force
        self._radius = radius
        self._color = color
        self._colorFg = tuple([int(c / 2) for c in self._color])
        self._type = type
        self._hasCollided = False
        self._age = 0

    def position(self): return self._pos

    def steerUpdate(self, track, vehicules):
        self._Strength = Point(0, 0)
        self._Strength = self._Strength + self.steerPathFollow(track)
        # steerSeparation(self, vehicules)

    def steerPathFollow(self, track):
        (s, p, l) = track._closestSegmentPointToPoint(self._coords)
        # TODO: We should first add a force if l is too large (too far from the middle of the track)
        # This is the future position
        (sf, futurePosition) = track._segmentPointAddLength(
            s, p, max(10, abs(self._speed)) * self._seeInFuture)
        # We just have to register a force to get to futurePosition !
        force = futurePosition - self._coords
        force = force * (self._maxStrength / abs(force))
        return force

    def drawMe(self, screen):
        if self._type == VehicleType.CIRCLE:
            pygame.draw.circle(screen, self._color,
                               self._coords.to_tuple(), self._radius, 0)
            pygame.draw.circle(screen, self._colorFg,
                               self._coords.to_tuple(), self._radius, 5)
        elif self._type == VehicleType.SQUARE:
            pygame.draw.rect(screen, self._color, pygame.Rect(
                self._coords.x - self._radius, self._coords.y - self._radius, self._radius * 2, self._radius * 2), 0)
            pygame.draw.rect(screen, self._color, pygame.Rect(
                self._coords.x - self._radius, self._coords.y - self._radius, self._radius * 2, self._radius * 2), 2)
        elif self._type == VehicleType.TRIANGLE:
            coordinates = []
            for i in range(3):
                coordinates.append([self._coords.x + self._radius * math.cos(2 * math.pi * i / 3),
                                    self._coords.y + self._radius * math.sin(2 * math.pi * i / 3)])
            pygame.draw.polygon(screen, (255, 0, 0), coordinates)


class SetOfVehicles:
    _vehicles = []

    def __init__(self):
        self._vehicles = []
        self._marks = 0
        self._killedTargets = 0
        self._weaponsUsed = 0

    def handleCollisions(self):
        " Simple collision checking. Not a very good one, but may do the job for simple simulations"
        for i, v1 in enumerate(self._vehicles):
            for v2 in self._vehicles[i + 1:]:
                offset = v2._coords - v1._coords
                al = abs(offset)
                if al != 0 and al < v1._radius + v2._radius - 1:  # collision
                    if v1._type in VehicleType.WEAPONS and v2._type in VehicleType.TARGETS:
                        self._vehicles.remove(v2)
                        v1._coords = Point(int(v1._coords.x+offset.x/al*(v1._radius+v2._radius)), int(
                            v2._coords.y+offset.y/al*(v1._radius+v2._radius)))
                        v1._hasCollided = True
                        self._marks += 10
                        self._killedTargets += 1
                    elif v1._type in VehicleType.TARGETS and v2._type in VehicleType.WEAPONS:
                        self._vehicles.remove(v1)
                        v2._hasCollided = True
                        self._marks += 10
                        self._killedTargets += 1
                    elif v1._type in VehicleType.WEAPONS and v2._type in VehicleType.WEAPONS:
                        self._marks -= 20

    def updatePositions(self):
        for v in self._vehicles:
            v._age += 1
            if v._age == 50 and v._type in VehicleType.WEAPONS:
                self._vehicles.remove(v)
                self._marks -= 3
                continue
            v._speed = v._speed + v._Strength
            l = abs(v._speed)
            if l > v._maxSpeed:
                v._speed = v._speed * (v._maxSpeed / l)
            v._coords = Point(v._coords.x+int(v._speed.x),
                              v._coords.y+int(v._speed.y))

    def append(self, item):
        self._vehicles.append(item)

    def drawMe(self, screen, scene=None):
        for v in self._vehicles:
            v.drawMe(screen)


class Track:
    _circuit = None
    _cback = (128, 128, 128)
    _cfore = (10, 10, 10)
    _width = 20
    _screen = None
    _cachedLength = []
    _cachedNormals = []

    def __init__(self, screen):
        self._moving = False
        self._circuit = __circuit__.copy()
        self._screen = screen
        for i in range(0, len(self._circuit)):
            self._cachedNormals.append(
                self._circuit[i] - self._circuit[len(self._circuit)-1 if i-1 < 0 else i-1])
            self._cachedLength.append(
                abs(self._cachedNormals[i]))
            self._cachedNormals[i] = Point(
                self._cachedNormals[i].x/self._cachedLength[i], self._cachedNormals[i].y/self._cachedLength[i])

    def _segmentPointAddLength(self, segment, point, length):
        """
        Get the segment and point (on it) after adding length to the segment and point (on it),
        by following the path
        """
        nextStep = point.distance_to(self._circuit[segment])
        if nextStep > length:  # We stay on the same segment
            nextPoint = point + self._cachedNormals[segment] * length
            return (segment, Point(int(nextPoint.x), int(nextPoint.y)))
        length -= nextStep
        segment = segment+1 if segment+1 < len(self._circuit) else 0
        while length > self._cachedLength[segment]:
            length -= self._cachedLength[segment]
            segment = segment+1 if segment+1 < len(self._circuit) else 0
        nextPoint = self._circuit[segment-1 if segment > 0 else len(
            self._circuit)-1] + self._cachedNormals[segment] * length
        return (segment, Point(int(nextPoint.x), int(nextPoint.y)))

    def _closestSegmentPointToPoint(self, point):
        bestLength = None
        bestPoint = None
        bestSegment = None
        for i in range(0, len(self._circuit)):
            p = self._closestPointToSegment(i, point)
            l = p.distance_to(point)
            if bestLength is None or l < bestLength:
                bestLength = l
                bestPoint = p
                bestSegment = i
        return (bestSegment, bestPoint, bestLength)

    def _closestPointToSegment(self, numSegment, point):
        ''' Returns the closest point on the circuit segment from point'''
        p0 = self._circuit[len(self._circuit) -
                           1 if numSegment-1 < 0 else numSegment-1]
        p1 = self._circuit[numSegment]
        local = point - p0
        projection = local * self._cachedNormals[numSegment]
        if projection < 0:
            return p0
        if projection > self._cachedLength[numSegment]:
            return p1
        return p0 + self._cachedNormals[numSegment] * projection

    def drawMe(self, scene=None):

        for p in self._circuit:  # Draw simple inner joins
            pygame.draw.circle(self._screen, self._cback,
                               p.to_tuple(), int(self._width/2), 0)
        pygame.draw.lines(self._screen, self._cback, True,
                          tuple(map(Point.to_tuple, self._circuit)), self._width)
        # pygame.draw.lines(self._screen, self._cfore, True,
        #                  tuple(map(Point.to_tuple, self._circuit)), 1)

        if self._moving:
            to_move = random.randint(0, len(self._circuit)-1)
            self._circuit[to_move] += Point(random.randint(-1, 1),
                                            random.randint(-1, 1))
        # if True:
        # for i, p in enumerate(self._circuit):
        # pygame.draw.line(self._screen, (0, 0, 250), p.to_tuple(),
        #               (p + self._cachedNormals[i] * 50).to_tuple())


class Control:
    _screen = None

    def __init__(self, screen):
        self._screen = screen

    def drawMe(self, scene=None):
        margin = 10
        pygame.draw.rect(self._screen, (255, 255, 255), pygame.Rect(
            margin, __gameHeight__, __screenWidth__ - 2 * margin, __screenheight__ - __gameHeight__ - margin), 2)
        scene.drawText(
            f"Points : {scene._vehicles._marks} \t|\t Killed targets : {scene._vehicles._killedTargets} \t|\t Weapons used : {scene._vehicles._weaponsUsed}", (20, (__gameHeight__ + __screenheight__ - margin) / 2))


class Scene:
    _track = None
    _vehicles = None
    _control = None
    _screen = None
    _font = None

    _mouseCoords = Point(0, 0)

    def __init__(self, screenSize=__screenSize__):
        pygame.init()
        self._screen = pygame.display.set_mode(screenSize.to_tuple())
        self._track = Track(self._screen)
        self._vehicles = SetOfVehicles()
        self._control = Control(self._screen)
        self._font = pygame.font.SysFont("Arial", 20)

    def drawMe(self):
        self._screen.fill((0, 0, 0))
        self._track.drawMe(scene=self)
        self._vehicles.drawMe(self._screen, scene=self)
        self._control.drawMe(scene=self)

        # Illustrate the closestSegmentPointToPoint function
        (s, p, l) = self._track._closestSegmentPointToPoint(self._mouseCoords)
        pygame.draw.line(self._screen, (128, 255, 128),
                         p.to_tuple(), self._mouseCoords.to_tuple())
        # print(self._track._segmentPointAddLength(s,p,150))
        pygame.draw.circle(self._screen, (128, 255, 128),
                           self._track._segmentPointAddLength(s, p, 150)[1].to_tuple(), 20, 5)

        pygame.display.flip()

    def drawText(self, text, position, color=(255, 0, 127)):
        text = self._font.render(text, 1, color)
        text_rect = text.get_rect(center=(__screenWidth__/2, position[1]))
        self._screen.blit(text, text_rect)

    def update(self):
        for v in self._vehicles._vehicles:
            v.steerUpdate(self._track, self._vehicles)
        self._vehicles.updatePositions()
        self._vehicles.handleCollisions()
        self.drawMe()

    def eventClic(self, coord, b):
        self._vehicles.append(
            Vehicle(Point(coord[0], coord[1]),
                    color=random.choices(range(256), k=3), radius=random.randint(5, 15), type=0))
        self._vehicles._weaponsUsed += 1

    def recordMouseMove(self, coord):
        self._mouseCoords = Point(coord[0], coord[1])


def main():
    scene = Scene()
    done = False
    clock = pygame.time.Clock()
    ticks = 0
    while not done:
        if ticks % 40 == 0:
            scene._vehicles.append(Vehicle(Point(random.randint(0, __gameWidth__ - 1), random.randint(0, __gameHeight__ - 1)),
                                           color=random.choices(range(256), k=3), radius=random.randint(5, 15), type=random.randint(1, 2)))
        ticks += 1
        clock.tick(20)
        scene.update()
        scene.drawMe()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                # ================ My events ================
                if event.key == pygame.K_t:
                    scene._track._moving = not scene._track._moving
                if event.key == pygame.K_r:
                    scene._track._circuit = __circuit__.copy()
                # ================ My events ================

            if event.type == pygame.MOUSEBUTTONDOWN:
                scene.eventClic(event.dict['pos'], event.dict['button'])
            elif event.type == pygame.MOUSEMOTION:
                scene.recordMouseMove(event.dict['pos'])

    pygame.quit()


if not sys.flags.interactive:
    main()
