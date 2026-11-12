"""Rate limiting for the FastAPI backend (slowapi).

Two layers protect the paid LLM / image endpoints:
  * a per-client limit, so one visitor can't hammer the API, and
  * a global daily cap shared by everyone, so total OpenAI spend has a ceiling
    even if someone rotates IPs.

All limits are configurable through environment variables (see src/core/config.py).
"""
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from src.core.config import settings


def client_ip(request: Request) -> str:
    """Return the caller's IP address in a way that can't be spoofed on Cloud Run.

    Cloud Run appends the IP it actually sees to the *right* of X-Forwarded-For.
    Anything to the left was supplied by the caller and can be faked, so we count
    `TRUSTED_PROXY_HOPS` entries from the right (1 = Cloud Run directly).
    Add one hop for every extra proxy you put in front (e.g. a load balancer).
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        hops = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
        if hops:
            index = max(len(hops) - settings.trusted_proxy_hops, 0)
            return hops[index]
    return request.client.host if request.client else "unknown"


def global_key() -> str:
    """Single shared bucket for limits that apply to all callers combined."""
    return "global"


limiter = Limiter(
    key_func=client_ip,
    default_limits=[settings.rate_limit_default],
    storage_uri=settings.rate_limit_storage_uri,
    enabled=settings.rate_limit_enabled,
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded ({exc.detail}). Please try again later."},
    )
