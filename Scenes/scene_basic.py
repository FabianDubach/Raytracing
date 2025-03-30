"""
scene_basic.py - Basic scene with a red cube and checkerboard floor
"""
from vector import Vector
from ray import Material

def setup_scene(raster):
    """Set up a basic scene with a red cube and checkerboard floor."""
    
    # Create materials
    red_material = Material((200, 50, 50))
    white_material = Material((240, 240, 240))
    gray_material = Material((120, 120, 120))
    blue_material = Material((50, 50, 200))
    glass_material = Material((255, 255, 255), reflectivity=0.1, transparency=0.9, refractive_index=1.5)
    
    # Add a red cube
    raster.add_cube(Vector(0, 0, 200), 100, red_material)
    
    # Add a blue sphere
    raster.add_sphere(Vector(-150, -30, 150), 70, blue_material)
    
    # Add a glass sphere
    raster.add_sphere(Vector(150, -30, 150), 70, glass_material)
    
    # Add a checkerboard floor
    raster.add_checkerboard(-100, 50, 20, white_material, gray_material)