import pygame
import random
from vector import Vector
from sphere import Sphere

class Raster3D:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("3D Spheres")

        self.spheres = []
    
    def add_sphere(self, sphere: Sphere):
        self.spheres.append(sphere)

    def generate_random_spheres(self, num_spheres):
        spheres = []
        for _ in range(num_spheres):
            x = random.randint(-self.width // 2, self.width // 2)  # Spread across screen width
            y = random.randint(-self.height // 2, self.height // 2)  # Spread across screen height
            z = random.randint(50, 400)  # Vary depth (closer or farther)
            radius = random.randint(10, 40)  # Keep radii reasonable
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random colors
            spheres.append(Sphere(Vector(x, y, z), radius, color))
        return spheres    

    def cast_ray(self, ray_origin, ray_direction):
        """ Cast a ray and find closest sphere """
        closest_t = float("inf")
        closest_sphere = None

        for sphere in self.spheres:
            t = sphere.intersects(ray_origin, ray_direction)
            if t and t < closest_t:
                closest_t = t
                closest_sphere = sphere

        return closest_sphere, closest_t

    def draw_scene(self):
        """ Render the scene with orthographic projection """
        for x in range(self.width):
            for y in range(self.height):
                # Each pixel has its own ray origin
                ray_origin = Vector(x - self.width / 2, y - self.height / 2, -500)
                ray_direction = Vector(0, 0, 1)  # Rays always point straight forward

                sphere, t = self.cast_ray(ray_origin, ray_direction)

                if sphere:
                    hit_point = ray_origin + ray_direction * t
                    normal = sphere.get_normal(hit_point)
                    light_dir = Vector(0, 0, -1).normalize()  # Simple light direction
                    brightness = max(0, normal.dot(light_dir))  # Lambertian shading
                    color = tuple(int(c * brightness) for c in sphere.color)
                    self.window.set_at((x, y), color)

        pygame.display.update()
        
    def generate_sphere_face(self):
        # Add spheres at different depths
        self.add_sphere(Sphere(Vector(0, 0, 0), 70, (255, 0, 0)))  # Red sphere
        self.add_sphere(Sphere(Vector(140, -140, 150), 80, (0, 255, 0)))  # Green sphere 1
        self.add_sphere(Sphere(Vector(-140, -140, 150), 80, (0, 255, 0)))  # Green sphere 2
        self.add_sphere(Sphere(Vector(0, 0, 300), 250, (0, 0, 255)))  # Blue sphere
        self.add_sphere(Sphere(Vector(-100, -100, 230), 150, (0, 255, 255)))  # Cyan sphere 1
        self.add_sphere(Sphere(Vector(100, -100, 230), 150, (0, 255, 255)))  # Cyan sphere 1
        
    def generate_random_num_of_spheres(self, num):
        spheres = self.generate_random_spheres(num)
        for sphere in spheres:
            self.add_sphere(sphere)

    def run(self):
        self.draw_scene()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()


def main():
    raster = Raster3D(800, 600)

    # raster.generate_sphere_face()
    
    # raster.generate_random_num_of_spheres(2)

    raster.run()

if __name__ == "__main__":
    main()