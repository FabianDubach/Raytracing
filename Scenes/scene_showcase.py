# scene_checkerboard.py - A scene with a checkerboard floor and colorful spheres
# Compatible with the original Main class
import math
from vector import Vector
from sphere import Sphere
from triangle import Triangle

def setup_scene(raster):
    """
    Set up a scene with a checkerboard floor and colorful spheres
    Compatible with the original Main class
    """
    # Create a checkerboard floor using triangles
    checker_size = 100
    floor_z = 200  # Center of the floor in z direction
    floor_width = 10  # Number of checkers in each direction
    
    for row in range(-floor_width, floor_width):
        for col in range(-floor_width, floor_width):
            # Determine if this is a white or black checker
            is_white = (row + col) % 2 == 0
            checker_color = (255, 255, 255) if is_white else (0, 0, 0)
            
            # Calculate corners of this checker
            x1 = col * checker_size
            x2 = (col + 1) * checker_size
            z1 = floor_z + row * checker_size
            z2 = floor_z + (row + 1) * checker_size
            
            # Create two triangles for this checker
            checker = [
                Triangle(Vector(x1, 100, z1), Vector(x2, 100, z1), Vector(x2, 100, z2), checker_color),
                Triangle(Vector(x1, 100, z1), Vector(x2, 100, z2), Vector(x1, 100, z2), checker_color)
            ]
            
            raster.add_objects(checker)
    
    # Add colorful spheres
    raster.add_object(Sphere(Vector(-250, 20, 200), 80, (255, 50, 50)))  # Red
    raster.add_object(Sphere(Vector(0, 20, 400), 100, (255, 255, 50)))   # Yellow
    raster.add_object(Sphere(Vector(250, 20, 200), 80, (50, 50, 255)))   # Blue
    raster.add_object(Sphere(Vector(-150, 20, 600), 80, (50, 255, 50)))  # Green
    raster.add_object(Sphere(Vector(150, 20, 600), 80, (50, 50, 255)))   # Blue
    
    # Add more spheres at different heights
    raster.add_object(Sphere(Vector(0, 100, 200), 60, (220, 220, 220)))  # Silver
    
    # Add some smaller spheres
    small_spheres = [
        (Vector(-400, 50, 300), 30, (255, 50, 50)),    # Red
        (Vector(400, 50, 300), 30, (50, 255, 50)),     # Green
        (Vector(-300, 50, 500), 30, (50, 50, 255)),    # Blue
        (Vector(300, 50, 500), 30, (255, 255, 50))     # Yellow
    ]
    
    for pos, size, color in small_spheres:
        raster.add_object(Sphere(pos, size, color))