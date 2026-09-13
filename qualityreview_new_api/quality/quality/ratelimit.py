"""
Lightweight rate limiting built on the Redis cache already configured in
settings.py (CACHES['default']). No new dependency required.

Two layers are used:
  - GlobalRateLimitMiddleware: a blanket per-IP/per-user cap on every request.
  - rate_limit(...): a decorator for tighter limits on specific sensitive
    endpoints (login, uploads, etc.), stacked on top of the global cap.
"""

import logging
import time

from django.core.cache import cache #type: ignore
from django.http import JsonResponse #type: ignore

logger = logging.getLogger(__name__)

_last_backend_warning = {"ts": 0.0}
_BACKEND_WARNING_INTERVAL = 30  # seconds


def get_client_ip(request):
    """Real client IP, honoring X-Forwarded-For from a trusted reverse proxy."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _too_many_requests(retry_after):
    response = JsonResponse(
        {"success": False, "message": "Too many requests. Please try again later."},
        status=429,
    )
    response['Retry-After'] = str(retry_after)
    return response


def check_rate_limit(key, limit, window_seconds):
    """
    Atomic fixed-window counter. Returns (allowed, retry_after_seconds).
    Fails open (allows the request) if the cache backend itself is down -
    a rate limiter should never become a site-wide outage.
    """
    try:
        added = cache.add(key, 1, timeout=window_seconds)
        if added:
            return True, 0

        try:
            count = cache.incr(key)
        except ValueError:
            # Key expired between add() and incr() - treat as a fresh window.
            cache.set(key, 1, timeout=window_seconds)
            return True, 0

        if count > limit:
            ttl = cache.ttl(key) if hasattr(cache, 'ttl') else window_seconds
            return False, ttl or window_seconds

        return True, 0
    except Exception:
        now = time.monotonic()
        if now - _last_backend_warning["ts"] > _BACKEND_WARNING_INTERVAL:
            _last_backend_warning["ts"] = now
            logger.warning("Rate-limit cache backend unavailable; allowing requests through.", exc_info=True)
        return True, 0


def rate_limit(limit, window_seconds, scope, key_func=None):
    """
    Decorator for function-based views or individual CBV methods.

    scope: short namespace for the counter, e.g. 'login'.
    key_func: optional callable(request) -> str. Defaults to per-IP.
    """
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            ident = key_func(request) if key_func else get_client_ip(request)
            cache_key = f"ratelimit:{scope}:{ident}"
            allowed, retry_after = check_rate_limit(cache_key, limit, window_seconds)
            if not allowed:
                logger.warning("Rate limit exceeded scope=%s ident=%s path=%s", scope, ident, request.path)
                return _too_many_requests(retry_after)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


class GlobalRateLimitMiddleware:
    """
    Blanket abuse guard applied to every request (IP-based for anonymous
    users, username-based once authenticated). Specific sensitive endpoints
    (e.g. login) layer a stricter @rate_limit on top of this.
    """
    LIMIT = 240           # requests
    WINDOW_SECONDS = 60   # per minute
    EXEMPT_PREFIXES = ('/static/', '/media/', '/admin/jsi18n/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.EXEMPT_PREFIXES):
            return self.get_response(request)

        user = getattr(request, 'user', None)
        ident = f"user:{user.pk}" if user is not None and user.is_authenticated else f"ip:{get_client_ip(request)}"

        cache_key = f"ratelimit:global:{ident}"
        allowed, retry_after = check_rate_limit(cache_key, self.LIMIT, self.WINDOW_SECONDS)
        if not allowed:
            logger.warning("Global rate limit exceeded ident=%s path=%s", ident, request.path)
            return _too_many_requests(retry_after)

        return self.get_response(request)
