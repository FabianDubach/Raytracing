# main.py - Main ray tracer code
import random
import time
import multiprocessing
import os
import sys
from vector import Vector
from sphere import Sphere
from triangle import Triangle
from mesh_builder import MeshBuilder
from ray import Ray
from PIL import Image

class Main:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.objects = []  # List to hold all renderable objects (spheres and triangles)
    
    def add_object(self, obj):
        """Add a renderable object (Sphere or Triangle) to the scene"""
        self.objects.append(obj)
    
    def add_objects(self, objects):
        """Add multiple objects to the scene at once"""
        self.objects.extend(objects)
    
    def generate_sphere_face(self):
        """Generate the original sphere face"""
        self.add_object(Sphere(Vector(0, 0, 0), 70, (255, 0, 0)))
        self.add_object(Sphere(Vector(140, -140, 150), 80, (0, 255, 0)))
        self.add_object(Sphere(Vector(-140, -140, 150), 80, (0, 255, 0)))
        self.add_object(Sphere(Vector(0, 0, 300), 250, (0, 0, 255)))
        self.add_object(Sphere(Vector(-100, -100, 230), 150, (0, 255, 255)))
        self.add_object(Sphere(Vector(100, -100, 230), 150, (0, 255, 255)))
    
    def generate_random_spheres(self, num_spheres):
        """Generate random spheres and add them to the scene"""
        for _ in range(num_spheres):
            x = random.randint(-self.width // 2, self.width // 2)
            y = random.randint(-self.height // 2, self.height // 2)
            z = random.randint(50, 400)
            radius = random.randint(10, 40)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.add_object(Sphere(Vector(x, y, z), radius, color))
    
    def add_cube(self, center, size, color):
        """Add a cube to the scene"""
        cube_triangles = MeshBuilder.create_cube(center, size, color)
        self.add_objects(cube_triangles)
    
    def add_pyramid(self, center, base_size, height, color):
        """Add a pyramid to the scene"""
        pyramid_triangles = MeshBuilder.create_pyramid(center, base_size, height, color)
        self.add_objects(pyramid_triangles)
    
    def add_cylinder(self, center, radius, height, segments, color):
        """Add a cylinder to the scene"""
        cylinder_triangles = MeshBuilder.create_cylinder(center, radius, height, segments, color)
        self.add_objects(cylinder_triangles)
    
    def compute_pixel(self, xy):
        x, y = xy
        ray_origin = Vector(x - self.width / 2, y - self.height / 2, -500)
        ray_direction = Vector(0, 0, 1)
        obj, t = Ray.cast_ray(self.objects, ray_origin, ray_direction)
        
        if obj:
            hit_point = ray_origin + ray_direction * t
            normal = obj.get_normal(hit_point)
            
            # Define light position(s)
            light_positions = [
                Vector(-300, -300, -200),  # Top-left light
                Vector(300, -300, -200),   # Top-right light
            ]
            
            # Ambient light component (to prevent completely black shadows)
            ambient_factor = 0.2
            light_intensity = 1.0 - ambient_factor
            
            # Start with ambient light
            brightness = ambient_factor
            
            # For each light source
            for light_pos in light_positions:
                # Calculate vector from hit point to light
                light_dir = (light_pos - hit_point).normalize()
                
                # Check if the point is in shadow by casting a ray from the hit point toward the light
                shadow_origin = hit_point + normal * 0.001  # Offset to prevent self-intersection
                shadow_direction = light_dir
                
                # Calculate distance to light
                light_distance = (light_pos - hit_point).magnitude()
                
                # Cast shadow ray with the light distance as the maximum
                shadow_obj, shadow_t = Ray.cast_ray(self.objects, shadow_origin, shadow_direction, light_distance)
                
                # If no object blocks the light, add diffuse lighting
                if shadow_obj is None:
                    # Calculate diffuse lighting using dot product of normal and light direction
                    diffuse = max(0, normal.dot(light_dir))
                    brightness += diffuse * light_intensity / len(light_positions)
            
            # Apply brightness to the object's color
            color = tuple(min(255, int(c * brightness)) for c in obj.color)
            return x, y, color
        
        return x, y, (0, 0, 0)  # Background color
    
    def draw_scene(self, output_file="raytraced_scene.png"):
        pixels = self.image.load()
        coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        
        print(f"Rendering scene with {len(self.objects)} objects...")
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.compute_pixel, coords)
        
        for x, y, color in results:
            pixels[x, y] = color
        
        self.image.save(output_file)
        print(f"Scene saved as {output_file}")
    
    def run(self, output_file="raytraced_scene.png"):
        self.draw_scene(output_file)

if __name__ == "__main__":
    # Get the scene filename from command line argument if provided
    if len(sys.argv) > 1:
        scene_file = sys.argv[1]
        
        # If the file doesn't have a .py extension, add it
        if not scene_file.endswith('.py'):
            scene_file += '.py'
        
        # Check if the scene file exists
        if not os.path.exists(scene_file):
            print(f"Error: Scene file '{scene_file}' not found")
            sys.exit(1)
        
        # Extract scene name (remove .py and path)
        scene_name = os.path.splitext(os.path.basename(scene_file))[0]
        
        # Import the scene module dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location(scene_name, scene_file)
        scene_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scene_module)
        
        # Check if the module has a setup_scene function
        if not hasattr(scene_module, 'setup_scene'):
            print(f"Error: Scene file '{scene_file}' does not contain a setup_scene function")
            sys.exit(1)
        
        # Create renderer and set up the scene
        start_time = time.time()
        raster = Main(1200, 800)
        
        # Call the setup_scene function from the imported module
        print(f"Setting up scene from {scene_file}...")
        scene_module.setup_scene(raster)
        
        # Output filename based on scene name
        output_file = f"{scene_name}.png"
        
        # Render the scene
        raster.run(output_file)
        
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.2f} seconds")
    else:
        print("Usage: py main.py scene_file")
        print("Example: py main.py scene_basic")