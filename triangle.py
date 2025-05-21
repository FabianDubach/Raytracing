class Triangle:
    def __init__(self, v0, v1, v2, color: tuple):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color
        
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = edge1.cross(edge2).normalize()
    
    def intersects(self, ray_origin, ray_direction):
        EPSILON = 0.0000001
        
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        
        h = ray_direction.cross(edge2)
        a = edge1.dot(h)
        
        if -EPSILON < a < EPSILON:
            return None
        
        f = 1.0 / a
        s = ray_origin - self.v0
        u = f * s.dot(h)
        
        if u < 0.0 or u > 1.0:
            return None
        
        q = s.cross(edge1)
        v = f * ray_direction.dot(q)
        
        if v < 0.0 or u + v > 1.0:
            return None
        
        t = f * edge2.dot(q)
        
        if t > EPSILON:
            return t
        
        return None
    
    def get_normal(self, _):
        return self.normal
    
    def __repr__(self):
        return f"Triangle(v0={self.v0}, v1={self.v1}, v2={self.v2}, color={self.color})"