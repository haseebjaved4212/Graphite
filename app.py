import streamlit as st
from streamlit_image_comparison import image_comparison
import cv2
import numpy as np
from PIL import Image
import io
import zipfile
from sketch_utils import convert_image

st.set_page_config(page_title="Graphite - Photo to Sketch", page_icon="✏️", layout="wide")

@st.cache_data
def process_image(img_bytes, style, blur_ksize, contrast, thickness, use_texture):
    """
    Cached image processing function. Takes raw bytes so hashing works well.
    """
    img_pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    result_bgr = convert_image(img_bgr, style, blur_ksize, contrast, thickness, use_texture)
    
    # Convert back to PIL
    if len(result_bgr.shape) == 3:
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
    else:
        # If it's 2-channel grayscale, keep it simple
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_GRAY2RGB)
        
    result_pil = Image.fromarray(result_rgb)
    return img_pil, result_pil

def pil_to_bytes(img_pil, format="PNG"):
    buf = io.BytesIO()
    img_pil.save(buf, format=format)
    return buf.getvalue()

def main():
    st.title("✏️ Graphite - Photo to Sketch Converter")
    
    # Sidebar Controls
    st.sidebar.header("Settings")
    
    blur_ksize = st.sidebar.slider("Blur / Softness", min_value=21, max_value=121, value=21, step=2)
    contrast = st.sidebar.slider("Contrast / Darkness", min_value=0.5, max_value=2.5, value=1.0, step=0.1)
    thickness = st.sidebar.slider("Line Thickness", min_value=1, max_value=11, value=3, step=2)
    use_texture = st.sidebar.checkbox("Add Paper Texture", value=False)
    
    # Style Selection
    st.subheader("Select Style")
    styles = ["Pencil Sketch", "Charcoal", "Line Art", "Color Sketch"]
    
    # Keep track of selected style in session state
    if "selected_style" not in st.session_state:
        st.session_state.selected_style = "Pencil Sketch"
        
    cols = st.columns(4)
    for i, style in enumerate(styles):
        with cols[i]:
            # We can use buttons to act as cards
            if st.button(style, use_container_width=True):
                st.session_state.selected_style = style
                
    st.write(f"**Current Style:** {st.session_state.selected_style}")
    
    # Input Area
    st.subheader("Upload Image(s)")
    
    input_method = st.radio("Choose Input Method", ["File Upload", "Camera"], horizontal=True, label_visibility="collapsed")
    
    uploaded_files = []
    if input_method == "File Upload":
        uploaded_files = st.file_uploader("Upload photos (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    else:
        cam_file = st.camera_input("Take a photo")
        if cam_file:
            uploaded_files = [cam_file]
            
    if not uploaded_files:
        st.info("Please upload an image or take a photo to begin.")
        return
        
    # Process First Image for Preview
    st.subheader("Preview")
    preview_file = uploaded_files[0]
    preview_bytes = preview_file.getvalue()
    
    with st.spinner("Applying sketch style..."):
        try:
            img_original, img_sketch = process_image(
                preview_bytes, 
                st.session_state.selected_style, 
                blur_ksize, 
                contrast, 
                thickness, 
                use_texture
            )
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return
        
    # Image Comparison Slider
    image_comparison(
        img1=img_original,
        img2=img_sketch,
        label1="Original",
        label2="Sketch",
        starting_position=50,
        show_labels=True,
        make_responsive=True,
        in_memory=True
    )
    
    st.download_button(
        label="Download Sketch",
        data=pil_to_bytes(img_sketch),
        file_name=f"sketch_{preview_file.name.split('.')[0]}.png",
        mime="image/png"
    )
    
    # Batch Processing
    if len(uploaded_files) > 1:
        st.subheader(f"Batch Processing ({len(uploaded_files)} images)")
        
        # We will process them all and show a zip download
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            
            # Show a grid of thumbnails
            cols = st.columns(min(len(uploaded_files), 4))
            
            for i, file in enumerate(uploaded_files):
                with st.spinner(f"Processing {file.name}..."):
                    try:
                        file_bytes = file.getvalue()
                        _, sketch_pil = process_image(
                            file_bytes, 
                            st.session_state.selected_style, 
                            blur_ksize, 
                            contrast, 
                            thickness, 
                            use_texture
                        )
                        
                        # Add to zip
                        sketch_bytes = pil_to_bytes(sketch_pil)
                        zip_file.writestr(f"sketch_{file.name.split('.')[0]}.png", sketch_bytes)
                        
                        # Show thumbnail
                        with cols[i % len(cols)]:
                            st.image(sketch_pil, caption=file.name, use_container_width=True)
                    except Exception as e:
                        st.error(f"Failed to process {file.name}: {e}")
                        
        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer.getvalue(),
            file_name="graphite_sketches.zip",
            mime="application/zip"
        )

if __name__ == "__main__":
    main()
