import os
import shutil

src_dir = r"C:\Users\abhay\.gemini\antigravity\brain\a3ec413a-096d-4141-bbfb-20941edf75a1"
dest_dir = r"c:\Users\abhay\OneDrive\Desktop\aiproject\Screenshots"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# File mapping based on timestamp order
mapping = {
    "media__1782676959793.png": "linkedin.png",
    "media__1782677009843.png": "website.png",
    "media__1782677183056.png": "facebook.png",
    "media__1782677215575.png": "instagram.png",
    "media__1782677239332.png": "youtube.png"
}

for src_name, dest_name in mapping.items():
    src_path = os.path.join(src_dir, src_name)
    dest_path = os.path.join(dest_dir, dest_name)
    
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_name} -> Screenshots/{dest_name}")
    else:
        print(f"Source file {src_name} not found.")
