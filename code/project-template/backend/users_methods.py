from fastapi import APIRouter

users_router = APIRouter()

@users_router.get("/hi")
async def hi_users():
    return {"message": "Hi from the users router"}

@users_router.post("/")
async def create():
    return {"message": "User created"}

@users_router.get("/")
async def search():
    return {"message": "All users"}

