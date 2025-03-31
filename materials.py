"""
materials.py - Material definitions and factory functions
"""
from ray import Material

def create_standard_materials():
    """
    Create a set of standard materials for common use cases.
    
    Returns:
        Dictionary of named materials
    """
    # Basic materials
    matte_red = Material((255, 50, 50))
    matte_green = Material((50, 255, 50))
    matte_blue = Material((50, 50, 255))
    matte_yellow = Material((255, 255, 50))
    matte_white = Material((255, 255, 255))
    matte_black = Material((0, 0, 0))
    
    # Reflective materials
    mirror = Material((255, 255, 255), reflectivity=0.9)
    chrome = Material((220, 220, 220), reflectivity=0.8)
    metal_red = Material((255, 50, 50), reflectivity=0.6)
    metal_blue = Material((50, 50, 255), reflectivity=0.6)
    
    # Transparent materials
    glass = Material((255, 255, 255), reflectivity=0.1, transparency=0.9, refractive_index=1.5)
    water = Material((200, 230, 255), reflectivity=0.1, transparency=0.8, refractive_index=1.33)
    diamond = Material((255, 255, 255), reflectivity=0.2, transparency=0.8, refractive_index=2.42)
    ruby = Material((255, 20, 20), reflectivity=0.1, transparency=0.7, refractive_index=1.77)
    
    return {
        'red': matte_red,
        'green': matte_green,
        'blue': matte_blue,
        'yellow': matte_yellow,
        'white': matte_white,
        'black': matte_black,
        'mirror': mirror,
        'chrome': chrome,
        'metal_red': metal_red, 
        'metal_blue': metal_blue,
        'glass': glass,
        'water': water,
        'diamond': diamond,
        'ruby': ruby
    }

# Additional material creation functions could be added here

def create_metallic_material(color, reflectivity=0.7):
    """
    Create a metallic material with the given color and reflectivity.
    
    Args:
        color: RGB color tuple (r, g, b)
        reflectivity: How reflective the material should be (0.0-1.0)
        
    Returns:
        Material object
    """
    return Material(color, reflectivity=reflectivity)

def create_glass_material(color=(255, 255, 255), transparency=0.9, refractive_index=1.5):
    """
    Create a glass-like transparent material.
    
    Args:
        color: RGB color tuple (r, g, b)
        transparency: How transparent the material should be (0.0-1.0)
        refractive_index: Refractive index (1.5 for typical glass)
        
    Returns:
        Material object
    """
    return Material(color, reflectivity=0.1, transparency=transparency, refractive_index=refractive_index)