"""
main.py - Main ray tracing engine with support for reflections and transparency
"""
import random
import time
import multiprocessing
import os
import sys
import math
from vector import Vector
from ray import Ray, Material, EnhancedSphere, EnhancedTriangle
from mesh_builder import MeshBuilder
from PIL import Image

class Main:
    """
    Main ray tracing engine with support for reflection, refraction, and materials.
    """
    def __init__(self, width, height):
        """
        Initialize the ray tracer.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
        """
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.objects = []  # List to hold all renderable objects
        self.max_depth = 5  # Maximum ray recursion depth
        self.background_color = (70, 130, 180)  # Steel blue sky
    
    def add_object(self, obj):
        """
        Add a renderable object to the scene.
        
        Args:
            obj: Object implementing intersects() and get_normal() methods
        """
        self.objects.append(obj)
    
    def add_objects(self, objects):
        """
        Add multiple objects to the scene at once.
        
        Args:
            objects: List of renderable objects
        """
        self.objects.extend(objects)
    
    def add_sphere(self, center, radius, material):
        """
        Add a sphere with material properties.
        
        Args:
            center: Vector position of the sphere's center
            radius: Radius of the sphere
            material: Material defining the sphere's optical properties
        """
        self.add_object(EnhancedSphere(center, radius, material))
    
    def add_triangle(self, v0, v1, v2, material):
        """
        Add a triangle with material properties.
        
        Args:
            v0, v1, v2: Vector vertices of the triangle
            material: Material defining the triangle's optical properties
        """
        self.add_object(EnhancedTriangle(v0, v1, v2, material))
    
    def add_cube(self, center, size, material):
        """
        Add a cube with material properties.
        
        Args:
            center: Vector position of the cube's center
            size: Side length of the cube
            material: Material defining the cube's optical properties
        """
        cube_triangles = MeshBuilder.create_cube(center, size, material.color)
        for triangle in cube_triangles:
            self.add_triangle(triangle.v0, triangle.v1, triangle.v2, material)
    
    def add_cylinder(self, center, radius, height, segments, material):
        """
        Add a cylinder with material properties.
        
        Args:
            center: Vector position of the cylinder's center
            radius: Radius of the cylinder
            height: Height of the cylinder
            segments: Number of segments around the circumference
            material: Material defining the cylinder's optical properties
        """
        cylinder_triangles = MeshBuilder.create_cylinder(center, radius, height, segments, material.color)
        for triangle in cylinder_triangles:
            self.add_triangle(triangle.v0, triangle.v1, triangle.v2, material)
    
    def add_checkerboard(self, y, size, dist, material1, material2):
        """
        Add a checkerboard pattern at specified y-coordinate.
        
        Args:
            y: Y coordinate of the plane
            size: Size of each square
            dist: Distance (in squares) from origin to edge
            material1, material2: Materials for the two colors
        """
        for row in range(-dist, dist):
            for col in range(-dist, dist):
                is_white = (row + col) % 2 == 0
                material = material1 if is_white else material2
                
                x1 = col * size
                x2 = (col + 1) * size
                z1 = row * size
                z2 = (row + 1) * size
                
                self.add_triangle(Vector(x1, y, z1), Vector(x2, y, z1), Vector(x2, y, z2), material)
                self.add_triangle(Vector(x1, y, z1), Vector(x2, y, z2), Vector(x1, y, z2), material)
    
    def reflect_ray(self, ray_dir, normal):
        """
        Calculate reflection direction.
        
        Args:
            ray_dir: Incoming ray direction Vector
            normal: Surface normal Vector
            
        Returns:
            Reflected ray direction Vector
        """
        return ray_dir - normal * (2 * ray_dir.dot(normal))
    
    def refract_ray(self, ray_dir, normal, n1, n2):
        """
        Calculate refraction direction using Snell's law.
        
        Args:
            ray_dir: Incoming ray direction Vector
            normal: Surface normal Vector
            n1, n2: Refractive indices of the two media
            
        Returns:
            Refracted ray direction Vector or reflection if total internal reflection occurs
        """
        # Ensure the normal is pointing against the incident ray
        if ray_dir.dot(normal) > 0:
            normal = normal * -1
            n1, n2 = n2, n1  # Swap refractive indices if we're exiting
        
        # Calculate refraction using Snell's law
        ratio = n1 / n2
        cos_i = -ray_dir.dot(normal)
        sin2_t = ratio * ratio * (1 - cos_i * cos_i)
        
        # Check for total internal reflection
        if sin2_t > 1:
            # Total internal reflection - return reflection instead
            return self.reflect_ray(ray_dir, normal)
        
        # Calculate refraction direction
        cos_t = math.sqrt(1 - sin2_t)
        return ray_dir * ratio + normal * (ratio * cos_i - cos_t)
    
    def fresnel(self, ray_dir, normal, n1, n2):
        """
        Calculate Fresnel coefficient (reflection vs. refraction ratio).
        
        Args:
            ray_dir: Incoming ray direction Vector
            normal: Surface normal Vector
            n1, n2: Refractive indices of the two media
            
        Returns:
            Reflectance factor (0.0-1.0)
        """
        # Ensure the normal is pointing against the incident ray
        if ray_dir.dot(normal) > 0:
            normal = normal * -1
            n1, n2 = n2, n1  # Swap indices if we're exiting
        
        # Calculate Fresnel using Schlick's approximation
        cos_i = -ray_dir.dot(normal)
        sin2_t = (n1 / n2) ** 2 * (1 - cos_i ** 2)
        
        # Total internal reflection
        if sin2_t > 1:
            return 1.0
        
        cos_t = math.sqrt(1 - sin2_t)
        
        # Compute Fresnel equations for polarized light
        rs = ((n1 * cos_i) - (n2 * cos_t)) / ((n1 * cos_i) + (n2 * cos_t))
        rp = ((n1 * cos_t) - (n2 * cos_i)) / ((n1 * cos_t) + (n2 * cos_i))
        
        # Return average reflectance (unpolarized light)
        return (rs * rs + rp * rp) / 2
    
    def trace_ray(self, ray_origin, ray_direction, depth=0):
        """
        Trace a ray through the scene, handling reflection and refraction.
        
        Args:
            ray_origin: Origin point of the ray (Vector)
            ray_direction: Direction vector of the ray (normalized Vector)
            depth: Current recursion depth
            
        Returns:
            RGB color tuple
        """
        # Stop recursing if we've hit the maximum depth
        if depth >= self.max_depth:
            return self.background_color
        
        # Find closest intersection
        obj, t = Ray.cast_ray(self.objects, ray_origin, ray_direction)
        
        if obj:
            # Calculate hit point and normal
            hit_point = ray_origin + ray_direction * t
            normal = obj.get_normal(hit_point)
            
            # Get material properties
            material = obj.get_material()
            local_color = material.color
            
            # Calculate lighting
            light_positions = [
                Vector(-300, -300, -200),  # Top-left light
                Vector(300, -300, -200),   # Top-right light
            ]
            
            # Ambient light component
            ambient_factor = 0.2
            light_intensity = 1.0 - ambient_factor
            
            # Start with ambient light
            brightness = ambient_factor
            
            # For each light source
            for light_pos in light_positions:
                # Vector from hit point to light
                light_dir = (light_pos - hit_point).normalize()
                
                # Check for shadows
                shadow_origin = hit_point + normal * 0.001  # Offset to prevent self-intersection
                shadow_direction = light_dir
                
                # Calculate distance to light
                light_distance = (light_pos - hit_point).magnitude()
                
                # Cast shadow ray
                shadow_obj, shadow_t = Ray.cast_ray(self.objects, shadow_origin, shadow_direction, light_distance)
                
                # If no object blocks the light, add diffuse lighting
                if shadow_obj is None:
                    # Calculate diffuse lighting using dot product of normal and light direction
                    diffuse = max(0, normal.dot(light_dir))
                    brightness += diffuse * light_intensity / len(light_positions)
            
            # Apply brightness to local color
            r = int(local_color[0] * brightness)
            g = int(local_color[1] * brightness)
            b = int(local_color[2] * brightness)
            local_color = (r, g, b)
            
            # Calculate reflection and refraction
            reflection_color = self.background_color
            refraction_color = self.background_color
            
            # Handle reflection if material is reflective
            if material.reflectivity > 0:
                reflection_dir = self.reflect_ray(ray_direction, normal)
                reflection_origin = hit_point + normal * 0.001  # Offset to avoid self-intersection
                reflection_color = self.trace_ray(reflection_origin, reflection_dir, depth + 1)
            
            # Handle transparency/refraction if material is transparent
            if material.transparency > 0:
                # Air refractive index = 1.0, material's refractive index from material
                refraction_dir = self.refract_ray(ray_direction, normal, 1.0, material.refractive_index)
                refraction_origin = hit_point - normal * 0.001  # Offset in opposite direction
                refraction_color = self.trace_ray(refraction_origin, refraction_dir, depth + 1)
            
            # Compute Fresnel factor for realistic glass
            if material.transparency > 0:
                fresnel = self.fresnel(ray_direction, normal, 1.0, material.refractive_index)
                reflection_contribution = material.reflectivity + material.transparency * fresnel
                refraction_contribution = material.transparency * (1 - fresnel)
            else:
                reflection_contribution = material.reflectivity
                refraction_contribution = 0
            
            # Blend local color with reflection and refraction
            direct_contribution = 1 - reflection_contribution - refraction_contribution
            
            final_r = int(local_color[0] * direct_contribution + 
                          reflection_color[0] * reflection_contribution +
                          refraction_color[0] * refraction_contribution)
            final_g = int(local_color[1] * direct_contribution + 
                          reflection_color[1] * reflection_contribution +
                          refraction_color[1] * refraction_contribution)
            final_b = int(local_color[2] * direct_contribution + 
                          reflection_color[2] * reflection_contribution +
                          refraction_color[2] * refraction_contribution)
            
            return (min(255, final_r), min(255, final_g), min(255, final_b))
        
        # No intersection, return background color
        return self.background_color
    
    def compute_pixel(self, xy):
        """
        Compute color for a single pixel.
        
        Args:
            xy: Tuple of (x, y) pixel coordinates
            
        Returns:
            Tuple of (x, y, color)
        """
        x, y = xy
        ray_origin = Vector(x - self.width / 2, y - self.height / 2, -500)
        ray_direction = Vector(0, 0, 1).normalize()
        
        color = self.trace_ray(ray_origin, ray_direction)
        return x, y, color
    
    def draw_scene(self):
        """
        Render the scene and save to an image file.
        """
        pixels = self.image.load()
        coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        
        print(f"Rendering scene with {len(self.objects)} objects...")
        print(f"Image resolution: {self.width}x{self.height}")
        start_time = time.time()
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.compute_pixel, coords)
        
        for x, y, color in results:
            pixels[x, y] = color
        
        end_time = time.time()
        print(f"Rendering finished in {end_time - start_time:.2f} seconds")
        
        self.image.save("raytraced_scene.png")
        print("Scene saved as raytraced_scene.png")
    
    def render_preview(self, scale=0.25, max_depth=2, output_file="preview.png"):
        """
        Render a quick preview of the scene with reduced settings.
        
        Args:
            scale: Scale factor for resolution (0.25 = quarter size)
            max_depth: Maximum ray recursion depth (lower = faster)
            output_file: Filename for the preview image
        
        Returns:
            Time taken to render the preview in seconds
        """
        import time
        
        # Save original settings
        orig_width, orig_height = self.width, self.height
        orig_depth = self.max_depth
        orig_image = self.image
        
        # Apply preview settings
        self.width = max(int(orig_width * scale), 1)
        self.height = max(int(orig_height * scale), 1)
        self.max_depth = max_depth
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        
        # Time the rendering
        print(f"Rendering preview at {self.width}x{self.height} with max_depth={max_depth}...")
        start_time = time.time()
        
        # Render the scene
        self.draw_scene()
        
        # Calculate and print time taken
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Preview rendered in {time_taken:.2f} seconds")
        
        # Save with the specified filename
        self.image.save(output_file)
        print(f"Preview saved as {output_file}")
        
        # Restore original settings
        self.width, self.height = orig_width, orig_height
        self.max_depth = orig_depth
        self.image = orig_image
        
        return time_taken

    def run(self):
        """
        Run the ray tracing process.
        """
        self.draw_scene()


def create_standard_materials():
    """
    Create a set of standard materials for common use cases.
    
    Returns:
        Dictionary of named materials
    """
    # Basic materials
    matte_red = Material((255, 50, 50))
    matte_green = Material((50, 255, 50))
    matte_blue = Material((50, 50, 255))
    matte_yellow = Material((255, 255, 50))
    matte_white = Material((255, 255, 255))
    matte_black = Material((0, 0, 0))
    
    # Reflective materials
    mirror = Material((255, 255, 255), reflectivity=0.9)
    chrome = Material((220, 220, 220), reflectivity=0.8)
    metal_red = Material((255, 50, 50), reflectivity=0.6)
    metal_blue = Material((50, 50, 255), reflectivity=0.6)
    
    # Transparent materials
    glass = Material((255, 255, 255), reflectivity=0.1, transparency=0.9, refractive_index=1.5)
    water = Material((200, 230, 255), reflectivity=0.1, transparency=0.8, refractive_index=1.33)
    diamond = Material((255, 255, 255), reflectivity=0.2, transparency=0.8, refractive_index=2.42)
    ruby = Material((255, 20, 20), reflectivity=0.1, transparency=0.7, refractive_index=1.77)
    
    return {
        'red': matte_red,
        'green': matte_green,
        'blue': matte_blue,
        'yellow': matte_yellow,
        'white': matte_white,
        'black': matte_black,
        'mirror': mirror,
        'chrome': chrome,
        'metal_red': metal_red, 
        'metal_blue': metal_blue,
        'glass': glass,
        'water': water,
        'diamond': diamond,
        'ruby': ruby
    }

def run_scene(scene_setup_func, width=1200, height=800, output_file=None):
    """
    Run a ray tracing scene with timing info.
    
    Args:
        scene_setup_func: Function that takes a Main instance and sets up the scene
        width: Image width in pixels
        height: Image height in pixels
        output_file: Optional custom output filename
    """
    start_time = time.time()
    
    # Initialize the ray tracer
    raster = Main(width, height)
    
    # Set up the scene
    print(f"Setting up scene: {scene_setup_func.__name__}")
    scene_setup_func(raster)
    
    # Check for preview flag
    preview_mode = False
    preview_scale = 0.25
    preview_depth = 2

    # Process additional command line arguments
    i = 4  # Start after scene_file, width, height
    while i < len(sys.argv):
        if sys.argv[i] == '--preview':
            preview_mode = True
            i += 1
            if i < len(sys.argv) and sys.argv[i].replace('.', '', 1).isdigit():
                preview_scale = float(sys.argv[i])
                i += 1
        elif sys.argv[i] == '--depth':
            i += 1
            if i < len(sys.argv) and sys.argv[i].isdigit():
                preview_depth = int(sys.argv[i])
                i += 1
        else:
            i += 1

    # Add this before "raster.run()"
    if preview_mode:
        print(f"Rendering preview (scale={preview_scale}, depth={preview_depth})...")
        raster.render_preview(
            scale=preview_scale, 
            max_depth=preview_depth, 
            output_file=f"{scene_name}_preview.png"
        )
        # Exit after preview unless --full flag is present
        if '--full' not in sys.argv:
            end_time = time.time()
            print(f"Total execution time: {end_time - start_time:.2f} seconds")
            sys.exit(0)

    # Render the scene
    print(f"Rendering scene with {len(raster.objects)} objects...")
    raster.run()
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    # Rename the output file if requested
    if output_file:
        import os
        os.rename("raytraced_scene.png", output_file)
        print(f"Saved as {output_file}")


"""
Updated 'if __name__ == "__main__":' section for main.py with working preview mode
"""

if __name__ == "__main__":
    # Check for help flag first
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("Ray Tracer Usage:")
        print("  python main.py scene_file [width height] [options]")
        print("\nOptions:")
        print("  --preview [scale]    Render a preview at reduced size (default scale: 0.25)")
        print("  --depth N            Set maximum recursion depth for preview (default: 2)")
        print("  --full               Render full quality after preview")
        print("\nExamples:")
        print("  python main.py Scenes/scene_basic --preview 0.1")
        print("  python main.py Scenes/scene_basic 1920 1080 --preview")
        sys.exit(0)
    
    # Parse command line arguments
    if len(sys.argv) <= 1:
        print("Usage: python main.py scene_file [width height] [options]")
        print("       python main.py --help   (for more information)")
        sys.exit(1)
    
    # First, identify any option flags
    preview_mode = False
    preview_scale = 0.25
    preview_depth = 2
    full_render = False
    width = 1200  # Default width
    height = 800  # Default height
    scene_file = None
    
    # Extract scene file and other parameters
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        # Skip option flags for scene file detection
        if arg.startswith('--'):
            # Handle options without immediately advancing
            if arg == '--preview':
                preview_mode = True
                i += 1
                # Check if next argument is a scale factor
                if i < len(sys.argv) and not sys.argv[i].startswith('--') and sys.argv[i].replace('.', '', 1).isdigit():
                    preview_scale = float(sys.argv[i])
                    i += 1
                continue
            elif arg == '--depth':
                i += 1
                if i < len(sys.argv) and sys.argv[i].isdigit():
                    preview_depth = int(sys.argv[i])
                    i += 1
                continue
            elif arg == '--full':
                full_render = True
                i += 1
                continue
            else:
                # Unknown option
                i += 1
                continue
        
        # First non-option argument is the scene file
        if scene_file is None:
            scene_file = arg
            i += 1
            continue
        
        # Next two non-option arguments might be width/height
        if scene_file is not None and width == 1200 and arg.isdigit():
            width = int(arg)
            i += 1
            continue
        
        if scene_file is not None and width != 1200 and height == 800 and arg.isdigit():
            height = int(arg)
            i += 1
            continue
        
        # Otherwise just advance
        i += 1
    
    # Make sure we have a scene file
    if scene_file is None:
        print("Error: No scene file specified")
        sys.exit(1)
    
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
    raster = Main(width, height)
    
    # Call the setup_scene function from the imported module
    print(f"Setting up scene from {scene_file}...")
    scene_module.setup_scene(raster)
    
    # Output filename based on scene name
    output_file = f"{scene_name}.png"
    
    # Handle preview mode if enabled
    if preview_mode:
        print(f"Rendering preview (scale={preview_scale}, depth={preview_depth})...")
        raster.render_preview(
            scale=preview_scale, 
            max_depth=preview_depth, 
            output_file=f"{scene_name}_preview.png"
        )
        
        if not full_render:
            end_time = time.time()
            print(f"Total execution time: {end_time - start_time:.2f} seconds")
            sys.exit(0)
    
    # Render the full quality scene
    raster.run()
    
    # Check if the output file exists and remove it if it does
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Rename the output file
    os.rename("raytraced_scene.png", output_file)
    print(f"Saved as {output_file}")
    
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")