from vector import Vector
from lighting import PointLight, DirectionalLight
from ray import Material, EnhancedTriangle
from font_renderer import FontRenderer
from materials import create_standard_materials
from triangle import Triangle

def setup_scene(renderer):
    """
    Set up an enhanced 3D scene with multiple spheres, text elements, and improved lighting
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
    
    # Create custom materials for additional elements
    diamond_blue = Material((100, 150, 255), reflectivity=0.2, transparency=0.8, refractive_index=2.4)
    green_metal = Material((50, 200, 100), reflectivity=0.6)
    gold = Material((255, 215, 0), reflectivity=0.7)
    
    # Create the room walls using triangles
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
    renderer.add_triangle(fl_bl, fl_br, fl_tr, materials['mirror'])
    renderer.add_triangle(fl_bl, fl_tr, fl_tl, materials['mirror'])
    
    # Add ceiling triangles
    renderer.add_triangle(cl_bl, cl_tr, cl_br, materials['mirror'])
    renderer.add_triangle(cl_bl, cl_tl, cl_tr, materials['mirror'])
    
    # Back wall
    renderer.add_triangle(fl_tl, fl_tr, cl_tr, materials['mirror'])
    renderer.add_triangle(fl_tl, cl_tr, cl_tl, materials['mirror'])
    
    # Left wall
    renderer.add_triangle(fl_bl, fl_tl, cl_tl, materials['mirror'])
    renderer.add_triangle(fl_bl, cl_tl, cl_bl, materials['mirror'])
    
    # Right wall
    renderer.add_triangle(fl_br, cl_br, cl_tr, materials['mirror'])
    renderer.add_triangle(fl_br, cl_tr, fl_tr, materials['mirror'])
    
    # Add lights that are positioned entirely within the scene
    # Main central light
    renderer.add_light(PointLight(Vector(0, -100, 0), intensity=0.6))
    # Corner lights
    renderer.add_light(PointLight(Vector(-200, -100, -200), intensity=0.4))
    renderer.add_light(PointLight(Vector(200, -100, -200), intensity=0.4))
    # Backlights for the text
    renderer.add_light(PointLight(Vector(0, 0, 300), intensity=0.3))
    
    # Set ambient light
    renderer.set_ambient_light(0.2)
    
    # Create a font renderer
    font_renderer = FontRenderer("arial.ttf", size=36, depth=10)
    
    # Add main "RAYTRACING" text in the background
    try:
        main_text_triangles = font_renderer.text_to_triangles_contour(
            "RAYTRACING", 
            position=Vector(0, 0, 250),
            material=materials['red'],
            scale=1.0,
            rotation=(0, 180, 0),
            detail_level=0.8
        )
    except (AttributeError, NameError):
        main_text_triangles = font_renderer.text_to_triangles(
            "RAYTRACING", 
            position=Vector(0, 0, 250),
            material=materials['red'],
            scale=1.0,
            rotation=(0, 180, 0)
        )
    
    renderer.add_objects(main_text_triangles)
    
    # Add the main crystal clear glass sphere (as before)
    renderer.add_sphere(
        center=Vector(0, 0, 50),
        radius=60,
        material=materials['glass']
    )
    
    # Add a smaller blue diamond sphere on the right
    renderer.add_sphere(
        center=Vector(120, 30, 100),
        radius=30,
        material=diamond_blue
    )
    
    # Add a metallic green sphere on the left
    renderer.add_sphere(
        center=Vector(-120, -20, 120),
        radius=40,
        material=green_metal
    )
    
    # Add a golden reflective sphere at the bottom
    renderer.add_sphere(
        center=Vector(0, 80, 150),
        radius=25,
        material=gold
    )
    
    # Add a chrome sphere near the top
    renderer.add_sphere(
        center=Vector(-30, -70, 100),
        radius=20,
        material=materials['chrome']
    )
    
    # Add a small ruby sphere
    renderer.add_sphere(
        center=Vector(100, -80, 170),
        radius=15,
        material=materials['ruby']
    )
    
    print("Enhanced scene setup complete with multiple spheres and text elements")