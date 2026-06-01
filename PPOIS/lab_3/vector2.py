import math


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
