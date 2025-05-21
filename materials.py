from ray import Material

def create_standard_materials():
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
    metal_red = Material((255, 50, 50), reflectivity=0.3)
    metal_blue = Material((50, 50, 255), reflectivity=0.3)
    metal_white = Material((255, 255, 255), reflectivity=0.3)
    metal_black = Material((0, 0, 0), reflectivity=0.3)
    
    # Transparent materials
    glass = Material((255, 255, 255), reflectivity=0.05, transparency=0.95, refractive_index=1.3)
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
        'metal_white': metal_white,
        'metal_black': metal_black,
        'glass': glass,
        'water': water,
        'diamond': diamond,
        'ruby': ruby
    }