import random
import time
import multiprocessing
from vector import Vector
from sphere import Sphere
from ray import Ray
from PIL import Image

class Main:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.spheres = []
    
    def add_sphere(self, sphere: Sphere):
        self.spheres.append(sphere)
    
    def generate_sphere_face(self):
        self.add_sphere(Sphere(Vector(0, 0, 0), 70, (255, 0, 0)))
        self.add_sphere(Sphere(Vector(140, -140, 150), 80, (0, 255, 0)))
        self.add_sphere(Sphere(Vector(-140, -140, 150), 80, (0, 255, 0)))
        self.add_sphere(Sphere(Vector(0, 0, 300), 250, (0, 0, 255)))
        self.add_sphere(Sphere(Vector(-100, -100, 230), 150, (0, 255, 255)))
        self.add_sphere(Sphere(Vector(100, -100, 230), 150, (0, 255, 255)))
    
    def generate_random_spheres(self, num_spheres):
        spheres = []
        for _ in range(num_spheres):
            x = random.randint(-self.width // 2, self.width // 2)
            y = random.randint(-self.height // 2, self.height // 2)
            z = random.randint(50, 400)
            radius = random.randint(10, 40)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            spheres.append(Sphere(Vector(x, y, z), radius, color))
        return spheres    

    def compute_pixel(self, xy):
        x, y = xy
        ray_origin = Vector(x - self.width / 2, y - self.height / 2, -500)
        ray_direction = Vector(0, 0, 1)
        sphere, t = Ray.cast_ray(self.spheres, ray_origin, ray_direction)
        if sphere:
            hit_point = ray_origin + ray_direction * t
            normal = sphere.get_normal(hit_point)
            light_dir = Vector(0, 0, -1).normalize()
            brightness = max(0, normal.dot(light_dir))
            color = tuple(int(c * brightness) for c in sphere.color)
            return x, y, color
        return x, y, (0, 0, 0)
    
    def draw_scene(self):
        pixels = self.image.load()
        coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.compute_pixel, coords)
        
        for x, y, color in results:
            pixels[x, y] = color
        
        self.image.save("raytraced_scene.png")
        print("Scene saved as raytraced_scene.png")
    
    def run(self):
        self.draw_scene()

def main():
    start_time = time.time()
    raster = Main(1200, 800)
    raster.generate_sphere_face()
    raster.run()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()