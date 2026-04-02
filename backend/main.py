"""
Chimera FSU-1Y — The Racing API
FastAPI backend. Wraps The Racing API with its own auth layer,
Firestore caching, and a built-in API key generator.

All consumer requests require:  X-API-Key: <fsu_key>
All admin requests require:     X-Admin-Key: <admin_key>
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from middleware.auth import APIKeyMiddleware
from routers import racecards, races, runners, odds, results, form, lookup, keys


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"FSU-1Y starting — project: {settings.gcp_project}")
    yield
    print("FSU-1Y shutting down")


app = FastAPI(
    title="Chimera FSU-1Y — The Racing API",
    description=(
        "Fractional Service Unit wrapping The Racing API. "
        "Provides UK/Ireland/HK horse racing data: racecards, runners, "
        "multi-bookmaker odds, results, form, and full reference lookups "
        "(courses, regions, horses, jockeys, trainers, owners, sires, dams, damsires). "
        "All endpoints require a valid X-API-Key except /health and /docs."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(APIKeyMiddleware)

# Core racing endpoints
app.include_router(racecards.router, prefix="/v1", tags=["Racecards"])
app.include_router(races.router,     prefix="/v1", tags=["Races"])
app.include_router(runners.router,   prefix="/v1", tags=["Runners"])
app.include_router(odds.router,      prefix="/v1", tags=["Odds"])
app.include_router(results.router,   prefix="/v1", tags=["Results"])
app.include_router(form.router,      prefix="/v1", tags=["Form"])

# Reference / lookup endpoints
app.include_router(lookup.router,    prefix="/v1", tags=["Lookup"])

# Key management
app.include_router(keys.router,      prefix="/v1", tags=["API Keys"])


@app.get("/health", tags=["System"])
async def health():
    """Health check — no auth required. Used by Cloud Run."""
    return {"status": "ok", "service": "fsu-1y-racing-api", "version": "1.0.0"}
