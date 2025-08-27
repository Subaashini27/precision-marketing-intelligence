from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from powerbi_integration.powerbi_service import powerbi_service

router = APIRouter()


@router.get("/status")
async def get_powerbi_status():
    return powerbi_service.get_service_status()


@router.get("/reports")
async def list_reports(workspace_id: Optional[str] = None):
    return powerbi_service.get_reports(workspace_id)


@router.get("/datasets")
async def list_datasets(workspace_id: Optional[str] = None):
    return powerbi_service.get_datasets(workspace_id)


@router.get("/embed-config")
async def get_embed_config(report_id: Optional[str] = None,
                           workspace_id: Optional[str] = None,
                           user_email: Optional[str] = None):
    config = powerbi_service.create_embed_config(report_id, workspace_id, user_email)
    if "error" in config:
        raise HTTPException(status_code=400, detail=config["error"])
    return config


@router.post("/datasets/{dataset_id}/refresh")
async def refresh_dataset(dataset_id: str, workspace_id: Optional[str] = None):
    ok = powerbi_service.refresh_dataset(dataset_id, workspace_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to initiate dataset refresh")
    return {"status": "refresh_started", "dataset_id": dataset_id}


@router.get("/datasets/{dataset_id}/refresh-history")
async def dataset_refresh_history(dataset_id: str, workspace_id: Optional[str] = None):
    return powerbi_service.get_dataset_refresh_history(dataset_id, workspace_id)



