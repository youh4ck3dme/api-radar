from PIL import Image
import os

def generate_icons(source_path, output_dir):
    print(f"Opening source: {source_path}")
    img = Image.open(source_path)
    
    # Ensure output dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    sizes = {
        "icon-192.png": (192, 192),
        "icon-512.png": (512, 512),
        "favicon.png": (32, 32),
        "apple-touch-icon.png": (180, 180)
    }
    
    for name, size in sizes.items():
        print(f"Generating {name} ({size}x{size})...")
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(os.path.join(output_dir, name))
    
    print("Done generating icons.")

if __name__ == "__main__":
    master = r"C:\Users\42195\.gemini\antigravity\brain\20ec7666-4e9b-4e7f-a23d-fed47d3d87fa\api_radar_pro_master_logo_1772945843114.png"
    target = r"C:\Users\42195\.gemini\antigravity\scratch\api-radar\dashboard\public"
    generate_icons(master, target)
