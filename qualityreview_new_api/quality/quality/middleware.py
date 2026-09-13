# quality/middleware.py

import json
import logging
import hashlib
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings #type: ignore
from django.contrib import messages #type: ignore
from django.contrib.auth import logout #type: ignore
from django.http import HttpResponse, JsonResponse  #type: ignore
from django.shortcuts import redirect #type: ignore
from django.utils.html import escape #type: ignore
from django.utils import timezone #type: ignore

logger = logging.getLogger(__name__)


def _browser_fingerprint(request):
    parts = [
        request.META.get("HTTP_USER_AGENT", ""),
        request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_skip(request):
            return self.get_response(request)

        if not request.user.is_authenticated:
            if self._is_ajax_request(request):
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Your session has expired. Please log in again.",
                        "detail": "Your session has expired. Please log in again.",
                    },
                    status=401,
                )

            self._add_warning_message(request)
            login_url = getattr(settings, "LOGIN_URL", "/login")
            if not login_url.startswith("/"):
                login_url = f"/{login_url}"

            if request.get_full_path() not in {"/", ""}:
                login_url = f"{login_url}?{urlencode({'next': request.get_full_path()})}"

            return redirect(login_url)

        # Normalize sessions created with an older, shorter expiry policy.
        # This also repairs existing sessions without forcing a logout.
        session_age = request.session.get_expiry_age()
        configured_age = getattr(settings, "SESSION_COOKIE_AGE", 604800)
        if session_age < configured_age:
            request.session.set_expiry(configured_age)

        return self.get_response(request)

    def _should_skip(self, request):
        excluded_paths = (
            "/login",
            "/login/",
            "/admin",
            "/admin/",
            "/static/",
            "/media/",
            "/favicon.ico",
            "/.well-known/",
        )
        return any(request.path.startswith(path) for path in excluded_paths)

    def _add_warning_message(self, request):
        if not hasattr(request, "_messages"):
            return
        messages.warning(request, "Your session has expired. Please log in again.")

    def _is_ajax_request(self, request):
        return request.headers.get("x-requested-with") == "XMLHttpRequest" or (
            "application/json" in request.headers.get("accept", "")
        )


class BrowserSessionIntegrityMiddleware:
    """
    Binds an authenticated session to a browser fingerprint and enforces
    an idle timeout that matches SESSION_COOKIE_AGE.

    This blocks casual replay of a copied session cookie in a different
    browser context and prevents the session from expiring earlier than
    the configured 30-minute window.
    """

    FINGERPRINT_KEY = "browser_fingerprint"
    LAST_SEEN_KEY = "browser_last_seen"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_skip(request) or not getattr(request, "user", None) or not request.user.is_authenticated:
            return self.get_response(request)

        fingerprint = _browser_fingerprint(request)
        stored_fingerprint = request.session.get(self.FINGERPRINT_KEY)

        if stored_fingerprint is None:
            request.session[self.FINGERPRINT_KEY] = fingerprint
            request.session[self.LAST_SEEN_KEY] = timezone.now().isoformat()
            request.session.modified = True
            return self.get_response(request)

        if stored_fingerprint != fingerprint:
            logger.warning(
                "Browser fingerprint mismatch user=%s path=%s",
                getattr(request.user, "username", "anonymous"),
                request.path,
            )
            logout(request)
            request.session.flush()

            if self._is_ajax_request(request):
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Your login session was used from another browser and has been ended. Please log in again.",
                    },
                    status=401,
                )

            login_url = getattr(settings, "LOGIN_URL", "/login")
            if not login_url.startswith("/"):
                login_url = f"/{login_url}"
            return redirect(f"{login_url}?{urlencode({'next': request.get_full_path()})}")

        max_age = getattr(settings, "SESSION_COOKIE_AGE", 86400)
        last_seen_raw = request.session.get(self.LAST_SEEN_KEY)

        if last_seen_raw:
            try:
                last_seen = timezone.datetime.fromisoformat(last_seen_raw)
                if timezone.is_naive(last_seen):
                    last_seen = timezone.make_aware(last_seen, timezone.get_current_timezone())
                if timezone.now() - last_seen > timedelta(seconds=max_age):
                    logger.warning(
                        "Session idle timeout exceeded user=%s path=%s",
                        getattr(request.user, "username", "anonymous"),
                        request.path,
                    )
                    logout(request)
                    request.session.flush()
                    if self._is_ajax_request(request):
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "Your session has expired after inactivity. Please log in again.",
                            },
                            status=401,
                        )
                    login_url = getattr(settings, "LOGIN_URL", "/login")
                    if not login_url.startswith("/"):
                        login_url = f"/{login_url}"
                    return redirect(f"{login_url}?{urlencode({'next': request.get_full_path()})}")
            except Exception:
                # If the timestamp is malformed, reset it instead of failing open.
                request.session[self.LAST_SEEN_KEY] = timezone.now().isoformat()
                request.session.modified = True
                return self.get_response(request)

        request.session[self.LAST_SEEN_KEY] = timezone.now().isoformat()
        request.session.modified = True
        return self.get_response(request)

    def _should_skip(self, request):
        excluded_paths = (
            "/login",
            "/login/",
            "/admin",
            "/admin/",
            "/static/",
            "/media/",
            "/favicon.ico",
            "/.well-known/",
        )
        return any(request.path.startswith(path) for path in excluded_paths)

    def _is_ajax_request(self, request):
        return request.headers.get("x-requested-with") == "XMLHttpRequest" or (
            "application/json" in request.headers.get("accept", "")
        )


class ExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            logger.exception("Unhandled exception while processing %s", request.path)

            message = "Something went wrong while processing your request. Please try again."

            if self._is_ajax_request(request):
                return JsonResponse(
                    {"success": False, "message": message, "detail": message},
                    status=500,
                )

            try:
                messages.error(request, message)
            except Exception:
                pass

            html = f"""
            <!DOCTYPE html>
            <html lang=\"en\">
            <head>
                <meta charset=\"utf-8\">
                <title>Request Error</title>
            </head>
            <body style=\"font-family: Arial, sans-serif; padding: 24px;\">
                <script>
                    window.alert({json.dumps(escape(message))});
                    window.history.back();
                </script>
                <p>{escape(message)}</p>
            </body>
            </html>
            """
            return HttpResponse(html, content_type="text/html", status=500)

    def _is_ajax_request(self, request):
        return request.headers.get("x-requested-with") == "XMLHttpRequest" or (
            "application/json" in request.headers.get("accept", "")
        )