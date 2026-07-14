import numpy as np
import cv2

def generate_paper_texture(width, height):
    """
    Generates a procedural Gaussian noise texture resembling paper.
    """
    # Create base white image
    base = np.full((height, width), 255, dtype=np.float32)
    
    # Generate Gaussian noise (mean=0, std=15)
    noise = np.random.normal(0, 15, (height, width))
    
    # Add noise to base
    texture = np.clip(base - noise, 0, 255).astype(np.uint8)
    
    # Blur slightly so it doesn't look like static TV grain
    texture = cv2.GaussianBlur(texture, (3, 3), 0)
    
    return texture

def apply_paper_texture(img, opacity=0.12):
    """
    Blends the paper texture onto the final sketch using multiply mode.
    Opacity 0.12 corresponds to ~12% (within 10-15% target).
    """
    height, width = img.shape[:2]
    
    # Generate texture
    texture = generate_paper_texture(width, height)
    
    # If image is color, convert texture to 3 channels
    if len(img.shape) == 3:
        texture = cv2.cvtColor(texture, cv2.COLOR_GRAY2BGR)
        
    # Multiply blend mode: (img * texture) / 255
    img_float = img.astype(np.float32) / 255.0
    texture_float = texture.astype(np.float32) / 255.0
    
    multiplied = cv2.multiply(img_float, texture_float) * 255.0
    multiplied = np.clip(multiplied, 0, 255).astype(np.uint8)
    
    # Blend with original image using specified opacity
    result = cv2.addWeighted(multiplied, opacity, img, 1.0 - opacity, 0)
    return result
