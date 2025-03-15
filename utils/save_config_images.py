import os
import sys
import shutil
from PIL import Image
import io
import base64

# Add parent directory to path to import from app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

def save_sample_config_images():
    """
    Save sample SAFe configuration images to the project's static directory.
    """
    # Define the source and destination directories
    source_dir = os.path.join(parent_dir, 'sample_images')
    dest_dir = os.path.join(parent_dir, 'static', 'images', 'safe_configurations')
    
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    
    # Define the configuration types and corresponding filenames
    config_types = [
        ('big_picture', 'big_picture.jpg'),
        ('core_competencies', 'core_competencies.jpg'),
        ('essential', 'essential.jpg'),
        ('large_solution', 'large_solution.jpg'),
        ('portfolio', 'portfolio.jpg'),
        ('full', 'full.jpg')
    ]
    
    print(f"Saving SAFe configuration images to {dest_dir}...")
    
    # Copy each sample image to the destination directory with the appropriate name
    for config_type, filename in config_types:
        source_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(dest_dir, config_type + '.jpg')
        
        try:
            if os.path.exists(source_file):
                shutil.copy2(source_file, dest_file)
                print(f"Saved {config_type} image: {dest_file}")
            else:
                print(f"Sample image not found: {source_file}")
                # Create a placeholder image with text
                create_placeholder_image(dest_file, config_type)
        except Exception as e:
            print(f"Error saving {config_type} image: {e}")
            # Create a placeholder image with text
            create_placeholder_image(dest_file, config_type)
    
    print("SAFe configuration images saved successfully!")

def create_placeholder_image(filepath, config_type):
    """
    Create a placeholder image with text for a SAFe configuration type.
    """
    # Create a blank image
    width, height = 800, 600
    background_color = (240, 240, 240)
    text_color = (60, 60, 60)
    
    # Create a new image with the given background color
    image = Image.new('RGB', (width, height), background_color)
    
    # Save the image
    image.save(filepath)
    print(f"Created placeholder image for {config_type}: {filepath}")

if __name__ == '__main__':
    save_sample_config_images()
