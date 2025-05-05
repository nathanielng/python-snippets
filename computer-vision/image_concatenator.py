# This code was generated using Amazon Q CLI

import numpy as np
from PIL import Image

def concatenate_images(image1_path, image2_path, orientation='horizontal', stretch_to_fit=False):
    """
    Concatenate two images either horizontally or vertically.
    
    Parameters:
    image1_path (str): Path to the first image
    image2_path (str): Path to the second image
    orientation (str): 'horizontal' or 'vertical'
    stretch_to_fit (bool): If True, resize images to match height (for horizontal) or width (for vertical)
    
    Returns:
    PIL.Image: Concatenated image
    """
    # Open images
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    
    # Get dimensions
    width1, height1 = img1.size
    width2, height2 = img2.size
    
    if orientation.lower() == 'horizontal':
        if stretch_to_fit:
            # Resize second image to match height of first image
            new_width2 = int(width2 * (height1 / height2))
            img2 = img2.resize((new_width2, height1), Image.LANCZOS)
            width2, height2 = img2.size
        
        # Create a new image with the combined width and max height
        result_width = width1 + width2
        result_height = max(height1, height2)
        result = Image.new('RGB', (result_width, result_height))
        
        # Paste images
        result.paste(img1, (0, 0))
        result.paste(img2, (width1, 0))
        
    elif orientation.lower() == 'vertical':
        if stretch_to_fit:
            # Resize second image to match width of first image
            new_height2 = int(height2 * (width1 / width2))
            img2 = img2.resize((width1, new_height2), Image.LANCZOS)
            width2, height2 = img2.size
        
        # Create a new image with the max width and combined height
        result_width = max(width1, width2)
        result_height = height1 + height2
        result = Image.new('RGB', (result_width, result_height))
        
        # Paste images
        result.paste(img1, (0, 0))
        result.paste(img2, (0, height1))
    
    else:
        raise ValueError("Orientation must be 'horizontal' or 'vertical'")
    
    return result

def main():
    # Example usage
    image1_path = "image1.jpg"  # Replace with your image paths
    image2_path = "image2.png"
    
    # Horizontal concatenation without stretching
    result_h = concatenate_images(image1_path, image2_path, orientation='horizontal', stretch_to_fit=False)
    result_h.save("horizontal_concat.jpg")
    
    # Horizontal concatenation with stretching
    result_h_stretch = concatenate_images(image1_path, image2_path, orientation='horizontal', stretch_to_fit=True)
    result_h_stretch.save("horizontal_concat_stretched.jpg")
    
    # Vertical concatenation without stretching
    result_v = concatenate_images(image1_path, image2_path, orientation='vertical', stretch_to_fit=False)
    result_v.save("vertical_concat.jpg")
    
    # Vertical concatenation with stretching
    result_v_stretch = concatenate_images(image1_path, image2_path, orientation='vertical', stretch_to_fit=True)
    result_v_stretch.save("vertical_concat_stretched.jpg")
    
    print("Images concatenated successfully!")

if __name__ == "__main__":
    main()
