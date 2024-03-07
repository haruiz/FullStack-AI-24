from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Model entry schema
class IrisModel(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    
    def to_list(self):
        return [self.sepal_length, self.sepal_width, self.petal_length, self.petal_width]



router = APIRouter()

@router.get("/hi")
async def hi_model():
    return {"message": "Hi from the model router"}


@router.post("/predict")
async def predict(request: Request, data: IrisModel):
    model_input = data.to_list()
    model_garden =  request.app.state.model_garden
    model = model_garden["iris-model"]
    predictions = model.predict([model_input])
    return JSONResponse(content={"prediction": predictions})
