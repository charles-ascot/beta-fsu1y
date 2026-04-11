"""
Async HTTP client for The Racing API v1.
Authentication: HTTP Basic Auth (username:password).
All calls are Firestore-cached.
"""

import httpx
import base64
from typing import Optional, Any
from fastapi import HTTPException

from config import settings
from services.cache import get_cached, set_cached, make_cache_key


def _make_auth_header() -> str:
    raw = f"{settings.racing_api_user}:{settings.racing_api_pass}"
    return "Basic " + base64.b64encode(raw.encode()).decode()


class RacingAPIClient:
    BASE = settings.racing_api_base_url

    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=20.0,
            headers={"Authorization": _make_auth_header()},
        )

    async def _get(self, path: str, params: dict) -> Any:
        """Raw GET — raises HTTPException on non-200."""
        clean = {k: v for k, v in params.items() if v is not None}
        resp = await self._client.get(f"{self.BASE}{path}", params=clean)

        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Racing API credentials rejected")
        if resp.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Racing API access denied — check plan tier for this endpoint"
            )
        if resp.status_code == 429:
            raise HTTPException(status_code=429, detail="Racing API rate limit exceeded")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Racing API error: {resp.text[:200]}",
            )
        return resp.json()

    async def _cached_get(self, cache_key: str, path: str, params: dict, ttl: int) -> dict:
        cached = await get_cached(cache_key)
        if cached is not None:
            return {**cached, "cache": "HIT"}
        data = await self._get(path, params)
        payload = {"data": data, "cache": "MISS"}
        try:
            await set_cached(cache_key, payload, ttl)
        except Exception:
            pass  # Cache write can fail (e.g. >1MB doc) — still return data
        return {**payload, "cache": "MISS"}

    # ── Racecards ─────────────────────────────────────────────────────────────

    async def get_racecards(
        self,
        day: str = "today",
        region: Optional[str] = None,
        race_class: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> dict:
        params = {"day": day, "limit": limit, "skip": skip}
        if region:     params["region"] = region
        if race_class: params["class"]  = race_class
        cache_key = make_cache_key("racecards", **params)
        return await self._cached_get(cache_key, "/v1/racecards/basic", params, settings.cache_ttl_racecards)

    async def get_racecard_pro(self, race_id: str) -> dict:
        cache_key = make_cache_key("racecard_pro", race_id=race_id)
        return await self._cached_get(cache_key, "/v1/racecards/pro", {"race_id": race_id}, settings.cache_ttl_racecards)

    # ── Races ─────────────────────────────────────────────────────────────────

    async def get_races(
        self,
        date: Optional[str] = None,
        region: Optional[str] = None,
        course: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if date:   params["date"]   = date
        if region: params["region"] = region
        if course: params["course"] = course
        cache_key = make_cache_key("races", **params)
        return await self._cached_get(cache_key, "/v1/races", params, settings.cache_ttl_meetings)

    # ── Runners ───────────────────────────────────────────────────────────────

    async def get_runners(self, race_id: str) -> dict:
        cache_key = make_cache_key("runners", race_id=race_id)
        return await self._cached_get(cache_key, "/v1/runners", {"race_id": race_id}, settings.cache_ttl_racecards)

    # ── Odds ──────────────────────────────────────────────────────────────────

    async def get_odds(self, race_id: str, limit: int = 50, skip: int = 0) -> dict:
        """20+ bookmaker odds per runner. Requires Standard plan or above."""
        params = {"race_id": race_id, "limit": limit, "skip": skip}
        cache_key = make_cache_key("odds", **params)
        return await self._cached_get(cache_key, "/v1/odds", params, settings.cache_ttl_odds)

    # ── Results ───────────────────────────────────────────────────────────────

    async def get_results(
        self,
        date: Optional[str] = None,
        region: Optional[str] = None,
        course: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if date:   params["date"]   = date
        if region: params["region"] = region
        if course: params["course"] = course
        cache_key = make_cache_key("results", **params)
        return await self._cached_get(cache_key, "/v1/results", params, settings.cache_ttl_results)

    async def get_result(self, race_id: str) -> dict:
        cache_key = make_cache_key("result", race_id=race_id)
        return await self._cached_get(cache_key, "/v1/results", {"race_id": race_id}, settings.cache_ttl_results)

    # ── Form ──────────────────────────────────────────────────────────────────

    async def get_horse_form(self, horse_id: str, limit: int = 10) -> dict:
        params = {"horse_id": horse_id, "limit": limit}
        cache_key = make_cache_key("horse_form", **params)
        return await self._cached_get(cache_key, "/v1/horses/form", params, settings.cache_ttl_form)

    async def get_meetings(self, date: Optional[str] = None, region: Optional[str] = None) -> dict:
        params: dict = {}
        if date:   params["date"]   = date
        if region: params["region"] = region
        cache_key = make_cache_key("meetings", **params)
        return await self._cached_get(cache_key, "/v1/meetings", params, settings.cache_ttl_meetings)

    # ── Courses ───────────────────────────────────────────────────────────────

    async def get_courses(
        self,
        region_codes: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if region_codes: params["region_codes"] = region_codes
        cache_key = make_cache_key("courses", **params)
        return await self._cached_get(cache_key, "/v1/courses", params, settings.cache_ttl_form)

    async def get_regions(self, limit: int = 50, skip: int = 0) -> dict:
        params = {"limit": limit, "skip": skip}
        cache_key = make_cache_key("regions", **params)
        return await self._cached_get(cache_key, "/v1/courses/regions", params, settings.cache_ttl_form)

    # ── Horses ────────────────────────────────────────────────────────────────

    async def get_horses(
        self,
        horse_name: Optional[str] = None,
        horse_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if horse_name: params["horse_name"] = horse_name
        if horse_id:   params["horse_id"]   = horse_id
        cache_key = make_cache_key("horses", **params)
        return await self._cached_get(cache_key, "/v1/horses", params, settings.cache_ttl_form)

    # ── Jockeys ───────────────────────────────────────────────────────────────

    async def get_jockeys(
        self,
        jockey_name: Optional[str] = None,
        jockey_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if jockey_name: params["jockey_name"] = jockey_name
        if jockey_id:   params["jockey_id"]   = jockey_id
        cache_key = make_cache_key("jockeys", **params)
        return await self._cached_get(cache_key, "/v1/jockeys", params, settings.cache_ttl_form)

    # ── Trainers ──────────────────────────────────────────────────────────────

    async def get_trainers(
        self,
        trainer_name: Optional[str] = None,
        trainer_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if trainer_name: params["trainer_name"] = trainer_name
        if trainer_id:   params["trainer_id"]   = trainer_id
        cache_key = make_cache_key("trainers", **params)
        return await self._cached_get(cache_key, "/v1/trainers", params, settings.cache_ttl_form)

    # ── Owners ────────────────────────────────────────────────────────────────

    async def get_owners(
        self,
        owner_name: Optional[str] = None,
        owner_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if owner_name: params["owner_name"] = owner_name
        if owner_id:   params["owner_id"]   = owner_id
        cache_key = make_cache_key("owners", **params)
        return await self._cached_get(cache_key, "/v1/owners", params, settings.cache_ttl_form)

    # ── Sires ─────────────────────────────────────────────────────────────────

    async def get_sires(
        self,
        sire_name: Optional[str] = None,
        sire_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if sire_name: params["sire_name"] = sire_name
        if sire_id:   params["sire_id"]   = sire_id
        cache_key = make_cache_key("sires", **params)
        return await self._cached_get(cache_key, "/v1/sires", params, settings.cache_ttl_form)

    # ── Dams ──────────────────────────────────────────────────────────────────

    async def get_dams(
        self,
        dam_name: Optional[str] = None,
        dam_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if dam_name: params["dam_name"] = dam_name
        if dam_id:   params["dam_id"]   = dam_id
        cache_key = make_cache_key("dams", **params)
        return await self._cached_get(cache_key, "/v1/dams", params, settings.cache_ttl_form)

    # ── Damsires ──────────────────────────────────────────────────────────────

    async def get_damsires(
        self,
        damsire_name: Optional[str] = None,
        damsire_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        params = {"limit": limit, "skip": skip}
        if damsire_name: params["damsire_name"] = damsire_name
        if damsire_id:   params["damsire_id"]   = damsire_id
        cache_key = make_cache_key("damsires", **params)
        return await self._cached_get(cache_key, "/v1/damsires", params, settings.cache_ttl_form)


# Singleton
racing_client = RacingAPIClient()
