from fastapi import Request, HTTPException
from time import time

# Simple in-memory limiter (good enough for demo/day-1). For production use Redis.
_BUCKET: dict[str, list[float]] = {}

def rate_limit(key_prefix: str, max_requests: int, window_seconds: int):
    async def _limiter(request: Request):
        ip = request.client.host if request.client else "unknown"
        key = f"{key_prefix}:{ip}"
        now = time()

        hits = _BUCKET.get(key, [])
        # Keep only events within window
        hits = [t for t in hits if now - t <= window_seconds]

        if len(hits) >= max_requests:
            raise HTTPException(status_code=429, detail="Too many requests. Try again later.")

        hits.append(now)
        _BUCKET[key] = hits

    return _limiter
