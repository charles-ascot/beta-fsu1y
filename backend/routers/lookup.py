"""
Lookup / reference endpoints — courses, regions, horses, jockeys,
trainers, owners, sires, dams, damsires.

All search by name or ID. Cached for 1 hour (reference data).
"""

from typing import Optional
from fastapi import APIRouter, Query
from services.racing_client import racing_client

router = APIRouter()


# ── Courses ───────────────────────────────────────────────────────────────────

@router.get("/courses", summary="List racecourses")
async def get_courses(
    region_codes: Optional[str] = Query(None, description="Comma-separated region codes e.g. gb,ire"),
    limit: int = Query(50, ge=1, le=200),
    skip: int  = Query(0, ge=0),
):
    """Returns racecourse data optionally filtered by region."""
    return await racing_client.get_courses(region_codes=region_codes, limit=limit, skip=skip)


@router.get("/courses/regions", summary="List available racing regions")
async def get_regions(
    limit: int = Query(50, ge=1, le=200),
    skip: int  = Query(0, ge=0),
):
    """Returns all available racing regions."""
    return await racing_client.get_regions(limit=limit, skip=skip)


# ── Horses ────────────────────────────────────────────────────────────────────

@router.get("/horses", summary="Search horses by name or ID")
async def get_horses(
    horse_name: Optional[str] = Query(None, description="Horse name search"),
    horse_id:   Optional[str] = Query(None, description="Exact horse ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for horses by name or look up by ID."""
    return await racing_client.get_horses(
        horse_name=horse_name, horse_id=horse_id, limit=limit, skip=skip
    )


# ── Jockeys ───────────────────────────────────────────────────────────────────

@router.get("/jockeys", summary="Search jockeys by name or ID")
async def get_jockeys(
    jockey_name: Optional[str] = Query(None, description="Jockey name search"),
    jockey_id:   Optional[str] = Query(None, description="Exact jockey ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for jockeys by name or look up by ID."""
    return await racing_client.get_jockeys(
        jockey_name=jockey_name, jockey_id=jockey_id, limit=limit, skip=skip
    )


# ── Trainers ──────────────────────────────────────────────────────────────────

@router.get("/trainers", summary="Search trainers by name or ID")
async def get_trainers(
    trainer_name: Optional[str] = Query(None, description="Trainer name search"),
    trainer_id:   Optional[str] = Query(None, description="Exact trainer ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for trainers by name or look up by ID."""
    return await racing_client.get_trainers(
        trainer_name=trainer_name, trainer_id=trainer_id, limit=limit, skip=skip
    )


# ── Owners ────────────────────────────────────────────────────────────────────

@router.get("/owners", summary="Search owners by name or ID")
async def get_owners(
    owner_name: Optional[str] = Query(None, description="Owner name search"),
    owner_id:   Optional[str] = Query(None, description="Exact owner ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for owners by name or look up by ID."""
    return await racing_client.get_owners(
        owner_name=owner_name, owner_id=owner_id, limit=limit, skip=skip
    )


# ── Sires ─────────────────────────────────────────────────────────────────────

@router.get("/sires", summary="Search sires by name or ID")
async def get_sires(
    sire_name: Optional[str] = Query(None, description="Sire name search"),
    sire_id:   Optional[str] = Query(None, description="Exact sire ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for sires by name or look up by ID."""
    return await racing_client.get_sires(
        sire_name=sire_name, sire_id=sire_id, limit=limit, skip=skip
    )


# ── Dams ──────────────────────────────────────────────────────────────────────

@router.get("/dams", summary="Search dams by name or ID")
async def get_dams(
    dam_name: Optional[str] = Query(None, description="Dam name search"),
    dam_id:   Optional[str] = Query(None, description="Exact dam ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for dams by name or look up by ID."""
    return await racing_client.get_dams(
        dam_name=dam_name, dam_id=dam_id, limit=limit, skip=skip
    )


# ── Damsires ──────────────────────────────────────────────────────────────────

@router.get("/damsires", summary="Search damsires by name or ID")
async def get_damsires(
    damsire_name: Optional[str] = Query(None, description="Damsire name search"),
    damsire_id:   Optional[str] = Query(None, description="Exact damsire ID"),
    limit: int = Query(20, ge=1, le=100),
    skip: int  = Query(0, ge=0),
):
    """Search for damsires by name or look up by ID."""
    return await racing_client.get_damsires(
        damsire_name=damsire_name, damsire_id=damsire_id, limit=limit, skip=skip
    )
