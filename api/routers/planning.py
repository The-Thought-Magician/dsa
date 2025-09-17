from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..models import StatsResponse, DailyPlanResponse, StudyPlanResponse, StudyTaskResponse
from ..services import data_service

router = APIRouter(prefix="/api", tags=["planning"])

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    try:
        return data_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/study-plan", response_model=DailyPlanResponse)
async def get_study_plan():
    try:
        return data_service.get_study_plan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/study-plan/today", response_model=StudyPlanResponse)
async def get_today_plan():
    try:
        plan_response = data_service.get_study_plan()
        today = datetime.now().strftime("%Y-%m-%d")

        for plan in plan_response.plans:
            if today in plan.date:
                return plan

        raise HTTPException(status_code=404, detail="No plan found for today")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild")
async def rebuild_data():
    try:
        data_service.rebuild_data()
        return {"message": "Data rebuilt successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))