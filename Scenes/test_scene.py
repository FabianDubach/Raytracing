from vector import Vector
from materials import create_standard_materials
from lighting import DirectionalLight
from scene_utils import create_rotated_shape

def setup_scene(raster):
    # Create materials
    materials = create_standard_materials()

    # Add checkerboard floor
    floor_y = -100
    checker_size = 500
    checker_count = 2
    
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
            
            
            # Add reverse-facing triangles
            raster.add_triangle(Vector(x1, floor_y, z1), Vector(x2, floor_y, z2), Vector(x2, floor_y, z1), material)
            raster.add_triangle(Vector(x1, floor_y, z1), Vector(x1, floor_y, z2), Vector(x2, floor_y, z2), material)
    
    # Create a large red sphere
    raster.add_sphere(Vector(0, 0, 200), 200, materials['red'])
    
    # Add a rotated cube in the middle of the scene    
    cube_center = Vector(-120, 100, 50)
    cube_size = 50
    rotation = (-10, 30, 45)
    rotated_triangles = create_rotated_shape("cube", cube_center, cube_size, rotation, materials['red'].color)
    for triangle in rotated_triangles:
        raster.add_triangle(triangle.v0, triangle.v1, triangle.v2, materials['red'])
    
    # Clear default lights
    raster.clear_lights()
    
    # Add multiple lights to ensure good coverage
    raster.add_light(DirectionalLight(
        direction=Vector(0.5, -1, 0.2).normalize(),
        intensity=0.7
    ))
    raster.add_light(DirectionalLight(
        direction=Vector(-0.5, -1, -0.2).normalize(),
        intensity=0.3
    ))
    
    # Set up ambient light
    raster.set_ambient_light(0.2)
    
    # Set up a camera to view the spheres clearly
    raster.set_camera(
        position=Vector(0, 200, -600),  # Higher and further back for better view
        look_at=Vector(0, 0, 200),      # Looking at the center of the large sphere
        fov=45                          # Narrower field of view for less distortion
    )