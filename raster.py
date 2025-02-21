import pygame
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
        angle = pygame.math.atan2(dy, dx)

        # Define two points for the arrowhead
        p1 = (end.x - size * pygame.math.cos(angle - pygame.math.pi / 6),
              end.y - size * pygame.math.sin(angle - pygame.math.pi / 6))
        p2 = (end.x - size * pygame.math.cos(angle + pygame.math.pi / 6),
              end.y - size * pygame.math.sin(angle + pygame.math.pi / 6))
        
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

    # Draw the circle and run the application
    raster.draw_circle()
    raster.run()
    
    # Create Vector instances for the start and end points
    start_vector = Vector(0, 0)
    end_vector = Vector(window_width / 2, window_height / 2)

    # Draw vector
    raster.draw_vector(start_vector, end_vector, color=(0, 255, 0), width=10)

# Run the main function
if __name__ == "__main__":
    main()