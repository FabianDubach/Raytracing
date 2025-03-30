# scene_realistic_fixed.py - A fixed realistic scene with a clearly visible floor
import math
from vector import Vector
from main import Material

def setup_scene(raster):
    """Create a realistic scene with checkerboard floor, reflections and glass spheres"""
    # Create materials
    materials = {
        'white': Material((255, 255, 255)),
        'black': Material((0, 0, 0)),
        'red': Material((255, 50, 50), reflectivity=0.2),
        'green': Material((50, 255, 50), reflectivity=0.2),
        'blue': Material((50, 50, 255), reflectivity=0.2),
        'yellow': Material((255, 255, 50), reflectivity=0.2),
        'mirror': Material((220, 220, 220), reflectivity=0.9),
        'glass': Material((255, 255, 255), reflectivity=0.1, transparency=0.9, refractive_index=1.5)
    }
    
    # FIXED: Create a checkerboard floor that's more visible from the camera
    # Move the floor forward and adjust the height to be more visible
    floor_y = 0  # Bring the floor to the base level
    checker_size = 50  # Smaller checker size for more detail
    checker_count = 20  # More checkers to cover a larger area

    for row in range(-checker_count, checker_count):
        for col in range(-checker_count, checker_count):
            is_white = (row + col) % 2 == 0
            material = materials['white'] if is_white else materials['black']
            
            x1 = col * checker_size
            x2 = (col + 1) * checker_size
            z1 = row * checker_size  # Removed the +0
            z2 = (row + 1) * checker_size
            
            # Create the checkerboard triangles
            raster.add_triangle(Vector(x1, floor_y, z1), Vector(x2, floor_y, z1), Vector(x2, floor_y, z2), material)
            raster.add_triangle(Vector(x1, floor_y, z1), Vector(x2, floor_y, z2), Vector(x1, floor_y, z2), material)
    
    # Adjust sphere positions to be above the floor
    sphere_height = 50  # Height above the floor
    base_y = floor_y - sphere_height  # Position spheres above the floor
    
    # Add large spheres
    raster.add_sphere(Vector(-200, base_y, 250), 80, materials['red'])
    raster.add_sphere(Vector(0, base_y - 10, 300), 100, materials['yellow'])  # Larger yellow sphere slightly lower
    raster.add_sphere(Vector(200, base_y, 250), 80, materials['blue'])
    
    # Add a glass sphere in the center
    raster.add_sphere(Vector(0, base_y, 150), 70, materials['glass'])
    
    # Add a mirror sphere
    raster.add_sphere(Vector(-300, base_y, 100), 60, materials['mirror'])
    
    # Add small colored spheres in the front
    small_spheres = [
        (Vector(-150, base_y + 25, 50), 35, materials['green']),
        (Vector(0, base_y + 25, 0), 35, materials['red']),
        (Vector(150, base_y + 25, 50), 35, materials['blue'])
    ]
    
    for pos, size, material in small_spheres:
        raster.add_sphere(pos, size, material)