# scene_lens.py - A scene demonstrating lens effects with transparent materials
import math
from vector import Vector
from main import Material

def setup_scene(raster):
    """Create a scene showcasing lens effects with glass spheres"""
    # Create materials
    materials = {
        'white': Material((255, 255, 255)),
        'black': Material((0, 0, 0)),
        'red': Material((255, 50, 50)),
        'green': Material((50, 255, 50)),
        'blue': Material((50, 50, 255)),
        'yellow': Material((255, 255, 50)),
        
        # Transparent materials
        'glass': Material((255, 255, 255), reflectivity=0.1, transparency=0.9, refractive_index=1.5),
        'water': Material((200, 230, 255), reflectivity=0.1, transparency=0.9, refractive_index=1.33),
        'diamond': Material((255, 255, 255), reflectivity=0.1, transparency=0.9, refractive_index=2.42),
    }
    
    # Create a checkered background wall
    checker_size = 40
    wall_z = 800
    for row in range(-8, 8):
        for col in range(-10, 10):
            is_white = (row + col) % 2 == 0
            checker_material = materials['white'] if is_white else materials['black']
            
            # Position of this checker on the back wall
            x1 = col * checker_size
            x2 = (col + 1) * checker_size
            y1 = row * checker_size
            y2 = (row + 1) * checker_size
            
            # Create two triangles for this checker
            raster.add_triangle(
                Vector(x1, y1, wall_z),
                Vector(x2, y1, wall_z),
                Vector(x2, y2, wall_z),
                checker_material
            )
            raster.add_triangle(
                Vector(x1, y1, wall_z),
                Vector(x2, y2, wall_z),
                Vector(x1, y2, wall_z),
                checker_material
            )
    
    # Create a striped floor
    floor_y = 100
    for i in range(-20, 20):
        stripe_material = materials['white'] if i % 2 == 0 else materials['black']
        z = i * checker_size + 400
        
        raster.add_triangle(
            Vector(-600, floor_y, z),
            Vector(600, floor_y, z),
            Vector(600, floor_y, z + checker_size),
            stripe_material
        )
        raster.add_triangle(
            Vector(-600, floor_y, z),
            Vector(600, floor_y, z + checker_size),
            Vector(-600, floor_y, z + checker_size),
            stripe_material
        )
    
    # Create small colored spheres in the background (to be viewed through the lens)
    small_sphere_positions = [
        (Vector(-80, 0, 600), 20, materials['red']),
        (Vector(-40, 0, 600), 20, materials['green']),
        (Vector(0, 0, 600), 20, materials['blue']),
        (Vector(40, 0, 600), 20, materials['yellow']),
        (Vector(80, 0, 600), 20, materials['red']),
    ]
    
    for pos, size, material in small_sphere_positions:
        raster.add_sphere(pos, size, material)
    
    # Add large glass spheres acting as lenses
    # The first glass sphere will magnify objects behind it
    raster.add_sphere(Vector(0, 0, 300), 100, materials['glass'])
    
    # Add a diamond sphere that will have stronger refraction
    raster.add_sphere(Vector(-200, 0, 200), 70, materials['diamond'])
    
    # Add a water sphere with weaker refraction
    raster.add_sphere(Vector(200, 0, 200), 70, materials['water'])
    
    # Add some spheres on the side that aren't being viewed through lenses
    raster.add_sphere(Vector(-350, 0, 400), 50, materials['red'])
    raster.add_sphere(Vector(350, 0, 400), 50, materials['blue'])
    
    # Add a floating reflective sphere to show reflections
    raster.add_sphere(Vector(0, -150, 150), 40, Material((220, 220, 220), reflectivity=0.8))