import math
from vector import Vector
from ray import EnhancedTriangle, Material
from mesh_builder import MeshBuilder

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