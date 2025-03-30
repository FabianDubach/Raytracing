# scene_realistic.py - A realistic scene mimicking the reference image
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
    
    # Create a checkerboard floor (large squares)
    raster.add_checkerboard(100, 100, 10, materials['white'], materials['black'])
    
    # Add a row of spheres near the back
    sphere_positions = [
        (Vector(-300, 30, 500), 60, materials['red']),
        (Vector(-100, 30, 500), 60, materials['green']),
        (Vector(100, 30, 500), 60, materials['blue']),
        (Vector(300, 30, 500), 60, materials['yellow'])
    ]
    
    for pos, size, material in sphere_positions:
        raster.add_sphere(pos, size, material)
    
    # Add large spheres near the middle
    raster.add_sphere(Vector(-200, 50, 250), 80, materials['red'])
    raster.add_sphere(Vector(0, 60, 300), 100, materials['yellow'])
    raster.add_sphere(Vector(200, 50, 250), 80, materials['blue'])
    
    # Add a glass sphere in the center
    raster.add_sphere(Vector(0, 60, 150), 70, materials['glass'])
    
    # Add a mirror sphere
    raster.add_sphere(Vector(-300, 40, 100), 60, materials['mirror'])
    
    # Add small colored spheres in the front
    small_spheres = [
        (Vector(-150, 25, 50), 35, materials['green']),
        (Vector(0, 25, 0), 35, materials['red']),
        (Vector(150, 25, 50), 35, materials['blue'])
    ]
    
    for pos, size, material in small_spheres:
        raster.add_sphere(pos, size, material)