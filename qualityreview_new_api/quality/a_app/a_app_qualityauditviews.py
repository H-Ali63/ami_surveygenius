# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import json
import logging
from datetime import datetime, time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db import connection
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from search.models import (
    Project,
    Employee,
    SurveyResponse,
    VerificationStatus,
)

from quality.ratelimit import rate_limit, get_client_ip


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------

PAGE_SIZE = 100

QUALITY_AUDIT_TEMPLATE = "a_app_templates/a_app_qualityaudit.html"

# Legacy IP replacement used inside params JSON.
OLD_IP_1 = "103.226.1.242:8888"
OLD_IP_2 = "103.218.101.38:8888"
NEW_IP = "192.168.1.251"


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def parse_json_field(value, default=None):
    """
    Safely parse JSON stored inside SurveyResponse.params / remarks.

    Some old records may contain invalid JSON, blank values or None.
    """

    if default is None:
        default = {}

    if not value:
        return default

    try:
        if isinstance(value, dict):
            return value

        return json.loads(value)

    except (ValueError, TypeError, json.JSONDecodeError):
        logger.warning(
            "Unable to parse JSON field. Returning default value."
        )
        return default


def normalize_params(value):
    """
    Parse params and replace old server IPs with current internal IP.
    """

    if not value:
        return {}

    try:
        value = value.replace(OLD_IP_1, NEW_IP)
        value = value.replace(OLD_IP_2, NEW_IP)

        return json.loads(value)

    except (ValueError, TypeError, json.JSONDecodeError):
        logger.warning(
            "Invalid params JSON encountered."
        )
        return {}


def normalize_remarks(value):
    """
    Safely parse remarks JSON.
    """

    if not value:
        return {}

    try:
        return json.loads(value)

    except (ValueError, TypeError, json.JSONDecodeError):
        return {}


def get_page_number(params):
    """
    Safely get pagination page number.
    """

    try:
        page = int(params.get("page", 0))

        if page < 0:
            return 0

        return page

    except (TypeError, ValueError):
        return 0


def get_date_range(params):
    """
    Convert fromdate/todate into timezone-aware datetime boundaries.

    Returns:
        (start_datetime, end_datetime)
    """

    from_date = params.get("fromdate", "").strip()
    to_date = params.get("todate", "").strip()

    start_datetime = None
    end_datetime = None

    try:
        if from_date:
            parsed_from = datetime.strptime(
                from_date,
                "%Y-%m-%d"
            )

            start_datetime = timezone.make_aware(
                datetime.combine(
                    parsed_from.date(),
                    time.min
                )
            )

    except ValueError:
        logger.warning(
            "Invalid fromdate received: %s",
            from_date
        )

    try:
        if to_date:
            parsed_to = datetime.strptime(
                to_date,
                "%Y-%m-%d"
            )

            end_datetime = timezone.make_aware(
                datetime.combine(
                    parsed_to.date(),
                    time.max
                )
            )

    except ValueError:
        logger.warning(
            "Invalid todate received: %s",
            to_date
        )

    return start_datetime, end_datetime


# ----------------------------------------------------------------------
# View
# ----------------------------------------------------------------------

@method_decorator(
    login_required(login_url="/login"),
    name="dispatch"
)
@method_decorator(
    rate_limit(
        limit=20,
        window_seconds=60,
        scope="quality_audit",
        key_func=lambda request: (
            request.user.pk
            if request.user.is_authenticated
            else get_client_ip(request)
        ),
    ),
    name="dispatch",
)
class QualityAuditView(TemplateView):
    """
    Optimized Quality Audit view.

    Main optimization points:

    1. Uses SurveyResponse.teamleader instead of params__contains.
    2. Uses select_related for all FK relationships.
    3. Uses database-level distinct().
    4. Does not load 10,000 SurveyResponse objects.
    5. Uses only() to reduce selected columns.
    6. Parses JSON only for the 100 displayed records.
    7. Uses a single filtering implementation for GET and POST.
    """

    template_name = "index.html"

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    def get(self, request, *args, **kwargs):

        try:
            data = self.process_request(
                request=request,
                params=request.GET,
                method="GET",
            )

            return render(
                request,
                self.template_name,
                data
            )

        except Exception:
            logger.exception(
                "QualityAuditView GET failed"
            )

            data = self.get_base_context(request)

            data["error"] = (
                "Unable to load quality audit data. "
                "Please try again."
            )

            return render(
                request,
                self.template_name,
                data
            )

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------

    def post(self, request, *args, **kwargs):

        try:
            data = self.process_request(
                request=request,
                params=request.POST,
                method="POST",
            )

            return render(
                request,
                self.template_name,
                data
            )

        except Exception:
            logger.exception(
                "QualityAuditView POST failed"
            )

            data = self.get_base_context(request)

            data["error"] = (
                "Unable to load quality audit data. "
                "Please try again."
            )

            return render(
                request,
                self.template_name,
                data
            )

    # ------------------------------------------------------------------
    # Base context
    # ------------------------------------------------------------------

    def get_base_context(self, request):

        data = {
            "first_name": "-",
            "last_name": "-",
            "userrole": "-",
            "department": "-",
            "htmlfilename": QUALITY_AUDIT_TEMPLATE,
            "maindata": [],
            "count": None,
            "totalcount": None,
            "page": 0,
            "previous": 0,
            "next": 1,
            "allfilters": {
                "projects": [],
                "fieldresearchers": [],
                "verifiedby": [],
            },
            "getdata": "",
        }

        try:

            employee = (
                Employee.objects
                .select_related(
                    "user",
                    "designation",
                    "designation__department",
                )
                .filter(user=request.user)
                .first()
            )

            if employee:

                data["userrole"] = (
                    employee.designation.name
                    if employee.designation
                    else "-"
                )

                data["department"] = (
                    employee.designation.department.name
                    if (
                        employee.designation
                        and employee.designation.department
                    )
                    else "-"
                )

            data["first_name"] = request.user.first_name or "-"
            data["last_name"] = request.user.last_name or "-"

        except Exception:
            logger.exception(
                "Unable to build user context."
            )

        return data

    # ------------------------------------------------------------------
    # Main request processor
    # ------------------------------------------------------------------

    def process_request(self, request, params, method):

        data = self.get_base_context(request)
        
        params = params.copy()
        page = get_page_number(params)

        offset = page * PAGE_SIZE
        end = offset + PAGE_SIZE

        data["page"] = page
        data["previous"] = max(page - 1, 0)
        data["next"] = page + 1

        # --------------------------------------------------------------
        # Filters
        # --------------------------------------------------------------

        data["allfilters"] = self.get_filter_data()
        data["selected_filters"] = {
            "project": params.get("Project", ""),
            "fromdate": params.get("fromdate", ""),
            "todate": params.get("todate", ""),
            "fieldresearcher": params.get("FieldResearcher", ""),
            "surveyor": params.get("Surveyor", ""),
            "uid": params.get("uid", ""),
            "verifiedby": params.get("VerifiedBy", ""),
            "verifiedflag": params.get("verifiedflag", ""),
        }

        filter_keys = (
            "Project",
            "fromdate",
            "todate",
            "FieldResearcher",
            "Surveyor",
            "uid",
            "VerifiedBy",
            "verifiedflag",
        )
        if not any(params.get(key, "").strip() for key in filter_keys):
            data["maindata"] = []
            data["count"] = 0
            data["totalcount"] = "Enter filters and click Submit to load audit data."
            data["getdata"] = ""
            return data

        queryset = self.get_filtered_queryset(params)

        # --------------------------------------------------------------
        # Stable ordering
        # --------------------------------------------------------------

        queryset = queryset.order_by("-verification_date", "-pk")

        # --------------------------------------------------------------
        # Count
        # --------------------------------------------------------------

        total_records = queryset.count()

        # --------------------------------------------------------------
        # Pagination
        # --------------------------------------------------------------

        responses = queryset[offset:end]

        # --------------------------------------------------------------
        # Convert result to template data
        # --------------------------------------------------------------

        maindata = []

        for response in responses:

            maindata.append(
                {
                    "uid": response.uid,

                    "user": response.user,

                    "project": response.project,

                    "verification_status": (
                        response.verification_status
                    ),

                    "verification_date": (
                        response.verification_date
                    ),

                    "otp_verified": (
                        response.otp_verified
                    ),

                    "surveyor": response.surveyor,

                    "params": normalize_params(
                        response.params
                    ),

                    "remarks": normalize_remarks(
                        response.remarks
                    ),

                    # New optimized denormalized value.
                    "teamleader": response.teamleader,

                    # Useful if template needs it.
                    "response_date": response.response_date,
                }
            )

        data["maindata"] = maindata

        # --------------------------------------------------------------
        # Pagination text
        # --------------------------------------------------------------

        if total_records == 0:

            data["totalcount"] = "0 to 0 out of 0"

        else:

            start_number = offset + 1
            end_number = min(
                offset + PAGE_SIZE,
                total_records
            )

            data["totalcount"] = (
                f"{start_number} to "
                f"{end_number} out of "
                f"{total_records}"
            )

        data["count"] = total_records

        # --------------------------------------------------------------
        # Preserve request filters
        # --------------------------------------------------------------

        data["getdata"] = self.build_query_string(
            params
        )

        return data

    # ------------------------------------------------------------------
    # Filter data
    # ------------------------------------------------------------------

    def get_filter_data(self):
        cache_key = "quality-audit-filter-data"
        cached_filters = cache.get(cache_key)
        if cached_filters is not None:
            return cached_filters

        # --------------------------------------------------------------
        # Projects
        # --------------------------------------------------------------

        projects = list(
            Project.objects
            .only(
                "id",
                "name",
            )
            .order_by("name")
        )

        # --------------------------------------------------------------
        # Field Researchers
        #
        # IMPORTANT:
        #
        # Previously this was obtained by loading 10,000 rows and
        # json.loads(params) on every row.
        #
        # Now teamleader is a dedicated indexed DB field.
        # --------------------------------------------------------------

        fieldresearchers = set(
            SurveyResponse.objects
            .exclude(
                teamleader__isnull=True
            )
            .exclude(
                teamleader=""
            )
            .values_list(
                "teamleader",
                flat=True,
            )
            .distinct()
            .order_by("teamleader")
        )

        # Older responses may not have been backfilled into teamleader yet.
        # Extract only distinct legacy values in the database instead of
        # transferring and parsing up to 10,000 complete response records.
        if not fieldresearchers and connection.vendor == "mysql":
            legacy_fieldresearchers = (
                SurveyResponse.objects
                .annotate(
                    legacy_teamleader=RawSQL(
                        "CASE WHEN JSON_VALID(params) THEN "
                        "JSON_UNQUOTE(JSON_EXTRACT(params, %s)) "
                        "ELSE NULL END",
                        ("$.tldetails",),
                    )
                )
                .exclude(legacy_teamleader__isnull=True)
                .exclude(legacy_teamleader="")
                .values_list("legacy_teamleader", flat=True)
                .distinct()
                .order_by("legacy_teamleader")
            )
            fieldresearchers.update(legacy_fieldresearchers)

        # --------------------------------------------------------------
        # Verified By
        #
        # SurveyResponse.user -> Employee
        # Employee.user      -> Django User
        #
        # Therefore:
        #
        # user__user__first_name
        # user__user__last_name
        # user__user__username
        #
        # NOT:
        #
        # user__first_name
        # --------------------------------------------------------------

        verifiedby = list(
            Employee.objects
            .filter(
                response_assigned_to_user__isnull=False
            )
            .select_related("user")
            .only(
                "id",
                "employee_id",
                "user__id",
                "user__first_name",
                "user__last_name",
                "user__username",
            )
            .distinct()
            .order_by(
                "user__first_name",
                "user__last_name",
            )
        )

        filters = {
            "projects": projects,
            "fieldresearchers": sorted(fieldresearchers),
            "verifiedby": verifiedby,
        }
        cache.set(cache_key, filters, timeout=600)
        return filters

    # ------------------------------------------------------------------
    # Main queryset
    # ------------------------------------------------------------------

    def get_filtered_queryset(self, params):

        # --------------------------------------------------------------
        # Base QuerySet
        # --------------------------------------------------------------

        queryset = (
            SurveyResponse.objects
            .select_related(
                "user",
                "user__user",
                "project",
                "surveyor",
                "surveyor__user",
                "verification_status",
            )
            .only(
                "id",
                "uid",
                "uidi",
                "user_id",
                "project_id",
                "surveyor_id",
                "verification_status_id",
                "otp_verified",
                "params",
                "remarks",
                "verification_date",
                "send_to_surveyor",
                "allocated_survey",
                "response_date",
                "teamleader",

                # Employee -> User
                "user__id",
                "user__employee_id",
                "user__user__id",
                "user__user__first_name",
                "user__user__last_name",
                "user__user__username",

                # Project
                "project__id",
                "project__name",

                # Surveyor
                "surveyor__id",
                "surveyor__employee_id",
                "surveyor__user__id",
                "surveyor__user__first_name",
                "surveyor__user__last_name",
                "surveyor__user__username",

                # Verification status
                "verification_status__id",
                "verification_status__name",
            )
        )

        # --------------------------------------------------------------
        # Project
        # --------------------------------------------------------------

        project = params.get("Project", "").strip()

        if project:

            try:

                queryset = queryset.filter(
                    project_id=int(project)
                )

            except (TypeError, ValueError):

                logger.warning(
                    "Invalid Project filter: %s",
                    project
                )

        # --------------------------------------------------------------
        # Field Researcher
        #
        # OLD:
        #
        # params__contains=...
        #
        # NEW:
        #
        # teamleader=...
        #
        # teamleader has db_index=True.
        # --------------------------------------------------------------

        field_researcher = params.get(
            "FieldResearcher",
            ""
        ).strip()

        if field_researcher:

            queryset = queryset.filter(
                Q(teamleader=field_researcher)
                | Q(params__contains=field_researcher)
            )

        # --------------------------------------------------------------
        # Surveyor
        # --------------------------------------------------------------

        surveyor = params.get(
            "Surveyor",
            ""
        ).strip()

        if surveyor:

            queryset = queryset.filter(
                surveyor__employee_id=surveyor
            )

        # --------------------------------------------------------------
        # Verified By
        #
        # Verified By is SurveyResponse.user -> Employee.
        # Therefore user_id is Employee.id.
        # --------------------------------------------------------------

        verified_by = params.get(
            "VerifiedBy",
            ""
        ).strip()

        if verified_by:

            try:

                queryset = queryset.filter(
                    user_id=int(verified_by)
                )

            except (TypeError, ValueError):

                logger.warning(
                    "Invalid VerifiedBy filter: %s",
                    verified_by
                )

        # --------------------------------------------------------------
        # Verification flag
        # --------------------------------------------------------------

        verified_flag = params.get(
            "verifiedflag",
            ""
        )

        if verified_flag == "on":

            queryset = queryset.filter(
                verification_status__name="Verified"
            )

        # --------------------------------------------------------------
        # Date filters
        # --------------------------------------------------------------

        start_datetime, end_datetime = get_date_range(
            params
        )

        if start_datetime:

            queryset = queryset.filter(
                verification_date__gte=start_datetime
            )

        if end_datetime:

            queryset = queryset.filter(
                verification_date__lte=end_datetime
            )

        # --------------------------------------------------------------
        # UID
        #
        # UID is unique=True in your model.
        # Therefore this becomes a highly selective lookup.
        # --------------------------------------------------------------

        uid = params.get(
            "uid",
            ""
        ).strip()

        if uid:

            queryset = queryset.filter(
                uid=uid
            )

        return queryset

    # ------------------------------------------------------------------
    # Build query string
    # ------------------------------------------------------------------

    def build_query_string(self, params):

        query_items = []

        for key, value in params.items():

            if key == "csrfmiddlewaretoken":
                continue

            if isinstance(value, list):

                for item in value:

                    query_items.append(
                        f"{key}={item}"
                    )

            else:

                query_items.append(
                    f"{key}={value}"
                )

        return "&".join(query_items)