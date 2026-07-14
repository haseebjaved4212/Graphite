from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
import cv2
import numpy as np
from sketch_utils import convert_image

app = FastAPI(title="Graphite API", description="Photo to Sketch Converter API")

@app.post("/convert")
async def convert_endpoint(
    file: UploadFile = File(...),
    style: str = Form("Pencil Sketch"),
    blur_ksize: int = Form(21),
    contrast: float = Form(1.0),
    thickness: int = Form(3),
    use_texture: bool = Form(False)
):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        return {"error": "Invalid image format or unreadable file"}
        
    try:
        result_bgr = convert_image(img_bgr, style, blur_ksize, contrast, thickness, use_texture)
    except Exception as e:
        return {"error": str(e)}
    
    # encode to png
    success, buffer = cv2.imencode('.png', result_bgr)
    if not success:
        return {"error": "Failed to encode resulting image"}
        
    return Response(content=buffer.tobytes(), media_type="image/png")
