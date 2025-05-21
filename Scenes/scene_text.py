from vector import Vector
from lighting import PointLight, DirectionalLight
from ray import Material, EnhancedTriangle
from font_renderer import FontRenderer
from materials import create_standard_materials
from triangle import Triangle

def setup_scene(renderer):
    room_width = 500
    room_height = 300
    room_depth = 600
    
    renderer.set_camera(
    position=Vector(0, 0, -400),
    look_at=Vector(0, 0, 100),
    fov=45
    )

    materials = create_standard_materials()

    half_width = room_width / 2
    half_height = room_height / 2
    half_depth = room_depth / 2

    fl_bl = Vector(-half_width, half_height, -half_depth)
    fl_br = Vector(half_width, half_height, -half_depth)
    fl_tr = Vector(half_width, half_height, half_depth)
    fl_tl = Vector(-half_width, half_height, half_depth)

    cl_bl = Vector(-half_width, -half_height, -half_depth)
    cl_br = Vector(half_width, -half_height, -half_depth)
    cl_tr = Vector(half_width, -half_height, half_depth)
    cl_tl = Vector(-half_width, -half_height, half_depth)

    renderer.add_triangle(fl_bl, fl_br, fl_tr, materials['white'])
    renderer.add_triangle(fl_bl, fl_tr, fl_tl, materials['white'])

    renderer.add_triangle(cl_bl, cl_tr, cl_br, materials['white'])
    renderer.add_triangle(cl_bl, cl_tl, cl_tr, materials['white'])

    renderer.add_triangle(fl_tl, fl_tr, cl_tr, materials['white'])
    renderer.add_triangle(fl_tl, cl_tr, cl_tl, materials['white'])

    renderer.add_triangle(fl_bl, fl_tl, cl_tl, materials['white'])
    renderer.add_triangle(fl_bl, cl_tl, cl_bl, materials['white'])

    renderer.add_triangle(fl_br, cl_br, cl_tr, materials['white'])
    renderer.add_triangle(fl_br, cl_tr, fl_tr, materials['white'])

    renderer.add_light(PointLight(Vector(-200, -150, -300), intensity=0.3))
    renderer.add_light(PointLight(Vector(200, -150, -300), intensity=0.3))
    renderer.add_light(PointLight(Vector(-200, -150, 300), intensity=0.3))
    renderer.add_light(PointLight(Vector(200, -150, 300), intensity=0.3))

    renderer.set_ambient_light(0.4)

    font_renderer = FontRenderer("arial.ttf", size=36, depth=10)
    main_text = "RAYTRACING"

    try:
        text_triangles = font_renderer.text_to_triangles_contour(
            main_text,
            position=Vector(0, 0, 250),
            material=materials['red'],
            scale=1.5,
            rotation=(0, 180, 0),
            detail_level=1.0
        )
    except (AttributeError, NameError):
        text_triangles = font_renderer.text_to_triangles(
            main_text,
            position=Vector(0, 0, 200),
            material=materials['red'],
            scale=1.5,
            rotation=(0, 180, 0)
        )

    renderer.add_objects(text_triangles)

    renderer.add_sphere(
        center=Vector(0, 0, 50),
        radius=70,
        material=materials['glass']
    )

    print("Scene setup complete with", len(text_triangles), "triangles for text")
