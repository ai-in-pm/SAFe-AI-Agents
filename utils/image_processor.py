import os
import sys
import base64
from PIL import Image
import io
import numpy as np
from pathlib import Path

# Add parent directory to path to import from app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

class SAFeImageProcessor:
    """
    A comprehensive image processing utility for SAFe configuration images.
    This class provides methods for extracting metadata, optimizing images,
    and preparing them for integration with the SAFe AI Agents application.
    """
    
    def __init__(self, static_dir=None):
        """
        Initialize the SAFeImageProcessor with the static directory path.
        
        Parameters:
        -----------
        static_dir : str, optional
            Path to the static directory. If None, will use the default path.
        """
        if static_dir is None:
            self.static_dir = os.path.join(parent_dir, 'static')
        else:
            self.static_dir = static_dir
        
        self.images_dir = os.path.join(self.static_dir, 'images')
        os.makedirs(self.images_dir, exist_ok=True)
    
    def process_configuration_images(self, image_mappings):
        """
        Process SAFe configuration images based on the provided mappings.
        
        Parameters:
        -----------
        image_mappings : dict
            Dictionary mapping configuration types to source file paths.
            Example: {'big_picture': '/path/to/image1.jpg', ...}
        
        Returns:
        --------
        dict
            Dictionary with processing results for each configuration.
        """
        results = {}
        
        for config_type, source_path in image_mappings.items():
            # Determine the target filename based on the configuration type
            if config_type == 'big_picture':
                target_filename = 'safe_config_1.jpg'
            elif config_type == 'core_competencies':
                target_filename = 'safe_config_2.jpg'
            elif config_type == 'essential':
                target_filename = 'safe_config_3.jpg'
            elif config_type == 'large_solution':
                target_filename = 'safe_config_4.jpg'
            elif config_type == 'portfolio':
                target_filename = 'safe_config_5.jpg'
            elif config_type == 'full':
                target_filename = 'safe_config_6.jpg'
            else:
                print(f"Warning: Unknown configuration type: {config_type}")
                continue
            
            target_path = os.path.join(self.images_dir, target_filename)
            
            try:
                # Process and save the image
                success = self._process_and_save_image(source_path, target_path)
                results[config_type] = {
                    'success': success,
                    'source_path': source_path,
                    'target_path': target_path
                }
                
                if success:
                    print(f"Successfully processed {config_type} image: {target_path}")
                else:
                    print(f"Failed to process {config_type} image from {source_path}")
            except Exception as e:
                print(f"Error processing {config_type} image: {e}")
                results[config_type] = {
                    'success': False,
                    'error': str(e),
                    'source_path': source_path,
                    'target_path': target_path
                }
        
        return results
    
    def _process_and_save_image(self, source_path, target_path):
        """
        Process an image (optimize, resize if needed) and save it to the target path.
        
        Parameters:
        -----------
        source_path : str
            Path to the source image file.
        target_path : str
            Path where the processed image will be saved.
        
        Returns:
        --------
        bool
            True if successful, False otherwise.
        """
        try:
            # For now, we're just copying the image as is
            # In a real application, you might want to optimize, resize, etc.
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            with open(source_path, 'rb') as src_file:
                with open(target_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            
            return True
        except Exception as e:
            print(f"Error in _process_and_save_image: {e}")
            return False

    def create_default_image(self, width=800, height=600, text="SAFe Configuration"):
        """
        Create a default image with text for when actual images are not available.
        
        Parameters:
        -----------
        width : int
            Width of the image in pixels.
        height : int
            Height of the image in pixels.
        text : str
            Text to display on the image.
            
        Returns:
        --------
        str
            Path to the created default image.
        """
        try:
            # Create a blank image with a light gray background
            img = Image.new('RGB', (width, height), color=(240, 240, 240))
            
            # Save the image as the default
            default_path = os.path.join(self.images_dir, 'default_safe_config.jpg')
            img.save(default_path, format='JPEG')
            
            print(f"Created default image at: {default_path}")
            return default_path
        except Exception as e:
            print(f"Error creating default image: {e}")
            return None

# Example usage
if __name__ == "__main__":
    processor = SAFeImageProcessor()
    
    # Create a default image
    processor.create_default_image()
    
    print("SAFe image processor initialized and default image created.")
