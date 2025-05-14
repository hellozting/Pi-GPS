import os
import shutil

def extract_png_images_from_subfolders(target_folder):
    current_path = f"data/geometry3k/test/"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    for root, files in os.walk(current_path):
        for file in files:
            if file.lower().endswith('.png') and "point" not in file:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_folder, root.split("/")[-1]+".png")
                shutil.copy2(source_file, target_file)

target_folder = 'data/geometry3k/Geo3KTest/'
extract_png_images_from_subfolders(target_folder)