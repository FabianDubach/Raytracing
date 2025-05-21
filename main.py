import time
import os
import sys
import importlib.util
from renderer import Renderer, ConsoleProgressListener

def run_scene(scene_file, width=800, height=600, preview=False, preview_scale=0.25, preview_depth=2):
   
    """
    Run a ray tracing scene with the given parameters.
    """
   
    # Check if the scene file exists
    if not os.path.exists(scene_file):
        print(f"Error: Scene file '{scene_file}' not found")
        return 0
    
    # Extract scene name (remove .py and path)
    scene_name = os.path.splitext(os.path.basename(scene_file))[0]
    
    # Import the scene module dynamically
    try:
        spec = importlib.util.spec_from_file_location(scene_name, scene_file)
        scene_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scene_module)
    except Exception as e:
        print(f"Error loading scene file: {e}")
        return 0
    
    # Check if the module has a setup_scene function
    if not hasattr(scene_module, 'setup_scene'):
        print(f"Error: Scene file '{scene_file}' does not contain a setup_scene function")
        return 0
    
    # Create renderer and set up the scene
    start_time = time.time()
    raster = Renderer(width, height)
    
    # Add a progress listener
    raster.add_progress_listener(ConsoleProgressListener())
    
    # Set up the scene
    print(f"Setting up scene from {scene_file}...")
    scene_module.setup_scene(raster)
    
    # Output filename based on scene name
    output_file = f"{scene_name}.png"
    
    # Handle preview mode if enabled
    if preview:
        print(f"Rendering preview (scale={preview_scale}, depth={preview_depth})...")
        raster.render_preview(
            scale=preview_scale, 
            max_depth=preview_depth, 
            output_file=f"{scene_name}_preview.png",
            samples=samples
        )
    else:
        # Render the full quality scene
        raster.run(output_file)
    
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Total execution time: {time_taken:.2f} seconds")
    
    return time_taken


if __name__ == "__main__":
    # Default settings
    scene_file = None
    width = 1920
    height = 1080
    preview_mode = False
    preview_scale = 0.25
    preview_depth = 2
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        scene_file = sys.argv[1]
        
        # Check for help flag
        if scene_file in ['-h', '--help', 'help']:
            print("Ray Tracer Usage:")
            print("  python main.py scene_file [width height] [options]")
            print("\nOptions:")
            print("  --preview [scale]    Render a preview (default scale: 0.25)")
            print("  --depth N            Set recursion depth for preview (default: 2)")
            print("  --progress           Show detailed progress updates")
            print("\nExamples:")
            print("  python main.py scene_glass 800 600 --preview 0.2")
            sys.exit(0)
    else:
        print("Usage: python main.py scene_file [width height] [options]")
        print("       python main.py --help   (for more information)")
        sys.exit(1)
    
    # Add .py extension if needed
    if not scene_file.endswith('.py'):
        scene_file += '.py'
    
    # Parse optional width/height
    if len(sys.argv) > 3 and sys.argv[2].isdigit() and sys.argv[3].isdigit():
        width = int(sys.argv[2])
        height = int(sys.argv[3])
    
    # Check for preview flag
    if '--preview' in sys.argv:
        preview_mode = True
        idx = sys.argv.index('--preview')
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].replace('.', '', 1).isdigit():
            preview_scale = float(sys.argv[idx + 1])
    
    # Check for depth flag
    if '--depth' in sys.argv:
        idx = sys.argv.index('--depth')
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            preview_depth = int(sys.argv[idx + 1])
    
    if '--samples' in sys.argv:
        idx = sys.argv.index('--samples')
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            samples = int(sys.argv[idx + 1])
    else:
        samples = 1  # Default to 1 sample per pixel
    
    # Run the scene
    run_scene(scene_file, width, height, preview_mode, preview_scale, preview_depth)