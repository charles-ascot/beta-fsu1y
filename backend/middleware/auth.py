"""
FSU API key middleware — identical pattern to FSU-1X.
Validates X-API-Key on every request except exempt paths.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from services.key_service import is_valid_key

EXEMPT_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"

        if path in EXEMPT_PATHS or path.startswith("/v1/keys"):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing X-API-Key header"},
            )

        if not await is_valid_key(api_key):
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or revoked API key"},
            )

        return await call_next(request)
