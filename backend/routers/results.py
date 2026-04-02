"""GET /v1/results — race results."""

from typing import Optional
from fastapi import APIRouter, Path, Query
from services.racing_client import racing_client

router = APIRouter()


@router.get("/results", summary="List recent results")
async def get_results(
    date: Optional[str]   = Query(None, description="ISO date e.g. 2025-04-01"),
    region: Optional[str] = Query(None, description="gb, ire, usa, aus, fr"),
    course: Optional[str] = Query(None, description="Course name"),
    limit: int = Query(50, ge=1, le=200),
    skip: int  = Query(0, ge=0),
):
    """Returns race results, optionally filtered by date, region or course."""
    return await racing_client.get_results(
        date=date, region=region, course=course, limit=limit, skip=skip
    )


@router.get("/results/{race_id}", summary="Get result for a single race")
async def get_result(race_id: str = Path(..., description="Race ID")):
    """Returns the result for a specific race."""
    return await racing_client.get_result(race_id=race_id)
