import pygame
import math
from vector import Vector  # Make sure the Vector class is imported correctly

class Raster:
    def __init__(self, window_width, window_height, radius, color):
        # Initialize pygame
        pygame.init()

        # Set window dimensions
        self.window_width = window_width
        self.window_height = window_height
        self.radius = radius
        self.color = color

        # Create a window
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Raster")

    def draw_circle(self):
        # Loop through each pixel and set its color
        for x in range(self.window_width):
            for y in range(self.window_height):
                if (x - self.window_width / 2) ** 2 + (y - self.window_height / 2) ** 2 <= self.radius ** 2:
                    self.window.set_at((x, y), self.color)

        # Update the display
        pygame.display.update()

    def draw_vector(self, start: Vector, end: Vector, color=(0, 255, 0), width=10):
        # Use pygame's draw.line to draw the vector
        pygame.draw.line(self.window, color, (start.x, start.y), (end.x, end.y), width)
        
        # Optionally, draw an arrowhead (for visualization)
        self.draw_arrowhead(start, end, color)

        # Update the display
        pygame.display.update()
        

    def draw_arrowhead(self, start, end, color, size=10):
        """Draw an arrowhead at the end of the vector."""
        dx = end.x - start.x
        dy = end.y - start.y
        angle = math.atan2(dy, dx)

        # Define two points for the arrowhead
        p1 = (end.x - size * math.cos(angle - math.pi / 6),
            end.y - size * math.sin(angle - math.pi / 6))
        p2 = (end.x - size * math.cos(angle + math.pi / 6),
            end.y - size * math.sin(angle + math.pi / 6))
        
        # Draw the arrowhead lines
        pygame.draw.line(self.window, color, (end.x, end.y), p1, 2)
        pygame.draw.line(self.window, color, (end.x, end.y), p2, 2)

    
    def run(self):
        # Event loop to keep the window open
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        # Quit pygame
        pygame.quit()


# Main function to initialize and run the application
def main():
    # Set window dimensions, radius, and color
    window_width = 1000
    window_height = 800
    radius = 100
    color = (255, 0, 0)

    # Create a Raster instance
    raster = Raster(window_width, window_height, radius, color)

    # Draw the circle
    raster.draw_circle()
    
    # Create Vector instances for the start and end points
    start_vector1 = Vector(0, 0)
    end_vector1 = Vector(window_width / 2, window_height / 2)
    
    start_vector2 = Vector(0, 0)
    end_vector2 = Vector(200, 100)
    
    start_vector3 = Vector(0, 0)
    end_vector3 = end_vector2.__add__(end_vector1)

    # Draw vector **before** running the event loop
    raster.draw_vector(start_vector1, end_vector1, color=(0, 0, 255), width=5)
    raster.draw_vector(start_vector2, end_vector2, color=(0, 255, 0), width=5)
    raster.draw_vector(start_vector3, end_vector3, color=(255, 255, 0), width=5)

    # Run the application
    raster.run()

# Run the main function
if __name__ == "__main__":
    main()