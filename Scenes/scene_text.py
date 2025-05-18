from vector import Vector
from lighting import PointLight, DirectionalLight
from ray import Material, EnhancedTriangle
from font_renderer import FontRenderer
from materials import create_standard_materials
from triangle import Triangle

def setup_scene(renderer):
    """
    Set up a 3D text rendering scene with a room, glass sphere, and text behind it
    """
    # Create a room that's open on the camera side
    room_width = 500
    room_height = 300
    room_depth = 600
    
    # Set up camera
    renderer.set_camera(
        position=Vector(0, 0, -400),
        look_at=Vector(0, 0, 100),
        fov=45
    )
    
    # Get standard materials
    materials = create_standard_materials()
    
    # Create the room walls using triangles
    
    # Define the coordinates of the room
    half_width = room_width / 2
    half_height = room_height / 2
    half_depth = room_depth / 2
    
    # Floor vertices (y is constant)
    fl_bl = Vector(-half_width, half_height, -half_depth)  # bottom left
    fl_br = Vector(half_width, half_height, -half_depth)   # bottom right
    fl_tr = Vector(half_width, half_height, half_depth)    # top right
    fl_tl = Vector(-half_width, half_height, half_depth)   # top left
    
    # Ceiling vertices (y is constant)
    cl_bl = Vector(-half_width, -half_height, -half_depth)
    cl_br = Vector(half_width, -half_height, -half_depth)
    cl_tr = Vector(half_width, -half_height, half_depth)
    cl_tl = Vector(-half_width, -half_height, half_depth)
    
    # Add floor triangles
    renderer.add_triangle(fl_bl, fl_br, fl_tr, materials['white'])
    renderer.add_triangle(fl_bl, fl_tr, fl_tl, materials['white'])
    
    # Add ceiling triangles
    renderer.add_triangle(cl_bl, cl_tr, cl_br, materials['white'])
    renderer.add_triangle(cl_bl, cl_tl, cl_tr, materials['white'])
    
    # Back wall
    renderer.add_triangle(fl_tl, fl_tr, cl_tr, materials['white'])
    renderer.add_triangle(fl_tl, cl_tr, cl_tl, materials['white'])
    
    # Left wall
    renderer.add_triangle(fl_bl, fl_tl, cl_tl, materials['white'])
    renderer.add_triangle(fl_bl, cl_tl, cl_bl, materials['white'])
    
    # Right wall
    renderer.add_triangle(fl_br, cl_br, cl_tr, materials['white'])
    renderer.add_triangle(fl_br, cl_tr, fl_tr, materials['white'])
    
    # Add better lighting - more lights from different directions
    renderer.add_light(PointLight(Vector(-200, -150, -300), intensity=0.5))
    renderer.add_light(PointLight(Vector(200, -150, -300), intensity=0.5))
    renderer.add_light(PointLight(Vector(0, -200, 100), intensity=0.3))
    
    # Set ambient light slightly higher
    renderer.set_ambient_light(0.3)
    
    # Create a font renderer
    font_renderer = FontRenderer("arial.ttf", size=36, depth=10)
    
    # Add 3D text to the scene - positioned BEHIND the glass sphere
    main_text = "RAYTRACING"
    
    try:
        text_triangles = font_renderer.text_to_triangles_contour(
            main_text, 
            position=Vector(0, 0, 250),         # Place well behind the sphere
            material=materials['red'],          # Use red material for visibility
            scale=1.5,                          # Larger text
            rotation=(0, 180, 0),                 # No rotation needed
            detail_level=0.8                    # Higher detail
        )
    except (AttributeError, NameError):
        text_triangles = font_renderer.text_to_triangles(
            main_text, 
            position=Vector(0, 0, 200),         # Place well behind the sphere
            material=materials['red'],          # Use red material for visibility
            scale=1.5,                          # Larger text
            rotation=(0, 180, 0)                  # No rotation needed
        )
    
    renderer.add_objects(text_triangles)
    
    # Add the crystal clear glass sphere in front of the text
    renderer.add_sphere(
        center=Vector(0, 0, 50),        # Closer to the camera
        radius=80,                      # Slightly smaller
        material=materials['glass']     # Use transparent glass
    )
    
    print("Scene setup complete with", len(text_triangles), "triangles for text")