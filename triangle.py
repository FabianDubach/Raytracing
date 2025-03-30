"""
triangle.py - Triangle object for ray tracing
"""
from vector import Vector

class Triangle:
    """
    Triangle class representing a 3D triangle with intersection testing for ray tracing.
    """
    def __init__(self, v0, v1, v2, color: tuple):
        """
        Initialize a triangle with three vertices and a color.
        
        Args:
            v0, v1, v2: Vector vertices of the triangle
            color: RGB color tuple (r, g, b)
        """
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color
        
        # Pre-compute the normal vector for the triangle
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = edge1.cross(edge2).normalize()
    
    def intersects(self, ray_origin, ray_direction):
        """
        Test if a ray intersects this triangle using the Möller–Trumbore algorithm.
        
        Args:
            ray_origin: Vector origin of the ray
            ray_direction: Vector direction of the ray
            
        Returns:
            Distance to intersection point or None if no intersection
        """
        EPSILON = 0.0000001  # Small value to prevent division by zero and handle precision issues
        
        # Calculate edges from v0
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        
        # Calculate determinant
        h = ray_direction.cross(edge2)
        a = edge1.dot(h)
        
        # Ray is parallel to the triangle
        if -EPSILON < a < EPSILON:
            return None
        
        f = 1.0 / a
        s = ray_origin - self.v0
        u = f * s.dot(h)
        
        # Ray doesn't intersect the triangle (u out of bounds)
        if u < 0.0 or u > 1.0:
            return None
        
        q = s.cross(edge1)
        v = f * ray_direction.dot(q)
        
        # Ray doesn't intersect the triangle (u+v out of bounds)
        if v < 0.0 or u + v > 1.0:
            return None
        
        # Compute the intersection distance
        t = f * edge2.dot(q)
        
        # Ensure it's a positive intersection (in front of the ray origin)
        if t > EPSILON:
            return t
        
        # No intersection or behind the ray
        return None
    
    def get_normal(self, _):
        """
        Get normal vector for the triangle.
        The point parameter is ignored since triangles have the same normal across their surface.
        
        Returns:
            Normalized Vector perpendicular to the triangle
        """
        return self.normal
    
    def __repr__(self):
        """
        String representation of the triangle for debugging.
        """
        return f"Triangle(v0={self.v0}, v1={self.v1}, v2={self.v2}, color={self.color})"