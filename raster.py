import pygame
import math
from vector import Vector
from circle import Circle


class Raster:

    
    def __init__(self, window_width, window_height):
        # Initialize pygame
        pygame.init()

        # Set window dimensions
        self.window_width = window_width
        self.window_height = window_height

        # Create a window
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Raster")

        # List of circles
        self.circles = []


    def add_circle(self, circle: Circle):
        self.circles.append(circle)


    def blend_colors(self, colors):
        """Blend multiple colors using additive mixing (like light)."""
        r = min(sum(color[0] for color in colors), 255)
        g = min(sum(color[1] for color in colors), 255)
        b = min(sum(color[2] for color in colors), 255)
        return (r, g, b)


    def draw_circles(self):
        for x in range(self.window_width):
            for y in range(self.window_height):
                overlapping_colors = []
                for circle in self.circles:
                    if (x - circle.center.x) ** 2 + (y - circle.center.y) ** 2 <= circle.radius ** 2:
                        overlapping_colors.append(circle.color)
                
                if overlapping_colors:
                    mixed_color = self.blend_colors(overlapping_colors)
                    self.window.set_at((x, y), mixed_color)
        pygame.display.update()


    def run(self):
        self.draw_circles()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()


# Main function to initialize and run the application
def main():
    window_width = 1000
    window_height = 800
    
    raster = Raster(window_width, window_height)
    
    # Create and add multiple circles
    raster.add_circle(Circle(Vector(300, 400), 150, (255, 0, 0)))  # Red
    raster.add_circle(Circle(Vector(500, 400), 150, (0, 255, 0)))  # Green
    raster.add_circle(Circle(Vector(400, 500), 150, (0, 0, 255)))  # Blue
    
    raster.run()

if __name__ == "__main__":
    main()