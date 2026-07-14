# Graphite

Graphite is a photo-to-sketch converter web app built with Python and Streamlit.

## Features
- **4 Art Styles**: Pencil Sketch, Charcoal, Line Art, and Color Sketch.
- **Adjustable Controls**: Fine-tune blur, contrast, line thickness, and add a procedural paper texture.
- **Interactive Preview**: Drag the slider to compare the original image with the generated sketch.
- **Batch Processing**: Upload multiple images at once and download a ZIP file of all sketches.
- **FastAPI Endpoint**: Includes an API endpoint (`/convert`) to use the core conversion logic outside of the UI.

![Graphite Screenshot](image.png)

## Setup Instructions

### 1. Requirements
Ensure you have Python 3.8+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit App
```bash
streamlit run app.py
```
This will open the web interface in your default browser.

### 4. Run the API (Optional)
If you want to use the API endpoints directly:
```bash
uvicorn api:app --reload
```
You can then access the interactive API docs at `http://127.0.0.1:8000/docs`.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
MIT License



