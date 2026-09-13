"""
Custom 400/403/404/500 handlers. Django only invokes these when DEBUG=False.
Full exception/request detail goes to logs only - the response body is
always the fixed generic message, matching the AJAX error shape used
elsewhere: {"success": false, "message": "..."}.
"""

import logging

from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
    JsonResponse,
)
from django.utils.html import escape

logger = logging.getLogger(__name__)

GENERIC_MESSAGES = {
    400: "The request could not be understood by the server.",
    403: "You do not have permission to access this resource.",
    404: "The page you're looking for could not be found.",
    500: "Something went wrong. Please try again.",
}

_RESPONSE_CLASSES = {
    400: HttpResponseBadRequest,
    403: HttpResponseForbidden,
    404: HttpResponseNotFound,
    500: HttpResponseServerError,
}


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or (
        "application/json" in request.headers.get("accept", "")
    )


def _render_error(request, status):
    message = GENERIC_MESSAGES[status]

    if _is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=status)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Error {status}</title></head>
<body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
    <h1>{status}</h1>
    <p>{escape(message)}</p>
    <a href="/">Go back home</a>
</body>
</html>"""
    return _RESPONSE_CLASSES[status](html, content_type="text/html")


def handler400(request, exception=None):
    logger.warning("400 Bad Request on %s: %s", request.path, exception)
    return _render_error(request, 400)


def handler403(request, exception=None):
    logger.warning("403 Forbidden on %s: %s", request.path, exception)
    return _render_error(request, 403)


def handler404(request, exception=None):
    logger.info("404 Not Found on %s", request.path)
    return _render_error(request, 404)


def handler500(request):
    logger.exception("500 Internal Server Error on %s", request.path)
    return _render_error(request, 500)
