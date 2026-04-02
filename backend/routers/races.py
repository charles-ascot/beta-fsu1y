"""GET /v1/races — list races."""

from typing import Optional
from fastapi import APIRouter, Query
from services.racing_client import racing_client

router = APIRouter()


@router.get("/races", summary="List races")
async def get_races(
    date: Optional[str] = Query(None, description="ISO date e.g. 2025-04-01"),
    region: Optional[str] = Query(None, description="gb, ire, usa, aus, fr"),
    course: Optional[str] = Query(None, description="Course name filter"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
):
    """Returns races optionally filtered by date, region or course."""
    return await racing_client.get_races(
        date=date, region=region, course=course, limit=limit, skip=skip
    )
