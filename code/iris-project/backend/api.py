from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from model import Model, Framework

model_garden = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("here we should load the model")
    # model_garden["iris"] = Model(
    #     model_path="models/sklearn/iris_model.pk",
    #     framework=Framework.sklearn,
    #     version=1,
    #     classes=["setosa", "versicolor", "virginica"]
    # )
    model_garden["iris"] = Model(
        model_path="models/tf/iris_model",
        framework=Framework.tensorflow,
        version=1,
        classes=["setosa", "versicolor", "virginica"]
    )
    yield 
    # Clean up the ML models and release the resources
    print("here we should clean up the model")

# creating the API
app = FastAPI(lifespan=lifespan)

# @app.on_event("startup")
# def startup_event():
#     print("here is where we should load the model and other things.")

# @app.on_event("shutdown")
# def shutdown_event():
#     print("Shutting down")

@app.get("/")
async def root():
    return {"message": "Welcome to the IRIS project API"}

@app.get("/hi")
async def hi():
    return {"message": "Hi from the IRIS project API"}


users_router = APIRouter(prefix="/users")

@users_router.get("/hi")
async def hi_users():
    return {"message": "Hi from the users router"}

@users_router.post("/")
async def create():

    return {"message": "User created"}

@users_router.get("/")
async def search():
    return {"message": "All users"}



model_router = APIRouter(prefix="/model")

@model_router.get("/hi")
async def hi_model():
    return {"message": "Hi from the model router"}

    
class IrisModel(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    
    def to_list(self):
        return [self.sepal_length, self.sepal_width, self.petal_length, self.petal_width]


# @model_router.post("/predict")
# async def predict(request: Request):
#     query_params = dict(request.query_params)
#     body_data = await request.json()
#     sepal_length = body_data.get("sepal_length")
#     sepal_width = body_data.get("sepal_width")
#     petal_length = body_data.get("petal_length")
#     petal_width = body_data.get("petal_width")
#     return {"message": "Prediction made"}
    

@model_router.post("/predict")
async def predict(request: Request, data: IrisModel):
    query_params = dict(request.query_params)
    model_name = query_params.get("model_name")
    model = model_garden.get(model_name, None)
    if model is None:
        return JSONResponse(status_code=404, content={"message": "Model not found"})
    model_input = data.to_list()
    prediction = model.predict([model_input])
    return JSONResponse(content={"prediction": prediction})

app.include_router(users_router)
app.include_router(model_router)


