from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi import UploadFile, Form, File
from typing import Optional
from PIL import Image as PILImage
from io import BytesIO
import tensorflow as tf
from models import Model, Framework
from keras.models import Sequential
import keras.layers as layers

router = APIRouter()

@router.get("/hi")
async def hi_model():
    return {"message": "Hi from the model router"}



@router.post("/predict")
async def predict(request: Request, 
                  image: UploadFile = File(...),
        lat: Optional[float] = Form(default=None),
        lng: Optional[float] = Form(default=None)):
    
    image_bytes: bytes = await image.read() # read the image as bytes
    model_garden = request.app.state.model_garden
    flowers_model = model_garden["flowers-model"]
    predictions = flowers_model.predict(image_bytes)
    return JSONResponse(content={"predictions": predictions})