"""GET /v1/racecards — today's / tomorrow's racecards."""

from typing import Optional
from fastapi import APIRouter, Query
from services.racing_client import racing_client

router = APIRouter()


@router.get("/racecards", summary="Get racecards")
async def get_racecards(
    day: str = Query("today", description="today or tomorrow"),
    region: Optional[str] = Query(None, description="gb, ire, usa, aus, fr"),
    race_class: Optional[str] = Query(None, description="Race class filter"),
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0),
):
    """
    Returns racecards with runners for today or tomorrow.
    Includes course, distance, class, runners with weights/jockeys/ratings.
    Cached for 3 minutes (matches Racing API update frequency).
    """
    return await racing_client.get_racecards(
        day=day, region=region, race_class=race_class, limit=limit, skip=skip
    )


@router.get("/racecards/pro/{race_id}", summary="Get full pro racecard for a race")
async def get_racecard_pro(race_id: str):
    """
    Full racecard including form, ratings, trainer/jockey stats, notes.
    Requires Standard plan or above.
    """
    return await racing_client.get_racecard_pro(race_id=race_id)
