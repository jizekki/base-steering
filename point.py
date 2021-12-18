import math


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def __repr__(self):
        return repr((self.x, self.y))

    def dot(self, other):
        if not isinstance(other, Point):
            raise TypeError(
                'Can only take dot product of two Point objects')
        return self.x * other.x + self.y * other.y
    __matmul__ = dot

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, element):
        if isinstance(element, int) or isinstance(element, float):
            return Point(self.x * element, self.y * element)
        elif isinstance(element, Point):
            return self.x * element.x + self.y * element.y
        raise NotImplementedError('Can only multiply Point by a scalar')

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, other):
        return abs(self - other)

    def to_tuple(self):
        return (self.x, self.y)
