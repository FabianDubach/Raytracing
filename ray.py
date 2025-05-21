import math

class Ray:
    @staticmethod
    def cast_ray(objects, ray_origin, ray_direction, max_distance=float("inf"), ignore_object=None):
        closest_t = float("inf")
        closest_obj = None

        for obj in objects:
            if obj == ignore_object:
                continue
            
            t = obj.intersects(ray_origin, ray_direction)
            
            if t and t < closest_t and t < max_distance:
                closest_t = t
                closest_obj = obj

        return closest_obj, closest_t


class Material:
    def __init__(self, color, reflectivity=0.0, transparency=0.0, refractive_index=1.0):
        self.color = color
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.refractive_index = refractive_index

        if self.reflectivity + self.transparency > 1.0:
            total = self.reflectivity + self.transparency
            self.reflectivity /= total
            self.transparency /= total


class EnhancedSphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material
        self.color = material.color

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
    
    def get_material(self):
        return self.material


class EnhancedTriangle:
    def __init__(self, v0, v1, v2, material):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        self.color = material.color

        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = edge1.cross(edge2).normalize()
    
    def intersects(self, ray_origin, ray_direction):
        EPSILON = 0.0000001
        
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        h = ray_direction.cross(edge2)
        a = edge1.dot(h)
        
        if -EPSILON < a < EPSILON:
            return None
        
        f = 1.0 / a
        s = ray_origin - self.v0
        u = f * s.dot(h)
        
        if u < 0.0 or u > 1.0:
            return None
        
        q = s.cross(edge1)
        v = f * ray_direction.dot(q)

        if v < 0.0 or u + v > 1.0:
            return None

        t = f * edge2.dot(q)
        
        if t > EPSILON:
            return t

        return None
    
    def get_normal(self, _):
        return self.normal
    
    def get_material(self):
        return self.material