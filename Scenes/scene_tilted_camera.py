"""
scene_tilted_camera.py - Example scene with tilted camera to see the floor better
"""
from vector import Vector
from materials import create_standard_materials
from lighting import PointLight, DirectionalLight
from scene_utils import create_rotated_shape

def setup_scene(raster):
    """
    Create a scene with a tilted camera that can see the floor properly.
    
    Args:
        raster: Renderer instance to set up
    """
    # Create materials
    materials = create_standard_materials()
    
    # Add checkerboard floor
    floor_y = 0
    checker_size = 100
    checker_count = 15
    
    # Add checkerboard floor
    for row in range(-checker_count, checker_count):
        for col in range(-checker_count, checker_count):
            # Skip some squares that are far from center for better performance
            if abs(row) > 8 and abs(col) > 8:
                continue
                
            is_white = (row + col) % 2 == 0
            material = materials['black'] if is_white else materials['white']
            
            x1 = col * checker_size
            x2 = (col + 1) * checker_size
            z1 = row * checker_size
            z2 = (row + 1) * checker_size
            
            # Create the checkerboard triangles
            raster.add_triangle(Vector(x1, floor_y, z1), Vector(x2, floor_y, z1), Vector(x2, floor_y, z2), material)
            raster.add_triangle(Vector(x1, floor_y, z1), Vector(x2, floor_y, z2), Vector(x1, floor_y, z2), material)
    
    # Rearranged colored spheres in a triangle formation
    # Yellow sphere (left front)
    raster.add_sphere(Vector(-160, 90, 10), 80, materials['yellow'])
    
    # Green sphere (right front)
    raster.add_sphere(Vector(180, 100, 80), 70, materials['green'])
    
    # Blue sphere (back center)
    raster.add_sphere(Vector(40, 200, 300), 150, materials['blue'])
    
    # Glass sphere (center with slight offset)
    raster.add_sphere(Vector(250, 120, 20), 60, materials['glass'])
    
    # Water sphere (right side)
    raster.add_sphere(Vector(-30, 80, 130), 65, materials['water'])

    # Red sphere (right front)
    raster.add_sphere(Vector(200, 40, 0), 40, materials['red'])
    
    # Add a rotated cube in the middle of the scene    
    cube_center = Vector(50, 50, 80)  # Positioned in the middle area
    cube_size = 80  # Size of the cube
    rotation = (-10, 30, 45)  # (x_angle, y_angle, z_angle) in degrees
    rotated_triangles = create_rotated_shape("cube", cube_center, cube_size, rotation, materials['mirror'].color)
    for triangle in rotated_triangles:
        raster.add_triangle(triangle.v0, triangle.v1, triangle.v2, materials['mirror'])

    # Add big Pyramid in the background
    pyramid_center = Vector(-400, 0, 200)  # Positioned in the back
    pyramid_base_size = 220  # Size of the square base
    rotation = (180, 30, 0)
    pyramid_triangles = create_rotated_shape("pyramid", pyramid_center, pyramid_base_size, rotation, materials['mirror'].color)
    for triangle in pyramid_triangles:
        raster.add_triangle(triangle.v0, triangle.v1, triangle.v2, materials['mirror'])

    # Add cylinder
    cylinder_center = Vector(500, 0, 220)
    radius = 100
    height = 600
    segments = 100  # Higher number means smoother cylinder
    raster.add_cylinder(cylinder_center, radius, height, segments, materials['chrome'])

    # Clear default lights
    raster.clear_lights()
    
    # Set ambient light
    raster.set_ambient_light(0.2)
    
    # Add key light (main illumination)
    raster.add_light(PointLight(
        position=Vector(-400, -400, -300),
        intensity=0.8
    ))
    
    # Add fill light (softer light from opposite side)
    raster.add_light(PointLight(
        position=Vector(400, -300, -200),
        intensity=0.4
    ))
    
    # Add rim light (creates highlights on edges)
    raster.add_light(PointLight(
        position=Vector(0, -200, -400),
        intensity=0.3
    ))
    
    # Add a directional light (like sunlight)
    raster.add_light(DirectionalLight(
        direction=Vector(0.5, -1, 0.2).normalize(),
        intensity=0.5
    ))
    
    # Set up a tilted camera that can see the floor
    raster.set_camera(
        position=Vector(0, 150, -500),  # Higher position
        look_at=Vector(0, 50, 200),     # Looking down at the scene
        fov=50                          # Narrower field of view for less distortion
    )