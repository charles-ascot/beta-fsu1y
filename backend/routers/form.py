"""GET /v1/form/{horse_id} — horse form."""

from fastapi import APIRouter, Path, Query
from services.racing_client import racing_client

router = APIRouter()


@router.get("/form/{horse_id}", summary="Get form for a horse")
async def get_horse_form(
    horse_id: str = Path(..., description="Horse ID"),
    limit: int    = Query(10, ge=1, le=50, description="Number of runs to return"),
):
    """
    Returns last N runs for a horse — date, course, distance, position, prize.
    Cached for 1 hour (historical data).
    """
    return await racing_client.get_horse_form(horse_id=horse_id, limit=limit)
