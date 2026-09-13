
from __future__ import unicode_literals

import logging
import pytz  ## #type: ignore

from collections import defaultdict

from pytz import timezone  #type: ignore

from dateutil import parser #type: ignore

# from StringIO import StringIO
import io
from django.contrib.auth.decorators import login_required  #type: ignore
from django.http import HttpResponse,JsonResponse  #type: ignore
from django.shortcuts import render,redirect #type: ignore
from django.utils.decorators import method_decorator  #type: ignore
from django.views.generic import TemplateView  #type: ignore
from django.shortcuts import HttpResponseRedirect #type: ignore
from django.contrib.auth import authenticate, login, logout #type: ignore
from django.contrib.auth.models import User #type: ignore
from django.conf import settings #type: ignore
from django.utils import timezone as django_timezone
from quality.access_control import require_roles #type: ignore
from quality.ratelimit import rate_limit, get_client_ip  #type: ignore
import requests as req #type: ignore
import MySQLdb #type: ignore
import mysql.connector #type: ignore
import uuid
import hashlib
# Create your views here.
import xlsxwriter #type: ignore

#from urllib2 import urlopen
from io import BytesIO
import json,datetime
from datetime import date,time
from .models import *
# from quality.models import *
import xlsxwriter   #type: ignore
# from django.db.models import Count,Case,When,Sum,FloatField, ExpressionWrapper, F, Q
try:
    from django.db.models import FloatField, F, Sum, Count, ExpressionWrapper, Value, Case, When, Q   #type: ignore
except ImportError:  # pragma: no cover
    from django.db import models   #type: ignore
    FloatField = models.FloatField
    F = models.F
    Sum = models.Sum
    Count = models.Count
    ExpressionWrapper = models.ExpressionWrapper
    Value = models.Value
    Case = models.Case
    When = models.When
    Q = models.Q
from django.db.models.functions import Cast   #type: ignore

logger = logging.getLogger(__name__)

sq3_list = []

value_list = SurveyResponse.objects.filter().exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())


datetime_today = '2024-07-22'
# print(datetime_today)
Project_ids = Assignment.objects.filter(employee__employee_id = 109691).values_list('project',flat= True) 
# print("-------",SurveyResponse.objects.filter(project__in = Project_ids,params__contains = datetime_today ).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))

def parse_surveyor_field(raw_value):
    """
    Parse and normalize surveyor value.

    Examples:
        (116415-(Ganesh Samarit))
        (116415 - (Ganesh Samarit))
        116415-(Ganesh Samarit)
        116415 - (Ganesh Samarit)
        116415 - Ganesh Samarit

    Returns:
        (surveyor_id, surveyor_name)

    Example:
        "(116415-(Ganesh Samarit))"
        -> (116415, "(Ganesh Samarit)")
    """

    raw_value = (raw_value or "").strip()

    if not raw_value:
        return None, ""

    surveyor_id = None
    surveyor_name = ""

    # ---------------------------------------------------------
    # Remove ONLY outer parentheses from the complete value
    # Example:
    # (116415-(Ganesh Samarit))
    # becomes:
    # 116415-(Ganesh Samarit)
    # ---------------------------------------------------------
    while raw_value.startswith("(") and raw_value.endswith(")"):
        raw_value = raw_value[1:-1].strip()

    # ---------------------------------------------------------
    # Split ID and name at first "-"
    # ---------------------------------------------------------
    if "-" in raw_value:
        id_part, name_part = raw_value.split("-", 1)

        # Clean ID
        id_part = id_part.strip().strip("()").strip()

        if id_part.isdigit():
            surveyor_id = int(id_part)

        # -----------------------------------------------------
        # Clean NAME
        # Remove any extra outer parentheses first
        # -----------------------------------------------------
        name_part = name_part.strip()

        while name_part.startswith("(") and name_part.endswith(")"):
            name_part = name_part[1:-1].strip()

        if name_part:
            surveyor_name = f"({name_part})"

    else:
        # -----------------------------------------------------
        # No "-" found
        # -----------------------------------------------------
        cleaned = raw_value.strip()

        # Remove outer parentheses
        while cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = cleaned[1:-1].strip()

        if cleaned.isdigit():
            surveyor_id = int(cleaned)
        else:
            # Try to find ID inside parentheses
            start = cleaned.find("(")
            end = cleaned.find(")", start + 1)

            if start != -1 and end != -1:
                possible_id = cleaned[start + 1:end].strip()

                if possible_id.isdigit():
                    surveyor_id = int(possible_id)

    return surveyor_id, surveyor_name


def _count_overall_forms(surveyor_id, project_id=None):
    """Count all distinct survey responses for one surveyor."""
    if not surveyor_id:
        return 0

    response_query = SurveyResponse.objects.filter(
        surveyor__employee_id=str(surveyor_id),
    )
    if project_id:
        response_query = response_query.filter(project_id=project_id)

    return response_query.values("uid").distinct().count()



@method_decorator(login_required(login_url='/login'), name='dispatch')
@method_decorator(
    rate_limit(limit=60, window_seconds=60, scope='search_v2',
               key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}"),
    name='dispatch',
)
class SearchV2(TemplateView):
    def __init__(self):

        pass

    def get(self,request):

        

        # print(value)

        data1 = []


        Project_ids = Assignment.objects.filter(employee__employee_id = 109691).values_list('project',flat= True)     ##cchangeeess



        if request.user.username == '112891':

            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids,verification_date__gte = datetime_today).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                
            for i in resulted:
                data1.append(i.uid)
        
        if request.user.username == '112418':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            for i in resulted:
                data1.append(i.uid)
        
        if request.user.username == '113124':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '110649':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '109691':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 5)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '111293':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 6)
            for i in resulted:
                data1.append(i.uid)
        
        if request.user.username == '107501':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 7)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '112418':

            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 8)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '108504':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey =9)
            for i in resulted:
                data1.append(i.uid)
        
        if request.user.username == '110880':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 10)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '104481':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 11)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '111264':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 12)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '111265':
            Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

            # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

            resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 13)
            for i in resulted:
                data1.append(i.uid)
        
        
        if request.user.username == '112779':
            resulted =SurveyResponse.objects.filter(allocated_survey = 14).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            list_of_uid = list()

            for value in resulted:
                d = json.loads(value.params)

                list_of_uid.append(d)
   

            dict_of_surveyors = defaultdict(list)

      

            for i in list_of_uid:
            
                surveyor = i["surveyor"]
                id1 = i["id1"]
                # surveyor_d = i["surveyor"] + "1"
                dates = i["date"]
                dict_of_surveyors[surveyor].append(id1)
                dict_of_surveyors[surveyor].append(parser.parse(dates).date())


            dict_of_surveyors2 = dict(dict_of_surveyors)

            dict_of_surveyors = []
            grouped_data = []
            for name, values in dict_of_surveyors2.items():
                groups = []
                for i in range(0, len(values), 2):
                    uid = values[i]
                    date = values[i + 1]
               
                    groups.append({'uid': uid, 'date': date})
                dict_of_surveyors.append({'name': name, 'groups': groups})
                    

            for i in resulted:
                data1.append(i.uid)
                # print(len(data1))
        
        if request.user.username == '109034':
            resulted =SurveyResponse.objects.filter(allocated_survey = 15).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 15)
            for i in resulted:
                data1.append(i.uid)
        
        if request.user.username == '102405':
            resulted =SurveyResponse.objects.filter(Q(allocated_survey = 16) | Q(allocated_survey = 15) | Q(allocated_survey = 14)).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
            # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 16)

            list_of_uid = list()

            for value in resulted:
                d = json.loads(value.params)

                list_of_uid.append(d)
           
            dict_of_surveyors = defaultdict(list)


            for i in list_of_uid:
                surveyor = i["surveyor"]
                id1 = i["id1"]
                dict_of_surveyors[surveyor].append(id1)


            dict_of_surveyors = dict(dict_of_surveyors)


            for i in resulted:
                data1.append(i.uid)
        

        
        max_val = 5

        # print(request.user.user_employee.designation.name,"=====",request.user.user_employee.employee_id,"<<<user::::",request.user.user_employee.designation.department.name)
        active_projects_list = QualityReview.objects.values("project_name").distinct()
        auditor_list = QualityReview.objects.values("quality_auditor","quality_auditor_id").distinct()
        sectionAIssueList = IssueList.objects.filter(section="section_A").values("issue_id","issues","related_question")
        sectionBIssueList = IssueList.objects.filter(section="section_B").values("issue_id", "issues","related_question")
        sectionCIssueList = IssueList.objects.filter(section="section_C").values("issue_id", "issues","related_question")
        sectionDIssueList = IssueList.objects.filter(section="section_D").values("issue_id", "issues","related_question")
        sectionEIssueList = IssueList.objects.filter(section="section_E").values("issue_id", "issues","related_question")
        # print(auditor_list,"<<<<<<<<<<<<<<<<,quality_auditor")

        data = {}
        
        today_min = django_timezone.make_aware(
            datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        )
        today_max = django_timezone.make_aware(
            datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        )
        
        ###################################################
        quality_project_wise_records = None
        auditor_count = 0
        if (request.user.user_employee.designation.department.name == "Quality" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance", "Manager"]) or \
            (request.user.user_employee.designation.department.name == "DRC" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance"]) or \
            (request.user.user_employee.designation.department.name == "Product" and request.user.user_employee.designation.name == "Manager"):
            quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max)).values("quality_auditor") \
                .annotate(Count('project_name'))
            auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max)).count()
            
        else:
            quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                    quality_auditor_id=request.user.user_employee.employee_id).values("project_name").annotate(Count('project_name'))
            auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                                                         quality_auditor_id=request.user.user_employee.employee_id).count()

        ###################################################




        uid_submitted = False
        
        if("filter" not in request.GET.keys() and "uid" in request.GET.keys() and request.GET["uid"]!=""):

            surveyResponse = SurveyResponse.objects.filter(uid=request.GET["uid"])
            # print(surveyResponse.count(),"<<<counttt")


            ####### code for highlighting submitted uids ##########

            submitted_uids_list = QualityReview.objects.filter(uid=request.GET["uid"])


            submitted_uids_list = [i.uid for i in submitted_uids_list]
            
            if submitted_uids_list:
                uid_submitted = True
            ####### code for highlighting submitted uids ##########


            # print("subbbbb",[i.uid for i in submitted_uids_list])

            if(surveyResponse.count()>0):
                params = json.loads(surveyResponse[0].params)

                remarks = json.loads(surveyResponse[0].remarks)
                surveyor_id, surveyor_name = parse_surveyor_field(params.get("surveyor", ""))
                tl_name=params["tldetails"]

                currentdatetime=datetime.datetime.now().strftime('%Y-%m-%d')


                data={
                    'user': request.user.user_employee,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    # #'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    "uid":request.GET["uid"],
                    "project_id":surveyResponse[0].project.id,
                    "project_name": surveyResponse[0].project.name,
                    "surveyor_name":surveyor_name,
                    "surveyor_id":surveyor_id,
                    "tl_name":tl_name,
                    "params":params,
                    "remarks":remarks,
                    "verification_status":surveyResponse[0].verification_status.name,
                    "audit_date":str(currentdatetime),
                    "interview_duration":params["timedifference"],
                    "interview_date":params["date"],
                    "quality_auditor_name":request.user.first_name +" "+ request.user.last_name,
                    "status":True,
                    'htmlfilename': 'search_quality_v2.html',
                    'maindata': [],
                    'notification': None,
                    "quality_auditor_id":request.user.user_employee.employee_id,
                    "auditor_position":request.user.user_employee.designation.department.name,
                    "active_projects_list":active_projects_list,
                    "auditor_list":auditor_list,
                    "msg": "",
                    "auditor_count_form":auditor_count,
                    "quality_project_wise_records":quality_project_wise_records,
                "sectionAIssueList":sectionAIssueList,
                "sectionBIssueList":sectionBIssueList,
                "sectionCIssueList":sectionCIssueList,
                "sectionDIssueList":sectionDIssueList,
                    "sectionEIssueList":sectionEIssueList,
                    "uids":data1,
                    #"dict_of_surveyors":dict_of_surveyors,
                    "submitted_uids_status":uid_submitted
                }
                # return render(request,"search_quality.html",data)
                return render(request, "index.html", data)
            else:
                data = {
                    'user': request.user.user_employee,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    #'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    'htmlfilename': 'search_quality_v2.html',
                    'maindata': [],
                    'notification': None,
                    "quality_auditor_id": request.user.user_employee.employee_id,
                    "auditor_position": request.user.user_employee.designation.department.name,
                    "active_projects_list": active_projects_list,
                    "auditor_list": auditor_list,
                    "msg": "",
                    "auditor_count_form": auditor_count,
                    "quality_project_wise_records":quality_project_wise_records,
                "sectionAIssueList":sectionAIssueList,
                "sectionBIssueList":sectionBIssueList,
                "sectionCIssueList":sectionCIssueList,
                "sectionDIssueList":sectionDIssueList,
                    "sectionEIssueList":sectionEIssueList,
                    "uids":data1,
                    #"dict_of_surveyors":dict_of_surveyors,
                    "submitted_uids_status":uid_submitted
                }
                return render(request, "index.html", data)
        elif("filter" in request.GET.keys()):
            if("auditor_project_name" in request.GET.keys() or "quality_auditor_name" in request.GET.keys() or "startdate" in request.GET.keys() or "enddate" in request.GET.keys()):

                if(request.GET["selected_form"]=="fetch" or request.GET["selected_form"]=="detailed_summary"):
                    qualityRecords = None

                    # Backend guard: at least one export date must be selected.
                    if(
                        request.GET.get("startdate", "") == "" and
                        request.GET.get("enddate", "") == "" and
                        request.GET.get("interview_startdate", "") == "" and
                        request.GET.get("interview_enddate", "") == ""
                    ):
                        return HttpResponse(
                            "Please select at least one date (To Date, From Date, Interview To Date, or Interview From Date) before export.",
                            status=400
                        )

                    if(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]!="" and request.GET["enddate"]!=""):

                        enddate=None
                        startdate = None
                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")


                        
                        qualityRecords = QualityReview.objects.filter(
                            auditor_date__range=[startdate, enddate],
                            project_name__icontains=request.GET.get("auditor_project_name", ""),
                            quality_auditor__icontains=request.GET.get("quality_auditor_name", "")
                        ).values("surveyor_name") \
                        .annotate(
                            surveyor_count=Count('surveyor_name', output_field=FloatField()),

                            # Define the division results with ExpressionWrapper
                            alisectionAskipping=ExpressionWrapper(
                                Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionAPercent=ExpressionWrapper(
                                (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                output_field=FloatField()
                            ) * 100,

                            alisectionBskills=ExpressionWrapper(
                                Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionBPercent=ExpressionWrapper(
                                (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                output_field=FloatField()
                            ) * 100,

                            alisectionCpolite=ExpressionWrapper(
                                Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionCspeech=ExpressionWrapper(
                                Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionCprofessional=ExpressionWrapper(
                                Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionCPercent=ExpressionWrapper(
                                (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                output_field=FloatField()
                            ) * 100,

                            alisectionDpolitecourteous=ExpressionWrapper(
                                Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionDrateofspeech=ExpressionWrapper(
                                Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                output_field=FloatField()
                            ) * 100,

                            alisectionDPercent=ExpressionWrapper(
                                (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                output_field=FloatField()
                            ) * 100,

                            alitotalABCD=ExpressionWrapper(
                                Sum("question_skipping_incomplete_recordings") +
                                Sum("question_subject_knowledge") +
                                Sum("voice_clarity") +
                                Sum("questioning_technique") +
                                Sum("convencing_skills") +
                                Sum("polite_courteous") +
                                Sum("rate_of_speech") +
                                Sum("professionalism_energetic_enthusiastic"),
                                output_field=FloatField()
                            ),

                            alisectionEvariation=Sum("variation"),
                            alisectionEsurvey=Sum("survey"),
                            alisectionEmovement=Sum("movement"),
                            alisectionEtagging=Sum("tagging"),
                            alisectionEtotal=ExpressionWrapper(
                                Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                output_field=FloatField()
                            ),

                            alisectionABCDE_diff=Sum("totalscore"),

                            test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                            test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                            test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                            test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                            qualityPercent=ExpressionWrapper(
                                (Sum("totalscore") / (
                                    Value(1 * int(max_val)) * F('surveyor_count') +
                                    Value(1 * int(max_val)) * F('surveyor_count') +
                                    Value(3 * int(max_val)) * F('surveyor_count') +
                                    Value(3 * int(max_val)) * F('surveyor_count')
                                )) * 40,
                                output_field=FloatField()
                            ),

                            sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                        )



                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]=="" and request.GET["enddate"]==""):





                        qualityRecords = QualityReview.objects.filter(
                            project_name__icontains=request.GET["auditor_project_name"],
                            quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                            .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()),

    # Define the division results with ExpressionWrapper
                                    alisectionAskipping=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionAPercent=ExpressionWrapper(
                                        (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,
                                    
                                    alisectionBskills=ExpressionWrapper(
                                        Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionBPercent=ExpressionWrapper(
                                        (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCpolite=ExpressionWrapper(
                                        Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCspeech=ExpressionWrapper(
                                        Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCprofessional=ExpressionWrapper(
                                        Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCPercent=ExpressionWrapper(
                                        (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDpolitecourteous=ExpressionWrapper(
                                        Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDrateofspeech=ExpressionWrapper(
                                        Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                        Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDPercent=ExpressionWrapper(
                                        (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alitotalABCD=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") +
                                        Sum("question_subject_knowledge") +
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills") +
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic"),
                                        output_field=FloatField()
                                    ),

                                    alisectionEvariation=Sum("variation"),
                                    alisectionEsurvey=Sum("survey"),
                                    alisectionEmovement=Sum("movement"),
                                    alisectionEtagging=Sum("tagging"),
                                    alisectionEtotal=ExpressionWrapper(
                                        Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                        output_field=FloatField()
                                    ),

                                    alisectionABCDE_diff=Sum("totalscore"),

                                    test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                                    qualityPercent=ExpressionWrapper(
                                        (Sum("totalscore") / (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )) * 40,
                                        output_field=FloatField()
                                    ),

                                    sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                                )
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] != "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

                        enddate=None
                        startdate=None

                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(
                            project_name__icontains=request.GET["auditor_project_name"],
                            auditor_date__range=[startdate,enddate]).values("surveyor_name") \
                            .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()),

    # Define the division results with ExpressionWrapper
                                    alisectionAskipping=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionAPercent=ExpressionWrapper(
                                        (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,
                                    
                                    alisectionBskills=ExpressionWrapper(
                                        Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionBPercent=ExpressionWrapper(
                                        (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCpolite=ExpressionWrapper(
                                        Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCspeech=ExpressionWrapper(
                                        Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCprofessional=ExpressionWrapper(
                                        Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCPercent=ExpressionWrapper(
                                        (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDpolitecourteous=ExpressionWrapper(
                                        Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDrateofspeech=ExpressionWrapper(
                                        Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                        Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDPercent=ExpressionWrapper(
                                        (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alitotalABCD=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") +
                                        Sum("question_subject_knowledge") +
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills") +
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic"),
                                        output_field=FloatField()
                                    ),

                                    alisectionEvariation=Sum("variation"),
                                    alisectionEsurvey=Sum("survey"),
                                    alisectionEmovement=Sum("movement"),
                                    alisectionEtagging=Sum("tagging"),
                                    alisectionEtotal=ExpressionWrapper(
                                        Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                        output_field=FloatField()
                                    ),

                                    alisectionABCDE_diff=Sum("totalscore"),

                                    test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                                    qualityPercent=ExpressionWrapper(
                                        (Sum("totalscore") / (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )) * 40,
                                        output_field=FloatField()
                                    ),

                                    sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                                )
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""): 

                        enddate = None
                        startdate = None


                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(
                            auditor_date__range=[startdate, enddate],
                            project_name__icontains=request.GET.get("auditor_project_name", ""),
                            quality_auditor__icontains=request.GET.get("quality_auditor_name", "")
                        ).values("surveyor_name") \
                        .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()),

    # Define the division results with ExpressionWrapper
                                    alisectionAskipping=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionAPercent=ExpressionWrapper(
                                        (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,
                                    
                                    alisectionBskills=ExpressionWrapper(
                                        Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionBPercent=ExpressionWrapper(
                                        (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCpolite=ExpressionWrapper(
                                        Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCspeech=ExpressionWrapper(
                                        Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCprofessional=ExpressionWrapper(
                                        Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCPercent=ExpressionWrapper(
                                        (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDpolitecourteous=ExpressionWrapper(
                                        Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDrateofspeech=ExpressionWrapper(
                                        Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                        Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDPercent=ExpressionWrapper(
                                        (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alitotalABCD=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") +
                                        Sum("question_subject_knowledge") +
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills") +
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic"),
                                        output_field=FloatField()
                                    ),

                                    alisectionEvariation=Sum("variation"),
                                    alisectionEsurvey=Sum("survey"),
                                    alisectionEmovement=Sum("movement"),
                                    alisectionEtagging=Sum("tagging"),
                                    alisectionEtotal=ExpressionWrapper(
                                        Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                        output_field=FloatField()
                                    ),

                                    alisectionABCDE_diff=Sum("totalscore"),

                                    test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                                    qualityPercent=ExpressionWrapper(
                                        (Sum("totalscore") / (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )) * 40,
                                        output_field=FloatField()
                                    ),

                                    sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                                )
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

                        enddate = None
                        startdate = None

                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(
                            auditor_date__range=[startdate,enddate]).values("surveyor_name") \
                        .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()),

    # Define the division results with ExpressionWrapper
                                    alisectionAskipping=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionAPercent=ExpressionWrapper(
                                        (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,
                                    
                                    alisectionBskills=ExpressionWrapper(
                                        Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionBPercent=ExpressionWrapper(
                                        (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCpolite=ExpressionWrapper(
                                        Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCspeech=ExpressionWrapper(
                                        Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCprofessional=ExpressionWrapper(
                                        Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCPercent=ExpressionWrapper(
                                        (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDpolitecourteous=ExpressionWrapper(
                                        Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDrateofspeech=ExpressionWrapper(
                                        Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                        Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDPercent=ExpressionWrapper(
                                        (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alitotalABCD=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") +
                                        Sum("question_subject_knowledge") +
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills") +
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic"),
                                        output_field=FloatField()
                                    ),

                                    alisectionEvariation=Sum("variation"),
                                    alisectionEsurvey=Sum("survey"),
                                    alisectionEmovement=Sum("movement"),
                                    alisectionEtagging=Sum("tagging"),
                                    alisectionEtotal=ExpressionWrapper(
                                        Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                        output_field=FloatField()
                                    ),

                                    alisectionABCDE_diff=Sum("totalscore"),

                                    test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                                    qualityPercent=ExpressionWrapper(
                                        (Sum("totalscore") / (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )) * 40,
                                        output_field=FloatField()
                                    ),

                                    sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                                )

                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] != "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] == "" and request.GET["enddate"] == ""):

                        enddate = None
                        startdate = None


                        if("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                            
                            from datetime import timedelta

                            startdate = datetime.datetime.strptime(
                                request.GET["interview_startdate"],
                                "%Y-%m-%d"
                            )

                            enddate = datetime.datetime.strptime(
                                request.GET["interview_enddate"],
                                "%Y-%m-%d"
                            ) + timedelta(days=1)



                            project_count = QualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"]
                            ).count()


                            date_count = QualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"],
                                interview_date__range=[startdate, enddate]
                            ).count()

                            
                            print(
                                QualityReview.objects.filter(
                                    project_name__icontains=request.GET["auditor_project_name"]
                                )
                                .values("interview_date")
                                .distinct()[:20]
                            )

                            qualityRecords = QualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"]
                            ).values("surveyor_name") \
                            .annotate(
                                surveyor_count=Count('surveyor_name', output_field=FloatField()),

                                alisectionAskipping=ExpressionWrapper(
                                    Sum("question_skipping_incomplete_recordings") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionAPercent=ExpressionWrapper(
                                    (Sum("question_skipping_incomplete_recordings") /
                                    (Value(int(max_val)) * F('surveyor_count'))),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionBskills=ExpressionWrapper(
                                    Sum("question_subject_knowledge") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionBPercent=ExpressionWrapper(
                                    (Sum("question_subject_knowledge") /
                                    (Value(int(max_val)) * F('surveyor_count'))),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionCpolite=ExpressionWrapper(
                                    Sum("voice_clarity") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionCspeech=ExpressionWrapper(
                                    Sum("questioning_technique") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionCprofessional=ExpressionWrapper(
                                    Sum("convencing_skills") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionCPercent=ExpressionWrapper(
                                    (
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills")
                                    ) /
                                    (Value(int(max_val)) * F('surveyor_count') * 3),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionDpolitecourteous=ExpressionWrapper(
                                    Sum("polite_courteous") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionDrateofspeech=ExpressionWrapper(
                                    Sum("rate_of_speech") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                    Sum("professionalism_energetic_enthusiastic") /
                                    (Value(int(max_val)) * F('surveyor_count')),
                                    output_field=FloatField()
                                ) * 100,

                                alisectionDPercent=ExpressionWrapper(
                                    (
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic")
                                    ) /
                                    (Value(int(max_val)) * F('surveyor_count') * 3),
                                    output_field=FloatField()
                                ) * 100,

                                alitotalABCD=ExpressionWrapper(
                                    Sum("question_skipping_incomplete_recordings") +
                                    Sum("question_subject_knowledge") +
                                    Sum("voice_clarity") +
                                    Sum("questioning_technique") +
                                    Sum("convencing_skills") +
                                    Sum("polite_courteous") +
                                    Sum("rate_of_speech") +
                                    Sum("professionalism_energetic_enthusiastic"),
                                    output_field=FloatField()
                                ),

                                alisectionEvariation=Sum("variation"),
                                alisectionEsurvey=Sum("survey"),
                                alisectionEmovement=Sum("movement"),
                                alisectionEtagging=Sum("tagging"),

                                alisectionEtotal=ExpressionWrapper(
                                    Sum("variation") +
                                    Sum("survey") +
                                    Sum("movement") +
                                    Sum("tagging"),
                                    output_field=FloatField()
                                ),

                                alisectionABCDE_diff=Sum("totalscore"),

                                test1=ExpressionWrapper(
                                    Value(1 * int(max_val)) * F('surveyor_count'),
                                    output_field=FloatField()
                                ),

                                test2=ExpressionWrapper(
                                    Value(1 * int(max_val)) * F('surveyor_count'),
                                    output_field=FloatField()
                                ),

                                test3=ExpressionWrapper(
                                    Value(3 * int(max_val)) * F('surveyor_count'),
                                    output_field=FloatField()
                                ),

                                test4=ExpressionWrapper(
                                    Value(3 * int(max_val)) * F('surveyor_count'),
                                    output_field=FloatField()
                                ),

                                qualityPercent=ExpressionWrapper(
                                    (
                                        Sum("totalscore") /
                                        (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )
                                    ) * 40,
                                    output_field=FloatField()
                                ),

                                sectionEfakeForms=Count(
                                    Case(
                                        When(is_fake_form=True, then=1)
                                    )
                                )
                            )
                        else:


                            qualityRecords = QualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"]).values("surveyor_name") \
                                .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()),

    # Define the division results with ExpressionWrapper
                                    alisectionAskipping=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionAPercent=ExpressionWrapper(
                                        (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,
                                    
                                    alisectionBskills=ExpressionWrapper(
                                        Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionBPercent=ExpressionWrapper(
                                        (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCpolite=ExpressionWrapper(
                                        Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCspeech=ExpressionWrapper(
                                        Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCprofessional=ExpressionWrapper(
                                        Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCPercent=ExpressionWrapper(
                                        (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDpolitecourteous=ExpressionWrapper(
                                        Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDrateofspeech=ExpressionWrapper(
                                        Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                        Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDPercent=ExpressionWrapper(
                                        (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alitotalABCD=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") +
                                        Sum("question_subject_knowledge") +
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills") +
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic"),
                                        output_field=FloatField()
                                    ),

                                    alisectionEvariation=Sum("variation"),
                                    alisectionEsurvey=Sum("survey"),
                                    alisectionEmovement=Sum("movement"),
                                    alisectionEtagging=Sum("tagging"),
                                    alisectionEtotal=ExpressionWrapper(
                                        Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                        output_field=FloatField()
                                    ),

                                    alisectionABCDE_diff=Sum("totalscore"),

                                    test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                                    qualityPercent=ExpressionWrapper(
                                        (Sum("totalscore") / (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )) * 40,
                                        output_field=FloatField()
                                    ),

                                    sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                                )
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] == "" and request.GET["enddate"] == ""):    ##### when we select only auditor name

                        enddate = None
                        startdate = None

                        qualityRecords = QualityReview.objects.filter(
                            quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                            .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()),

    # Define the division results with ExpressionWrapper
                                    alisectionAskipping=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionAPercent=ExpressionWrapper(
                                        (Sum("question_skipping_incomplete_recordings") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,
                                    
                                    alisectionBskills=ExpressionWrapper(
                                        Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionBPercent=ExpressionWrapper(
                                        (Sum("question_subject_knowledge") / (Value(int(max_val)) * F('surveyor_count'))) * 100 / 100,
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCpolite=ExpressionWrapper(
                                        Sum("voice_clarity") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCspeech=ExpressionWrapper(
                                        Sum("questioning_technique") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCprofessional=ExpressionWrapper(
                                        Sum("convencing_skills") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionCPercent=ExpressionWrapper(
                                        (Sum("voice_clarity") + Sum("questioning_technique") + Sum("convencing_skills")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDpolitecourteous=ExpressionWrapper(
                                        Sum("polite_courteous") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDrateofspeech=ExpressionWrapper(
                                        Sum("rate_of_speech") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDprofessionalismenergeticenthusiastic=ExpressionWrapper(
                                        Sum("professionalism_energetic_enthusiastic") / (Value(int(max_val)) * F('surveyor_count')),
                                        output_field=FloatField()
                                    ) * 100,

                                    alisectionDPercent=ExpressionWrapper(
                                        (Sum("polite_courteous") + Sum("rate_of_speech") + Sum("professionalism_energetic_enthusiastic")) / (Value(int(max_val)) * F('surveyor_count') * 3),
                                        output_field=FloatField()
                                    ) * 100,

                                    alitotalABCD=ExpressionWrapper(
                                        Sum("question_skipping_incomplete_recordings") +
                                        Sum("question_subject_knowledge") +
                                        Sum("voice_clarity") +
                                        Sum("questioning_technique") +
                                        Sum("convencing_skills") +
                                        Sum("polite_courteous") +
                                        Sum("rate_of_speech") +
                                        Sum("professionalism_energetic_enthusiastic"),
                                        output_field=FloatField()
                                    ),

                                    alisectionEvariation=Sum("variation"),
                                    alisectionEsurvey=Sum("survey"),
                                    alisectionEmovement=Sum("movement"),
                                    alisectionEtagging=Sum("tagging"),
                                    alisectionEtotal=ExpressionWrapper(
                                        Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                                        output_field=FloatField()
                                    ),

                                    alisectionABCDE_diff=Sum("totalscore"),

                                    test1=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test2=ExpressionWrapper(Value(1 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test3=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),
                                    test4=ExpressionWrapper(Value(3 * int(max_val)) * F('surveyor_count'), output_field=FloatField()),

                                    qualityPercent=ExpressionWrapper(
                                        (Sum("totalscore") / (
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(1 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count') +
                                            Value(3 * int(max_val)) * F('surveyor_count')
                                        )) * 40,
                                        output_field=FloatField()
                                    ),

                                    sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))
                                )
                        # return self.exportData(qualityRecords)
                    if qualityRecords is None:
                        return HttpResponse(
                            "Unable to export data with the selected filters. Please select valid date filters and try again.",
                            status=400
                        )
                    return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)

                else:

           
                    qualityRecords = None
                    if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]!="default"):

                        enddate = None
                        startdate = None


                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate,enddate],project_name__icontains=request.GET["auditor_project_name"])
                    else:
                        if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]=="default"):

                            enddate = None
                            startdate = None


                            enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                            startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                            qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate, enddate])
                        else:
                            qualityRecords = QualityReview.objects.filter(project_name__icontains=request.GET["auditor_project_name"])
                    # print(qualityRecords.count(),"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<counttt")
                    return self.exportData(qualityRecords)


            elif("quality_auditor_id" in request.GET.keys()):

                try:

                    if(request.user.user_employee.designation.department.name=="Quality"):
                        if(request.GET["quality_auditor_id"] == str(request.user.user_employee.employee_id)):
                            qualityRecords = None
                            if(request.GET["auditor_date"]!=""):
                                qualityRecords = QualityReview.objects.filter(quality_auditor_id=request.GET["quality_auditor_id"],auditor_date=request.GET["auditor_date"])
                            else:
                                qualityRecords = QualityReview.objects.filter(quality_auditor_id=request.GET["quality_auditor_id"])
                            # print(qualityRecords.count())
                            return self.exportData(qualityRecords)
                        else:
                            data = {
                                'user': request.user.user_employee,
                                'first_name': request.user.first_name,
                                'last_name': request.user.last_name,
                                #'employee_pic': request.user.user_employee.get_profile_pic(),
                                'userrole': request.user.user_employee.designation.name,
                                'department': request.user.user_employee.designation.department.name,
                                'htmlfilename': 'search_quality_v2.html',
                                'maindata': [],
                                'notification': None,
                                "quality_auditor_id": request.user.user_employee.employee_id,
                                "auditor_position": request.user.user_employee.designation.department.name,
                                "active_projects_list": active_projects_list,
                                "auditor_list": auditor_list,
                                "msg": "",
                                "auditor_count_form": auditor_count,
                                "quality_project_wise_records":quality_project_wise_records,
                                "data":data1,
                                #"dict_of_surveyors":dict_of_surveyors,
                                "submitted_uids_status":uid_submitted
                            }
                            return render(request, "index.html", data)
                    else:
                        # print("qualityyyy")
                        qualityRecords = QualityReview.objects.filter(
                            quality_auditor_id=request.GET["quality_auditor_id"])
                        return self.exportData(qualityRecords)
                except Exception as exception:
                    # print("exceptionnn:::",exception)
                    data = {
                        'user': request.user.user_employee,
                        'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                        #'employee_pic': request.user.user_employee.get_profile_pic(),
                        'userrole': request.user.user_employee.designation.name,
                        'department': request.user.user_employee.designation.department.name,
                        'htmlfilename': 'search_quality_v2.html',
                        'maindata': [],
                        'notification': None,
                        "quality_auditor_id": request.user.user_employee.employee_id,
                        "auditor_position": request.user.user_employee.designation.department.name,
                        "active_projects_list": active_projects_list,
                        "auditor_list": auditor_list,
                        "msg": "",
                        "auditor_count_form": auditor_count,
                        "quality_project_wise_records":quality_project_wise_records,
                        "data":data1,
                        #"dict_of_surveyors":dict_of_surveyors,
                        "submitted_uids_status":uid_submitted
                    }
                    return render(request, "index.html", data)

        elif("hourly_report" in request.GET.keys()):
            hourly_auditor_name = request.GET.get("hourly_auditor_name", "default")
            selected_date = request.GET.get("Pickdate", "").strip()

            if hourly_auditor_name == "default" or selected_date == "":
                return HttpResponse(
                    "Please select Auditor Name and Date before generating hourly report.",
                    status=400
                )

            params = hourly_auditor_name.split("$-$")[-1]
            return self.hourlyReports(params, selected_date)

        else:
            data = {
                'user': request.user.user_employee,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                #'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'search_quality_v2.html',
                'maindata': [],
                'notification': None,
                "quality_auditor_id": request.user.user_employee.employee_id,
                "auditor_position": request.user.user_employee.designation.department.name,
                "active_projects_list": active_projects_list,
                "auditor_list": auditor_list,
                "msg": "",
                "auditor_count_form": auditor_count,
                "quality_project_wise_records":quality_project_wise_records,
                "sectionAIssueList":sectionAIssueList,
                "sectionBIssueList":sectionBIssueList,
                "sectionCIssueList":sectionCIssueList,
                "sectionDIssueList":sectionDIssueList,
                    "sectionEIssueList":sectionEIssueList,
                    "uids":data1,
                    #"dict_of_surveyors":dict_of_surveyors,
                    "submitted_uids_status":uid_submitted

            }
            return render(request, "index.html", data)


    def post(self,request):
        from django.db.models import Count  # type: ignore
        if request.POST.get('submit') == "Search" and 'uid' in request.POST:
            data1 = []
            surveyResponse = SurveyResponse.objects.filter(uid=request.POST["uid"])
            # print(surveyResponse.count(),"<<<counttt")


            ####### code for highlighting submitted uids ##########

            submitted_uids_list = QualityReview.objects.filter(uid=request.POST["uid"])


            submitted_uids_list = [i.uid for i in submitted_uids_list]
            uid_submitted = False
            if submitted_uids_list:
                uid_submitted = True
            ####### code for highlighting submitted uids ##########


            # print("subbbbb",[i.uid for i in submitted_uids_list])
            active_projects_list = QualityReview.objects.values("project_name").distinct()

            active_projects_list = QualityReview.objects.values("project_name").distinct()
            auditor_list = QualityReview.objects.values("quality_auditor","quality_auditor_id").distinct()
            sectionAIssueList = IssueList.objects.filter(section="section_A").values("issue_id","issues","related_question")
            sectionBIssueList = IssueList.objects.filter(section="section_B").values("issue_id", "issues","related_question")
            sectionCIssueList = IssueList.objects.filter(section="section_C").values("issue_id", "issues","related_question")
            sectionDIssueList = IssueList.objects.filter(section="section_D").values("issue_id", "issues","related_question")
            sectionEIssueList = IssueList.objects.filter(section="section_E").values("issue_id", "issues","related_question")
            # print(auditor_list,"<<<<<<<<<<<<<<<<,quality_auditor")

            data = {}
      
            today_min = django_timezone.make_aware(
                datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            )
            today_max = django_timezone.make_aware(
                datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            )
   
            ###################################################
            quality_project_wise_records = None
            auditor_count = 0
            if (request.user.user_employee.designation.department.name == "Quality" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance", "Manager"]) or \
                (request.user.user_employee.designation.department.name == "DRC" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance"]) or \
                (request.user.user_employee.designation.department.name == "Product" and request.user.user_employee.designation.name == "Manager"):
                quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max)).values("quality_auditor").annotate(Count('project_name'))
                auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max)).count()
                
            else:
                quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                        quality_auditor_id=request.user.user_employee.employee_id).values("project_name").annotate(Count('project_name'))
                auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                                                            quality_auditor_id=request.user.user_employee.employee_id).count()

            if(surveyResponse.count()>0):
                params = json.loads(surveyResponse[0].params)

                remarks = json.loads(surveyResponse[0].remarks)
                surveyor_id, surveyor_name = parse_surveyor_field(params.get("surveyor", ""))
                tl_name=params["tldetails"]

                currentdatetime=datetime.datetime.now().strftime('%Y-%m-%d')
                

                data={
                    'user': request.user.user_employee,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    # #'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    "uid":request.POST["uid"],
                    "project_id":surveyResponse[0].project.id,
                    "project_name": surveyResponse[0].project.name,
                    "surveyor_name":surveyor_name,
                    "surveyor_id":surveyor_id,
                    "tl_name":tl_name,
                    "params":params,
                    "remarks":remarks,
                    "verification_status":surveyResponse[0].verification_status.name,
                    "audit_date":str(currentdatetime),
                    "interview_duration":params["timedifference"],
                    "interview_date":params["date"],
                    "quality_auditor_name":request.user.first_name +" "+ request.user.last_name,
                    "status":True,
                    'htmlfilename': 'search_quality_v2.html',
                    'maindata': [],
                    'notification': None,
                    "quality_auditor_id":request.user.user_employee.employee_id,
                    "auditor_position":request.user.user_employee.designation.department.name,
                    "active_projects_list":active_projects_list,
                    "auditor_list":auditor_list,
                    "msg": "",
                    "auditor_count_form":auditor_count,
                    "quality_project_wise_records":quality_project_wise_records,
                "sectionAIssueList":sectionAIssueList,
                "sectionBIssueList":sectionBIssueList,
                "sectionCIssueList":sectionCIssueList,
                "sectionDIssueList":sectionDIssueList,
                    "sectionEIssueList":sectionEIssueList,
                    "uids":data1,
                    #"dict_of_surveyors":dict_of_surveyors,
                    "submitted_uids_status":uid_submitted
                }
                # return render(request,"search_quality.html",data)
                return render(request, "index.html", data)
            else:
                data = {
                    'user': request.user.user_employee,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    #'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    'htmlfilename': 'search_quality_v2.html',
                    'maindata': [],
                    'notification': None,
                    "quality_auditor_id": request.user.user_employee.employee_id,
                    "auditor_position": request.user.user_employee.designation.department.name,
                    "active_projects_list": active_projects_list,
                    "auditor_list": auditor_list,
                    "msg": "",
                    "auditor_count_form": auditor_count,
                    "quality_project_wise_records":quality_project_wise_records,
                "sectionAIssueList":sectionAIssueList,
                "sectionBIssueList":sectionBIssueList,
                "sectionCIssueList":sectionCIssueList,
                "sectionDIssueList":sectionDIssueList,
                    "sectionEIssueList":sectionEIssueList,
                    "uids":data1,
                    #"dict_of_surveyors":dict_of_surveyors,
                    "submitted_uids_status":uid_submitted
                }
                return render(request, "index.html", data)

        else:
            from django.db.models import FloatField, F, Sum, Count, ExpressionWrapper, Value, Case, When,Q #type: ignore



            data1 = []

 
            
            if request.user.username == '112891':

                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                    
                for i in resulted:
                    data1.append(i.uid)
            
            if request.user.username == '112418':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                for i in resulted:
                    data1.append(i.uid)
            
            if request.user.username == '113124':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '110649':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids,verification_date__gte = datetime_today).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids,verification_date__gte = datetime_today).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '109691':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 5)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '111293':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 6)
                for i in resulted:
                    data1.append(i.uid)
            
            if request.user.username == '107501':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 7)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '112418':

                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 8)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '108504':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey =9)
                for i in resulted:
                    data1.append(i.uid)
            
            if request.user.username == '110880':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 10)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '104481':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 11)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '111264':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 12)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '111265':
                Project_ids = Assignment.objects.filter(employee__employee_id = request.user.username).values_list('project',flat= True)     ##cchangeeess

                # print("-------",SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))  ##### chandggeeess

                resulted =SurveyResponse.objects.filter(project__in = Project_ids).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 13)
                for i in resulted:
                    data1.append(i.uid)
            
            
            if request.user.username == '112779':
                resulted =SurveyResponse.objects.filter(allocated_survey = 14).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                list_of_uid = list()

                for value in resulted:
                    d = json.loads(value.params)

                    list_of_uid.append(d)
 

                dict_of_surveyors = defaultdict(list)


                for i in list_of_uid:
                
                    surveyor = i["surveyor"]
                    id1 = i["id1"]
                    # surveyor_d = i["surveyor"] + "1"
                    dates = i["date"]
                    dict_of_surveyors[surveyor].append(id1)
                    dict_of_surveyors[surveyor].append(parser.parse(dates).date())


                dict_of_surveyors2 = dict(dict_of_surveyors)

                dict_of_surveyors = []
                grouped_data = []
                for name, values in dict_of_surveyors2.items():
                    groups = []
                    for i in range(0, len(values), 2):
                        uid = values[i]
                        date = values[i + 1]
                       
                        groups.append({'uid': uid, 'date': date})
                    dict_of_surveyors.append({'name': name, 'groups': groups})
                        

                for i in resulted:
                    data1.append(i.uid)
                    # print(len(data1))
            
            if request.user.username == '109034':
                resulted =SurveyResponse.objects.filter(allocated_survey = 15).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 15)
                for i in resulted:
                    data1.append(i.uid)
            
            if request.user.username == '102405':
                resulted =SurveyResponse.objects.filter(Q(allocated_survey = 16) | Q(allocated_survey = 15) | Q(allocated_survey = 14)).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True).all())
                # resulted = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))&SurveyResponse.objects.filter(allocated_survey = 16)


                list_of_uid = list()

                for value in resulted:
                    d = json.loads(value.params)

                    list_of_uid.append(d)

                dict_of_surveyors = defaultdict(list)


                for i in list_of_uid:
                    surveyor = i["surveyor"]
                    id1 = i["id1"]
                    dict_of_surveyors[surveyor].append(id1)


                dict_of_surveyors = dict(dict_of_surveyors)

                for i in resulted:
                    data1.append(i.uid)
            


            


            msg = ""

            if ("mis_match_uid" in request.POST.keys()):
                if (QualityReviewMismatch.objects.filter(uid=int(request.POST["mis_match_uid"])).count() == 0):
                    QualityReviewMismatch.objects.create(
                        uid=int(request.POST["mis_match_uid"]),
                        project_name=request.POST["mis_project_name"],
                        surveyor_name=request.POST["mis_surveyor_id"]+"-"+request.POST["mis_surveyor_name"],
                        fr_name=request.POST["mis_tl_name"],
                        interview_date=request.POST["mis_interview_date"],
                        # interview_date=datetime.datetime.strptime(str(request.POST["mis_interview_date"]), '"%Y-%m-%d"').strftime("%Y-%m-%d"),
                        interview_duration=request.POST["mis_interview_duration"],
                        quality_auditor=request.user.first_name + " " + request.user.last_name,
                        auditor_date=request.POST["mis_audit_date"],
                        review=request.POST["mis_match_reason_review"]
                    )
                    msg = "Submitted"
                else:
                    msg = "Duplicated Entry Please verify"

            else:

                # print(request.POST.keys())

                data = {}
                msg=""



                # Section A
                # A = request.POST["section_A_question_skipping_"]
                # B = request.POST["section_A_incomplete_recording_"]
                # C = request.POST["section_A_voice_quality_"]
                # knowledge = request.POST["section_A_question_knowledge_"]
                A = request.POST["section_A_question_skipping_"]




                # Section B
                D = request.POST["section_B_question_subject_knowledge_"]
                # E = request.POST["section_B_prompt_answers_"]
                # F = request.POST["section_B_convincing_skills_"]

                # Section C
                G = request.POST["section_C_voice_clarity_"]
                H = request.POST["section_C_question_techniques_"]
                I = request.POST["section_C_convincing_skills_"]


                # Section D
                J = request.POST["section_D_variation_"]
                K = request.POST["section_D_force_survey_"]
                L = request.POST["section_D_moment_during_interview_"]
                M = request.POST["section_D_geo_tagging_"]
                N = request.POST["section_D_fake_form_"]

                O = request.POST["section_D_polite_courteous_"]
                P = request.POST["section_D_rate_of_speech_"]
                Q = request.POST["section_D_professionalism_"]

                def _normalize_score(value):
                    value = "" if value is None else str(value).strip()
                    return "0" if value == "" else value

                def _to_float(value):
                    value = "" if value is None else str(value).strip()
                    if value == "":
                        return 0.0
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        return 0.0

                # Persist skipped/empty scores as 0 instead of blank strings.
                A = _normalize_score(A)
                D = _normalize_score(D)
                G = _normalize_score(G)
                H = _normalize_score(H)
                I = _normalize_score(I)
                J = _normalize_score(J)
                K = _normalize_score(K)
                L = _normalize_score(L)
                M = _normalize_score(M)
                N = _normalize_score(N)
                O = _normalize_score(O)
                P = _normalize_score(P)
                Q = _normalize_score(Q)


                isFake = False
                if(_to_float(N) < 0):
                    A = 0
                    # B = 0
                    # C = 0
                    D = 0
                    # E = 0
                    # F = 0
                    G = 0
                    H = 0
                    I = 0
                    #J = 0
                    #K = 0
                    #L = 0
                    #M = 0
                    #N = 0
                    O = 0
                    P = 0
                    Q = 0

                    # knowledge = 0
                    isFake = True





                # score_A_B_C =  int(A) + int(B) +  int(C) + int(knowledge) + int(D) + int(E) + int(F) + int(G) + int(H) + int(I) 
                # score_D = int(J) + int(K) + int(L) + int(M) + int(N)

                score_A_B_C = _to_float(A) + _to_float(D) + _to_float(G) + _to_float(H) + _to_float(I)
            score_D=0
            if (isFake==True):
                score_D=0
                total_score=0
            else:
                score_D = _to_float(J) + _to_float(K) + _to_float(L) + _to_float(M) + _to_float(N) + _to_float(O) + _to_float(P) + _to_float(Q)

                total_score = ((score_A_B_C + score_D)/40)*100




            if(QualityReview.objects.filter(uid=int(request.POST["uid_id"])).count()==0):
                    QualityReview.objects.create(
                        uid=int(request.POST["uid_id"]),
                        project_name=request.POST["project_name"],
                        surveyor_name=request.POST["surveyor_id"]+"-"+request.POST["surveyor_name"],
                        fr_name=request.POST["fr_name"],

                        interview_date = request.POST["interview_date"],
                        # interview_date=datetime.datetime(request.POST["interview_date"][:10]).strftime("%Y-%m-%d"),
                        interview_duration=request.POST["interview_duration"],
                        quality_auditor=request.user.first_name +" "+ request.user.last_name,
                        auditor_date=request.POST["auditing_date"],

                        skipping="",
                        knowledge="",
                        recordings="",
                        voice="",
                        remarksSection_A="",

                        skills="",
                        answer="",
                        convince="",
                        remarksSection_B="",


                        polite="",
                        speech="",
                        professional="",
                        remarksSection_C="",


                        variation= J,
                        survey=K,
                        movement=L,
                        tagging=M,
                        fake=N,
                        remarksSection_D=request.POST["section_D_remarks_"],

                        totalscore=total_score,
                        # created_at=datetime.datetime.now(),
                        quality_auditor_id = request.user.user_employee.employee_id,
                        is_fake_form = isFake,
                        version="June2020-Dec2020",


                    #     New Format
                        question_skipping_incomplete_recordings=A,
                        remarksSection_A_skipping_incomplete_recordings_1=request.POST["section_A_remarks_1_"],
                        remarksSection_A_skipping_incomplete_recordings_2=request.POST["section_A_remarks_2_"],
                        question_subject_knowledge=D,
                        remarksSection_B_question_subject_knowledge_1=request.POST["section_B_remarks_1_"],
                        remarksSection_B_question_subject_knowledge_2=request.POST["section_B_remarks_2_"],
                        voice_clarity=G,
                        remarksSection_C_voice_clarity_1=request.POST["section_C_remarks_1_"],
                        remarksSection_C_voice_clarity_2=request.POST["section_C_remarks_2_"],
                        questioning_technique=H,
                        remarksSection_C_questioning_technique_1=request.POST["section_C_remarks_questioning_technique_1_"],
                        remarksSection_C_questioning_technique_2=request.POST["section_C_remarks_questioning_technique_2_"],
                        convencing_skills=I,
                        remarksSection_C_convencing_skills_1=request.POST["section_C_remarks_convicing_skills_1_"],
                        remarksSection_C_convencing_skills_2=request.POST["section_C_remarks_convicing_skills_2_"],
                        polite_courteous=O,
                        remarksSection_D_polite_courteous_1=request.POST["section_D_remarks_polite_courages_1_"],
                        remarksSection_D_polite_courteous_2=request.POST["section_D_remarks_polite_courages_2_"],
                        rate_of_speech=P,
                        remarksSection_D_rate_of_speech_1=request.POST["section_D_remarks_rate_of_speech_1_"],
                        remarksSection_D_rate_of_speech_2=request.POST["section_D_remarks_rate_of_speech_2_"],
                        professionalism_energetic_enthusiastic=Q,
                        remarksSection_D_professionalism_energetic_enthusiastic_1=request.POST["section_D_remarks_pro_energy_1_"],
                        remarksSection_D_professionalism_energetic_enthusiastic_2=request.POST["section_D_remarks_pro_energy_2_"],
                        remarksSection_E_variation_1 = request.POST["section_E_question_variation_remarks_1_"],
                        remarksSection_E_force_survey_1 = request.POST["section_E_question_force_survey_remarks_1_"],

                        # Issue Reason
                        question_skipping_incomplete_recordings_reason = IssueList.objects.get(issue_id=request.POST["section_A_question_skipping_issue"]),
                        question_subject_knowledge_reason = IssueList.objects.get(issue_id=request.POST["section_B_question_questionnaire_subject_issue"]),
                        voice_clarity_reason= IssueList.objects.get(issue_id=request.POST["section_C_question_voice_clarity_issue"]),
                        questioning_technique_reason =IssueList.objects.get(issue_id=request.POST["section_C_question_questioning_technique_issue"]),
                        convencing_skills_reason=IssueList.objects.get(issue_id=request.POST["section_C_question_convincing_skills_issue"]),
                        polite_courteous_reason=IssueList.objects.get(issue_id=request.POST["section_D_question_polite_courteous_issue"]),
                        rate_of_speech_reason=IssueList.objects.get(issue_id=request.POST["section_D_question_rate_speech_issue"]),
                        professionalism_energetic_enthusiastic_reason = IssueList.objects.get(issue_id=request.POST["section_D_question_professional_issue"]),
                        variation_reason = IssueList.objects.get(issue_id=request.POST["section_E_question_variation_issue"]),
                        force_survey_reason = IssueList.objects.get(issue_id=request.POST["section_E_question_force_survey_issue"])
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,
                        # remarksSection_D_rate_of_speech_1=A,





                    )
                    msg = "Submitted"
            else:
                    # print("duplicate entryyy")
                    msg = "Duplicated Entry Please verify"

            active_projects_list = QualityReview.objects.values("project_name").distinct()
            auditor_list = QualityReview.objects.values("quality_auditor","quality_auditor_id").distinct()
            today_min = django_timezone.make_aware(
                datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            )
            today_max = django_timezone.make_aware(
                datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            )

            if (request.user.user_employee.designation.department.name == "Quality" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance", "Manager"]) or \
                (request.user.user_employee.designation.department.name == "DRC" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance"]) or \
                (request.user.user_employee.designation.department.name == "Product" and request.user.user_employee.designation.name == "Manager"):
                quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max)).values("quality_auditor").annotate(Count('project_name'))
                auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max)).count()
            else:
                quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                        quality_auditor_id=request.user.user_employee.employee_id).values("project_name").annotate(Count('project_name'))
                auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                                                            quality_auditor_id=request.user.user_employee.employee_id).count()
            active_projects_list = QualityReview.objects.values("project_name").distinct()
            auditor_list = QualityReview.objects.values("quality_auditor", "quality_auditor_id").distinct()
            sectionAIssueList = IssueList.objects.filter(section="section_A").values("issue_id", "issues","related_question")
            sectionBIssueList = IssueList.objects.filter(section="section_B").values("issue_id", "issues","related_question")
            sectionCIssueList = IssueList.objects.filter(section="section_C").values("issue_id", "issues","related_question")
            sectionDIssueList = IssueList.objects.filter(section="section_D").values("issue_id", "issues","related_question")
            sectionEIssueList = IssueList.objects.filter(section="section_E").values("issue_id", "issues","related_question")


            submitted_uids_list = QualityReview.objects.filter(uid=request.POST["uid_id"])

            # print("ddddd",submitted_uids_list)
            uid_submitted = False
            if submitted_uids_list == []:
                uid_submitted = True
                

            data = {
                'user': request.user.user_employee,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                #'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'search_quality_v2.html',
                'maindata': [],
                'notification': None,
                "quality_auditor_id": request.user.user_employee.employee_id,
                "auditor_position": request.user.user_employee.designation.department.name,
                "active_projects_list": active_projects_list,
                "auditor_list": auditor_list,
                "msg": msg,
                "auditor_count_form":auditor_count,
                "quality_project_wise_records":quality_project_wise_records,
                "sectionAIssueList": sectionAIssueList,
                "sectionBIssueList": sectionBIssueList,
                "sectionCIssueList": sectionCIssueList,
                "sectionDIssueList": sectionDIssueList,
                "sectionEIssueList": sectionEIssueList,
                "uids":data1,
                #"dict_of_surveyors":dict_of_surveyors,
                # "submitted_uids_status":uid_submitted
            }
            return render(request, "index.html", data)






    def hourlyReports(self,params,selected_date):
            present_date = datetime.datetime.now()
            hourly_based_data_arr = []
            dd = present_date.replace(hour=23,minute=00)

            # print(dd,"========",present_date,"====>>",type(str(selected_date)),"===",str(selected_date))
            new_date = datetime.datetime.strptime(str(selected_date),"%Y-%m-%d")
            new_new_date=new_date.replace(hour=23,minute=59,second=59)
            # print(new_date,"<<<<new",new_new_date)

            # auditor_json = [{
            #   "id":12345,
            #     "obj":[]
            # }]
            auditor_arr = [{
                "id": 12345,
                "obj": []
            }]

            for x in range(0, 24):
                hourlyJson = {}
                result_date = new_new_date - datetime.timedelta(hours=1)
                # print(new_new_date,"-",datetime.timedelta(hours=1),"=",result_date)

                hourlyJson["starting_hour"] = result_date
                hourlyJson["ending_hour"] = new_new_date



                # print(selected_date,"=======")

                hourlyBasedData = None
                if(params=="default"):
                    # print("default called")
                    # print(result_date, "*******", new_new_date)
                    hourlyBasedData = QualityReview.objects.filter(created_at__range=(result_date, new_new_date),auditor_date=selected_date)


                else:
                    # print("not default called")
                    # print(result_date, "*******" ,new_new_date)
                    hourlyBasedData = QualityReview.objects.filter(created_at__range=(result_date, new_new_date),auditor_date=selected_date, quality_auditor_id=params)



                # print(hourlyBasedData,"<<<<<<<<hourlybaseddata")

                auditor_arr = self.getFilter_hourData(hourlyBasedData,auditor_arr,result_date,new_new_date)

                # print(hourlyBasedData,"<<<<<hourlyBasedData")
                hourly_uids = []
                hourly_auditor_ids = []

                if (hourlyBasedData.count() > 0):
                    for hour_data in hourlyBasedData:

                        hourly_uids.append(hour_data.uid)
                        hourly_auditor_ids.append(hour_data.quality_auditor_id)

                    hourlyJson["hourly_uids"] = hourly_uids
                    hourlyJson["hourly_auditor_ids"] = hourly_auditor_ids

                else:
                    # print("elseeeee")
                    hourlyJson["hourly_uids"] = []
                    hourlyJson["hourly_auditor_ids"] = []
                hourly_based_data_arr.append(hourlyJson)
                # present_date = result_date
                new_new_date = result_date

            return self.exportHourlyBased(hourly_based_data_arr,auditor_arr,selected_date)






    def getFilter_hourData(self,hourlyBasedData,auditor_arr,starting_hour,ending_hour):
            # print(auditor_arr,"<<<<",hourlyBasedData)

            # auditor_arr = [{
            #     "id": 12345,
            #     "obj": []
            # }]
            for hourData in hourlyBasedData:
                if (len(auditor_arr)!=0):
                    found = False
                    for auditor_arrData in auditor_arr:

                        if(hourData.quality_auditor_id==auditor_arrData["id"]):
                            auditor_arrData["obj"].append(hourData)
                            auditor_arrData["uids"].append(hourData.uid)
                            found= True
                    if(found == False):
                        auditor_arr.append({
                            "id": hourData.quality_auditor_id,
                            "obj": [hourData],
                            "name":hourData.quality_auditor,
                            "uids":[hourData.uid],

                        })

                else:
                    auditor_arr.append({
                        "id":hourData.quality_auditor_id,
                        "obj":[hourData],
                        "name": hourData.quality_auditor,
                        "uids":[hourData.uid]
                    })

                # print(hourData,">>>>>>>>>>>>>>>",auditor_arrData)
            return auditor_arr




    def exportData(self,data):
            output = io.BytesIO()  # Use BytesIO for binary data, which is required for xlsxwriter
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('output')
            row = 0
            col = 0
            
            worksheet.write(0,1,"ID".title())
            worksheet.write(0, 2, "UID".title())
            worksheet.write(0, 3, "Project_Name".title())
            worksheet.write(0,4,"Surveyor_Name".title())
            worksheet.write(0, 5, "FR_Name".title())
            worksheet.write(0, 6, "Interview_Date".title())
            worksheet.write(0, 7, "Interview_Duration".title())
            worksheet.write(0, 8, "quality_auditor".title())
            worksheet.write(0, 9, "auditor_date".title())


            worksheet.write(0, 10, "Question Skipping/ Incomplete Recording".title())
            # worksheet.write(0, 11, "knowledge".title())
            # worksheet.write(0, 12, "recordings".title())
            # worksheet.write(0, 13, "voice".title())
            worksheet.write(0, 11, "remarks_Question Skipping/ Incomplete Recording_reason".title())
            worksheet.write(0, 12, "remarks_A_1".title())
            worksheet.write(0, 13, "remarks_A_2".title())

            worksheet.write(0, 14, "Questionnaire / Subject Knowledge".title())
            # worksheet.write(0, 16, "answer".title())
            # worksheet.write(0, 17, "convince".title())
            worksheet.write(0, 15, "remarks_Questionnaire / Subject Knowledge_reason".title())
            worksheet.write(0, 16, "remarks_B_1".title())
            worksheet.write(0, 17, "remarks_B_2".title())

            worksheet.write(0, 18, "Voice Clarity".title())
            worksheet.write(0, 19, "Voice Clarity_reason".title())
            worksheet.write(0, 20, "remarks_C_voice_clarity_1".title())
            worksheet.write(0, 21, "remarks_C_voice_clarity_2".title())
            worksheet.write(0, 22, "Questioning Technique".title())
            worksheet.write(0, 23, "Questioning Technique_reason".title())
            worksheet.write(0, 24, "remarks_C_question_technique_1".title())
            worksheet.write(0, 25, "remarks_C_question_technique_2".title())
            worksheet.write(0, 26, "Convincing skills".title())
            worksheet.write(0, 27, "Convincing skills_reason".title())
            worksheet.write(0, 28, "remarks_C_convencing_skills_1".title())
            worksheet.write(0, 29, "remarks_C_convencing_skills_2".title())

            worksheet.write(0, 30, "Being Polite & courteous".title())
            worksheet.write(0, 31, "Being Polite & courteous_reason".title())
            worksheet.write(0, 32, "remarksSection_D_polite_courteous_1".title())
            worksheet.write(0, 33, "remarksSection_D_polite_courteous_2".title())
            worksheet.write(0, 34, "Rate of Speech".title())
            worksheet.write(0, 35, "Rate of Speech_reason".title())
            worksheet.write(0, 36, "remarksSection_D_rate_of_speech_1".title())
            worksheet.write(0, 37, "remarksSection_D_rate_of_speech_2".title())
            worksheet.write(0, 38, "Professionalism/ Energetic/Enthusiastic".title())
            worksheet.write(0, 39, "Professionalism/ Energetic/Enthusiastic_reason".title())
            worksheet.write(0, 40, "remarksSection_D_professionalism_energetic_enthusiastic_1".title())
            worksheet.write(0, 41, "remarksSection_D_professionalism_energetic_enthusiastic_2".title())

            worksheet.write(0, 42, "variation".title())
            worksheet.write(0, 43, "variation_reason".title())
            worksheet.write(0, 44, "remarksSectionE_variation_1".title())
            worksheet.write(0, 45, "survey".title())
            worksheet.write(0, 46, "survey_reason".title())
            worksheet.write(0, 47, "remarksSectionE_force_survey_1".title())
            worksheet.write(0, 48, "movement".title())
            worksheet.write(0, 49, "tagging".title())
            worksheet.write(0, 50, "fake".title())
            worksheet.write(0, 51, "remarks_D".title())

            worksheet.write(0, 52, "total_score".title())
            worksheet.write(0, 53, "created_date".title())
            worksheet.write(0, 54, "auditor_id".title())

            row = row + 1
            col = 0
            for data in data:
                # print(data.id,"<<<<< ")
                worksheet.write(row, 1, str(data.id))
                worksheet.write(row, 2, str(data.uid))
                worksheet.write(row, 3, str(data.project_name))
                raw_surveyor = str(data.surveyor_name or "").strip()
                s_id, s_name = parse_surveyor_field(raw_surveyor)
                
                # Standardize format to: 116415 - (Ganesh Samarit)
                if s_id and s_name:
                    formatted_surveyor = f"{s_id} - {s_name}"
                else:
                    formatted_surveyor = raw_surveyor

                worksheet.write(row, 4, formatted_surveyor)
                
                worksheet.write(row, 5, str(data.fr_name))
                try:
                    interview_date = datetime.datetime.strptime(
                        str(data.interview_date),
                        "%d-%b-%Y"
                    ).strftime("%d-%m-%Y")
                except:
                    interview_date = str(data.interview_date)

                worksheet.write(row, 6, interview_date)
                worksheet.write(row, 7, str(data.interview_duration))
                worksheet.write(row, 8, str(data.quality_auditor))
                
                auditor_date = ""

                if data.auditor_date:
                    try:
                        auditor_date = datetime.datetime.strptime(
                            str(data.auditor_date),
                            "%Y-%m-%d"
                        ).strftime("%d-%m-%Y")
                    except:
                        auditor_date = str(data.auditor_date)

                worksheet.write(row, 9, auditor_date)
                worksheet.write(row, 10, round(float(str(data.question_skipping_incomplete_recordings)),2))
                # worksheet.write(row, 11, int(round(float(str(data.knowledge)))))
                # worksheet.write(row, 12, int(round(float(str(data.recordings)))))
                # worksheet.write(row, 13, int(round(float(str(data.voice)))))
                worksheet.write(row, 11, str(data.question_skipping_incomplete_recordings_reason.related_question))
                worksheet.write(row, 12, str(data.remarksSection_A_skipping_incomplete_recordings_1))
                worksheet.write(row, 13, str(data.remarksSection_A_skipping_incomplete_recordings_2))

                worksheet.write(row, 14, round(float(str(data.question_subject_knowledge)),2))
                # worksheet.write(row, 16, int(round(float(str(data.answer)))))
                # worksheet.write(row, 17, int(round(float(str(data.convince)))))
                worksheet.write(row, 15,str(data.question_subject_knowledge_reason.related_question))
                worksheet.write(row, 16, str(data.remarksSection_B_question_subject_knowledge_1))
                worksheet.write(row, 17, str(data.remarksSection_B_question_subject_knowledge_2))

                worksheet.write(row, 18, round(float(str(data.voice_clarity)),2))
                worksheet.write(row, 19, str(data.voice_clarity_reason.related_question))
                worksheet.write(row, 20, str(data.remarksSection_C_voice_clarity_1))
                worksheet.write(row, 21, str(data.remarksSection_C_voice_clarity_2))
                worksheet.write(row, 22, round(float(str(data.questioning_technique)),2))
                worksheet.write(row, 23, str(data.questioning_technique_reason.related_question))
                worksheet.write(row, 24, str(data.remarksSection_C_questioning_technique_1))
                worksheet.write(row, 25, str(data.remarksSection_C_questioning_technique_2))
                worksheet.write(row, 26, round(float(str(data.convencing_skills)),2))
                worksheet.write(row, 27, str(data.convencing_skills_reason.related_question))
                worksheet.write(row, 28, str(data.remarksSection_C_convencing_skills_1))
                worksheet.write(row, 29, str(data.remarksSection_C_convencing_skills_2))

                worksheet.write(row, 30, round(float(str(data.polite_courteous)),2))
                worksheet.write(row, 31, str(data.polite_courteous_reason.related_question))
                worksheet.write(row, 32, str(data.remarksSection_D_polite_courteous_1))
                worksheet.write(row, 33, str(data.remarksSection_D_polite_courteous_2))
                worksheet.write(row, 34, round(float(str(data.rate_of_speech)),2))
                worksheet.write(row, 35, str(data.rate_of_speech_reason.related_question))
                worksheet.write(row, 36, str(data.remarksSection_D_rate_of_speech_1))
                worksheet.write(row, 37, str(data.remarksSection_D_rate_of_speech_2))
                worksheet.write(row, 38, round(float(str(data.professionalism_energetic_enthusiastic)),2))
                worksheet.write(row, 39, str(data.professionalism_energetic_enthusiastic_reason.related_question))
                worksheet.write(row, 40, str(data.remarksSection_D_professionalism_energetic_enthusiastic_1))
                worksheet.write(row, 41, str(data.remarksSection_D_professionalism_energetic_enthusiastic_2))



                worksheet.write(row, 42, round(float(str(data.variation)),2))
                worksheet.write(row, 43, (str(data.variation_reason.related_question)))
                worksheet.write(row, 44, str(data.remarksSection_E_variation_1))
                worksheet.write(row, 45, round(float(str(data.survey)),2))
                worksheet.write(row, 46, (str(data.force_survey_reason.related_question)))
                worksheet.write(row, 47, str(data.remarksSection_E_force_survey_1))
                worksheet.write(row, 48, round(float(str(data.movement)),2))
                worksheet.write(row, 49, round(float(str(data.tagging)),2))
                worksheet.write(row, 50, round(float(str(data.fake)),2))
                worksheet.write(row, 51, str(data.remarksSection_D))


                worksheet.write(row, 52, int(round(float(str(data.totalscore)))))
                created_date = ""

                if data.created_at:
                    created_date = data.created_at.strftime("%d-%m-%Y")

                worksheet.write(row, 53, created_date)
                worksheet.write(row, 54, str(data.quality_auditor_id))

                row = row + 1


            workbook.close()
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={datetime.date.today()}.xlsx'
            import gc
            gc.collect()

            return response






    def exportData_auditor(self,data,type,request):
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('output')
            # print(type,"<<<<,type")
            if(type=="fetch"):
                row = 0
                col = 0
                worksheet.write(0, 1, "surveyor_name")
                worksheet.write(0, 2, "Question Skipping/ Incomplete Recording")
                # worksheet.write(0, 3, "Thorough Knowledge of Questionnaire")
                # worksheet.write(0, 4, "No Incomplete Recordings")
                # worksheet.write(0, 5, "Respondent voice can be heard clearly/Background noises")
                worksheet.write(0, 3, "Section - A Subject Knowledge (Questionnaire) & Tab Knowledge/Handling Skills")

                worksheet.write(0, 4, "Questionnaire / Subject Knowledge ")
                # worksheet.write(0, 8, "Prompting Answer/ Options")
                # worksheet.write(0, 9, "Good Convincing Skills")
                worksheet.write(0, 5, "Section - B Survey Handling Skills")

                worksheet.write(0, 6, "Voice Clarity")
                worksheet.write(0, 7, "Questioning Skills")
                worksheet.write(0, 8, "Convincing skills")
                worksheet.write(0, 9, "Section - C Survey Handling Skills")

                worksheet.write(0, 10, "Being Polite & courteous")
                worksheet.write(0, 11, "Rate of Speech")
                worksheet.write(0, 12, "Professionalism/ Energetic/Enthusiastic")
                worksheet.write(0, 13, "Section - D Soft Skills")

                worksheet.write(0, 14, "Variation")
                worksheet.write(0, 15, "Force Survey/False Promises/False Information")
                worksheet.write(0, 16, "Movement During Interview")
                worksheet.write(0, 17, "Geo Tagging")
                worksheet.write(0, 18, "Fake Forms Count")
                worksheet.write(0, 19, "Section - E Fatal Errors")

                worksheet.write(0, 20, "total_forms_verified")

                worksheet.write(0, 21, "quality_score % ")
                worksheet.write(0, 22, "total_quality_score % ")
                worksheet.write(0, 23, "overall_total_forms")

                # worksheet.write(0, 24, "Percent Section A total_quality_score % ")
                # worksheet.write(0, 25, "Percent Section B total_quality_score % ")
                # worksheet.write(0, 26, "Percent Section C total_quality_score % ")




                row = row + 1
                col = 0

                ################################################# For Surveyor_Count Start####################################################

                project_id_val = 0
                if ("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"] != "default"):
                    projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                    project_id_val = projectId.id

                ################################################ For Surveyor_Count ####################################################

                # print("data",data)
                for data in data:

                    ################################################# For Surveyor_Count Start####################################################

                    try:
                        surveyor_id_val = data["surveyor_name"].split("-")[0]
                        
                    except Exception as e:
                        surveyor_id_val = data["surveyor_name"].split("(")[1][:len(data["surveyor_name"].split("(")[1])-1]


                    # if type(surveyor_id_val) == 

                    count_total = _count_overall_forms(
                        surveyor_id_val,
                        project_id_val or None,
                    )

                    # print(data)

                                # print(survey_response_obj.count(),"coount")

                    ################################################ For Surveyor_Count END####################################################

                    raw_surveyor = str(data["surveyor_name"] or "").strip()
                    s_id, s_name = parse_surveyor_field(raw_surveyor)
                    
                    if s_id and s_name:
                        formatted_surveyor = f"{s_id} - {s_name}"
                    else:
                        formatted_surveyor = raw_surveyor
                        
                    worksheet.write(row, 1, formatted_surveyor)

                    worksheet.write(row, 2, round(float(str(data["alisectionAskipping"])),2))
                    # worksheet.write(row, 3, int(round(float(str(data["alisectionAknowledge"])))))
                    # worksheet.write(row, 4, int(round(float(str(data["alisectionArecordings"])))))
                    # worksheet.write(row, 5, int(round(float(str(data["alisectionAvoice"])))))
                    worksheet.write(row, 3, round(float(str(data["alisectionAPercent"])),2))


                    worksheet.write(row, 4, round(float(str(data["alisectionBskills"])),2))
                    # worksheet.write(row, 8, int(round(float(str(data["alisectionBknowledge"])))))
                    # worksheet.write(row, 9, int(round(float(str(data["alisectionBrecordings"])))))
                    worksheet.write(row, 5, round(float(str(data["alisectionBPercent"])),2))


                    worksheet.write(row, 6, round(float(str(data["alisectionCpolite"])),2))
                    worksheet.write(row, 7, round(float(str(data["alisectionCspeech"])),2))
                    worksheet.write(row, 8, round(float(str(data["alisectionCprofessional"])),2))
                    worksheet.write(row, 9, round(float(str(data["alisectionCPercent"])),2))


                    worksheet.write(row, 10, round(float(str(data["alisectionDpolitecourteous"])),2))
                    worksheet.write(row, 11, round(float(str(data["alisectionDrateofspeech"])),2))
                    worksheet.write(row, 12, round(float(str(data["alisectionDprofessionalismenergeticenthusiastic"])),2))
                    worksheet.write(row, 13, round(float(str(data["alisectionDPercent"])),2))


                    worksheet.write(row, 14, round(float(str(data["alisectionEvariation"])),2))
                    worksheet.write(row, 15, round(float(str(data["alisectionEsurvey"])),2))
                    worksheet.write(row, 16, round(float(str(data["alisectionEmovement"])),2))
                    worksheet.write(row, 17, round(float(str(data["alisectionEtagging"])),2))
                    worksheet.write(row, 18, round(float(str(data["sectionEfakeForms"])),2))
                    worksheet.write(row, 19, round(float(str(data["alisectionEtotal"])),2))

                    worksheet.write(row, 20, round(float(str(data["surveyor_count"])),2)) ##comment by me
                    worksheet.write(row, 21, int(round(float(str(data["qualityPercent"])))))
                    worksheet.write(row, 22, int(round(float(str(100)))))
                    # worksheet.write(row,24, str(data["surveyor_name"]))
                    worksheet.write(row, 23, int(round(float(str(count_total)))))
                    # worksheet.write(row, 24, str(data["alisectionAPercent"]))
                    # worksheet.write(row, 25, str(data["alisectionBPercent"]))
                    # worksheet.write(row, 26, str(data["alisectionCPercent"]))




                    row = row + 1


                workbook.close()
                output.seek(0)
            elif(type=="detailed_summary"):
                row = 0
                col = 0
                worksheet.write(0, 1, "surveyor_name")
                # worksheet.write(0, 2, "No Questions Skipping")
                # worksheet.write(0, 3, "Thorough Knowledge of Questionnaire")
                # worksheet.write(0, 4, "No Incomplete Recordings")
                # worksheet.write(0, 5, "Respondent voice can be heard clearly/Background noises")
                worksheet.write(0, 2,"Section - A Behavioural Aspect ")

                # worksheet.write(0, 7, "Good probing or questioning Skills")
                # worksheet.write(0, 8, "Prompting Answer/ Options")
                # worksheet.write(0, 9, "Good Convincing Skills")
                worksheet.write(0, 3, "Section - B Subject Knowledge")

                # worksheet.write(0, 11, "Being polite and courteous during survey")
                # worksheet.write(0, 12, "Good rate of speech")
                # worksheet.write(0, 13, "Professional / Enthusiastic / Energetic")
                worksheet.write(0, 4, "Section - C Survey Handling Skills")

                worksheet.write(0, 5, "Section - D Soft skills")

                # worksheet.write(0, 15, "Variation")
                # worksheet.write(0, 16, "Force Survey/False Promises/False Information")
                # worksheet.write(0, 17, "Movement During Interview")
                worksheet.write(0, 6, "Geo Tagging")
                worksheet.write(0, 7, "Fake Forms Count")
                worksheet.write(0, 8, "Section - E Fatal Errors")

                worksheet.write(0, 9, "total_forms_verified")

                worksheet.write(0, 10, "quality_score % ")
                worksheet.write(0, 11, "total_quality_score % ")
                worksheet.write(0, 16, "overall_total_forms")

                # worksheet.write(0, 24, "Percent Section A total_quality_score % ")
                # worksheet.write(0, 25, "Percent Section B total_quality_score % ")
                # worksheet.write(0, 26, "Percent Section C total_quality_score % ")

                row = row + 1
                col = 0



                ################################################# For Surveyor_Count Start####################################################

                project_id_val=0
                if("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"]!="default"):
                    projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                    project_id_val = projectId.id

                ################################################ For Surveyor_Count ####################################################

                for data in data:

                    ################################################# For Surveyor_Count Start####################################################

                    try:
                        surveyor_id_val = data["surveyor_name"].split("-")[0]
                        
                    except Exception as e:
                        surveyor_id_val = data["surveyor_name"].split("(")[1][:len(data["surveyor_name"].split("(")[1])-1]

                    # surveyor_id_val = data["surveyor_name"].split("-")[0]



                    count_total = _count_overall_forms(
                        surveyor_id_val,
                        project_id_val or None,
                    )

                    ################################################ For Surveyor_Count END####################################################



                    worksheet.write(row, 1, str(data["surveyor_name"]))

                    # worksheet.write(row, 2, str(data["alisectionAskipping"]))
                    # worksheet.write(row, 3, str(data["alisectionAknowledge"]))
                    # worksheet.write(row, 4, str(data["alisectionArecordings"]))
                    # worksheet.write(row, 5, str(data["alisectionAvoice"]))
                    worksheet.write(row, 2, round(float(str(data["alisectionAPercent"])),2))

                    # worksheet.write(row, 7, str(data["alisectionBskills"]))
                    # worksheet.write(row, 8, str(data["alisectionBknowledge"]))
                    # worksheet.write(row, 9, str(data["alisectionBrecordings"]))
                    worksheet.write(row, 3, round(float(str(data["alisectionBPercent"])),2))

                    # worksheet.write(row, 11, str(data["alisectionCpolite"]))
                    # worksheet.write(row, 12, str(data["alisectionCspeech"]))
                    # worksheet.write(row, 13, str(data["alisectionCprofessional"]))
                    worksheet.write(row, 4, round(float(str(data["alisectionCPercent"])),2))

                    worksheet.write(row, 5, round(float(str(data["alisectionDPercent"])),2))

                    # worksheet.write(row, 15, str(data["alisectionDvariation"]))
                    # worksheet.write(row, 16, str(data["alisectionDsurvey"]))
                    # worksheet.write(row, 17, str(data["alisectionDmovement"]))
                    worksheet.write(row, 6, round(float(str(data["alisectionEtagging"])),2))
                    worksheet.write(row, 7, round(float(str(data["sectionEfakeForms"])),2))
                    worksheet.write(row, 8, round(float(str(data["alisectionEtotal"])),2))

                    worksheet.write(row, 9, round(float(str(data["surveyor_count"])),2))
                    worksheet.write(row, 10, int(round(float(str(data["qualityPercent"])))))
                    worksheet.write(row, 11, (float(str(100))))
                    # worksheet.write(row, 24, str(data["surveyor_name"]))

                    # worksheet.write(row, 24, str(data["alisectionAPercent"]))
                    # worksheet.write(row, 25, str(data["alisectionBPercent"]))
                    # worksheet.write(row, 26, str(data["alisectionCPercent"]))
                    if(request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                        worksheet.write(row, 16, (float(str(count_total))))

                    row = row + 1

                # workbook.close()
                # output.seek(0)

            workbook.close()
            output.seek(0)  # Go to the start of the BytesIO buffer

            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={str(date.today())}_hourly.xlsx'
            import gc
            gc.collect()

            return response





    def exportHourlyBased(self,data,auditor_arr,selected_date):
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output);
            worksheet = workbook.add_worksheet('output')

            row = 0
            col = 0;

            # worksheet.write(0, 0, "Date")
            worksheet.write(0, 1, "Name")
            worksheet.write(0, 2, "00.00 - 01.00")
            worksheet.write(0, 3, "01.00 - 02.00")
            worksheet.write(0, 4, "02.00 - 03.00")
            worksheet.write(0, 5, "03.00 - 04.00")
            worksheet.write(0, 6, "04.00 - 05.00")
            worksheet.write(0, 7, "05.00 - 06.00")
            worksheet.write(0, 8, "06.00 - 07.00")
            worksheet.write(0, 9, "07.00 - 08.00")
            worksheet.write(0, 10, "08.00 - 09.00")
            worksheet.write(0, 11, "09.00 - 10.00")
            worksheet.write(0, 12, "10.00 - 11.00")
            worksheet.write(0, 13, "11.00 - 12.00")
            worksheet.write(0, 14, "12.00 - 13.00")
            worksheet.write(0, 15, "13.00 - 14.00")
            worksheet.write(0, 16, "14.00 - 15.00")
            worksheet.write(0, 17, "15.00 - 16.00")
            worksheet.write(0, 18, "16.00 - 17.00")
            worksheet.write(0, 19, "17.00 - 18.00")
            worksheet.write(0, 20, "18.00 - 19.00")
            worksheet.write(0, 21, "19.00 - 20.00")
            worksheet.write(0, 22, "20.00 - 21.00")
            worksheet.write(0, 23, "21.00 - 22.00")
            worksheet.write(0, 24, "22.00 - 23.00")
            worksheet.write(0, 25, "23.00 - 00.00")

            worksheet.write(0, 27, "Total Count")


            row = row + 1
            col = 0;
            for hrdata in auditor_arr:
                # print(hrdata)
                if("name" in hrdata.keys()):
                    # worksheet.write(row, 0, str(selected_date))
                    worksheet.write(row, 1, str(hrdata["name"]))
                    worksheet.write(row, 2, int(str(0)))
                    worksheet.write(row, 3, int(str(0)))
                    worksheet.write(row, 4, int(str(0)))
                    worksheet.write(row, 5, int(str(0)))
                    worksheet.write(row, 6, int(str(0)))
                    worksheet.write(row, 7, int(str(0)))
                    worksheet.write(row, 8, int(str(0)))
                    worksheet.write(row, 9, int(str(0)))
                    worksheet.write(row, 10, int(str(0)))
                    worksheet.write(row, 11, int(str(0)))
                    worksheet.write(row, 12, int(str(0)))
                    worksheet.write(row, 13, int(str(0)))
                    worksheet.write(row, 14, int(str(0)))
                    worksheet.write(row, 15, int(str(0)))
                    worksheet.write(row, 16, int(str(0)))
                    worksheet.write(row, 17, int(str(0)))
                    worksheet.write(row, 18, int(str(0)))
                    worksheet.write(row, 19, int(str(0)))
                    worksheet.write(row, 20, int(str(0)))
                    worksheet.write(row, 21, int(str(0)))
                    worksheet.write(row, 22, int(str(0)))
                    worksheet.write(row, 23, int(str(0)))
                    worksheet.write(row, 24, int(str(0)))
                    worksheet.write(row, 25, int(str(0)))

                    worksheet.write(row, 27, int(str(len(hrdata["obj"]))))




                    # print(hrdata["obj"],"=====",hrdata["name"])
                    hour_count={}
                    for hourlyData in hrdata["obj"]:
                        if(hourlyData.created_at.hour in hour_count.keys()):
                            hour_count[hourlyData.created_at.hour] = hour_count[hourlyData.created_at.hour]+1;
                        else:
                            hour_count[hourlyData.created_at.hour] = 1;

                    for x in hour_count.keys():
                        worksheet.write(row, x+2 , int(str(hour_count[x])))

                row = row + 1

            # for data in data:
            #     # print(data)
            #     # print(data["starting_hour"],"======",data["ending_hour"]," count::",len(data["hourly_uids"]))
            #     date_time_obj = data["starting_hour"]
            #     date_time_obj = data["ending_hour"]
            #     d=(date_time_obj.date())
            #
            #
            #     a = (date_time_obj.time())
            #     h=(a.hour)
            #     # print(h)
            #
            #
            #     # print(data["hourly_uids"],"<<<<hourly auditor ids::::",h)
            #
            #     worksheet.write(1, col, str(d))
            #
            #     worksheet.write(1, h+2, str(len(data["hourly_uids"])))
            #     worksheet.write(1,27,str(data["hourly_auditor_ids"]))
            #
            #     row = row + 1
            #
            #
            #
            #
            #
            #
            #     # worksheet.write(row, 1, str(data["starting_hour"]))
            #     # worksheet.write(row, 2, str(data["ending_hour"]))
            #     # worksheet.write(row, 3, str(len(data["hourly_uids"])))
            #     # worksheet.write(row, 4, ",".join(map(str,data["hourly_uids"])))
            #     #row = row + 1



            workbook.close();
            output.seek(0)

            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={selected_date}_hourly.xlsx'
            import gc
            gc.collect()

            return response

        
        # def exportHourlyBased(self, data, auditor_arr, selected_date):
        # 	output = io.BytesIO()  # Use BytesIO for binary data, which is required for xlsxwriter
        # 	workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # 	worksheet = workbook.add_worksheet('output')

        # 	row = 0
        # 	col = 0

        # 	# Write headers
        # 	headers = [
        # 		"Name", "00.00 - 01.00", "01.00 - 02.00", "02.00 - 03.00", "03.00 - 04.00",
        # 		"04.00 - 05.00", "05.00 - 06.00", "06.00 - 07.00", "07.00 - 08.00", "08.00 - 09.00",
        # 		"09.00 - 10.00", "10.00 - 11.00", "11.00 - 12.00", "12.00 - 13.00", "13.00 - 14.00",
        # 		"14.00 - 15.00", "15.00 - 16.00", "16.00 - 17.00", "17.00 - 18.00", "18.00 - 19.00",
        # 		"19.00 - 20.00", "20.00 - 21.00", "21.00 - 22.00", "22.00 - 23.00", "23.00 - 00.00",
        # 		"Total Count"
        # 	]

        # 	for col, header in enumerate(headers):
        # 		worksheet.write(row, col, header)

        # 	row += 1

        # 	# Write data
        # 	for hrdata in auditor_arr:
        # 		if "name" in hrdata.keys():
        # 			worksheet.write(row, 1, hrdata["name"])
        # 			total_count = len(hrdata.get("obj", []))
        # 			worksheet.write(row, 25, total_count)

        # 			hour_count = {}
        # 			for hourlyData in hrdata.get("obj", []):
        # 				hour = hourlyData.created_at.hour
        # 				hour_count[hour] = hour_count.get(hour, 0) + 1

        # 			for hour, count in hour_count.items():
        # 				worksheet.write(row, hour + 2, count)

        # 			row += 1

        # 	workbook.close()
        # 	output.seek(0)  # Go to the start of the BytesIO buffer

        # 	response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 	response['Content-Disposition'] = f'attachment; filename={selected_date}_hourly.xlsx'

        # 	return response

class assign_projects(TemplateView):

    def __init__(self):

        pass

    def get(self,request):


        
        context = {}

        project_ids = SurveyResponse.objects.all().values_list('project',flat = True).distinct()


        surveyor_count = None

        projects = []
        

        

        for ids in project_ids:


            project_name = Project.objects.get(id = ids)
            # project_name = project_name.name
            projects.append(project_name)

            

            # for value in SurveyResponse.objects.all():
            # qualityRecords = SurveyResponse.objects.filter(project=2).values('surveyor') \
            #                 .annotate(surveyor_count=Count('surveyor'))
            
            # for i in qualityRecords:
            #     surveyor_name = User.objects.get(user_employee=i['surveyor']).get_full_name()
            #     print(surveyor_name)
            #     uid = SurveyResponse.objects.filter(surveyor=i['surveyor']).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True)).values_list('uid',flat=True)[:round(int(i['surveyor_count']) * 0.3)]
        context = {"projects": projects, "test": "abcde",'htmlfilename':'quality.html'}

        return render(request,'index.html',context)
    

@require_roles(roles=["Manager"])
def assign_projects_view(request):
    employees = Employee.objects.filter(employee_id__in = (112418,113124,110649,109691,111293,107501,112418,108504,110880,111264,111265,112779))
    projects = Project.objects.filter(active = 1)
    
    # Fetch assignments with related employees and projects
    assignments = Assignment.objects.select_related('employee', 'project')

    

    # Create a mapping of employee IDs to their assigned project names
    employee_assignments = {}
    for assignment in assignments:
        employee_id = assignment.employee.id
        # print(employee_id)
        project_name = assignment.project.name
        # print(project_name)
        if employee_id not in employee_assignments:
            employee_assignments[employee_id] = {
                'name': assignment.employee.user.get_full_name(),
                'projects': []
            }
        employee_assignments[employee_id]['projects'].append(project_name)


    return render(request, 'index.html', {
        'employees': employees,
        'projects': projects,
        'htmlfilename':'search_quality_Assign_QA.html',
        'employee_assignments': employee_assignments,
        'assignments':assignments,
        'user': request.user.user_employee,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        #'employee_pic': request.user.user_employee.get_profile_pic(),
        'userrole': request.user.user_employee.designation.name,
        'department': request.user.user_employee.designation.department.name,
    })

@require_roles(roles=["Manager"])
def assign_projects(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        project_ids = request.POST.getlist('project_ids[]')

        # Check if the employee is already assigned to the selected projects
        existing_assignments = Assignment.objects.filter(employee_id=employee_id, project__in=project_ids)

        if existing_assignments.exists():
            return JsonResponse({'success': False, 'message': 'Some projects are already assigned to this employee.'})

        for project_id in project_ids:
            Assignment.objects.create(employee_id=employee_id, project_id=project_id)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)

@require_roles(roles=["Manager"])
def assigned_delete(request, id):
      # Get your current cat

    if request.method == 'POST':
        assign_id = Assignment.objects.get(pk=id)         # If method is POST,
        assign_id.delete()                     # delete the cat.
        return redirect('/assign_projects')
    return render(request, 'index.html', {'htmlfilename':'search_quality_Assign_QA.html'})

    