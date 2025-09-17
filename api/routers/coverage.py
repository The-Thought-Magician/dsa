from fastapi import APIRouter, HTTPException
from typing import List
from ..models import CoverageResponse, MappingResponse
from ..services import data_service

router = APIRouter(prefix="/api", tags=["coverage"])

@router.get("/coverage", response_model=CoverageResponse)
async def get_coverage():
    try:
        return data_service.get_coverage()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings", response_model=List[MappingResponse])
async def get_mappings():
    try:
        return data_service.get_mappings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))