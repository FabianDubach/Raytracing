class Light:
    def __init__(self, intensity=1.0, color=(255, 255, 255)):
        self.intensity = intensity
        self.color = color
    
    def get_direction(self, hit_point):
        raise NotImplementedError("Subclasses must implement get_direction")
    
    def get_distance(self, hit_point):
        raise NotImplementedError("Subclasses must implement get_distance")


class PointLight(Light):
    def __init__(self, position, intensity=1.0, color=(255, 255, 255)):
        super().__init__(intensity, color)
        self.position = position
    
    def get_direction(self, hit_point):
        return (self.position - hit_point).normalize()
    
    def get_distance(self, hit_point):
        return (self.position - hit_point).magnitude()


class DirectionalLight(Light):
    def __init__(self, direction, intensity=1.0, color=(255, 255, 255)):
        super().__init__(intensity, color)
        self.direction = direction.normalize() * -1
    
    def get_direction(self, hit_point):
        return self.direction
    
    def get_distance(self, hit_point):
        return float("inf")