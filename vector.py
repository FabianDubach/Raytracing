"""
vector.py - 3D Vector class for ray tracing operations
"""
import math

class Vector:
    """
    3D Vector class with support for vector operations used in ray tracing.
    """
    def __init__(self, x, y, z=0):
        """
        Initialize a vector with x, y, and optional z components.
        """
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        """
        Add two vectors: v1 + v2
        Returns a new Vector
        """
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        """
        Subtract two vectors: v1 - v2
        Returns a new Vector
        """
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        """
        Multiply vector by a scalar: v * s
        Returns a new Vector
        """
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        """
        Compute the dot product of two vectors: v1 · v2
        Returns a scalar value
        """
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """
        Compute the cross product of two 3D vectors: v1 × v2
        Returns a new Vector perpendicular to both input vectors
        """
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def magnitude(self):
        """
        Compute the magnitude (length) of the vector.
        Returns a scalar value.
        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        """
        Return a unit vector (length 1) in the same direction.
        Returns a new Vector.
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0, 1)  # Default direction if magnitude is zero
        return self * (1 / mag)
    
    def __repr__(self):
        """
        String representation of the vector for debugging.
        """
        return f"Vector({self.x}, {self.y}, {self.z})"