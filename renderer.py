import time
import math
import multiprocessing
from PIL import Image
from vector import Vector
from ray import Ray, EnhancedSphere, EnhancedTriangle
from mesh_builder import MeshBuilder
from camera import Camera

class ConsoleProgressListener():
    """
    Progress listener that prints updates to the console.
    """
    def __init__(self, update_frequency=5.0):
        self.update_frequency = update_frequency
        self.last_percentage = 0
        self.start_time = None
    
    def on_progress_update(self, completed, total):
        if self.start_time is None:
            self.start_time = time.time()
        
        percentage = (completed / total) * 100
        
        # Only update when we've reached the next threshold
        if percentage - self.last_percentage >= self.update_frequency or percentage >= 100:       
            print(f"Rendering: {percentage:.1f}% complete ({completed}/{total} pixels)")
            self.last_percentage = percentage
    
    def on_render_complete(self, time_taken):
        print(f"Rendering complete in {time_taken:.2f} seconds")

class Renderer:
    """
    Main ray tracing engine with support for reflection, refraction, and materials.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.objects = []  # List to hold all renderable objects
        self.lights = []   # List to hold all lights
        self.max_depth = 8  # Increased max recursion depth for better transparency
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
    
    def add_progress_listener(self, listener):
        if listener not in self.progress_listeners:
            self.progress_listeners.append(listener)
    
    def notify_progress(self, completed, total):
        for listener in self.progress_listeners:
            listener.on_progress_update(completed, total)
    
    def notify_complete(self, time_taken):
        for listener in self.progress_listeners:
            listener.on_render_complete(time_taken)
    
    def set_camera(self, position, look_at, up=None, fov=60):
        self.camera = Camera(
            position=position,
            look_at=look_at,
            up=up,
            fov=fov,
            aspect_ratio=self.width/self.height
        )
        self.use_advanced_camera = True
    
    def set_ambient_light(self, factor):
        self.ambient_factor = max(0.0, min(1.0, factor))
    
    def add_light(self, light):
        self.lights.append(light)
    
    def clear_lights(self):
        self.lights = []
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def add_objects(self, objects):
        self.objects.extend(objects)
    
    def add_sphere(self, center, radius, material):
        self.add_object(EnhancedSphere(center, radius, material))
    
    def add_triangle(self, v0, v1, v2, material):
        self.add_object(EnhancedTriangle(v0, v1, v2, material))
    
    def add_cube(self, center, size, material):
        cube_triangles = MeshBuilder.create_cube(center, size, material.color)
        for triangle in cube_triangles:
            self.add_triangle(triangle.v0, triangle.v1, triangle.v2, material)
    
    def add_cylinder(self, center, radius, height, segments, material):
        cylinder_triangles = MeshBuilder.create_cylinder(center, radius, height, segments, material.color)
        for triangle in cylinder_triangles:
            self.add_triangle(triangle.v0, triangle.v1, triangle.v2, material)
    
    def add_checkerboard(self, y, size, dist, material1, material2):
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
        return ray_dir - normal * (2 * ray_dir.dot(normal))
    
    def refract_ray(self, ray_dir, normal, n1, n2):
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
    
    def trace_shadow_ray(self, origin, direction, max_distance):
        """
        Trace a shadow ray and return accumulated transparency
        """
        current_origin = origin.copy() if hasattr(origin, 'copy') else Vector(origin.x, origin.y, origin.z)
        transparency = 1.0  # Start with full transparency (no shadow)
        
        # Maximum shadow bounces to prevent infinite loops
        max_bounces = 10
        for _ in range(max_bounces):
            obj, t = Ray.cast_ray(self.objects, current_origin, direction, max_distance)
            
            if obj is None:
                # No more intersections, ray reaches the light
                break
                
            # Check if object has transparency
            if hasattr(obj, 'get_material'):
                material = obj.get_material()
                if hasattr(material, 'transparency') and material.transparency > 0:
                    # Let some light through based on transparency
                    transparency *= material.transparency
                    
                    # If object is nearly fully transparent, just ignore it
                    if transparency < 0.01:
                        break
                        
                    # Continue tracing through the object
                    hit_point = current_origin + direction * t
                    current_origin = hit_point + direction * 0.001
                else:
                    # Opaque object blocks all light
                    transparency = 0.0
                    break
            else:
                # Object without material blocks all light
                transparency = 0.0
                break
                
        return (1.0 - transparency)  # Convert to shadow intensity (0 = no shadow, 1 = full shadow)
    
    def trace_ray(self, ray_origin, ray_direction, depth=0, inside_medium=False):
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
                    
                    # Calculate distance to light
                    light_distance = (light_pos - hit_point).magnitude()
                    
                    # Offset to prevent self-intersection
                    shadow_origin = hit_point + normal * 0.001
                    
                    # Use the shadow ray tracer
                    shadow_intensity = self.trace_shadow_ray(shadow_origin, light_dir, light_distance)
                    
                    # Add diffuse lighting (attenuated by shadow)
                    if shadow_intensity < 1.0:
                        diffuse = max(0, normal.dot(light_dir))
                        brightness += diffuse * light_intensity * (1.0 - shadow_intensity) / len(light_positions)
            else:
                # Use the proper light system
                light_intensity = 1.0 - self.ambient_factor
                
                # For each light source
                for light in self.lights:
                    # Get light direction and distance
                    light_dir = light.get_direction(hit_point)
                    light_distance = light.get_distance(hit_point)
                    
                    # Offset to prevent self-intersection
                    shadow_origin = hit_point + normal * 0.001
                    
                    # Use the shadow ray tracer
                    shadow_intensity = self.trace_shadow_ray(shadow_origin, light_dir, light_distance)
                    
                    # Add diffuse lighting (attenuated by shadow)
                    if shadow_intensity < 1.0:
                        diffuse = max(0, normal.dot(light_dir))
                        brightness += diffuse * light_intensity * light.intensity * (1.0 - shadow_intensity)
            
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
                reflection_origin = hit_point + normal * 0.01  # Offset to avoid self-intersection
                reflection_color = self.trace_ray(reflection_origin, reflection_dir, depth + 1, inside_medium)  # Keep same medium
            
            # Handle transparency/refraction if material is transparent
            if material.transparency > 0:
                # Determine if we're entering or exiting based on ray direction relative to normal
                is_entering = ray_direction.dot(normal) < 0
                
                # Use the correct refractive indices based on whether we're entering or exiting
                n1 = 1.0 if is_entering else material.refractive_index
                n2 = material.refractive_index if is_entering else 1.0
                
                # Calculate refraction with correct indices
                refraction_dir = self.refract_ray(ray_direction, normal, n1, n2)
                
                # Create offset origin in refraction direction
                refraction_origin = hit_point + refraction_dir * 0.01
                
                # Recursive ray trace with flipped inside_medium state
                refraction_color = self.trace_ray(refraction_origin, refraction_dir, depth + 1, not inside_medium)
                
                # Calculate Fresnel with correct indices (only calculate once!)
                fresnel = self.fresnel(ray_direction, normal, n1, n2)
                # Reduce the influence of Fresnel to make transparency more dominant
                fresnel *= 0.1  # Scale down Fresnel effect
                
                reflection_contribution = material.reflectivity * (1 - material.transparency) + material.transparency * fresnel
                refraction_contribution = material.transparency * (1.0 - fresnel)
            else:
                reflection_contribution = material.reflectivity
                refraction_contribution = 0.0
            
            # Ensure contributions don't exceed 1.0
            total = reflection_contribution + refraction_contribution
            if total > 1.0:
                reflection_contribution /= total
                refraction_contribution /= total
            
            # Calculate direct contribution
            direct_contribution = max(0.0, 1.0 - reflection_contribution - refraction_contribution)
            
            # Blend colors
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
        x, y = xy
        
        # Get ray from camera
        if self.use_advanced_camera:
            ray_origin, ray_direction = self.camera.get_ray(x, y, self.width, self.height)
        else:
            ray_origin, ray_direction = self.camera.get_simple_ray(x, y, self.width, self.height)
        
        # Pass inside_medium=False to start outside any medium
        color = self.trace_ray(ray_origin, ray_direction, 0, False)
        return x, y, color
    
    def draw_scene(self, output_file="raytraced_scene.png"):
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
    
    def render_preview(self, scale=0.25, max_depth=4, output_file="preview.png"):
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
        self.draw_scene(output_file)