"""
renderer.py - Ray tracing renderer class
"""
import time
import math
import multiprocessing
from PIL import Image
from vector import Vector
from ray import Ray, EnhancedSphere, EnhancedTriangle
from mesh_builder import MeshBuilder
from camera import Camera
from lighting import Light, PointLight, DirectionalLight

class ProgressListener:
    """
    Base class for progress listeners to track rendering progress.
    """
    def on_progress_update(self, completed, total):
        """
        Called when progress is updated.
        
        Args:
            completed: Number of completed pixels
            total: Total number of pixels to render
        """
        pass

    def on_render_complete(self, time_taken):
        """
        Called when rendering is complete.
        
        Args:
            time_taken: Time taken to render in seconds
        """
        pass

class ConsoleProgressListener(ProgressListener):
    """
    Progress listener that prints updates to the console.
    """
    def __init__(self, update_frequency=5.0):
        """
        Initialize the console progress listener.
        
        Args:
            update_frequency: How often to print updates in percentage points
        """
        self.update_frequency = update_frequency
        self.last_percentage = 0
        self.start_time = None
    
    def on_progress_update(self, completed, total):
        """
        Print progress updates to the console when threshold is reached.
        
        Args:
            completed: Number of completed pixels
            total: Total number of pixels to render
        """
        if self.start_time is None:
            self.start_time = time.time()
        
        percentage = (completed / total) * 100
        
        # Only update when we've reached the next threshold
        if percentage - self.last_percentage >= self.update_frequency or percentage >= 100:       
            print(f"Rendering: {percentage:.1f}% complete ({completed}/{total} pixels)")
            self.last_percentage = percentage
    
    def on_render_complete(self, time_taken):
        """
        Print completion message.
        
        Args:
            time_taken: Time taken to render in seconds
        """
        print(f"Rendering complete in {time_taken:.2f} seconds")

class Renderer:
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
        self.lights = []   # List to hold all lights
        self.max_depth = 5  # Maximum ray recursion depth
        self.background_color = (70, 130, 180)  # Steel blue sky
        self.progress_listeners = []  # List of progress listeners
        self.ambient_factor = 0.2  # Global ambient light factor
        
        # Default camera (compatible with original code)
        self.camera = Camera(
            position=Vector(0, 0, -500),
            look_at=Vector(0, 0, 0),
            aspect_ratio=width/height
        )
        
        # Flag to use advanced camera or legacy mode
        self.use_advanced_camera = False
        
        # Add default lights if none are specified later
        self.add_light(PointLight(Vector(-300, -300, -200)))
        self.add_light(PointLight(Vector(300, -300, -200)))
    
    def add_progress_listener(self, listener):
        """
        Add a progress listener to track rendering progress.
        
        Args:
            listener: A ProgressListener instance
        """
        if listener not in self.progress_listeners:
            self.progress_listeners.append(listener)
    
    def notify_progress(self, completed, total):
        """
        Notify all progress listeners of rendering progress.
        
        Args:
            completed: Number of completed pixels
            total: Total number of pixels to render
        """
        for listener in self.progress_listeners:
            listener.on_progress_update(completed, total)
    
    def notify_complete(self, time_taken):
        """
        Notify all progress listeners that rendering is complete.
        
        Args:
            time_taken: Time taken to render in seconds
        """
        for listener in self.progress_listeners:
            listener.on_render_complete(time_taken)
    
    def set_camera(self, position, look_at, up=None, fov=60):
        """
        Set a new camera for the renderer.
        
        Args:
            position: Vector position of the camera
            look_at: Vector position the camera is looking at
            up: Vector defining the up direction (default is Vector(0, 1, 0))
            fov: Field of view in degrees (default is 60)
        """
        self.camera = Camera(
            position=position,
            look_at=look_at,
            up=up,
            fov=fov,
            aspect_ratio=self.width/self.height
        )
        self.use_advanced_camera = True
    
    def set_ambient_light(self, factor):
        """
        Set the global ambient light intensity.
        
        Args:
            factor: Ambient light factor (0.0-1.0)
        """
        self.ambient_factor = max(0.0, min(1.0, factor))
    
    def add_light(self, light):
        """
        Add a light to the scene.
        
        Args:
            light: Light object (PointLight, DirectionalLight, etc.)
        """
        self.lights.append(light)
    
    def clear_lights(self):
        """
        Remove all lights from the scene.
        """
        self.lights = []
    
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
            
            # Start with ambient light
            brightness = self.ambient_factor
            
            # If there are no lights, use the hardcoded light positions (fallback)
            if not self.lights:
                light_positions = [
                    Vector(-300, -300, -200),  # Top-left light
                    Vector(300, -300, -200),   # Top-right light
                ]
                
                # Ambient light component
                light_intensity = 1.0 - self.ambient_factor
                
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
            else:
                # Use the proper light system
                light_intensity = 1.0 - self.ambient_factor
                
                # For each light source
                for light in self.lights:
                    # Get light direction and distance
                    light_dir = light.get_direction(hit_point)
                    light_distance = light.get_distance(hit_point)
                    
                    # Check for shadows
                    shadow_origin = hit_point + normal * 0.001  # Offset to prevent self-intersection
                    
                    # Cast shadow ray
                    shadow_obj, shadow_t = Ray.cast_ray(self.objects, shadow_origin, light_dir, light_distance)
                    
                    # If no object blocks the light, add diffuse lighting
                    if shadow_obj is None:
                        # Calculate diffuse lighting using dot product of normal and light direction
                        diffuse = max(0, normal.dot(light_dir))
                        brightness += diffuse * light_intensity * light.intensity
            
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
        
        # Get ray from camera
        if self.use_advanced_camera:
            ray_origin, ray_direction = self.camera.get_ray(x, y, self.width, self.height)
        else:
            ray_origin, ray_direction = self.camera.get_simple_ray(x, y, self.width, self.height)
        
        color = self.trace_ray(ray_origin, ray_direction)
        return x, y, color
    
    def draw_scene(self, output_file="raytraced_scene.png"):
        """
        Render the scene and save to an image file.
        
        Args:
            output_file: Filename to save the rendered image
        """
        pixels = self.image.load()
        coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        total_pixels = len(coords)
        
        print(f"Rendering scene with {len(self.objects)} objects and {len(self.lights)} lights...")
        print(f"Image resolution: {self.width}x{self.height}")
        start_time = time.time()
        
        # Set up progress tracking
        progress_interval = max(1, total_pixels // 100)  # Update progress every 1%
        completed_pixels = 0
        
        # Use multiprocessing for better performance
        with multiprocessing.Pool() as pool:
            # Process in chunks to allow progress updates
            chunk_size = max(100, total_pixels // 20)  # 5% at a time
            
            for i, result in enumerate(pool.imap(self.compute_pixel, coords, chunk_size)):
                x, y, color = result
                pixels[x, y] = color
                
                # Update progress
                completed_pixels += 1
                if completed_pixels % progress_interval == 0 or completed_pixels == total_pixels:
                    self.notify_progress(completed_pixels, total_pixels)
        
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Rendering finished in {time_taken:.2f} seconds")
        
        # Notify listeners that rendering is complete
        self.notify_complete(time_taken)
        
        self.image.save(output_file)
        print(f"Scene saved as {output_file}")
    
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
        # Save original settings
        orig_width, orig_height = self.width, self.height
        orig_depth = self.max_depth
        orig_image = self.image
        
        # Apply preview settings
        self.width = max(int(orig_width * scale), 1)
        self.height = max(int(orig_height * scale), 1)
        self.max_depth = max_depth
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        
        # Update camera aspect ratio if using advanced camera
        if self.use_advanced_camera:
            self.camera.aspect_ratio = self.width / self.height
            self.camera._calculate_basis()
        
        # Time the rendering
        print(f"Rendering preview at {self.width}x{self.height} with max_depth={max_depth}...")
        start_time = time.time()
        
        # Render the scene
        self.draw_scene(output_file)
        
        # Calculate and print time taken
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Preview rendered in {time_taken:.2f} seconds")
        
        # Restore original settings
        self.width, self.height = orig_width, orig_height
        self.max_depth = orig_depth
        self.image = orig_image
        
        # Update camera aspect ratio if using advanced camera
        if self.use_advanced_camera:
            self.camera.aspect_ratio = self.width / self.height
            self.camera._calculate_basis()
        
        return time_taken

    def run(self, output_file="raytraced_scene.png"):
        """
        Run the ray tracing process and save to a file.
        
        Args:
            output_file: Filename to save the rendered image
        """
        self.draw_scene(output_file)