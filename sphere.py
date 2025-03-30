"""
sphere.py - Sphere object for ray tracing
"""
import math
from vector import Vector

class Sphere:
    """
    Sphere class representing a 3D sphere with intersection testing for ray tracing.
    """
    def __init__(self, center: Vector, radius: float, color: tuple):
        """
        Initialize a sphere.
        
        Args:
            center: Vector position of the sphere's center
            radius: Radius of the sphere
            color: RGB color tuple (r, g, b)
        """
        self.center = center
        self.radius = radius
        self.color = color

    def intersects(self, ray_origin, ray_direction):
        """
        Test if a ray intersects this sphere.
        
        Args:
            ray_origin: Vector origin of the ray
            ray_direction: Vector direction of the ray
            
        Returns:
            Distance to intersection point or None if no intersection
        """
        # Vector from ray origin to sphere center
        oc = ray_origin - self.center
        
        # Quadratic equation coefficients
        a = ray_direction.dot(ray_direction)
        b = 2.0 * oc.dot(ray_direction)
        c = oc.dot(oc) - self.radius ** 2
        discriminant = b * b - 4 * a * c

        # No intersection if discriminant is negative
        if discriminant < 0:
            return None

        # Compute nearest intersection distance
        t1 = (-b - math.sqrt(discriminant)) / (2.0 * a)
        t2 = (-b + math.sqrt(discriminant)) / (2.0 * a)
        
        # Return first positive intersection
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        return None

    def get_normal(self, point):
        """
        Get normal vector at a given point on the sphere surface.
        
        Args:
            point: Vector point on the sphere surface
            
        Returns:
            Normalized Vector perpendicular to the sphere at that point
        """
        return (point - self.center).normalize()