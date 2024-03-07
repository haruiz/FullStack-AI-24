from fastapi import FastAPI
from contextlib import asynccontextmanager
from model import Model, Framework
from users_methods import users_router
from iris_model_methods import iris_model_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("here you should add the code you want to run when the app is starting")
    # We are going to use a dictionary to store the models
    app.state.model_garden = dict()
    # register the iris model
    model = Model(
        model_path="models/tf/iris_model",
        framework=Framework.tensorflow,
        version=1,
        classes=["setosa", "versicolor", "virginica"]
    )
    app.state.model_garden["iris_model"] = model
    yield 
    # Clean up the ML models and release the resources
    print("here you should add the code you want to run when the app is shutting down")

# creating the API
app = FastAPI(lifespan=lifespan)
app.include_router(users_router, prefix="/users")
app.include_router(iris_model_router, prefix="/iris-model")

# creating global routes
@app.get("/")
async def root():
    return {"message": "Welcome to the IRIS project API"}

@app.get("/hi")
async def hi():
    return {"message": "Hi from the IRIS project API"}



