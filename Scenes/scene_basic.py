# scene_basic.py - Basic scene with simple shapes
from vector import Vector
from sphere import Sphere

def setup_scene(raster):
    """Set up a basic scene with simple shapes"""
    # Add a red cube
    raster.add_cube(Vector(0, 0, 200), 150, (200, 50, 50))
    
    # Add a green pyramid
    raster.add_pyramid(Vector(-200, 50, 200), 100, 150, (50, 200, 50))
    
    # Add a blue cylinder
    raster.add_cylinder(Vector(200, 0, 200), 60, 150, 16, (50, 50, 200))
    
    # Add a yellow sphere
    raster.add_object(Sphere(Vector(0, -150, 150), 80, (200, 200, 50)))