"""Simple in-memory rate limiter for exposed API routes."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, limit: int = 120, window: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in {"/health", "/docs", "/redoc", "/openapi.json"}:
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)

        segment = path.split("/")[3] if path.count("/") >= 3 else path
        key = f"{self._client_key(request)}:{segment}"
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            while bucket and now - bucket[0] > self.window:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return JSONResponse(
                    {
                        "detail": "Demasiadas solicitudes. Intenta de nuevo en unos segundos.",
                        "code": "rate_limited",
                    },
                    status_code=429,
                    headers={"Retry-After": str(self.window)},
                )
            bucket.append(now)
        return await call_next(request)
