"""GET /v1/odds/{race_id} — multi-bookmaker odds for a race."""

from fastapi import APIRouter, Path, Query
from services.racing_client import racing_client

router = APIRouter()


@router.get("/odds/{race_id}", summary="Get bookmaker odds for a race")
async def get_odds(
    race_id: str = Path(..., description="Race ID"),
    limit: int = Query(50, ge=1, le=200),
    skip: int  = Query(0, ge=0),
):
    """
    Returns 20+ bookmaker odds per runner for a race.
    Cached for 60 seconds — odds change rapidly in the final minutes.
    Requires Standard plan or above on The Racing API.
    """
    return await racing_client.get_odds(race_id=race_id, limit=limit, skip=skip)
