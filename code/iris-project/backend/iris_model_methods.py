from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class IrisModel(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    
    def to_list(self):
        return [self.sepal_length, self.sepal_width, self.petal_length, self.petal_width]



iris_model_router = APIRouter()

@iris_model_router.get("/hi")
async def hi_model():
    return {"message": "Hi from the model router"}


@iris_model_router.post("/predict")
async def predict(request: Request, data: IrisModel):
    query_params = dict(request.query_params)
    model_name = query_params.get("model_name")
    model_garden =  request.app.state.model_garden
    model = model_garden.get(model_name, None)
    if model is None:
        return JSONResponse(status_code=404, content={"message": "Model not found"})
    model_input = data.to_list()
    prediction = model.predict([model_input])
    return JSONResponse(content={"prediction": prediction})

@iris_model_router.post("/receive-image")
async def receive_image(request: Request):
    bytes_image = await request.body()
    with open("image.jpg", "wb") as f:
        f.write(bytes_image)    
    return "Image received!"