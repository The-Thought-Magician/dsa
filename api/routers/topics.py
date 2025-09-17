from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models import TopicResponse
from ..services import data_service

router = APIRouter(prefix="/api/topics", tags=["topics"])

@router.get("", response_model=List[TopicResponse])
async def get_topics(
    section: Optional[str] = Query(None, description="Filter by section name"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    try:
        return data_service.get_topics(section=section, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic_by_id(topic_id: str):
    try:
        topic = data_service.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))