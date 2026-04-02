"""
Central config. All values from environment variables.
In Cloud Run, set via Secret Manager (--set-secrets).
Locally, copy .env.example → .env and fill in values.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── The Racing API ────────────────────────────────────────────────────────
    # Basic Auth: username and password from theracingapi.com/dashboard
    racing_api_user: str                    # RACING_API_USER env var
    racing_api_pass: str                    # RACING_API_PASS env var
    racing_api_base_url: str = "https://api.theracingapi.com"

    # ── FSU Admin ─────────────────────────────────────────────────────────────
    admin_key: str                          # ADMIN_KEY env var

    # ── GCP / Firestore ───────────────────────────────────────────────────────
    gcp_project: str = "chimera-v4"
    firestore_cache_collection: str = "fsu_1y_cache"
    firestore_keys_collection: str  = "fsu_1y_api_keys"

    # ── Cache TTLs (seconds) ──────────────────────────────────────────────────
    cache_ttl_racecards: int  = 180    # 3 min — matches Racing API update freq
    cache_ttl_odds: int       = 60     # 1 min — odds change fast pre-race
    cache_ttl_results: int    = 300    # 5 min — results don't change
    cache_ttl_form: int       = 3600   # 1 hour — form is historical
    cache_ttl_meetings: int   = 600    # 10 min

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
