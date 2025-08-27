from fastapi import APIRouter

router = APIRouter()

@router.get('/kpis')
async def get_kpis():
    return {"ctr": 0.12, "cpa": 5.4}



