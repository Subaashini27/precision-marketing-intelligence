from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ml_pipeline.ml_service import ml_service

router = APIRouter()


class FeaturesPayload(BaseModel):
    features: Dict[str, Any]


@router.get("/status")
async def get_model_status():
    return ml_service.get_model_status()


@router.post("/predict/conversion")
async def predict_conversion(payload: FeaturesPayload):
    result = ml_service.predict_conversion(payload.features)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/predict/churn")
async def predict_churn(payload: FeaturesPayload):
    result = ml_service.predict_churn(payload.features)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/predict/roi")
async def predict_roi(payload: FeaturesPayload):
    result = ml_service.predict_roi(payload.features)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/predict/campaign-performance")
async def predict_campaign_performance(payload: FeaturesPayload):
    result = ml_service.predict_campaign_performance(payload.features)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result



