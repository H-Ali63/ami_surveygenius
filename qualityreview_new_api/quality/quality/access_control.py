"""
Server-side access-control decorators.

The templates already hide nav links based on request.user.user_employee's
department/designation/employee_id - but hiding a link doesn't stop someone
from typing the URL directly. These decorators enforce the same checks on
the view itself, so a hidden link can't be bypassed by forced browsing.

Usage (function-based view):
    @require_employee_ids("107424")
    def my_view(request): ...

Usage (class-based view):
    @method_decorator(require_employee_ids("107424"), name="dispatch")
    class MyView(TemplateView): ...
"""

import logging
from functools import wraps

from django.conf import settings  #type: ignore
from django.http import HttpResponseForbidden, JsonResponse #type: ignore
from django.shortcuts import redirect #type: ignore

logger = logging.getLogger(__name__)


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or (
        "application/json" in request.headers.get("accept", "")
    )


def _login_redirect(request):
    login_url = getattr(settings, "LOGIN_URL", "/login")
    return redirect(f"{login_url}?next={request.path}")


def _deny(request, reason):
    logger.warning(
        "Access denied (%s) user=%s path=%s",
        reason,
        getattr(request.user, "username", "anonymous"),
        request.path,
    )
    message = "You do not have permission to access this resource."
    if _is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=403)
    return HttpResponseForbidden(message)


def require_staff(view_func):
    """Restrict a view to Django staff/superuser accounts."""

    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _login_redirect(request)

        if not request.user.is_staff:
            return _deny(request, "staff required")

        return view_func(request, *args, **kwargs)

    return wrapped


def require_employee_ids(*employee_ids):
    """Restrict a view to specific employee IDs (matches legacy hardcoded checks)."""
    allowed = {str(e) for e in employee_ids}

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _login_redirect(request)

            employee = getattr(request.user, "user_employee", None)
            employee_id = str(getattr(employee, "employee_id", "")) if employee else ""

            if employee_id not in allowed:
                return _deny(request, "employee_id not allowed")

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def require_roles(departments=None, roles=None):
    """
    Restrict a view to users whose designation.department.name is in
    `departments` (if given) AND whose designation.name is in `roles`
    (if given). Pass an iterable for either; leave as None to skip that check.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _login_redirect(request)

            employee = getattr(request.user, "user_employee", None)
            designation = getattr(employee, "designation", None)
            department = getattr(designation, "department", None)

            department_name = getattr(department, "name", None)
            role_name = getattr(designation, "name", None)

            if departments is not None and department_name not in departments:
                return _deny(request, "department not allowed")
            if roles is not None and role_name not in roles:
                return _deny(request, "role not allowed")

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
