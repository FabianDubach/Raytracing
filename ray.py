import random
import time
import multiprocessing
import os
import sys
import math
from vector import Vector
from sphere import Sphere
from triangle import Triangle
from mesh_builder import MeshBuilder
from PIL import Image

class Ray:
    @staticmethod
    def cast_ray(objects, ray_origin, ray_direction, max_distance=float("inf"), ignore_object=None):
        """ 
        Cast a ray and find closest object
        
        Args:
            objects: list of renderable objects
            ray_origin: Vector representing the ray's origin
            ray_direction: Vector representing the ray's direction
            max_distance: maximum distance to check (for shadow rays)
            ignore_object: object to ignore (for reflection rays to avoid self-intersection)
            
        Returns:
            (object, distance) tuple for the closest intersection, or (None, None) if no intersection
        """
        closest_t = float("inf")
        closest_obj = None

        for obj in objects:
            if obj == ignore_object:
                continue
                
            t = obj.intersects(ray_origin, ray_direction)
            if t and t < closest_t and t < max_distance:
                closest_t = t
                closest_obj = obj

        return closest_obj, closest_t

class Material:
    def __init__(self, color, reflectivity=0.0, glossiness=0.0, is_checkerboard=False, checker_size=50.0):
        """
        Initialize a material with color and reflection properties
        
        Args:
            color: RGB color tuple
            reflectivity: 0.0-1.0, how reflective the material is
            glossiness: 0.0-1.0, how glossy the material is (for specular highlights)
            is_checkerboard: Whether this material uses a checkerboard pattern
            checker_size: Size of checkerboard squares
        """
        self.base_color = color
        self.reflectivity = reflectivity
        self.glossiness = glossiness
        self.is_checkerboard = is_checkerboard
        self.checker_size = checker_size
    
    def get_color(self, point):
        """Get the color at a specific point, for procedural textures like checkerboard"""
        if self.is_checkerboard:
            # Create a checkerboard pattern based on x and z coordinates
            x_check = int(point.x / self.checker_size) % 2 == 0
            z_check = int(point.z / self.checker_size) % 2 == 0
            
            if x_check == z_check:
                return self.base_color
            else:
                # Return the alternate color (black)
                return (0, 0, 0)
        else:
            return self.base_color

class EnhancedSphere(Sphere):
    def __init__(self, center, radius, material):
        """Initialize a sphere with a material"""
        self.center = center
        self.radius = radius
        self.material = material
    
    def get_normal(self, point):
        """Get normal vector at a point on the sphere surface"""
        return (point - self.center).normalize()
    
    def get_color(self, point):
        """Get the color at a specific point on the surface"""
        return self.material.get_color(point)
    
    def get_material(self):
        """Get the material of this object"""
        return self.material

class EnhancedTriangle(Triangle):
    def __init__(self, v0, v1, v2, material):
        """Initialize a triangle with a material"""
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        
        # Pre-compute the normal vector
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = edge1.cross(edge2).normalize()
    
    def get_normal(self, _):
        """Get the normal vector (same for all points on a triangle)"""
        return self.normal
    
    def get_color(self, point):
        """Get the color at a specific point on the surface"""
        return self.material.get_color(point)
    
    def get_material(self):
        """Get the material of this object"""
        return self.material

class EnhancedRayTracer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.objects = []
        self.background_color = (200, 220, 255)  # Light blue sky
        self.ambient_light = 0.2
        self.light_positions = [
            Vector(-500, -500, -500),  # Top-left light
            Vector(500, -500, -500),   # Top-right light
        ]
        self.light_colors = [
            (255, 255, 255),  # White light
            (255, 255, 255)   # White light
        ]
        self.max_reflection_depth = 3
    
    def add_object(self, obj):
        """Add a renderable object to the scene"""
        self.objects.append(obj)
    
    def add_objects(self, objects):
        """Add multiple objects to the scene at once"""
        self.objects.extend(objects)
    
    def add_sphere(self, center, radius, material):
        """Add a sphere with the given material"""
        self.add_object(EnhancedSphere(center, radius, material))
    
    def add_triangle(self, v0, v1, v2, material):
        """Add a triangle with the given material"""
        self.add_object(EnhancedTriangle(v0, v1, v2, material))
    
    def add_cube(self, center, size, material):
        """Add a cube with the given material"""
        triangles = MeshBuilder.create_cube(center, size, (0, 0, 0))  # Color doesn't matter
        for triangle in triangles:
            self.add_triangle(triangle.v0, triangle.v1, triangle.v2, material)
    
    def add_cylinder(self, center, radius, height, segments, material):
        """Add a cylinder with the given material"""
        triangles = MeshBuilder.create_cylinder(center, radius, height, segments, (0, 0, 0))
        for triangle in triangles:
            self.add_triangle(triangle.v0, triangle.v1, triangle.v2, material)
    
    def add_plane(self, y, material):
        """Add an infinite plane at the given y coordinate"""
        size = 10000  # Very large to appear infinite
        v0 = Vector(-size, y, -size)
        v1 = Vector(size, y, -size)
        v2 = Vector(size, y, size)
        v3 = Vector(-size, y, size)
        
        self.add_triangle(v0, v1, v2, material)
        self.add_triangle(v0, v2, v3, material)
    
    def reflect_ray(self, incoming_dir, normal):
        """Calculate the reflection direction for a ray"""
        return incoming_dir - normal * (2 * incoming_dir.dot(normal))
    
    def compute_lighting(self, obj, hit_point, normal, view_dir):
        """
        Compute lighting at a point with Phong illumination model
        
        Args:
            obj: The object that was hit
            hit_point: Point of intersection
            normal: Surface normal at hit point
            view_dir: Direction from hit point to viewer (negated ray direction)
            
        Returns:
            RGB tuple with the computed color
        """
        material = obj.get_material()
        object_color = obj.get_color(hit_point)
        
        # Start with ambient lighting
        r = object_color[0] * self.ambient_light
        g = object_color[1] * self.ambient_light
        b = object_color[2] * self.ambient_light
        
        # For each light source
        for i, light_pos in enumerate(self.light_positions):
            light_dir = (light_pos - hit_point).normalize()
            
            # Check for shadows
            shadow_origin = hit_point + normal * 0.001  # Offset to avoid self-intersection
            shadow_direction = light_dir
            light_distance = (light_pos - hit_point).magnitude()
            
            shadow_obj, _ = Ray.cast_ray(self.objects, shadow_origin, shadow_direction, light_distance)
            
            # If not in shadow
            if shadow_obj is None:
                # Diffuse lighting (Lambert's cosine law)
                diffuse = max(0, normal.dot(light_dir))
                
                # Specular lighting (Phong model)
                reflection_dir = self.reflect_ray(-light_dir, normal)
                specular = max(0, reflection_dir.dot(view_dir)) ** (material.glossiness * 50 + 1)
                specular_intensity = material.glossiness * 0.8
                
                # Add diffuse and specular contributions
                light_color = self.light_colors[i]
                r += object_color[0] * diffuse * light_color[0] / 255
                g += object_color[1] * diffuse * light_color[1] / 255
                b += object_color[2] * diffuse * light_color[2] / 255
                
                # Add specular (white)
                r += 255 * specular * specular_intensity
                g += 255 * specular * specular_intensity
                b += 255 * specular * specular_intensity
        
        return (min(255, int(r)), min(255, int(g)), min(255, int(b)))
    
    def trace_ray(self, ray_origin, ray_direction, depth=0, ignore_object=None):
        """
        Trace a ray through the scene with reflection
        
        Args:
            ray_origin: Origin point of the ray
            ray_direction: Direction vector of the ray
            depth: Current recursion depth
            ignore_object: Object to ignore (for reflection)
            
        Returns:
            RGB color tuple
        """
        # If we've reached maximum reflection depth, return black
        if depth > self.max_reflection_depth:
            return self.background_color
        
        obj, t = Ray.cast_ray(self.objects, ray_origin, ray_direction, ignore_object=ignore_object)
        
        if obj:
            # Calculate hit point and normal
            hit_point = ray_origin + ray_direction * t
            normal = obj.get_normal(hit_point)
            
            # Direction to viewer (for specular)
            view_dir = ray_direction * -1
            
            # Calculate lighting
            color = self.compute_lighting(obj, hit_point, normal, view_dir)
            
            # Calculate reflections if material is reflective
            material = obj.get_material()
            if material.reflectivity > 0 and depth < self.max_reflection_depth:
                # Calculate reflection direction
                reflection_dir = self.reflect_ray(ray_direction, normal)
                
                # Cast reflection ray (slightly offset along normal to avoid self-intersection)
                reflection_origin = hit_point + normal * 0.001
                reflection_color = self.trace_ray(reflection_origin, reflection_dir, depth + 1, obj)
                
                # Blend original color with reflection color based on reflectivity
                r = int(color[0] * (1 - material.reflectivity) + reflection_color[0] * material.reflectivity)
                g = int(color[1] * (1 - material.reflectivity) + reflection_color[1] * material.reflectivity)
                b = int(color[2] * (1 - material.reflectivity) + reflection_color[2] * material.reflectivity)
                
                color = (min(255, r), min(255, g), min(255, b))
            
            return color
        
        # No intersection, return background color
        return self.background_color
    
    def compute_pixel(self, xy):
        """Compute color for a single pixel"""
        x, y = xy
        ray_origin = Vector(x - self.width / 2, y - self.height / 2, -1000)
        ray_direction = Vector(0, 0, 1).normalize()
        
        color = self.trace_ray(ray_origin, ray_direction)
        return x, y, color
    
    def draw_scene(self, output_file="raytraced_scene.png"):
        """Render the scene and save to an image file"""
        print(f"Rendering scene with {len(self.objects)} objects...")
        start_time = time.time()
        
        pixels = self.image.load()
        coords = [(x, y) for y in range(self.height) for x in range(self.width)]
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.compute_pixel, coords)
        
        for x, y, color in results:
            pixels[x, y] = color
        
        self.image.save(output_file)
        end_time = time.time()
        print(f"Scene rendered in {end_time - start_time:.2f} seconds. Saved as {output_file}")

def create_chess_scene():
    """Create a scene similar to the reference image with reflections and checkerboard"""
    raytracer = EnhancedRayTracer(1600, 900)
    
    # Create a checkerboard floor
    floor_material = Material((255, 255, 255), reflectivity=0.3, glossiness=0.7, is_checkerboard=True, checker_size=100)
    raytracer.add_plane(100, floor_material)
    
    # Create materials
    red_material = Material((255, 50, 50), reflectivity=0.2, glossiness=0.8)
    blue_material = Material((50, 50, 255), reflectivity=0.2, glossiness=0.8)
    green_material = Material((50, 255, 50), reflectivity=0.2, glossiness=0.8)
    yellow_material = Material((255, 255, 50), reflectivity=0.2, glossiness=0.8)
    reflective_material = Material((220, 220, 220), reflectivity=0.9, glossiness=1.0)
    
    # Add spheres with different colors
    raytracer.add_sphere(Vector(-250, 20, 200), 80, red_material)
    raytracer.add_sphere(Vector(0, 20, 400), 100, yellow_material)
    raytracer.add_sphere(Vector(250, 20, 200), 80, blue_material)
    raytracer.add_sphere(Vector(-150, 20, 600), 80, green_material)
    raytracer.add_sphere(Vector(150, 20, 600), 80, blue_material)
    
    # Add a highly reflective sphere (like chrome)
    raytracer.add_sphere(Vector(0, 100, 200), 60, reflective_material)
    
    # Add some smaller spheres
    small_sphere_positions = [
        (Vector(-400, 50, 300), 30, red_material),
        (Vector(400, 50, 300), 30, green_material),
        (Vector(-300, 50, 500), 30, blue_material),
        (Vector(300, 50, 500), 30, yellow_material)
    ]
    
    for pos, size, material in small_sphere_positions:
        raytracer.add_sphere(pos, size, material)
    
    # Render the scene
    raytracer.draw_scene("realistic_scene.png")
    print("Scene rendered! Check realistic_scene.png")

if __name__ == "__main__":
    create_chess_scene()