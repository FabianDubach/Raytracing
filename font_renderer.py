import numpy as np
from PIL import Image, ImageDraw, ImageFont
from vector import Vector
from ray import EnhancedTriangle

class FontRenderer:
    def __init__(self, ttf_path, size=32, depth=5):
        self.ttf_path = ttf_path
        self.size = size
        self.depth = depth
        self.font = None
        
        try:
            self.font = ImageFont.truetype(ttf_path, size)
            print(f"Successfully loaded font: {ttf_path}")
        except Exception as e:
            print(f"Error loading font: {e}")
            try:
                self.font = ImageFont.load_default()
                print("Using default font instead")
            except:
                print("Could not load any font")
    
    def get_text_dimensions(self, text):
        if self.font is None:
            return (0, 0)
        
        img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(img)
        
        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=self.font)
            width = right - left
            height = bottom - top
        except AttributeError:
            width, height = draw.textsize(text, font=self.font)
        
        return (width, height)
    
    def rasterize_text(self, text):
        if self.font is None:
            return None
        
        width, height = self.get_text_dimensions(text)
        
        padding = 5
        width += padding * 2
        height += padding * 2
        
        img = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(img)
        
        try:
            draw.text((padding, padding), text, font=self.font, fill=255)
        except:
            draw.text((padding, padding), text, font=self.font, fill=255)
        
        return img
    
    def bitmap_to_triangles(self, bitmap, position, material, scale=1.0, rotation=(0, 0, 0)):
        if bitmap is None:
            return []
        
        width, height = bitmap.size
        pixels = np.array(bitmap)
        triangles = []
        threshold = 128
        
        for y in range(height-1):
            for x in range(width-1):
                if pixels[y, x] > threshold:
                    x_pos = position.x + (x - width/2) * scale
                    y_pos = position.y - (y - height/2) * scale
                    z_pos = position.z
                    
                    v0 = Vector(x_pos, y_pos, z_pos)
                    v1 = Vector(x_pos + scale, y_pos, z_pos)
                    v2 = Vector(x_pos, y_pos - scale, z_pos)
                    v3 = Vector(x_pos + scale, y_pos - scale, z_pos)
                    
                    v4 = Vector(x_pos, y_pos, z_pos + self.depth)
                    v5 = Vector(x_pos + scale, y_pos, z_pos + self.depth)
                    v6 = Vector(x_pos, y_pos - scale, z_pos + self.depth)
                    v7 = Vector(x_pos + scale, y_pos - scale, z_pos + self.depth)
                    
                    if rotation != (0, 0, 0):
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
                    
                    triangles.append(EnhancedTriangle(v0, v1, v2, material))
                    triangles.append(EnhancedTriangle(v1, v3, v2, material))
                    
                    triangles.append(EnhancedTriangle(v4, v6, v5, material))
                    triangles.append(EnhancedTriangle(v5, v6, v7, material))
                    
                    if y == 0 or pixels[y-1, x] <= threshold:
                        triangles.append(EnhancedTriangle(v0, v4, v1, material))
                        triangles.append(EnhancedTriangle(v1, v4, v5, material))
                    
                    if y == height-2 or pixels[y+1, x] <= threshold:
                        triangles.append(EnhancedTriangle(v2, v3, v6, material))
                        triangles.append(EnhancedTriangle(v3, v7, v6, material))
                    
                    if x == 0 or pixels[y, x-1] <= threshold:
                        triangles.append(EnhancedTriangle(v0, v2, v4, material))
                        triangles.append(EnhancedTriangle(v2, v6, v4, material))
                    
                    if x == width-2 or pixels[y, x+1] <= threshold:
                        triangles.append(EnhancedTriangle(v1, v5, v3, material))
                        triangles.append(EnhancedTriangle(v3, v5, v7, material))
        
        return triangles
    
    def text_to_triangles(self, text, position, material, scale=1.0, rotation=(0, 0, 0)):
        bitmap = self.rasterize_text(text)
        return self.bitmap_to_triangles(bitmap, position, material, scale, rotation)