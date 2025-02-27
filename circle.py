from vector import Vector

class Circle:
    def __init__(self, center: Vector, radius: float, color: str):
        self.center = center
        self.radius = radius
        self.color = color

    def includes(self, point: Vector):
        return bool(self.center.distance(point) <= self.radius)
    
    def get_color(self):
        return str(self.color)