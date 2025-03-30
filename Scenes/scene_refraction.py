# scene_refraction.py - A scene demonstrating different refractive materials
import math
from vector import Vector
from main import Material

def setup_scene(raster):
    """Create a scene showcasing various refractive materials"""
    # Create materials
    materials = {
        'white': Material((255, 255, 255)),
        'black': Material((0, 0, 0)),
        'red': Material((255, 50, 50)),
        'green': Material((50, 255, 50)),
        'blue': Material((50, 50, 255)),
        'yellow': Material((255, 255, 50)),
        
        # Transparent materials with different refractive indices
        'air': Material((255, 255, 255), transparency=1.0, refractive_index=1.0),
        'water': Material((200, 230, 255), transparency=0.9, refractive_index=1.33),
        'glass': Material((255, 255, 255), transparency=0.9, refractive_index=1.5),
        'crystal': Material((240, 255, 255), transparency=0.9, refractive_index=1.6),
        'sapphire': Material((100, 100, 255), transparency=0.8, refractive_index=1.77),
        'ruby': Material((255, 20, 20), transparency=0.8, refractive_index=1.77),
        'emerald': Material((20, 255, 50), transparency=0.8, refractive_index=1.57),
        'diamond': Material((255, 255, 255), transparency=0.8, refractive_index=2.42),
    }
    
    # Create a striped background to better demonstrate refraction
    stripe_width = 40
    stripe_height = 400
    for i in range(-10, 10):
        stripe_material = materials['white'] if i % 2 == 0 else materials['black']
        x = i * stripe_width
        
        # Vertical stripes on back wall
        raster.add_triangle(
            Vector(x, stripe_height, 600), 
            Vector(x + stripe_width, stripe_height, 600), 
            Vector(x + stripe_width, -stripe_height, 600), 
            stripe_material
        )
        raster.add_triangle(
            Vector(x, stripe_height, 600), 
            Vector(x + stripe_width, -stripe_height, 600), 
            Vector(x, -stripe_height, 600), 
            stripe_material
        )
    
    # Create a striped floor
    for i in range(-10, 10):
        stripe_material = materials['white'] if i % 2 == 0 else materials['black']
        z = i * stripe_width + 300
        
        # Horizontal stripes on floor
        raster.add_triangle(
            Vector(-stripe_height, 100, z), 
            Vector(stripe_height, 100, z), 
            Vector(stripe_height, 100, z + stripe_width), 
            stripe_material
        )
        raster.add_triangle(
            Vector(-stripe_height, 100, z), 
            Vector(stripe_height, 100, z + stripe_width), 
            Vector(-stripe_height, 100, z + stripe_width), 
            stripe_material
        )
    
    # Add spheres with different refractive materials in a row
    refractive_materials = [
        ('water', materials['water']),
        ('glass', materials['glass']),
        ('crystal', materials['crystal']),
        ('diamond', materials['diamond'])
    ]
    
    # Place the transparent spheres with labels
    sphere_size = 70
    spacing = 150
    start_x = -225
    
    for i, (name, material) in enumerate(refractive_materials):
        x = start_x + i * spacing
        raster.add_sphere(Vector(x, 0, 200), sphere_size, material)
        
        # Add colored sphere behind each transparent sphere
        if i % 2 == 0:
            raster.add_sphere(Vector(x, 0, 400), 40, materials['red'])
        else:
            raster.add_sphere(Vector(x, 0, 400), 40, materials['blue'])
    
    # Add colored transparent materials to showcase color refraction
    colored_materials = [
        ('ruby', materials['ruby']),
        ('emerald', materials['emerald']),
        ('sapphire', materials['sapphire'])
    ]
    
    # Place the colored transparent spheres
    for i, (name, material) in enumerate(colored_materials):
        x = -150 + i * 150
        raster.add_sphere(Vector(x, 0, 100), 50, material)
    
    # Add a prism-like structure to demonstrate dispersion
    # (Note: true dispersion would require spectral rendering, 
    # but we can approximate the look with a triangular prism)
    prism_center = Vector(0, -120, 300)
    prism_size = 60
    prism_height = 100
    
    # Create a triangular prism using a custom function
    def create_triangular_prism(center, size, height, material):
        # Define the vertices of the triangular prism
        half_size = size / 2
        half_height = height / 2
        
        # Base triangle vertices (bottom)
        v0 = Vector(center.x, center.y - half_height, center.z - half_size)
        v1 = Vector(center.x + half_size, center.y - half_height, center.z + half_size)
        v2 = Vector(center.x - half_size, center.y - half_height, center.z + half_size)
        
        # Top triangle vertices
        v3 = Vector(center.x, center.y + half_height, center.z - half_size)
        v4 = Vector(center.x + half_size, center.y + half_height, center.z + half_size)
        v5 = Vector(center.x - half_size, center.y + half_height, center.z + half_size)
        
        # Create the triangular prism triangles
        triangles = []
        
        # Bottom face
        triangles.append((v0, v1, v2))
        
        # Top face
        triangles.append((v3, v5, v4))
        
        # Side faces
        triangles.append((v0, v2, v5))
        triangles.append((v0, v5, v3))
        
        triangles.append((v0, v3, v4))
        triangles.append((v0, v4, v1))
        
        triangles.append((v1, v4, v5))
        triangles.append((v1, v5, v2))
        
        # Add all triangles to the scene
        for v_a, v_b, v_c in triangles:
            raster.add_triangle(v_a, v_b, v_c, material)
    
    # Add a glass prism
    create_triangular_prism(prism_center, prism_size, prism_height, materials['glass'])
    
    # Add a small light source above the prism (represented by a small yellow sphere)
    raster.add_sphere(Vector(0, -200, 200), 20, materials['yellow'])