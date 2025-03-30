from vector import Vector
from triangle import Triangle

class MeshBuilder:
    @staticmethod
    def create_cube(center, size, color):
        """
        Create a cube mesh consisting of 12 triangles (2 triangles per face).
        Triangles are created in counter-clockwise order when viewed from outside
        to ensure outward-facing normals.
        
        Args:
            center: Vector - center position of the cube
            size: float - side length of the cube
            color: tuple - RGB color for the cube
            
        Returns:
            list of Triangle objects
        """
        # Calculate the half-size for vertex positions
        half = size / 2
        
        # Define the 8 vertices of the cube
        v = []
        v.append(Vector(center.x - half, center.y - half, center.z - half))  # v0: bottom-left-back
        v.append(Vector(center.x + half, center.y - half, center.z - half))  # v1: bottom-right-back
        v.append(Vector(center.x + half, center.y + half, center.z - half))  # v2: top-right-back
        v.append(Vector(center.x - half, center.y + half, center.z - half))  # v3: top-left-back
        v.append(Vector(center.x - half, center.y - half, center.z + half))  # v4: bottom-left-front
        v.append(Vector(center.x + half, center.y - half, center.z + half))  # v5: bottom-right-front
        v.append(Vector(center.x + half, center.y + half, center.z + half))  # v6: top-right-front
        v.append(Vector(center.x - half, center.y + half, center.z + half))  # v7: top-left-front
        
        # Create triangles for each face - ensure counter-clockwise winding when viewed from outside
        triangles = []
        
        # Front face (counter-clockwise when looking at front)
        triangles.append(Triangle(v[4], v[5], v[6], color))
        triangles.append(Triangle(v[4], v[6], v[7], color))
        
        # Back face (counter-clockwise when looking at back)
        triangles.append(Triangle(v[1], v[0], v[3], color))
        triangles.append(Triangle(v[1], v[3], v[2], color))
        
        # Left face (counter-clockwise when looking from left)
        triangles.append(Triangle(v[0], v[4], v[7], color))
        triangles.append(Triangle(v[0], v[7], v[3], color))
        
        # Right face (counter-clockwise when looking from right)
        triangles.append(Triangle(v[5], v[1], v[2], color))
        triangles.append(Triangle(v[5], v[2], v[6], color))
        
        # Top face (counter-clockwise when looking from top)
        triangles.append(Triangle(v[7], v[6], v[2], color))
        triangles.append(Triangle(v[7], v[2], v[3], color))
        
        # Bottom face (counter-clockwise when looking from bottom)
        triangles.append(Triangle(v[0], v[1], v[5], color))
        triangles.append(Triangle(v[0], v[5], v[4], color))
        
        return triangles
    
    @staticmethod
    def create_pyramid(center, base_size, height, color):
        """
        Create a square-base pyramid with correctly oriented triangles
        
        Args:
            center: Vector - center of the base
            base_size: float - side length of the square base
            height: float - height of the pyramid
            color: tuple - RGB color
            
        Returns:
            list of Triangle objects
        """
        # Define the vertices
        half = base_size / 2
        base_y = center.y
        apex = Vector(center.x, center.y - height, center.z)  # Apex is BELOW the base for correct orientation
        
        # Base vertices (counter-clockwise from bottom left when looking from below)
        base_verts = []
        base_verts.append(Vector(center.x - half, base_y, center.z - half))  # v0: bottom-left
        base_verts.append(Vector(center.x + half, base_y, center.z - half))  # v1: bottom-right
        base_verts.append(Vector(center.x + half, base_y, center.z + half))  # v2: top-right
        base_verts.append(Vector(center.x - half, base_y, center.z + half))  # v3: top-left
        
        triangles = []
        
        # Base (2 triangles) - counter-clockwise when viewed from below
        triangles.append(Triangle(base_verts[0], base_verts[2], base_verts[1], color))
        triangles.append(Triangle(base_verts[0], base_verts[3], base_verts[2], color))
        
        # 4 triangular faces - counter-clockwise when viewed from outside
        triangles.append(Triangle(base_verts[0], base_verts[1], apex, color))  # Front face
        triangles.append(Triangle(base_verts[1], base_verts[2], apex, color))  # Right face
        triangles.append(Triangle(base_verts[2], base_verts[3], apex, color))  # Back face
        triangles.append(Triangle(base_verts[3], base_verts[0], apex, color))  # Left face
        
        return triangles
    
    @staticmethod
    def create_cylinder(center, radius, height, segments, color):
        """
        Create a cylinder mesh with proper normals
        
        Args:
            center: Vector - center of the base
            radius: float - radius of the cylinder
            height: float - height of the cylinder
            segments: int - number of segments around the circumference
            color: tuple - RGB color
            
        Returns:
            list of Triangle objects
        """
        import math
        
        triangles = []
        
        # Create vertices for top and bottom circles
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
        
        # Create triangles for the top face (fan) - counter-clockwise
        for i in range(segments):
            next_i = (i + 1) % segments
            triangles.append(Triangle(top_verts[i], top_verts[next_i], top_center, color))
        
        # Create triangles for the bottom face (fan) - counter-clockwise when viewed from below
        for i in range(segments):
            next_i = (i + 1) % segments
            triangles.append(Triangle(bottom_verts[next_i], bottom_verts[i], bottom_center, color))
        
        # Create triangles for the sides (quads split into 2 triangles)
        for i in range(segments):
            next_i = (i + 1) % segments
            
            # First triangle of the quad - counter-clockwise when viewed from outside
            triangles.append(Triangle(bottom_verts[i], bottom_verts[next_i], top_verts[i], color))
            
            # Second triangle of the quad - counter-clockwise when viewed from outside
            triangles.append(Triangle(bottom_verts[next_i], top_verts[next_i], top_verts[i], color))
        
        return triangles