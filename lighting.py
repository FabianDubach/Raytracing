"""
lighting.py - Lighting classes for ray tracing
"""
from vector import Vector

class Light:
    """
    Base class for all lights in the ray tracing scene.
    """
    def __init__(self, intensity=1.0, color=(255, 255, 255)):
        """
        Initialize a light with intensity and color.
        
        Args:
            intensity: Light intensity as a scalar (default 1.0)
            color: RGB color tuple for the light (default white)
        """
        self.intensity = intensity
        self.color = color
    
    def get_direction(self, hit_point):
        """
        Get the light direction at a hit point.
        Must be implemented by subclasses.
        
        Args:
            hit_point: Vector position of the surface hit point
            
        Returns:
            Normalized direction Vector from hit point to light
        """
        raise NotImplementedError("Subclasses must implement get_direction")
    
    def get_distance(self, hit_point):
        """
        Get the distance from the hit point to the light.
        Must be implemented by subclasses.
        
        Args:
            hit_point: Vector position of the surface hit point
            
        Returns:
            Distance to the light
        """
        raise NotImplementedError("Subclasses must implement get_distance")


class PointLight(Light):
    """
    Point light that emits light in all directions from a single point.
    """
    def __init__(self, position, intensity=1.0, color=(255, 255, 255)):
        """
        Initialize a point light.
        
        Args:
            position: Vector position of the light
            intensity: Light intensity as a scalar (default 1.0)
            color: RGB color tuple for the light (default white)
        """
        super().__init__(intensity, color)
        self.position = position
    
    def get_direction(self, hit_point):
        """
        Get the light direction at a hit point.
        
        Args:
            hit_point: Vector position of the surface hit point
            
        Returns:
            Normalized direction Vector from hit point to light
        """
        return (self.position - hit_point).normalize()
    
    def get_distance(self, hit_point):
        """
        Get the distance from the hit point to the light.
        
        Args:
            hit_point: Vector position of the surface hit point
            
        Returns:
            Distance to the light
        """
        return (self.position - hit_point).magnitude()


class DirectionalLight(Light):
    """
    Directional light with parallel rays (like the sun).
    """
    def __init__(self, direction, intensity=1.0, color=(255, 255, 255)):
        """
        Initialize a directional light.
        
        Args:
            direction: Vector direction the light is coming from
            intensity: Light intensity as a scalar (default 1.0)
            color: RGB color tuple for the light (default white)
        """
        super().__init__(intensity, color)
        self.direction = direction.normalize() * -1  # Invert for light direction
    
    def get_direction(self, hit_point):
        """
        Get the light direction at a hit point.
        
        Args:
            hit_point: Vector position of the surface hit point
            
        Returns:
            Normalized direction Vector (constant for directional lights)
        """
        return self.direction
    
    def get_distance(self, hit_point):
        """
        Get the distance from the hit point to the light.
        
        Args:
            hit_point: Vector position of the surface hit point
            
        Returns:
            Always returns infinity for directional lights
        """
        return float("inf")