import cv2
import numpy as np
from texture_utils import apply_paper_texture

def adjust_contrast(img, contrast=1.0):
    if contrast == 1.0:
        return img
    img_float = img.astype(np.float32)
    # Scale around 128 (middle gray) to change contrast properly
    adjusted = (img_float - 128) * contrast + 128
    return np.clip(adjusted, 0, 255).astype(np.uint8)

def pencil_sketch_manual(img_bgr, blur_ksize, contrast):
    """
    Classic dodge-blend technique for pencil sketch.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(inverted, (blur_ksize, blur_ksize), 0)
    
    # Dodge blend: (gray * 255) / (255 - blurred)
    sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
    
    sketch = adjust_contrast(sketch, contrast)
    return sketch

def charcoal_sketch(img_bgr, blur_ksize, contrast):
    """
    Darker, higher contrast sketch with added grain.
    """
    # Base is similar to pencil but darker and higher contrast
    sketch = pencil_sketch_manual(img_bgr, blur_ksize, contrast * 1.5)
    
    # Make it darker
    sketch_float = sketch.astype(np.float32)
    sketch_float = sketch_float * 0.8 - 20 # Darken
    sketch_dark = np.clip(sketch_float, 0, 255).astype(np.uint8)
    
    # Add actual grain/noise as requested
    noise = np.random.normal(0, 20, sketch_dark.shape)
    sketch_noise = np.clip(sketch_dark + noise, 0, 255).astype(np.uint8)
    
    return sketch_noise

def line_art(img_bgr, blur_ksize, thickness, contrast):
    """
    Pure edge detection for line art.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Mild blur to reduce noise before edge detection
    small_blur = max(3, blur_ksize // 5)
    if small_blur % 2 == 0: small_blur += 1
    gray_blurred = cv2.GaussianBlur(gray, (small_blur, small_blur), 0)
    
    # Adaptive thresholding to find edges
    block_size = max(3, blur_ksize)
    if block_size % 2 == 0: block_size += 1
    
    edges = cv2.adaptiveThreshold(
        gray_blurred, 255, 
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 
        block_size, 
        9
    )
    
    # Thickness adjustment
    if thickness > 1:
        kernel = np.ones((thickness, thickness), np.uint8)
        # edges are black (0) on white (255) background. 
        # to make lines thicker, we erode (which expands the darker regions).
        edges = cv2.erode(edges, kernel, iterations=1)
        
    edges = adjust_contrast(edges, contrast)
    return edges

def color_sketch(img_bgr, blur_ksize, thickness, contrast):
    """
    Color sketch using cv2.pencilSketch.
    """
    sigma_s = min(200, blur_ksize)
    _, color_sk = cv2.pencilSketch(img_bgr, sigma_s=sigma_s, sigma_r=0.07, shade_factor=0.05)
    
    adjusted = adjust_contrast(color_sk, contrast)
    
    # Apply line thickness by blending Line Art edges on top
    if thickness > 1:
        edges = line_art(img_bgr, blur_ksize, thickness, 1.0)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # multiply blend
        adj_float = adjusted.astype(np.float32) / 255.0
        edges_float = edges_bgr.astype(np.float32) / 255.0
        
        adjusted = cv2.multiply(adj_float, edges_float) * 255.0
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
    return adjusted

def convert_image(img_bgr, style, blur_ksize=21, contrast=1.0, thickness=3, use_texture=False):
    """
    Main entry point for processing an image based on the selected style.
    """
    if style == "Pencil Sketch":
        result = pencil_sketch_manual(img_bgr, blur_ksize, contrast)
    elif style == "Charcoal":
        result = charcoal_sketch(img_bgr, blur_ksize, contrast)
    elif style == "Line Art":
        result = line_art(img_bgr, blur_ksize, thickness, contrast)
    elif style == "Color Sketch":
        result = color_sketch(img_bgr, blur_ksize, thickness, contrast)
    else:
        result = pencil_sketch_manual(img_bgr, blur_ksize, contrast)
        
    if use_texture:
        result = apply_paper_texture(result)
        
    return result
