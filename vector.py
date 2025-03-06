import math

class Vector:
    def __init__(self, x, y, z=0):
        """Initialize a vector with x, y, and optional z components."""
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        """Add two vectors."""
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        """Subtract two vectors."""
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        """Multiply vector by a scalar."""
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        """Compute the dot product of two vectors."""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """Compute the cross product of two 3D vectors."""
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def magnitude(self):
        """Compute the magnitude of the vector."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        """Return a unit vector in the same direction."""
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0, 1)
        return self * (1 / mag)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"