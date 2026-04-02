"""GET /v1/runners/{race_id} — runners for a race."""

from fastapi import APIRouter, Path
from services.racing_client import racing_client

router = APIRouter()


@router.get("/runners/{race_id}", summary="Get runners for a race")
async def get_runners(race_id: str = Path(..., description="Race ID")):
    """Returns all runners in a race with weights, jockeys, trainers and ratings."""
    return await racing_client.get_runners(race_id=race_id)
