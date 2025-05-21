import math
from vector import Vector

class Sphere:
    def __init__(self, center: Vector, radius: float, color: tuple):
        self.center = center
        self.radius = radius
        self.color = color

    def intersects(self, ray_origin, ray_direction):
        oc = ray_origin - self.center
        
        a = ray_direction.dot(ray_direction)
        b = 2.0 * oc.dot(ray_direction)
        c = oc.dot(oc) - self.radius ** 2
        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return None

        t1 = (-b - math.sqrt(discriminant)) / (2.0 * a)
        t2 = (-b + math.sqrt(discriminant)) / (2.0 * a)
        
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        return None

    def get_normal(self, point):
        return (point - self.center).normalize()