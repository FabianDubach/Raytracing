import math
from vector import Vector

class Camera:

    def __init__(self, position=None, look_at=None, up=None, fov=60, aspect_ratio=1.5):
        self.position = position or Vector(0, 0, -500)
        self.look_at = look_at or Vector(0, 0, 0)
        self.up = up or Vector(0, 1, 0)
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        
        self._calculate_basis()
    
    def _calculate_basis(self):
        self.forward = (self.look_at - self.position).normalize()
        self.right = self.forward.cross(self.up).normalize()
        self.true_up = self.right.cross(self.forward).normalize()
        self.image_distance = 1.0 / math.tan(math.radians(self.fov / 2))
    
    def get_ray(self, x, y, width, height):
        ndc_x = (2.0 * x / width - 1.0) * self.aspect_ratio
        ndc_y = 1.0 - 2.0 * y / height
        ray_direction = (self.forward * self.image_distance + 
                         self.right * ndc_x + 
                         self.true_up * ndc_y).normalize()
        
        return self.position, ray_direction
    
    def get_simple_ray(self, x, y, width, height):
        ray_origin = Vector(x - width / 2, y - height / 2, -500)
        ray_direction = Vector(0, 0, 1).normalize()

        return ray_origin, ray_direction