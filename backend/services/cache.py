"""
Firestore TTL cache — identical pattern to FSU-1X.
Keyed by SHA256 hash of namespace + params.
"""

import time
import json
import hashlib
from typing import Optional, Any

from google.cloud import firestore
from config import settings

_db: Optional[firestore.AsyncClient] = None


def _get_db() -> firestore.AsyncClient:
    global _db
    if _db is None:
        _db = firestore.AsyncClient(project=settings.gcp_project)
    return _db


def make_cache_key(namespace: str, **kwargs) -> str:
    raw = namespace + json.dumps(kwargs, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:40]


async def get_cached(key: str) -> Optional[Any]:
    db = _get_db()
    doc = await db.collection(settings.firestore_cache_collection).document(key).get()
    if not doc.exists:
        return None
    entry = doc.to_dict()
    if time.time() > entry.get("expires_at", 0):
        await db.collection(settings.firestore_cache_collection).document(key).delete()
        return None
    return entry.get("data")


async def set_cached(key: str, data: Any, ttl: int) -> None:
    db = _get_db()
    await db.collection(settings.firestore_cache_collection).document(key).set(
        {
            "data":       data,
            "expires_at": time.time() + ttl,
            "source":     "the-racing-api",
            "cached_at":  time.time(),
        }
    )
