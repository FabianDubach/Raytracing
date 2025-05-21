import time
import math
import multiprocessing
from PIL import Image
from vector import Vector
from ray import Ray, EnhancedSphere, EnhancedTriangle
from mesh_builder import MeshBuilder
from camera import Camera

class ConsoleProgressListener():
    def __init__(self, update_frequency=5.0):
        self.update_frequency = update_frequency
        self.last_percentage = 0
        self.start_time = None
    
    def on_progress_update(self, completed, total):
        if self.start_time is None:
            self.start_time = time.time()
        
        percentage = (completed / total) * 100
        
        if percentage - self.last_percentage >= self.update_frequency or percentage >= 100:       
            print(f"Rendering: {percentage:.1f}% complete ({completed}/{total} pixels)")
            self.last_percentage = percentage
    
    def on_render_complete(self, time_taken):
        print(f"Rendering complete in {time_taken:.2f} seconds")

class Renderer:
    def __init__(self, width, height, samples_per_pixel=1):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.objects = []
        self.lights = []
        self.max_depth = 8
        self.background_color = (70, 130, 180)
        self.progress_listeners = []
        self.ambient_factor = 0.2
        self.samples_per_pixel = samples_per_pixel
        
        self.camera = Camera(
            position=Vector(0, 0, -500),
            look_at=Vector(0, 0, 0),
            aspect_ratio=width/height
        )
        
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
        if ray_dir.dot(normal) > 0:
            normal = normal * -1
            n1, n2 = n2, n1
        
        ratio = n1 / n2
        cos_i = -ray_dir.dot(normal)
        sin2_t = ratio * ratio * (1 - cos_i * cos_i)
        
        if sin2_t > 1:
            return self.reflect_ray(ray_dir, normal)
        
        cos_t = math.sqrt(1 - sin2_t)
        return ray_dir * ratio + normal * (ratio * cos_i - cos_t)
    
    def fresnel(self, ray_dir, normal, n1, n2):
        if ray_dir.dot(normal) > 0:
            normal = normal * -1
            n1, n2 = n2, n1
        
        cos_i = -ray_dir.dot(normal)
        sin2_t = (n1 / n2) ** 2 * (1 - cos_i ** 2)
        
        if sin2_t > 1:
            return 1.0
        
        cos_t = math.sqrt(1 - sin2_t)
        
        rs = ((n1 * cos_i) - (n2 * cos_t)) / ((n1 * cos_i) + (n2 * cos_t))
        rp = ((n1 * cos_t) - (n2 * cos_i)) / ((n1 * cos_t) + (n2 * cos_i))
        
        return (rs * rs + rp * rp) / 2
    
    def trace_shadow_ray(self, origin, direction, max_distance):
        current_origin = origin.copy() if hasattr(origin, 'copy') else Vector(origin.x, origin.y, origin.z)
        transparency = 1.0
        
        max_bounces = 10
        for _ in range(max_bounces):
            obj, t = Ray.cast_ray(self.objects, current_origin, direction, max_distance)
            
            if obj is None:
                break
                
            if hasattr(obj, 'get_material'):
                material = obj.get_material()
                if hasattr(material, 'transparency') and material.transparency > 0:
                    transparency *= material.transparency
                    
                    if transparency < 0.01:
                        break
                        
                    hit_point = current_origin + direction * t
                    current_origin = hit_point + direction * 0.001
                else:
                    transparency = 0.0
                    break
            else:
                transparency = 0.0
                break
                
        return (1.0 - transparency)
    
    def trace_ray(self, ray_origin, ray_direction, depth=0, inside_medium=False):
        if depth >= self.max_depth:
            return self.background_color
        
        obj, t = Ray.cast_ray(self.objects, ray_origin, ray_direction)
        
        if obj:
            hit_point = ray_origin + ray_direction * t
            normal = obj.get_normal(hit_point)
            
            material = obj.get_material()
            local_color = material.color
            
            brightness = self.ambient_factor
            
            if not self.lights:
                light_positions = [
                    Vector(-300, -300, -200),
                    Vector(300, -300, -200),
                ]
                
                light_intensity = 1.0 - self.ambient_factor
                
                for light_pos in light_positions:
                    light_dir = (light_pos - hit_point).normalize()
                    
                    light_distance = (light_pos - hit_point).magnitude()
                    
                    shadow_origin = hit_point + normal * 0.001
                    
                    shadow_intensity = self.trace_shadow_ray(shadow_origin, light_dir, light_distance)
                    
                    if shadow_intensity < 1.0:
                        diffuse = max(0, normal.dot(light_dir))
                        brightness += diffuse * light_intensity * (1.0 - shadow_intensity) / len(light_positions)
            else:
                light_intensity = 1.0 - self.ambient_factor
                
                for light in self.lights:
                    light_dir = light.get_direction(hit_point)
                    light_distance = light.get_distance(hit_point)
                    
                    shadow_origin = hit_point + normal * 0.001
                    
                    shadow_intensity = self.trace_shadow_ray(shadow_origin, light_dir, light_distance)
                    
                    if shadow_intensity < 1.0:
                        diffuse = max(0, normal.dot(light_dir))
                        brightness += diffuse * light_intensity * light.intensity * (1.0 - shadow_intensity)
            
            r = int(local_color[0] * brightness)
            g = int(local_color[1] * brightness)
            b = int(local_color[2] * brightness)
            local_color = (r, g, b)
            
            reflection_color = self.background_color
            refraction_color = self.background_color
            
            if material.reflectivity > 0:
                reflection_dir = self.reflect_ray(ray_direction, normal)
                reflection_origin = hit_point + normal * 0.01
                reflection_color = self.trace_ray(reflection_origin, reflection_dir, depth + 1, inside_medium)
            
            if material.transparency > 0:
                is_entering = ray_direction.dot(normal) < 0
                
                n1 = 1.0 if is_entering else material.refractive_index
                n2 = material.refractive_index if is_entering else 1.0
                
                refraction_dir = self.refract_ray(ray_direction, normal, n1, n2)
                
                refraction_origin = hit_point + refraction_dir * 0.01
                
                refraction_color = self.trace_ray(refraction_origin, refraction_dir, depth + 1, not inside_medium)
                
                fresnel = self.fresnel(ray_direction, normal, n1, n2)
                
                reflection_contribution = material.reflectivity * (1 - material.transparency) + material.transparency * fresnel
                refraction_contribution = material.transparency * (1.0 - fresnel)
            else:
                reflection_contribution = material.reflectivity
                refraction_contribution = 0.0
            
            total = reflection_contribution + refraction_contribution
            if total > 1.0:
                reflection_contribution /= total
                refraction_contribution /= total
            
            direct_contribution = max(0.0, 1.0 - reflection_contribution - refraction_contribution)
            
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
        
        return self.background_color
    
    def compute_pixel(self, xy):
        x, y = xy
        
        r_total, g_total, b_total = 0, 0, 0
        
        for s in range(self.samples_per_pixel):
            if self.samples_per_pixel > 1:
                if self.samples_per_pixel > 4:
                    import random
                    sample_x = x + random.random()
                    sample_y = y + random.random()
                else:
                    sample_x = x + (s % 2) * 0.5
                    sample_y = y + (s // 2) * 0.5
            else:
                sample_x, sample_y = x, y
            
            if self.use_advanced_camera:
                ray_origin, ray_direction = self.camera.get_ray(sample_x, sample_y, self.width, self.height)
            else:
                ray_origin, ray_direction = self.camera.get_simple_ray(sample_x, sample_y, self.width, self.height)
            
            color = self.trace_ray(ray_origin, ray_direction, 0, None)
            
            r_total += color[0]
            g_total += color[1]
            b_total += color[2]
        
        r_avg = r_total // self.samples_per_pixel
        g_avg = g_total // self.samples_per_pixel
        b_avg = b_total // self.samples_per_pixel
        
        return x, y, (r_avg, g_avg, b_avg)
    
    def draw_scene(self, output_file="raytraced_scene.png"):
        pixels = self.image.load()
        coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        total_pixels = len(coords)
        
        print(f"Rendering scene with {len(self.objects)} objects and {len(self.lights)} lights...")
        print(f"Image resolution: {self.width}x{self.height}")
        start_time = time.time()
        
        progress_interval = max(1, total_pixels // 100)
        completed_pixels = 0
        
        with multiprocessing.Pool() as pool:
            chunk_size = max(100, total_pixels // 20)
            
            for i, result in enumerate(pool.imap(self.compute_pixel, coords, chunk_size)):
                x, y, color = result
                pixels[x, y] = color
                
                completed_pixels += 1
                if completed_pixels % progress_interval == 0 or completed_pixels == total_pixels:
                    self.notify_progress(completed_pixels, total_pixels)
        
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Rendering finished in {time_taken:.2f} seconds")
        
        self.notify_complete(time_taken)
        
        self.image.save(output_file)
        print(f"Scene saved as {output_file}")
    
    def render_preview(self, scale=0.25, max_depth=4, output_file="preview.png", samples=2):
        orig_width, orig_height = self.width, self.height
        orig_depth = self.max_depth
        orig_image = self.image
        orig_samples = self.samples_per_pixel
        
        self.width = max(int(orig_width * scale), 1)
        self.height = max(int(orig_height * scale), 1)
        self.max_depth = max_depth
        self.samples_per_pixel = samples
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        
        if self.use_advanced_camera:
            self.camera.aspect_ratio = self.width / self.height
            self.camera._calculate_basis()
        
        print(f"Rendering preview at {self.width}x{self.height} with max_depth={max_depth} and samples={samples}...")
        start_time = time.time()
        self.draw_scene(output_file)
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Preview rendered in {time_taken:.2f} seconds")
        
        self.width, self.height = orig_width, orig_height
        self.max_depth = orig_depth
        self.image = orig_image
        self.samples_per_pixel = orig_samples
        
        if self.use_advanced_camera:
            self.camera.aspect_ratio = self.width / self.height
            self.camera._calculate_basis()
        
        return time_taken

    def run(self, output_file="raytraced_scene.png", samples_per_pixel=None):
        if samples_per_pixel is not None:
            self.samples_per_pixel = samples_per_pixel
        self.draw_scene(output_file)