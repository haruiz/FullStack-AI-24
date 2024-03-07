from fastapi import APIRouter

router = APIRouter()

@router.get("/hi")
async def hi_users():
    return {"message": "Hi from the users router"}

@router.post("/")
async def create():
    return {"message": "User created"}

@router.get("/")
async def search():
    return {"message": "All users"}

