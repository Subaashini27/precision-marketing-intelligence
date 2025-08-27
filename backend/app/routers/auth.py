from fastapi import APIRouter

router = APIRouter()

@router.post('/login')
async def login():
    return {"access_token": "demo", "token_type": "bearer"}

@router.post('/register')
async def register():
    return {"status": "registered"}



