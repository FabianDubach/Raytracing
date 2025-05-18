import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from vector import Vector
from triangle import Triangle
from ray import EnhancedTriangle, Material

class FontRenderer:
    """
    Class for loading TTF fonts and converting text to 3D geometry for ray tracing.
    """
    
    def __init__(self, ttf_path, size=32, depth=5):
        """
        Initialize the font renderer.
        
        Args:
            ttf_path (str): Path to the TTF font file
            size (int): Font size in points
            depth (float): Depth/extrusion of the 3D text
        """
        self.ttf_path = ttf_path
        self.size = size
        self.depth = depth
        self.font = None
        
        try:
            # Load the font using PIL
            self.font = ImageFont.truetype(ttf_path, size)
            print(f"Successfully loaded font: {ttf_path}")
        except Exception as e:
            print(f"Error loading font: {e}")
            # Fall back to default font if available
            try:
                self.font = ImageFont.load_default()
                print("Using default font instead")
            except:
                print("Could not load any font")
    
    def get_text_dimensions(self, text):
        """
        Get the pixel dimensions of a text string.
        
        Args:
            text (str): The text to measure
            
        Returns:
            tuple: (width, height) in pixels
        """
        if self.font is None:
            return (0, 0)
        
        # Create a temporary image to measure text dimensions
        # The size doesn't matter as we're just measuring
        img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(img)
        
        # Get text bounding box
        try:
            # For newer versions of PIL
            left, top, right, bottom = draw.textbbox((0, 0), text, font=self.font)
            width = right - left
            height = bottom - top
        except AttributeError:
            # For older versions of PIL
            width, height = draw.textsize(text, font=self.font)
        
        return (width, height)
    
    def rasterize_text(self, text):
        """
        Convert text to a bitmap image.
        
        Args:
            text (str): The text to rasterize
            
        Returns:
            PIL.Image: Bitmap representation of the text
        """
        if self.font is None:
            return None
        
        # Get text dimensions
        width, height = self.get_text_dimensions(text)
        
        # Add padding
        padding = 5
        width += padding * 2
        height += padding * 2
        
        # Create a transparent image
        img = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(img)
        
        # Draw text in white on transparent background
        try:
            # For newer versions of PIL
            draw.text((padding, padding), text, font=self.font, fill=255)
        except:
            # For older versions of PIL
            draw.text((padding, padding), text, font=self.font, fill=255)
        
        return img
    
    def bitmap_to_triangles(self, bitmap, position, material, scale=1.0, rotation=(0, 0, 0)):
        """
        Convert a bitmap to 3D triangles for ray tracing.
        
        Args:
            bitmap (PIL.Image): The bitmap image
            position (Vector): The 3D position where the text should be placed
            material (Material): The material to use for the triangles
            scale (float): The scale factor for the text
            rotation (tuple): Rotation angles in degrees (x, y, z)
            
        Returns:
            list: List of EnhancedTriangle objects
        """
        if bitmap is None:
            return []
        
        # Get bitmap dimensions
        width, height = bitmap.size
        
        # Convert the bitmap to a numpy array for easier processing
        pixels = np.array(bitmap)
        
        triangles = []
        
        # Threshold for considering a pixel as part of the text (0-255)
        threshold = 128
        
        # Iterate through pixels and create triangles for text
        for y in range(height-1):
            for x in range(width-1):
                # Check if current pixel is part of the text
                if pixels[y, x] > threshold:
                    # Calculate 3D positions
                    # Scale and position the vertices
                    x_pos = position.x + (x - width/2) * scale
                    y_pos = position.y - (y - height/2) * scale  # Flip y for proper orientation
                    z_pos = position.z
                    
                    # Front face vertices
                    v0 = Vector(x_pos, y_pos, z_pos)
                    v1 = Vector(x_pos + scale, y_pos, z_pos)
                    v2 = Vector(x_pos, y_pos - scale, z_pos)
                    v3 = Vector(x_pos + scale, y_pos - scale, z_pos)
                    
                    # Back face vertices
                    v4 = Vector(x_pos, y_pos, z_pos + self.depth)
                    v5 = Vector(x_pos + scale, y_pos, z_pos + self.depth)
                    v6 = Vector(x_pos, y_pos - scale, z_pos + self.depth)
                    v7 = Vector(x_pos + scale, y_pos - scale, z_pos + self.depth)
                    
                    # Apply rotation if needed
                    if rotation != (0, 0, 0):
                        # Import the utility function for rotation
                        from scene_utils import rotate_vertex
                        center = Vector(position.x, position.y, position.z + self.depth/2)
                        v0 = rotate_vertex(v0, center, rotation)
                        v1 = rotate_vertex(v1, center, rotation)
                        v2 = rotate_vertex(v2, center, rotation)
                        v3 = rotate_vertex(v3, center, rotation)
                        v4 = rotate_vertex(v4, center, rotation)
                        v5 = rotate_vertex(v5, center, rotation)
                        v6 = rotate_vertex(v6, center, rotation)
                        v7 = rotate_vertex(v7, center, rotation)
                    
                    # Create triangles for the front face
                    triangles.append(EnhancedTriangle(v0, v1, v2, material))
                    triangles.append(EnhancedTriangle(v1, v3, v2, material))
                    
                    # Create triangles for the back face
                    triangles.append(EnhancedTriangle(v4, v6, v5, material))
                    triangles.append(EnhancedTriangle(v5, v6, v7, material))
                    
                    # Create triangles for the sides (only where edges are exposed)
                    # Top edge
                    if y == 0 or pixels[y-1, x] <= threshold:
                        triangles.append(EnhancedTriangle(v0, v4, v1, material))
                        triangles.append(EnhancedTriangle(v1, v4, v5, material))
                    
                    # Bottom edge
                    if y == height-2 or pixels[y+1, x] <= threshold:
                        triangles.append(EnhancedTriangle(v2, v3, v6, material))
                        triangles.append(EnhancedTriangle(v3, v7, v6, material))
                    
                    # Left edge
                    if x == 0 or pixels[y, x-1] <= threshold:
                        triangles.append(EnhancedTriangle(v0, v2, v4, material))
                        triangles.append(EnhancedTriangle(v2, v6, v4, material))
                    
                    # Right edge
                    if x == width-2 or pixels[y, x+1] <= threshold:
                        triangles.append(EnhancedTriangle(v1, v5, v3, material))
                        triangles.append(EnhancedTriangle(v3, v5, v7, material))
        
        return triangles
    
    def text_to_triangles(self, text, position, material, scale=1.0, rotation=(0, 0, 0)):
        """
        Convert text to 3D triangles for ray tracing.
        
        Args:
            text (str): The text to convert
            position (Vector): The 3D position where the text should be placed
            material (Material): The material to use for the triangles
            scale (float): The scale factor for the text
            rotation (tuple): Rotation angles in degrees (x, y, z)
            
        Returns:
            list: List of EnhancedTriangle objects
        """
        # Rasterize the text to a bitmap
        bitmap = self.rasterize_text(text)
        
        # Convert the bitmap to triangles
        return self.bitmap_to_triangles(bitmap, position, material, scale, rotation)