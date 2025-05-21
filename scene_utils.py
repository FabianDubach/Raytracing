import math
from vector import Vector
from ray import EnhancedTriangle, Material
from mesh_builder import MeshBuilder

def create_truncated_icosahedron(center, radius, color):
    phi = (1 + math.sqrt(5)) / 2
    
    vertices = []
    
    vertices.append(Vector(0, phi, 1))
    vertices.append(Vector(0, phi, -1))
    vertices.append(Vector(0, -phi, 1))
    vertices.append(Vector(0, -phi, -1))
    
    vertices.append(Vector(1, 0, phi))
    vertices.append(Vector(-1, 0, phi))
    vertices.append(Vector(1, 0, -phi))
    vertices.append(Vector(-1, 0, -phi))
    
    vertices.append(Vector(phi, 1, 0))
    vertices.append(Vector(phi, -1, 0))
    vertices.append(Vector(-phi, 1, 0))
    vertices.append(Vector(-phi, -1, 0))

    scaled_vertices = []

    for v in vertices:
        magnitude = math.sqrt(v.x**2 + v.y**2 + v.z**2)
        scaled_v = Vector(
            (v.x / magnitude) * radius + center.x,
            (v.y / magnitude) * radius + center.y,
            (v.z / magnitude) * radius + center.z
        )
        scaled_vertices.append(scaled_v)
    
    faces = [
        [0, 4, 5], [0, 5, 10], [0, 10, 1], [0, 1, 8], [0, 8, 4],
        [4, 8, 9], [5, 4, 2], [10, 5, 11], [1, 10, 7], [8, 1, 6],
        [3, 6, 7], [3, 7, 11], [3, 11, 2], [3, 2, 9], [3, 9, 6],
        [9, 2, 4], [2, 11, 5], [11, 7, 10], [7, 6, 1], [6, 9, 8]
    ]
    
    triangles = []
    for face in faces:
        v0 = scaled_vertices[face[0]]
        v1 = scaled_vertices[face[1]]
        v2 = scaled_vertices[face[2]]
        
        face_color = color
        if (face[0] + face[1] + face[2]) % 2 == 0:
            dark_color = (max(0, color[0] - 120), max(0, color[1] - 120), max(0, color[2] - 120))
            face_color = dark_color
        
        material = Material(face_color)
        triangles.append(EnhancedTriangle(v0, v1, v2, material))
    
    return triangles

def rotate_vertex(vertex, origin, rotation_degrees):
    angle_x = math.radians(rotation_degrees[0])
    angle_y = math.radians(rotation_degrees[1])
    angle_z = math.radians(rotation_degrees[2])
    
    v = Vector(vertex.x - origin.x, vertex.y - origin.y, vertex.z - origin.z)
    
    y1 = v.y * math.cos(angle_x) - v.z * math.sin(angle_x)
    z1 = v.y * math.sin(angle_x) + v.z * math.cos(angle_x)
    
    x2 = v.x * math.cos(angle_y) + z1 * math.sin(angle_y)
    z2 = -v.x * math.sin(angle_y) + z1 * math.cos(angle_y)
    
    x3 = x2 * math.cos(angle_z) - y1 * math.sin(angle_z)
    y3 = x2 * math.sin(angle_z) + y1 * math.cos(angle_z)
    
    return Vector(x3 + origin.x, y3 + origin.y, z2 + origin.z)

def create_rotated_shape(shape_type, center, size, rotation_degrees, color):
    material = Material(color)
    
    if shape_type == "cube":
        original_triangles = MeshBuilder.create_cube(center, size, color)
        
        rotated_triangles = []
        for triangle in original_triangles:
            rotated_v0 = rotate_vertex(triangle.v0, center, rotation_degrees)
            rotated_v1 = rotate_vertex(triangle.v1, center, rotation_degrees)
            rotated_v2 = rotate_vertex(triangle.v2, center, rotation_degrees)

            rotated_triangles.append(EnhancedTriangle(rotated_v0, rotated_v1, rotated_v2, material))
        
        return rotated_triangles
        
    elif shape_type == "pyramid":
        original_triangles = MeshBuilder.create_pyramid(center, size, size*1.5, color)
        
        rotated_triangles = []
        for triangle in original_triangles:
            rotated_v0 = rotate_vertex(triangle.v0, center, rotation_degrees)
            rotated_v1 = rotate_vertex(triangle.v1, center, rotation_degrees)
            rotated_v2 = rotate_vertex(triangle.v2, center, rotation_degrees)

            rotated_triangles.append(EnhancedTriangle(rotated_v0, rotated_v1, rotated_v2, material))
        
        return rotated_triangles
        
    elif shape_type == "cylinder":
        original_triangles = MeshBuilder.create_cylinder(center, size/2, size, 16, color)
        
        rotated_triangles = []
        for triangle in original_triangles:
            rotated_v0 = rotate_vertex(triangle.v0, center, rotation_degrees)
            rotated_v1 = rotate_vertex(triangle.v1, center, rotation_degrees)
            rotated_v2 = rotate_vertex(triangle.v2, center, rotation_degrees)

            rotated_triangles.append(EnhancedTriangle(rotated_v0, rotated_v1, rotated_v2, material))
        
        return rotated_triangles
    
    elif shape_type == "sphere":
        from ray import EnhancedSphere
        return [EnhancedSphere(center, size, material)]
    
    else:
        raise ValueError(f"Unknown shape type: {shape_type}")