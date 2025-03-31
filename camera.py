"""
camera.py - Camera class for ray tracing
"""
import math
from vector import Vector

class Camera:
    """
    Camera class for generating rays based on pixel coordinates.
    """
    def __init__(self, position=None, look_at=None, up=None, fov=60, aspect_ratio=1.5):
        """
        Initialize a camera for ray tracing.
        
        Args:
            position: Vector position of the camera
            look_at: Vector position the camera is looking at
            up: Vector defining the up direction
            fov: Field of view in degrees
            aspect_ratio: Aspect ratio of the camera (width/height)
        """
        # Default camera setup
        self.position = position or Vector(0, 0, -500)
        self.look_at = look_at or Vector(0, 0, 0)
        self.up = up or Vector(0, 1, 0)
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        
        # Calculate camera basis vectors
        self._calculate_basis()
    
    def _calculate_basis(self):
        """
        Calculate the camera's basis vectors for ray generation.
        """
        # Calculate forward vector (z-axis)
        self.forward = (self.look_at - self.position).normalize()
        
        # Calculate right vector (x-axis)
        self.right = self.forward.cross(self.up).normalize()
        
        # Calculate true up vector (y-axis)
        self.true_up = self.right.cross(self.forward).normalize()
        
        # Calculate the image plane distance based on FOV
        self.image_distance = 1.0 / math.tan(math.radians(self.fov / 2))
    
    def get_ray(self, x, y, width, height):
        """
        Generate a ray for the given pixel coordinates.
        
        Args:
            x, y: Pixel coordinates
            width, height: Image dimensions
            
        Returns:
            Tuple of (ray_origin, ray_direction)
        """
        # Calculate normalized device coordinates
        ndc_x = (2.0 * x / width - 1.0) * self.aspect_ratio
        ndc_y = 1.0 - 2.0 * y / height
        
        # Calculate ray direction
        ray_direction = (self.forward * self.image_distance + 
                         self.right * ndc_x + 
                         self.true_up * ndc_y).normalize()
        
        return self.position, ray_direction
    
    def get_simple_ray(self, x, y, width, height):
        """
        Generate a simple ray for the given pixel coordinates using the default
        straight-ahead camera model (compatible with original implementation).
        
        Args:
            x, y: Pixel coordinates
            width, height: Image dimensions
            
        Returns:
            Tuple of (ray_origin, ray_direction)
        """
        ray_origin = Vector(x - width / 2, y - height / 2, -500)
        ray_direction = Vector(0, 0, 1).normalize()
        
        return ray_origin, ray_direction