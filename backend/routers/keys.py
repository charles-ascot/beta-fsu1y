"""
POST   /v1/keys           — create FSU consumer key (admin)
GET    /v1/keys           — list all keys (admin)
DELETE /v1/keys/{key_id} — revoke a key (admin)

All routes require X-Admin-Key header.
"""

from fastapi import APIRouter, Header, HTTPException, Path
from pydantic import BaseModel
from typing import Optional

from config import settings
from services.key_service import create_key, list_keys, revoke_key

router = APIRouter()


def _require_admin(x_admin_key: Optional[str]):
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Invalid or missing X-Admin-Key")


class CreateKeyRequest(BaseModel):
    name: str
    created_by: str = "admin"


@router.post("/keys", summary="Create a new FSU API key", status_code=201)
async def create_api_key(
    body: CreateKeyRequest,
    x_admin_key: Optional[str] = Header(None),
):
    """Creates a new FSU-1Y consumer key. Key is only shown once — store it."""
    _require_admin(x_admin_key)
    record = await create_key(name=body.name, created_by=body.created_by)
    return {
        "message": "Key created. Store the key value now — it will not be shown again in full.",
        "key_id":  record["key_id"],
        "key":     record["key"],
        "name":    record["name"],
    }


@router.get("/keys", summary="List all FSU API keys")
async def list_api_keys(x_admin_key: Optional[str] = Header(None)):
    _require_admin(x_admin_key)
    keys = await list_keys()
    return {"count": len(keys), "keys": keys}


@router.delete("/keys/{key_id}", summary="Revoke an FSU API key")
async def revoke_api_key(
    key_id: str = Path(...),
    x_admin_key: Optional[str] = Header(None),
):
    _require_admin(x_admin_key)
    if not await revoke_key(key_id):
        raise HTTPException(status_code=404, detail="Key not found")
    return {"message": "Key revoked", "key_id": key_id}
