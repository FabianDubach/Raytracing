import math
from vector import Vector
from triangle import Triangle

class MeshBuilder:
    
    @staticmethod
    def create_cube(center, size, color):
        half = size / 2
        
        v = []
        v.append(Vector(center.x - half, center.y - half, center.z - half))
        v.append(Vector(center.x + half, center.y - half, center.z - half))
        v.append(Vector(center.x + half, center.y + half, center.z - half))
        v.append(Vector(center.x - half, center.y + half, center.z - half))
        v.append(Vector(center.x - half, center.y - half, center.z + half))
        v.append(Vector(center.x + half, center.y - half, center.z + half))
        v.append(Vector(center.x + half, center.y + half, center.z + half))
        v.append(Vector(center.x - half, center.y + half, center.z + half))
        
        triangles = []
        
        triangles.append(Triangle(v[4], v[5], v[6], color))
        triangles.append(Triangle(v[4], v[6], v[7], color))
        
        triangles.append(Triangle(v[1], v[0], v[3], color))
        triangles.append(Triangle(v[1], v[3], v[2], color))
        
        triangles.append(Triangle(v[0], v[4], v[7], color))
        triangles.append(Triangle(v[0], v[7], v[3], color))
        
        triangles.append(Triangle(v[5], v[1], v[2], color))
        triangles.append(Triangle(v[5], v[2], v[6], color))
        
        triangles.append(Triangle(v[7], v[6], v[2], color))
        triangles.append(Triangle(v[7], v[2], v[3], color))
        
        triangles.append(Triangle(v[0], v[1], v[5], color))
        triangles.append(Triangle(v[0], v[5], v[4], color))
        
        return triangles
    
    @staticmethod
    def create_pyramid(center, base_size, height, color):
        half = base_size / 2
        base_y = center.y
        apex = Vector(center.x, center.y - height, center.z)
        
        base_verts = []
        base_verts.append(Vector(center.x - half, base_y, center.z - half))
        base_verts.append(Vector(center.x + half, base_y, center.z - half))
        base_verts.append(Vector(center.x + half, base_y, center.z + half))
        base_verts.append(Vector(center.x - half, base_y, center.z + half))

        triangles = []
        
        triangles.append(Triangle(base_verts[0], base_verts[2], base_verts[1], color))
        triangles.append(Triangle(base_verts[0], base_verts[3], base_verts[2], color))
        
        triangles.append(Triangle(base_verts[0], base_verts[1], apex, color))
        triangles.append(Triangle(base_verts[1], base_verts[2], apex, color))
        triangles.append(Triangle(base_verts[2], base_verts[3], apex, color))
        triangles.append(Triangle(base_verts[3], base_verts[0], apex, color))
        
        return triangles
    
    @staticmethod
    def create_cylinder(center, radius, height, segments, color):
        
        triangles = []
        
        top_center = Vector(center.x, center.y - height/2, center.z)
        bottom_center = Vector(center.x, center.y + height/2, center.z)
        
        top_verts = []
        bottom_verts = []
        
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = center.x + radius * math.cos(angle)
            z = center.z + radius * math.sin(angle)
            
            top_verts.append(Vector(x, top_center.y, z))
            bottom_verts.append(Vector(x, bottom_center.y, z))
        
        for i in range(segments):
            next_i = (i + 1) % segments
            triangles.append(Triangle(top_verts[i], top_verts[next_i], top_center, color))
        
        for i in range(segments):
            next_i = (i + 1) % segments
            triangles.append(Triangle(bottom_verts[next_i], bottom_verts[i], bottom_center, color))
        
        for i in range(segments):
            next_i = (i + 1) % segments
            
            triangles.append(Triangle(bottom_verts[i], bottom_verts[next_i], top_verts[i], color))
            
            triangles.append(Triangle(bottom_verts[next_i], top_verts[next_i], top_verts[i], color))
        
        return triangles