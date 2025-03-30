"""
ray.py - Ray class and material definitions for ray tracing
"""
from vector import Vector
import math

class Ray:
    """
    Ray class with intersection testing for ray tracing.
    """
    @staticmethod
    def cast_ray(objects, ray_origin, ray_direction, max_distance=float("inf"), ignore_object=None):
        """
        Cast a ray and find closest object intersection.
        
        Args:
            objects: List of renderable objects
            ray_origin: Vector origin of the ray
            ray_direction: Vector direction of the ray
            max_distance: Maximum distance to check (for shadow rays)
            ignore_object: Object to ignore (for reflection rays to avoid self-intersection)
            
        Returns:
            Tuple of (closest_object, distance) or (None, None) if no intersection
        """
        closest_t = float("inf")
        closest_obj = None

        for obj in objects:
            # Skip the object we're ignoring (if specified)
            if obj == ignore_object:
                continue
            
            # Test intersection
            t = obj.intersects(ray_origin, ray_direction)
            
            # If there's an intersection and it's closer than any previous one
            if t and t < closest_t and t < max_distance:
                closest_t = t
                closest_obj = obj

        return closest_obj, closest_t


class Material:
    """
    Material class defining optical properties for ray tracing.
    """
    def __init__(self, color, reflectivity=0.0, transparency=0.0, refractive_index=1.0):
        """
        Initialize a material with color and optical properties.
        
        Args:
            color: RGB color tuple (r, g, b)
            reflectivity: 0.0-1.0, how reflective the material is
            transparency: 0.0-1.0, how transparent the material is
            refractive_index: Refractive index for transparent materials 
                              (1.0 for air, 1.5 for glass)
        """
        self.color = color
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.refractive_index = refractive_index
        
        # Ensure reflectivity + transparency <= 1.0
        if self.reflectivity + self.transparency > 1.0:
            total = self.reflectivity + self.transparency
            self.reflectivity /= total
            self.transparency /= total


class EnhancedSphere:
    """
    Enhanced sphere with material properties for ray tracing.
    """
    def __init__(self, center, radius, material):
        """
        Initialize a sphere with material properties.
        
        Args:
            center: Vector position of the sphere's center
            radius: Radius of the sphere
            material: Material object defining the sphere's optical properties
        """
        self.center = center
        self.radius = radius
        self.material = material
        # For compatibility with original methods
        self.color = material.color

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
    
    def get_material(self):
        """
        Get the material of this sphere.
        
        Returns:
            Material object
        """
        return self.material


class EnhancedTriangle:
    """
    Enhanced triangle with material properties for ray tracing.
    """
    def __init__(self, v0, v1, v2, material):
        """
        Initialize a triangle with material properties.
        
        Args:
            v0, v1, v2: Vector vertices of the triangle
            material: Material object defining the triangle's optical properties
        """
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        # For compatibility with original methods
        self.color = material.color
        
        # Pre-compute the normal vector
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = edge1.cross(edge2).normalize()
    
    def intersects(self, ray_origin, ray_direction):
        """
        Test if a ray intersects this triangle.
        
        Args:
            ray_origin: Vector origin of the ray
            ray_direction: Vector direction of the ray
            
        Returns:
            Distance to intersection point or None if no intersection
        """
        EPSILON = 0.0000001
        
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        h = ray_direction.cross(edge2)
        a = edge1.dot(h)
        
        # Ray is parallel to the triangle
        if -EPSILON < a < EPSILON:
            return None
        
        f = 1.0 / a
        s = ray_origin - self.v0
        u = f * s.dot(h)
        
        # Ray doesn't intersect the triangle
        if u < 0.0 or u > 1.0:
            return None
        
        q = s.cross(edge1)
        v = f * ray_direction.dot(q)
        
        # Ray doesn't intersect the triangle
        if v < 0.0 or u + v > 1.0:
            return None
        
        # Compute the intersection distance
        t = f * edge2.dot(q)
        
        if t > EPSILON:
            return t
        
        # No intersection or behind the ray
        return None
    
    def get_normal(self, _):
        """
        Get normal vector for the triangle.
        
        Returns:
            Normalized Vector perpendicular to the triangle
        """
        return self.normal
    
    def get_material(self):
        """
        Get the material of this triangle.
        
        Returns:
            Material object
        """
        return self.material