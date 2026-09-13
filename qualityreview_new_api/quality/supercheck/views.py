
from __future__ import unicode_literals

import pytz #type: ignore

from collections import defaultdict

from pytz import timezone  #type: ignore

from dateutil import parser #type: ignore

# from StringIO import StringIO
import io
from django.http import HttpResponse,JsonResponse #type: ignore
from django.shortcuts import render,redirect #type: ignore
from django.views.generic import TemplateView #type: ignore
from django.shortcuts import HttpResponseRedirect #type: ignore
from django.contrib.auth import authenticate, login, logout #type: ignore
from django.contrib.auth.models import User #type: ignore
from django.conf import settings #type: ignore
from django.utils import timezone as django_timezone
from django.utils.decorators import method_decorator #type: ignore
from quality.access_control import require_roles #type: ignore
import logging #type: ignore
import os #type: ignore
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
import xlsxwriter #type: ignore
# from django.db.models import Count,Case,When,Sum,FloatField, ExpressionWrapper, F, Q
from django.db.models import FloatField, F, Sum, Count, ExpressionWrapper, Value, Case, When,Q #type: ignore
from django.db.models.functions import Cast #type: ignore

logger = logging.getLogger(__name__)

def _get_surveygenius_connection():
    """Return a mysql.connector connection to the SurveyGenius DB using env vars."""
    return mysql.connector.connect(
        user=os.environ.get('SURVEYGENIUS_DB_USER', 'root'),
        password=os.environ.get('SURVEYGENIUS_DB_PASSWORD', ''),
        host=os.environ.get('SURVEYGENIUS_DB_HOST', '127.0.0.1'),
        port=int(os.environ.get('SURVEYGENIUS_DB_PORT', 9000)),
        database=os.environ.get('SURVEYGENIUS_DB_NAME', 'surveygeniusdb'),
    )



@method_decorator(require_roles(departments=["Quality"], roles=["Manager", "Assistant_Manager"]), name='dispatch')
class capi_supercheck(TemplateView):
    def __init__(self):

        pass

    def get(self,request):
        #### connection with 32
        cnx2 = _get_surveygenius_connection()


        mycursor = cnx2.cursor()
        
        data1 = []      

        
        # print(data1)
        max_val = 5

        # print("searchv222")
        # print(request.user.user_employee.designation.name,"=====",request.user.user_employee.employee_id,"<<<user::::",request.user.user_employee.designation.department.name)
        # sql = "SELECT DISTINCT project_name FROM `quality_qualityreview`"
        # mycursor.execute(sql)

        # results = mycursor.fetchall()
        # active_projects_list = results[0]
        
        active_projects_list = SuperCheckQualityReview.objects.values("project_name").distinct()
        # sql = "SELECT DISTINCT quality_auditor, quality_auditor_id FROM `quality_qualityreview`"
        # mycursor.execute(sql)
        # results = mycursor.fetchall()
        # auditor_list = results
        auditor_list = SuperCheckQualityReview.objects.values("quality_auditor","quality_auditor_id").distinct()

        # sql = "SELECT `quality_issuelist`.`issue_id`, `quality_issuelist`.`issues`, `quality_issuelist`.`related_question` FROM `quality_issuelist` WHERE `quality_issuelist`.`section` = 'section_A'"
        # mycursor.execute(sql)
        # results = mycursor.fetchall()
        # sectionAIssueList = results

        sectionAIssueList = IssueList.objects.filter(section="section_A").values("issue_id","issues","related_question")
        
        # sql = "SELECT `quality_issuelist`.`issue_id`, `quality_issuelist`.`issues`, `quality_issuelist`.`related_question` FROM `quality_issuelist` WHERE `quality_issuelist`.`section` = 'section_B'"
        # mycursor.execute(sql)
        # results = mycursor.fetchall()
        # sectionBIssueList = results

        sectionBIssueList = IssueList.objects.filter(section="section_B").values("issue_id", "issues","related_question")

        # sql = "SELECT `quality_issuelist`.`issue_id`, `quality_issuelist`.`issues`, `quality_issuelist`.`related_question` FROM `quality_issuelist` WHERE `quality_issuelist`.`section` = 'section_C'"
        # mycursor.execute(sql)
        # results = mycursor.fetchall()
        # sectionCIssueList = results
        sectionCIssueList = IssueList.objects.filter(section="section_C").values("issue_id", "issues","related_question")

        # sql = "SELECT `quality_issuelist`.`issue_id`, `quality_issuelist`.`issues`, `quality_issuelist`.`related_question` FROM `quality_issuelist` WHERE `quality_issuelist`.`section` = 'section_D'"
        # mycursor.execute(sql)
        # results = mycursor.fetchall()
        # sectionDIssueList = results
        sectionDIssueList = IssueList.objects.filter(section="section_D").values("issue_id", "issues","related_question")

        # sql = "SELECT `quality_issuelist`.`issue_id`, `quality_issuelist`.`issues`, `quality_issuelist`.`related_question` FROM `quality_issuelist` WHERE `quality_issuelist`.`section` = 'section_E'"
        # mycursor.execute(sql)
        # results = mycursor.fetchall()
        # sectionEIssueList = results
        sectionEIssueList = IssueList.objects.filter(section="section_E").values("issue_id", "issues","related_question")
        # print(auditor_list,"<<<<<<<<<<<<<<<<,quality_auditor")


        data = {}
        # print(request.GET.keys())

        
        today_min = django_timezone.make_aware(datetime.datetime.combine(datetime.date.today(), datetime.time.min))
        today_max = django_timezone.make_aware(datetime.datetime.combine(datetime.date.today(), datetime.time.max))
        
        ###################################################
        quality_project_wise_records = None
        auditor_count = 0
        if (request.user.user_employee.designation.department.name == "Quality" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance", "Manager"]) or \
            (request.user.user_employee.designation.department.name == "DRC" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance"]) or \
            (request.user.user_employee.designation.department.name == "Product" and request.user.user_employee.designation.name == "Manager"):
            
            
            # sql = f"SELECT `quality_qualityreview`.`quality_auditor`, COUNT(`quality_qualityreview`.`project_name`) AS `project_name__count` FROM `quality_qualityreview` WHERE `quality_qualityreview`.`created_at` BETWEEN '{today_min}' AND '{today_max}' GROUP BY `quality_qualityreview`.`quality_auditor` ORDER BY NULL"
            # mycursor.execute(sql)

            # results = mycursor.fetchall()
            # quality_project_wise_records = results

            quality_project_wise_records = SuperCheckQualityReview.objects.filter(created_at__range=(today_min, today_max)).values("quality_auditor") \
                .annotate(Count('project_name'))

            # sql = f"SELECT COUNT(`quality_qualityreview`.`id`) FROM `quality_qualityreview` WHERE `quality_qualityreview`.`created_at` BETWEEN '{today_min}' AND '{today_max}';"
            # mycursor.execute(sql)

            # results = mycursor.fetchall()
            # auditor_count = results
            
            auditor_count = SuperCheckQualityReview.objects.filter(created_at__range=(today_min, today_max)).count()

            
            
            # print(quality_project_wise_records, "><<<")
        else:

            # sql = f"SELECT `quality_qualityreview`.`project_name`, COUNT(`quality_qualityreview`.`project_name`) AS `project_name__count` FROM `quality_qualityreview` WHERE (`quality_qualityreview`.`created_at` BETWEEN {today_min} AND {today_max} AND `quality_qualityreview`.`quality_auditor_id` = {request.user.user_employee.employee_id}) GROUP BY `quality_qualityreview`.`project_name` ORDER BY NULL"
            # mycursor.execute(sql)

            # results = mycursor.fetchall()
            # quality_project_wise_records = results

            quality_project_wise_records = SuperCheckQualityReview.objects.filter(created_at__range=(today_min, today_max),
                    quality_auditor_id=request.user.user_employee.employee_id).values("project_name").annotate(Count('project_name'))

            # sql = f"select count (`quality_qualityreview`.`id`) FROM `quality_qualityreview` WHERE (`quality_qualityreview`.`created_at` BETWEEN {today_min}  AND {today_max} AND `quality_qualityreview`.`quality_auditor_id` = {request.user.user_employee.employee_id})"
            # mycursor.execute(sql)

            # results = mycursor.fetchall()
            # auditor_count = results
            auditor_count = SuperCheckQualityReview.objects.filter(created_at__range=(today_min, today_max),
                                                         quality_auditor_id=request.user.user_employee.employee_id).count()
            # print(quality_project_wise_records)

        ###################################################



        # print(request.GET)

        uid_submitted = False
        
        if("filter" not in request.GET.keys() and "uid" in request.GET.keys() and request.GET["uid"]!=""):

            print("if calledddd")

            sql = """
                SELECT `mainapp_project`.`name`, `mainapp_verificationstatus`.`name`, `mainapp_surveyresponse`.`id`, 
                    `mainapp_surveyresponse`.`uid`, `mainapp_surveyresponse`.`uidi`, `mainapp_surveyresponse`.`user_id`, 
                    `mainapp_surveyresponse`.`project_id`, `mainapp_surveyresponse`.`surveyor_id`, 
                    `mainapp_surveyresponse`.`verification_status_id`, `mainapp_surveyresponse`.`otp_verified`, 
                    `mainapp_surveyresponse`.`params`, `mainapp_surveyresponse`.`remarks`, 
                    `mainapp_surveyresponse`.`verification_date`, `mainapp_surveyresponse`.`send_to_surveyor` 
                FROM `mainapp_surveyresponse` 
                INNER JOIN `mainapp_project` ON `mainapp_project`.id = `mainapp_surveyresponse`.`project_id` 
                INNER JOIN `mainapp_verificationstatus` ON `mainapp_verificationstatus`.id = `mainapp_surveyresponse`.`verification_status_id` 
                WHERE `mainapp_surveyresponse`.`uid` = %s
            """
            # surveyResponse = SurveyResponse.objects.filter(uid=request.GET["uid"])
            mycursor.execute(sql)

            surveyResponse = mycursor.fetchall()
            # print(surveyResponse)
            ####### code for highlighting submitted uids ##########

            submitted_uids_list = SuperCheckQualityReview.objects.filter(uid=request.GET["uid"])

            # print("ddddd",submitted_uids_list)

            submitted_uids_list = [i.uid for i in submitted_uids_list]
            
            if submitted_uids_list:
                uid_submitted = True

            # print(uid_submitted,"uid submiteed")
        
            ####### code for highlighting submitted uids ##########

            sql = f"SELECT count(`mainapp_surveyresponse`.`id`) FROM `mainapp_surveyresponse` WHERE `mainapp_surveyresponse`.`uid` = {request.GET['uid']}"
            # surveyResponse = SurveyResponse.objects.filter(uid=request.GET["uid"])
            mycursor.execute(sql)

            surveyResponse_count = mycursor.fetchall()
            # print(surveyResponse_count)

            # print("subbbbb",[i.uid for i in submitted_uids_list])

            if(surveyResponse_count[0][0] >0):
                params = json.loads(surveyResponse[0][10])

                remarks = json.loads(surveyResponse[0][11])
                try:
                    surveyor_id=params["surveyor"].split("-")[0]
                    surveyor_id=int(surveyor_id)
                except:   
                    surveyor_id=(params["surveyor"].split("(")[1])[:(params["surveyor"].split("(")[1]).find(")")]
                try:
                    surveyor_name = params["surveyor"].split("-")[1];
                except:
                    surveyor_name = (params["surveyor"].split("-")[1])[:(params["surveyor"].split("-")[1]).find("(")]
                tl_name=params["tldetails"]

                currentdatetime=datetime.datetime.now().strftime('%d-%m-%Y')

                # print(params,remarks,surveyor_id,surveyor_name,tl_name,currentdatetime)

                # params["date"] = parser.parse(params["date"])

                # params["date"] = params["date"].astimezone(timezone('Asia/Kolkata'))
                # print((params["date"]))


                sql = f"SELECT count(`mainapp_surveyresponse`.`id`) FROM `mainapp_surveyresponse` WHERE `mainapp_surveyresponse`.`uid` = {request.GET['uid']}"
                # surveyResponse = SurveyResponse.objects.filter(uid=request.GET["uid"])
                mycursor.execute(sql)

                surveyResponse_count = mycursor.fetchall()
                

                data={
                    'user': request.user.user_employee,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    # #'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    "uid":request.GET["uid"],
                    "project_id":surveyResponse[0][6],
                    "project_name": surveyResponse[0][0],
                    "surveyor_name":surveyor_name,
                    "surveyor_id":surveyor_id,
                    "tl_name":tl_name,
                    "params":params,
                    "remarks":remarks,
                    "verification_status":surveyResponse[0][1],
                    "audit_date":str(currentdatetime),
                    "interview_duration":params["timedifference"],
                    "interview_date":params["date"],
                    "quality_auditor_name":request.user.first_name +" "+ request.user.last_name,
                    "status":True,
                    'htmlfilename': 'supercheck_templates/capi_supercheck.html',
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
                # print("if-else called calledddd")
                data = {
                    'user': request.user.user_employee,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    #'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    'htmlfilename': 'supercheck_templates/capi_supercheck.html',
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
                    "submitted_uids_status":uid_submitted
                    
                }
                return render(request, "index.html", data)
        elif("filter" in request.GET.keys()):
            # print("elif calledddd::::")
            if("auditor_project_name" in request.GET.keys() or "quality_auditor_name" in request.GET.keys() or "startdate" in request.GET.keys() or "enddate" in request.GET.keys()):

                if(request.GET["selected_form"]=="fetch" or request.GET["selected_form"]=="detailed_summary"):

                    if(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]!="" and request.GET["enddate"]!=""):

                        enddate=None
                        startdate = None
                        # print(request.GET["interview_startdate"],"=====1======",request.GET["interview_enddate"])
                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")


                        # print(request.GET["auditor_project_name"],"<<<<<<<<,,nameeee::::",request.GET["quality_auditor_name"])
                        # qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate,enddate],project_name__icontains=request.GET["auditor_project_name"],
                        #                                               quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                        #     .annotate(Count('surveyor_name'),
                        #               alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("voice") / (
                        #                                                10 * Count('surveyor_name'))) * 100) / 400) * 100,
                        #
                        #               alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("convince") / (
                        #                                            10 * Count('surveyor_name'))) * 100) / 300) * 100,
                        #
                        #               alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                        #               alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                        #                                    (Sum("professional") / (
                        #                                            10 * Count('surveyor_name'))) * 100) / 300) * 100,
                        #
                        #               alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                        #                   "voice") + Sum(
                        #                   "skills") +
                        #                            Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                        #                           "professional")),
                        #
                        #               alisectionDvariation=Sum("variation"),
                        #               alisectionDsurvey=Sum("survey"),
                        #               alisectionDmovement=Sum("movement"),
                        #               alisectionDtagging=Sum("tagging"),
                        #               alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),
                        #
                        #               alisectionABCD_diff=Sum("totalscore"),
                        #               test1=(4 * 10) * Count('surveyor_name'),
                        #               test2=(3 * 10) * Count('surveyor_name'),
                        #               test3=(3 * 10) * Count('surveyor_name'),
                        #               qualityPercent=((Sum("totalscore")) / (
                        #                       (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                        #                       3 * 10) * Count('surveyor_name')) * 100),
                        #               sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))


                    # 	# print(QualityReview.objects.filter(auditor_date__range=[startdate, enddate],
                    # 												  project_name__icontains=request.GET[
                    # 													  "auditor_project_name"],
                    # 												  quality_auditor__icontains=request.GET[
                    # 													#   "quality_auditor_name"]).values("surveyor_name") \
                    # # .annotate(Count('surveyor_name', output_field=FloatField())), 
                    
                        # print((Sum("question_skipping_incomplete_recordings") / (max_val * Count('surveyor_name', output_field=FloatField()))) * 100)


                        # value = QualityReview.objects.filter(auditor_date__range=[startdate, enddate],
                        # 											  project_name__icontains=request.GET[
                        # 												  "auditor_project_name"],
                        # 											  quality_auditor__icontains=request.GET[
                        # 												  "quality_auditor_name"]).values(
                        # 	"surveyor_name") \
                        # 	.annotate(Count('surveyor_name', output_field=FloatField()))
                 
                         # 				# total_group=Sum(F('total_sold')*F('final_price'), output_field=FloatField())
                                         
                        
                             
                 
                        # alisectionAskipping=(Sum(F("question_skipping_incomplete_recordings")) / (max_val * Count(F('surveyor_name'), output_field=FloatField()))) * 100
                        
                        # print(alisectionAskipping)

                        qualityRecords = SuperCheckQualityReview.objects.filter(
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

                        # print(qualityRecords.count(), "*****************************************")


                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]=="" and request.GET["enddate"]==""):


                        # print(request.GET["interview_startdate"], "======2=====", request.GET["interview_enddate"])



                        qualityRecords = SuperCheckQualityReview.objects.filter(
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
                        # print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] != "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

                        enddate=None
                        startdate=None
                        # print(request.GET["interview_startdate"], "======3=====", request.GET["interview_enddate"])

                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")

                         #### qualityrecords auditor ####

                                                #### qualityrecords auditor ####

                        sql = f"SELECT `quality_qualityreview`.`surveyor_name`, COUNT(`quality_qualityreview`.`surveyor_name`) AS `surveyor_name__count`, ((SUM(`quality_qualityreview`.`question_skipping_incomplete_recordings`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionAskipping`, ((((SUM(`quality_qualityreview`.`question_skipping_incomplete_recordings`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) / 100) * 100) AS `alisectionAPercent`, ((SUM(`quality_qualityreview`.`question_subject_knowledge`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionBskills`, ((((SUM(`quality_qualityreview`.`question_subject_knowledge`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) / 100) * 100) AS `alisectionBPercent`, ((SUM(`quality_qualityreview`.`voice_clarity`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionCpolite`, ((SUM(`quality_qualityreview`.`questioning_technique`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionCspeech`, ((SUM(`quality_qualityreview`.`convencing_skills`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionCprofessional`, ((((((SUM(`quality_qualityreview`.`voice_clarity`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) + ((SUM(`quality_qualityreview`.`questioning_technique`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100)) + ((SUM(`quality_qualityreview`.`convencing_skills`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100)) / 300) * 100) AS `alisectionCPercent`, ((SUM(`quality_qualityreview`.`polite_courteous`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionDpolitecourteous`, ((SUM(`quality_qualityreview`.`rate_of_speech`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionDrateofspeech`, ((SUM(`quality_qualityreview`.`professionalism_energetic_enthusiastic`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) AS `alisectionDprofessionalismenergeticenthusiastic`, ((((((SUM(`quality_qualityreview`.`polite_courteous`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100) + ((SUM(`quality_qualityreview`.`rate_of_speech`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100)) + ((SUM(`quality_qualityreview`.`professionalism_energetic_enthusiastic`) / (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) * 100)) / 300) * 100) AS `alisectionDPercent`, (((((((SUM(`quality_qualityreview`.`question_skipping_incomplete_recordings`) + SUM(`quality_qualityreview`.`question_subject_knowledge`)) + SUM(`quality_qualityreview`.`voice_clarity`)) + SUM(`quality_qualityreview`.`questioning_technique`)) + SUM(`quality_qualityreview`.`convencing_skills`)) + SUM(`quality_qualityreview`.`polite_courteous`)) + SUM(`quality_qualityreview`.`rate_of_speech`)) + SUM(`quality_qualityreview`.`professionalism_energetic_enthusiastic`)) AS `alitotalABCD`, SUM(`quality_qualityreview`.`variation`) AS `alisectionEvariation`, SUM(`quality_qualityreview`.`survey`) AS `alisectionEsurvey`, SUM(`quality_qualityreview`.`movement`) AS `alisectionEmovement`, SUM(`quality_qualityreview`.`tagging`) AS `alisectionEtagging`, (((SUM(`quality_qualityreview`.`variation`) + SUM(`quality_qualityreview`.`survey`)) + SUM(`quality_qualityreview`.`movement`)) + SUM(`quality_qualityreview`.`tagging`)) AS `alisectionEtotal`, SUM(`quality_qualityreview`.`totalscore`) AS `alisectionABCDE_diff`, (5 * COUNT(`quality_qualityreview`.`surveyor_name`)) AS `test1`, (5 * COUNT(`quality_qualityreview`.`surveyor_name`)) AS `test2`, (15 * COUNT(`quality_qualityreview`.`surveyor_name`)) AS `test3`, (15 * COUNT(`quality_qualityreview`.`surveyor_name`)) AS `test4`, ((SUM(`quality_qualityreview`.`totalscore`) / ((((5 * COUNT(`quality_qualityreview`.`surveyor_name`)) + (5 * COUNT(`quality_qualityreview`.`surveyor_name`))) + (15 * COUNT(`quality_qualityreview`.`surveyor_name`))) + (15 * COUNT(`quality_qualityreview`.`surveyor_name`)))) * 40) AS `qualityPercent`, COUNT(CASE WHEN `quality_qualityreview`.`is_fake_form` = True THEN 1 ELSE NULL END) AS `sectionEfakeForms` FROM `quality_qualityreview` WHERE  `quality_qualityreview`.`auditor_date` BETWEEN '{startdate}' AND '{enddate}' AND `quality_qualityreview`.`project_name` LIKE '%{request.GET.get('auditor_project_name', '')}%' GROUP BY  `quality_qualityreview`.`surveyor_name`;"


                        mycursor.execute(sql)

                        qualityrecords_auditor = mycursor.fetchall()
                        # print(qualityrecords_auditor,">>>>>>>>")

                        #### supercheck ####

                        qualityRecords = SuperCheckQualityReview.objects.filter(
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
                        # print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor_supercheck(qualityRecords,request.GET["selected_form"],request,quality_aud_data=qualityrecords_auditor)

                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""): 
                        # print("*********************************")

                        enddate = None
                        startdate = None
                        # print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])


                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = SuperCheckQualityReview.objects.filter(
                            auditor_date__range=[startdate, enddate],
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
                        # print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

                        enddate = None
                        startdate = None
                        # print(request.GET["interview_startdate"], "======5=====", request.GET["interview_enddate"])

                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = SuperCheckQualityReview.objects.filter(
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

                        # print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] != "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] == "" and request.GET["enddate"] == ""):
                        # qualityRecords = QualityReview.objects.filter(
                        #     project_name__icontains=request.GET["auditor_project_name"]).values("surveyor_name") \
                        #     .annotate(Count('surveyor_name'),Sum("skipping"), Sum("knowledge"), Sum("recordings"), Sum("voice"),
                        #               Sum("skills"), Sum("answer"), Sum("convince"),
                        #               Sum("polite"), Sum("speech"), Sum("professional"),
                        #               Sum("variation"), Sum("survey"), Sum("movement"), Sum("tagging"), Sum("fake"),
                        #               aliquots=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                        #                   "voice")) / 4.0,
                        #               alisectionB=(Sum("skills") + Sum("answer") + Sum("convince")) / 3.0,
                        #               alisectionC=(Sum("polite") + Sum("speech") + Sum("professional")) / 3.0,
                        #               alisectionD=(Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging") + Sum("fake")) / 5.0,
                        #               alisectionAPercent=((Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum("voice"))/((10*Count('surveyor_name'))*4))*100,
                        #               alisectionBPercent=((Sum("skills") + Sum("answer") + Sum("convince"))/((10*Count('surveyor_name'))*3))*100,
                        #               alisectionCPercent=((Sum("polite") + Sum("speech") + Sum("professional"))/((10*Count('surveyor_name'))*3))*100)

                        enddate = None
                        startdate = None
                        # print(request.GET["interview_startdate"], "======6=====", request.GET["interview_enddate"])


                        if("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                            enddate = datetime.datetime.strptime(str(request.GET["interview_enddate"]), "%Y-%m-%d")
                            startdate = datetime.datetime.strptime(str(request.GET["interview_startdate"]), "%Y-%m-%d")
                            # print("endDateeeeeeee called************",enddate,"=====",startdate)
                            qualityRecords = SuperCheckQualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"],interview_date__range=[startdate,enddate]).values("surveyor_name") \
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
                        else:


                            qualityRecords = SuperCheckQualityReview.objects.filter(
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
                            # print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] == "" and request.GET["enddate"] == ""):    ##### when we select only auditor name

                        enddate = None
                        startdate = None
                        # print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])

                        qualityRecords = SuperCheckQualityReview.objects.filter(
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
                        # print(qualityRecords)
                        # return self.exportData(qualityRecords)
                    return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)

                else:

                    # print("****123****")
                    # enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                    # startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                    # print("request.GET:::::",request.GET["auditor_project_name"])
                    qualityRecords = None
                    if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]!="default"):
                        # print("12345")

                        enddate = None
                        startdate = None
                        # print(request.GET["interview_startdate"], "======7=====", request.GET["interview_enddate"])


                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = SuperCheckQualityReview.objects.filter(auditor_date__range=[startdate,enddate],project_name__icontains=request.GET["auditor_project_name"])
                    else:
                       ####supercheck filter code
                        # print("****1234****")
                        if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]=="default"):

                            enddate = None
                            startdate = None
                            # print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])


                            enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                            startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                            qualityRecords = SuperCheckQualityReview.objects.filter(auditor_date__range=[startdate, enddate])
                        else:
                            qualityRecords = SuperCheckQualityReview.objects.filter(project_name__icontains=request.GET["auditor_project_name"])
                            
                        uids_list = []
                        for value in qualityRecords:
                            uids_list.append(value.uid)
                        uids_list = tuple(uids_list)
                        # print(uids_list)
                        if len(uids_list) == 1:
                            uids_list = f"= {uids_list[0]}"
                        else:
                            uids_list = f"IN {uids_list}"
                            # sql = f"SELECT `quality_qualityreview`.`id`, `quality_qualityreview`.`uid`, `quality_qualityreview`.`project_name`, `quality_qualityreview`.`surveyor_name`, `quality_qualityreview`.`fr_name`, `quality_qualityreview`.`interview_date`, `quality_qualityreview`.`interview_duration`, `quality_qualityreview`.`quality_auditor`, `quality_qualityreview`.`auditor_date`, `quality_qualityreview`.`skipping`, `quality_qualityreview`.`knowledge`, `quality_qualityreview`.`recordings`, `quality_qualityreview`.`voice`, `quality_qualityreview`.`remarksSection_A`, `quality_qualityreview`.`skills`, `quality_qualityreview`.`answer`, `quality_qualityreview`.`convince`, `quality_qualityreview`.`remarksSection_B`, `quality_qualityreview`.`polite`, `quality_qualityreview`.`speech`, `quality_qualityreview`.`professional`, `quality_qualityreview`.`remarksSection_C`, `quality_qualityreview`.`variation`, `quality_qualityreview`.`survey`, `quality_qualityreview`.`variation_reason_id`, `quality_qualityreview`.`remarksSection_E_variation_1`, `quality_qualityreview`.`force_survey_reason_id`, `quality_qualityreview`.`remarksSection_E_force_survey_1`, `quality_qualityreview`.`movement`, `quality_qualityreview`.`tagging`, `quality_qualityreview`.`fake`, `quality_qualityreview`.`remarksSection_D`, `quality_qualityreview`.`totalscore`, `quality_qualityreview`.`created_at`, `quality_qualityreview`.`quality_auditor_id`, `quality_qualityreview`.`is_fake_form`, `quality_qualityreview`.`version`, `quality_qualityreview`.`question_skipping_incomplete_recordings`, `quality_qualityreview`.`remarksSection_A_skipping_incomplete_recordings_1`, `quality_qualityreview`.`remarksSection_A_skipping_incomplete_recordings_2`, `quality_qualityreview`.`question_skipping_incomplete_recordings_reason_id`, `quality_qualityreview`.`question_subject_knowledge`, `quality_qualityreview`.`remarksSection_B_question_subject_knowledge_1`, `quality_qualityreview`.`remarksSection_B_question_subject_knowledge_2`, `quality_qualityreview`.`question_subject_knowledge_reason_id`, `quality_qualityreview`.`voice_clarity`, `quality_qualityreview`.`remarksSection_C_voice_clarity_1`, `quality_qualityreview`.`remarksSection_C_voice_clarity_2`, `quality_qualityreview`.`voice_clarity_reason_id`, `quality_qualityreview`.`questioning_technique`, `quality_qualityreview`.`remarksSection_C_questioning_technique_1`, `quality_qualityreview`.`remarksSection_C_questioning_technique_2`, `quality_qualityreview`.`questioning_technique_reason_id`, `quality_qualityreview`.`convencing_skills`, `quality_qualityreview`.`remarksSection_C_convencing_skills_1`, `quality_qualityreview`.`remarksSection_C_convencing_skills_2`, `quality_qualityreview`.`convencing_skills_reason_id`, `quality_qualityreview`.`polite_courteous`, `quality_qualityreview`.`remarksSection_D_polite_courteous_1`, `quality_qualityreview`.`remarksSection_D_polite_courteous_2`, `quality_qualityreview`.`polite_courteous_reason_id`, `quality_qualityreview`.`rate_of_speech`, `quality_qualityreview`.`remarksSection_D_rate_of_speech_1`, `quality_qualityreview`.`remarksSection_D_rate_of_speech_2`, `quality_qualityreview`.`rate_of_speech_reason_id`, `quality_qualityreview`.`professionalism_energetic_enthusiastic`, `quality_qualityreview`.`remarksSection_D_professionalism_energetic_enthusiastic_1`, `quality_qualityreview`.`remarksSection_D_professionalism_energetic_enthusiastic_2`, `quality_qualityreview`.`professionalism_energetic_enthusiastic_reason_id` FROM `quality_qualityreview` WHERE `quality_qualityreview`.`uid` in {uids_list}"
                        sql = f"""
                            SELECT 
                                q.id,
                                q.uid,
                                q.project_name,
                                q.surveyor_name,
                                q.fr_name,
                                q.interview_date,
                                q.interview_duration,
                                q.quality_auditor,
                                q.auditor_date,
                                q.skipping,
                                q.knowledge,
                                q.recordings,
                                q.voice,
                                q.remarksSection_A,
                                q.skills,
                                q.answer,
                                q.convince,
                                q.remarksSection_B,
                                q.polite,
                                q.speech,
                                q.professional,
                                q.remarksSection_C,
                                q.variation,
                                q.survey,
                                variation_reason.issues AS variation_reason_issues,
                                q.remarksSection_E_variation_1,
                                force_survey_reason.issues AS force_survey_reason_issues,
                                q.remarksSection_E_force_survey_1,
                                q.movement,
                                q.tagging,
                                q.fake,
                                q.remarksSection_D,
                                q.totalscore,
                                q.created_at,
                                q.quality_auditor_id,
                                q.is_fake_form,
                                q.version,
                                q.question_skipping_incomplete_recordings,
                                q.remarksSection_A_skipping_incomplete_recordings_1,
                                q.remarksSection_A_skipping_incomplete_recordings_2,
                                skipping_reason.issues AS skipping_incomplete_recordings_issues,
                                q.question_subject_knowledge,
                                q.remarksSection_B_question_subject_knowledge_1,
                                q.remarksSection_B_question_subject_knowledge_2,
                                knowledge_reason.issues AS subject_knowledge_issues,
                                q.voice_clarity,
                                q.remarksSection_C_voice_clarity_1,
                                q.remarksSection_C_voice_clarity_2,
                                voice_reason.issues AS voice_clarity_issues,
                                q.questioning_technique,
                                q.remarksSection_C_questioning_technique_1,
                                q.remarksSection_C_questioning_technique_2,
                                questioning_reason.issues AS questioning_technique_issues,
                                q.convencing_skills,
                                q.remarksSection_C_convencing_skills_1,
                                q.remarksSection_C_convencing_skills_2,
                                convincing_reason.issues AS convencing_skills_issues,
                                q.polite_courteous,
                                q.remarksSection_D_polite_courteous_1,
                                q.remarksSection_D_polite_courteous_2,
                                polite_reason.issues AS polite_courteous_issues,
                                q.rate_of_speech,
                                q.remarksSection_D_rate_of_speech_1,
                                q.remarksSection_D_rate_of_speech_2,
                                speech_reason.issues AS rate_of_speech_issues,
                                q.professionalism_energetic_enthusiastic,
                                q.remarksSection_D_professionalism_energetic_enthusiastic_1,
                                q.remarksSection_D_professionalism_energetic_enthusiastic_2,
                                professional_reason.issues AS professionalism_energetic_enthusiastic_issues



                            FROM quality_qualityreview q

                            -- Join IssueList for each reason
                            LEFT JOIN quality_issuelist AS variation_reason ON q.variation_reason_id = variation_reason.id
                            LEFT JOIN quality_issuelist AS force_survey_reason ON q.force_survey_reason_id = force_survey_reason.id
                            LEFT JOIN quality_issuelist AS skipping_reason ON q.question_skipping_incomplete_recordings_reason_id = skipping_reason.id
                            LEFT JOIN quality_issuelist AS knowledge_reason ON q.question_subject_knowledge_reason_id = knowledge_reason.id
                            LEFT JOIN quality_issuelist AS voice_reason ON q.voice_clarity_reason_id = voice_reason.id
                            LEFT JOIN quality_issuelist AS questioning_reason ON q.questioning_technique_reason_id = questioning_reason.id
                            LEFT JOIN quality_issuelist AS convincing_reason ON q.convencing_skills_reason_id = convincing_reason.id
                            LEFT JOIN quality_issuelist AS polite_reason ON q.polite_courteous_reason_id = polite_reason.id
                            LEFT JOIN quality_issuelist AS speech_reason ON q.rate_of_speech_reason_id = speech_reason.id
                            LEFT JOIN quality_issuelist AS professional_reason ON q.professionalism_energetic_enthusiastic_reason_id = professional_reason.id

                            WHERE q.uid  {uids_list};
                            """
                        mycursor.execute(sql)

                        qualityrecords_auditor = mycursor.fetchall()
                        # print(qualityrecords_auditor,">>>>>>>>")
                    # print(qualityRecords.count(),"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<counttt")
                    return self.exportData_supercheck(qualityRecords,quality_aud = qualityrecords_auditor)



            elif("quality_auditor_id" in request.GET.keys()):

                # print("getQualityFilter:::",request.GET["quality_auditor_id"],"======",request.GET["auditor_date"])
                try:

                    if(request.user.user_employee.designation.department.name=="Quality"):
                        if(request.GET["quality_auditor_id"] == str(request.user.user_employee.employee_id)):
                            qualityRecords = None
                            if(request.GET["auditor_date"]!=""):
                                qualityRecords = SuperCheckQualityReview.objects.filter(quality_auditor_id=request.GET["quality_auditor_id"],auditor_date=request.GET["auditor_date"])
                            else:
                                qualityRecords = SuperCheckQualityReview.objects.filter(quality_auditor_id=request.GET["quality_auditor_id"])
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
                                'htmlfilename': 'supercheck_templates/capi_supercheck.html',
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
                        qualityRecords = SuperCheckQualityReview.objects.filter(
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
                        'htmlfilename': 'supercheck_templates/capi_supercheck.html',
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
            # print(request.GET["hourly_auditor_name"],"<<<<<<<<hourly auditor")
            params = None;
            if(request.GET["hourly_auditor_name"] != "default"):
                params = request.GET["hourly_auditor_name"].split("$-$")[1];
            else:
                params = request.GET["hourly_auditor_name"]
            # print(request.GET)
            return self.hourlyReports(params,request.GET["Pickdate"])

        else:
            # print("pppf calledddd*v2")
            data = {
                'user': request.user.user_employee,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                # 'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'supercheck_templates/capi_supercheck.html',
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
                    "submitted_uids_status":uid_submitted

            }
            return render(request, "index.html", data);

    def post(self,request):
        cnx2 = _get_surveygenius_connection()


        mycursor = cnx2.cursor()
        
        from django.db.models import FloatField, F, Sum, Count, ExpressionWrapper, Value, Case, When,Q   #type: ignore


        msg = ""

        # if ("mis_match_uid" in request.POST.keys()):
        #     if (QualityReviewMismatch.objects.filter(uid=int(request.POST["mis_match_uid"])).count() == 0):
        #         QualityReviewMismatch.objects.create(
        #             uid=int(request.POST["mis_match_uid"]),
        #             project_name=request.POST["mis_project_name"],
        #             surveyor_name=request.POST["mis_surveyor_id"]+"-"+request.POST["mis_surveyor_name"],
        #             fr_name=request.POST["mis_tl_name"],
        #             interview_date=request.POST["mis_interview_date"],
        #             # interview_date=datetime.datetime.strptime(str(request.POST["mis_interview_date"]), '"%Y-%m-%d"').strftime("%Y-%m-%d"),
        #             interview_duration=request.POST["mis_interview_duration"],
        #             quality_auditor=request.user.first_name + " " + request.user.last_name,
        #             auditor_date=request.POST["mis_audit_date"],
        #             review=request.POST["mis_match_reason_review"]
        #         )
        #         msg = "Submitted"
        #     else:
        #         print("duplicate entryyy")
        #         msg = "Duplicated Entry Please verify"

        # else:

        #     # print(request.POST.keys())

        #     data = {}
        #     msg=""


        if ("mis_match_uid" not in request.POST.keys()):
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


            isFake = False
            # print(N,"nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
            if(int(N)<0):
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

            score_A_B_C = float(A) + float(D) + float(G) + float(H) + float(I)
        score_D=0
        if (isFake==True):
            score_D=0
            # print("truuuuuuuuuu")
            total_score=0
        else:
            score_D = float(J) + float(K) + float(L) + float(M) + float(N) + float(O) + float(P) + float(Q)

            total_score = ((score_A_B_C + score_D)/40)*100
            # print("total scoreee",datetime.datetime.now(),"========")

            # print(datetime.datetime.now() - datetime.timedelta(hours=1))

            # ================================================================= #
          
            # ================================================================= #

            # print(request.POST,"jkhakdjhfukahkjhkjhkahkfh")

        
        # print(request.POST,"after")

        
        ### CREATION OF QUALITYREVIEW OF SUPERCHECK

        # sql = f"select id from IssueList where issue_id = {request.POST["section_A_question_skipping_issue"]}"

        # results = mycursor.fetchall()
        # question_skipping_incomplete_recordings_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_B_question_questionnaire_subject_issue"]}"

        # results = mycursor.fetchall()
        # question_subject_knowledge_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_C_question_voice_clarity_issue"]}"

        # results = mycursor.fetchall()
        # voice_clarity_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_C_question_questioning_technique_issue"]}"

        # results = mycursor.fetchall()
        # questioning_technique_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_C_question_convincing_skills_issue"]}"

        # results = mycursor.fetchall()
        # convencing_skills_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_D_question_polite_courteous_issue"]}"

        # results = mycursor.fetchall()
        # polite_courteous_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_D_question_rate_speech_issue"]}"

        # results = mycursor.fetchall()
        # rate_of_speech_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_D_question_professional_issue"]}"

        # results = mycursor.fetchall()
        # professionalism_energetic_enthusiastic_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_E_question_variation_issue"]}"

        # results = mycursor.fetchall()
        # variation_reason = results

        # sql = f"select id from IssueList where issue_id = {request.POST["section_E_question_force_survey_issue"]}"

        # results = mycursor.fetchall()
        # force_survey_reason = results
        if(SuperCheckQualityReview.objects.filter(uid=int(request.POST["uid_id"])).count()==0):
            SuperCheckQualityReview.objects.create(
                uid=int(request.POST["uid_id"]),
                project_name=request.POST["project_name"],
                surveyor_name=request.POST["surveyor_id"]+"-"+request.POST["surveyor_name"],
                fr_name=request.POST["fr_name"],

                interview_date=datetime.datetime.strptime(request.POST["interview_date"], '%d-%b-%Y').strftime("%Y-%m-%d"),
                # interview_date=datetime.datetime(request.POST["interview_date"][:10]).strftime("%Y-%m-%d"),
                interview_duration=request.POST["interview_duration"],
                quality_auditor=request.user.first_name +" "+ request.user.last_name,
                auditor_date = datetime.datetime.strptime(request.POST["auditing_date"], "%d-%m-%Y").strftime("%Y-%m-%d"),

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
            # print("inserted")
            msg = "Submitted"

        else:
                    # print("duplicate entryyy")
                    msg = "Duplicated Entry Please verify"
        


        active_projects_list = SuperCheckQualityReview.objects.values("project_name").distinct();
        auditor_list = SuperCheckQualityReview.objects.values("quality_auditor","quality_auditor_id").distinct();
        # auditor_count = SuperCheckQualityReview.objects.filter(created_at=datetime.today().strftime("%Y-%m-%d")).count()
        # print(auditor_count)
        today_min = django_timezone.make_aware(datetime.datetime.combine(datetime.date.today(), datetime.time.min))
        today_max = django_timezone.make_aware(datetime.datetime.combine(datetime.date.today(), datetime.time.max))
        auditor_count = SuperCheckQualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).count()
        # print(auditor_count)
        quality_project_wise_records = SuperCheckQualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).values("project_name") \
            .annotate(Count('project_name'))
        active_projects_list = SuperCheckQualityReview.objects.values("project_name").distinct();
        auditor_list = SuperCheckQualityReview.objects.values("quality_auditor", "quality_auditor_id").distinct();
        sectionAIssueList = IssueList.objects.filter(section="section_A").values("issue_id", "issues","related_question")
        sectionBIssueList = IssueList.objects.filter(section="section_B").values("issue_id", "issues","related_question")
        sectionCIssueList = IssueList.objects.filter(section="section_C").values("issue_id", "issues","related_question")
        sectionDIssueList = IssueList.objects.filter(section="section_D").values("issue_id", "issues","related_question")
        sectionEIssueList = IssueList.objects.filter(section="section_E").values("issue_id", "issues","related_question")

        submitted_uids_list = SuperCheckQualityReview.objects.filter(uid=request.GET["uid"])

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
            'htmlfilename': 'supercheck_templates/capi_supercheck.html',
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
            "submitted_uids_status":uid_submitted
            
        }
        return render(request, "index.html", data)






    def hourlyReports(self,params,selected_date):
        # print(selected_date,"====",selected_date)
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
            # print(x,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(new_new_date,"-",datetime.timedelta(hours=1),"=",result_date)

            hourlyJson["starting_hour"] = result_date
            hourlyJson["ending_hour"] = new_new_date



            # print(selected_date,"=======")

            hourlyBasedData = None
            if(params=="default"):
                # print("default called")
                # print(result_date, "*******", new_new_date)
                hourlyBasedData = SuperCheckQualityReview.objects.filter(created_at__range=(result_date, new_new_date),auditor_date=selected_date)


            else:
                # print("not default called")
                # print(result_date, "*******" ,new_new_date)
                hourlyBasedData = SuperCheckQualityReview.objects.filter(created_at__range=(result_date, new_new_date),auditor_date=selected_date, quality_auditor_id=params)



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
            worksheet.write(row, 4, str(data.surveyor_name))
            worksheet.write(row, 5, str(data.fr_name))
            worksheet.write(row, 6, str(data.interview_date))
            worksheet.write(row, 7, str(data.interview_duration))
            worksheet.write(row, 8, str(data.quality_auditor))
            worksheet.write(row, 9, str(data.auditor_date))

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
            worksheet.write(row, 53, str(data.created_at))
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

        #### connection with 32
        cnx2 = _get_surveygenius_connection()


        mycursor = cnx2.cursor()

        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        # print(type,"<<<<,type")
        if(type=="fetch"):
            # print('fetch')
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

            # worksheet.write(0, 24, "Percent Section A total_quality_score % ")
            # worksheet.write(0, 25, "Percent Section B total_quality_score % ")
            # worksheet.write(0, 26, "Percent Section C total_quality_score % ")




            row = row + 1
            col = 0

            ################################################# For Surveyor_Count Start####################################################

            interview_startdate = None
            interview_enddate = None
            dates_arr = []
            if ("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys()   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                interview_startdate = str(request.GET["interview_startdate"])
                # print(interview_startdate)
                interview_enddate = str(request.GET["interview_enddate"])
                # print(interview_enddate)
                delta = datetime.datetime.strptime(interview_enddate, '%Y-%m-%d') - datetime.datetime.strptime(
                    interview_startdate, '%Y-%m-%d')
                # print(delta)  # as timedelta
                
                # print('okkk')

                for i in range(delta.days + 1):
                    day = datetime.datetime.strptime(interview_startdate, '%Y-%m-%d') + datetime.timedelta(days=i)
                    # print(day)
                    # start_vall = '"date": "%s"' % (
                        # datetime.datetime.strptime(str(day.date()), '%Y-%m-%d').strftime('%d-%b-%Y'))
                    # print(start_vall)
                    dates_arr.append(day)


            project_id_val = 0
            if ("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"] != "default"):

                sql = f"SELECT id FROM `mainapp_project` WHERE name = '{request.GET['auditor_project_name']}'"
                mycursor.execute(sql)
                results = mycursor.fetchall()
                # projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                project_id_val = results[0][0]

            ################################################ For Surveyor_Count ####################################################

            # print("data",data)
            for data in data:

                ################################################# For Surveyor_Count Start####################################################

                try:
                    surveyor_id_val = data["surveyor_name"].split("-")[0]
                    
                except Exception as e:
                    surveyor_id_val = data["surveyor_name"].split("(")[1][:len(data["surveyor_name"].split("(")[1])-1]

                # print(surveyor_id_val, "====idd")

                # if type(surveyor_id_val) == 

                count_total = 0
                # print(data["surveyor_name"])
                if (len(data["surveyor_name"].split("-")) > 1   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                    # print('hello')
                    if (len(dates_arr) > 0):
                        # print("hello2")
                        for dateVal in dates_arr:
                            if (project_id_val != 0):
                                # print("calling surveyresponse*******1")
                                dateVal = dateVal.date()
                                sql = (
                                    f"SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) "
                                    f"FROM `mainapp_surveyresponse` "
                                    f"WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} "
                                    f"AND `mainapp_surveyresponse`.`params` LIKE '%{dateVal}%' "
                                    f"AND `mainapp_surveyresponse`.`project_id` = {project_id_val})"
                                )

                                # sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}% AND `mainapp_surveyresponse`.`project_id` = {project_id_val})'
                                mycursor.execute(sql)
                                survey_response_obj = mycursor.fetchall()
                                
                                # print(survey_response_obj[0][0])
                                count_total = count_total + survey_response_obj[0][0]
                                # print(count_total,"count_total")
                            else:
                                # print("calling surveyresponse*******2")
                                # datetime_obj = datetime.strptime(dateVal, 
                                #  "%d%b%Y%H%M%S")
                                dateVal = dateVal.date()
                                # dateVal = dateVal.split(" ")[0]
                                sql = (
                                    f"SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) "
                                    f"FROM `mainapp_surveyresponse` "
                                    f"WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} "
                                    f"AND `mainapp_surveyresponse`.`params` LIKE '%{dateVal}%' "
                                    f"AND `mainapp_surveyresponse`.`project_id` = {project_id_val})"
                                )
                                # sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}%'
                                mycursor.execute(sql)
                                survey_response_obj = mycursor.fetchall()
                                count_total = count_total + survey_response_obj[0][0]
                                # print(count_total,"count_total>>>")

                # print(data)

                            # print(survey_response_obj.count(),"coount")

                ################################################ For Surveyor_Count END####################################################

                worksheet.write(row, 1, str(data["surveyor_name"]))

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
            # print("shortttttt:::",request)
            row = 0
            col = 0
            worksheet.write(0, 1, "surveyor_name")
          

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

            # worksheet.write(0, 24, "Percent Section A total_quality_score % ")
            # worksheet.write(0, 25, "Percent Section B total_quality_score % ")
            # worksheet.write(0, 26, "Percent Section C total_quality_score % ")

            row = row + 1
            col = 0



            ################################################# For Surveyor_Count Start####################################################

            interview_startdate=None
            interview_enddate=None
            dates_arr = []
            if("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys()  and request.GET['interview_enddate']!="" and request.GET['interview_startdate']!=""):

                interview_startdate = str(request.GET["interview_startdate"])
                interview_enddate = str(request.GET["interview_enddate"])
                delta = datetime.datetime.strptime(interview_enddate, '%Y-%m-%d') -datetime.datetime.strptime(interview_startdate, '%Y-%m-%d')  # as timedelta

                for i in range(delta.days + 1):
                    day = datetime.datetime.strptime(interview_startdate, '%Y-%m-%d') + datetime.timedelta(days=i)
                    # start_vall = '"date": "%s"' % (datetime.datetime.strptime(str(day.date()), '%Y-%m-%d').strftime('%d-%b-%Y'))
                    # dates_arr.append(start_vall)
                    dates_arr.append(day)



            project_id_val=0
            if("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"]!="default"):
                sql = f"SELECT id FROM `mainapp_project` WHERE name = '{request.GET['auditor_project_name']}'"
                mycursor.execute(sql)
                results = mycursor.fetchall()
                # projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                project_id_val = results[0][0]

            ################################################ For Surveyor_Count ####################################################

            for data in data:

                ################################################# For Surveyor_Count Start####################################################

                try:
                    surveyor_id_val = data["surveyor_name"].split("-")[0]
                    
                except Exception as e:
                    surveyor_id_val = data["surveyor_name"].split("(")[1][:len(data["surveyor_name"].split("(")[1])-1]

                # surveyor_id_val = data["surveyor_name"].split("-")[0]

                # print(surveyor_id_val,"====idd====",project_id_val)


                count_total = 0
                if(len(data["surveyor_name"].split("-"))>1 and "interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                    # print("surrrrrrr:::",dates_arr)
                    if(len(dates_arr)>0):
                        for dateVal in dates_arr:
                            # print(dateVal)
                            if(project_id_val!=0):
                                # print(Employee.objects.get(employee_id=surveyor_id_val),"======valll")

                                sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}% AND `mainapp_surveyresponse`.`project_id` = {project_id_val})'
                                mycursor.execute(sql)
                                survey_response_obj = mycursor.fetchcall()
                                
                                count_total = count_total + survey_response_obj[0][0]
                                # print(count_total,"count_total")
                            else:
                                # print("callling elsee*")
                                # dateVal = dateVal.date()
                                dateVal = dateVal.date()
                                # dateVal = dateVal.split(" ")[0]
                                sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}%'
                                mycursor.execute(sql)
                                survey_response_obj = mycursor.fetchcall()
                                count_total = count_total + survey_response_obj[0][0]
                                # count_total = count_total + survey_response_obj.count()
                                # print(count_total,"count_total>>>")

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

            workbook.close()
            output.seek(0)

        workbook.close()
        output.seek(0)  # Go to the start of the BytesIO buffer

        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={str(date.today())}_hourly.xlsx'
        import gc
        gc.collect()

        return response




      #### export auditor with supercheck

    def exportData_auditor_supercheck(self,data,type,request,quality_aud_data):

        #### connection with 32
        cnx2 = _get_surveygenius_connection()


        mycursor = cnx2.cursor()

        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        # print(type,"<<<<,type")
        if(type=="fetch"):
            # print('fetch')
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
            worksheet.write(0, 24, "auditor_qualityscore % ")

            # worksheet.write(0, 24, "Percent Section A total_quality_score % ")
            # worksheet.write(0, 25, "Percent Section B total_quality_score % ")
            # worksheet.write(0, 26, "Percent Section C total_quality_score % ")




            row = row + 1
            col = 0

            ################################################# For Surveyor_Count Start####################################################

            interview_startdate = None
            interview_enddate = None
            dates_arr = []
            if ("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys()   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                interview_startdate = str(request.GET["interview_startdate"])
                # print(interview_startdate)
                interview_enddate = str(request.GET["interview_enddate"])
                # print(interview_enddate)
                delta = datetime.datetime.strptime(interview_enddate, '%Y-%m-%d') - datetime.datetime.strptime(
                    interview_startdate, '%Y-%m-%d')
                # print(delta)  # as timedelta
                
                # print('okkk')

                for i in range(delta.days + 1):
                    day = datetime.datetime.strptime(interview_startdate, '%Y-%m-%d') + datetime.timedelta(days=i)
                    # print(day)
                    # start_vall = '"date": "%s"' % (
                        # datetime.datetime.strptime(str(day.date()), '%Y-%m-%d').strftime('%d-%b-%Y'))
                    # print(start_vall)
                    dates_arr.append(day)


            project_id_val = 0
            if ("auditor_project_name" in request.GET.keys() and request.GET['auditor_project_name'] != "default"):

                sql = f"SELECT id FROM `mainapp_project` WHERE name = '{request.GET['auditor_project_name']}'"
                mycursor.execute(sql)
                results = mycursor.fetchall()
                # projectId = Project.objects.get(name=request.GET['auditor_project_name'])
                project_id_val = results[0][0]

            ################################################ For Surveyor_Count ####################################################

            # print("data",data)
            for data in data:

                    ################################################# For Surveyor_Count Start####################################################
                for auditor_data in quality_aud_data:
                    
                    try:
                        surveyor_id_val = data["surveyor_name"].split("-")[0]
                        
                    except Exception as e:
                        surveyor_id_val = data["surveyor_name"].split("(")[1][:len(data["surveyor_name"].split("(")[1])-1]

                    # print(surveyor_id_val, "====idd")


                    try:
                        auditor_data_surveyor_id = auditor_data[0].split("-")[0]

                    except Exception as e:
                        auditor_data_surveyor_id = auditor_data[0].split("(")[1][:len(auditor_data["surveyor_name"].split("(")[1])-1]

                    if surveyor_id_val == auditor_data_surveyor_id:

                    # if type(surveyor_id_val) == 

                        count_total = 0
                        # print(data["surveyor_name"])
                        if (len(data["surveyor_name"].split("-")) > 1   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                            # print('hello')
                            if (len(dates_arr) > 0):
                                # print("hello2")
                                for dateVal in dates_arr:
                                    if (project_id_val != 0):
                                        # print("calling surveyresponse*******1")
                                        dateVal = dateVal.date()
                                        sql = (
                                            f"SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) "
                                            f"FROM `mainapp_surveyresponse` "
                                            f"WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} "
                                            f"AND `mainapp_surveyresponse`.`params` LIKE '%{dateVal}%' "
                                            f"AND `mainapp_surveyresponse`.`project_id` = {project_id_val})"
                                        )

                                        # sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}% AND `mainapp_surveyresponse`.`project_id` = {project_id_val})'
                                        mycursor.execute(sql)
                                        survey_response_obj = mycursor.fetchall()
                                        
                                        # print(survey_response_obj[0][0])
                                        count_total = count_total + survey_response_obj[0][0]
                                        # print(count_total,"count_total")
                                    else:
                                        # print("calling surveyresponse*******2")
                                        # datetime_obj = datetime.strptime(dateVal, 
                                        #  "%d%b%Y%H%M%S")
                                        dateVal = dateVal.date()
                                        # dateVal = dateVal.split(" ")[0]
                                        sql = (
                                            f"SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) "
                                            f"FROM `mainapp_surveyresponse` "
                                            f"WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} "
                                            f"AND `mainapp_surveyresponse`.`params` LIKE '%{dateVal}%' "
                                            f"AND `mainapp_surveyresponse`.`project_id` = {project_id_val})"
                                        )
                                        # sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}%'
                                        mycursor.execute(sql)
                                        survey_response_obj = mycursor.fetchall()
                                        count_total = count_total + survey_response_obj[0][0]
                                        # print(count_total,"count_total>>>")

                        # print(data)

                                    # print(survey_response_obj.count(),"coount")

                        ################################################ For Surveyor_Count END####################################################

                        worksheet.write(row, 1, str(data["surveyor_name"]))

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
                        worksheet.write(row, 24 ,int(round(float(str(auditor_data[-2])))))




                        row = row + 1


            workbook.close()
            output.seek(0)
        elif(type=="detailed_summary"):
            # print("shortttttt:::",request)
            row = 0
            col = 0
            worksheet.write(0, 1, "surveyor_name")
          

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

            # worksheet.write(0, 24, "Percent Section A total_quality_score % ")
            # worksheet.write(0, 25, "Percent Section B total_quality_score % ")
            # worksheet.write(0, 26, "Percent Section C total_quality_score % ")

            row = row + 1
            col = 0



            ################################################# For Surveyor_Count Start####################################################

            interview_startdate=None
            interview_enddate=None
            dates_arr = []
            if("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys()  and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                interview_startdate = str(request.GET["interview_startdate"])
                interview_enddate = str(request.GET["interview_enddate"])
                delta = datetime.datetime.strptime(interview_enddate, '%Y-%m-%d') -datetime.datetime.strptime(interview_startdate, '%Y-%m-%d')  # as timedelta

                for i in range(delta.days + 1):
                    day = datetime.datetime.strptime(interview_startdate, '%Y-%m-%d') + datetime.timedelta(days=i)
                    # start_vall = '"date": "%s"' % (datetime.datetime.strptime(str(day.date()), '%Y-%m-%d').strftime('%d-%b-%Y'))
                    # dates_arr.append(start_vall)
                    dates_arr.append(day)



            project_id_val=0
            if("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"]!="default"):
                sql = f"SELECT id FROM `mainapp_project` WHERE name = '{request.GET['auditor_project_name']}'"
                mycursor.execute(sql)
                results = mycursor.fetchall()
                # projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                project_id_val = results[0][0]

            ################################################ For Surveyor_Count ####################################################

            for data in data:

                ################################################# For Surveyor_Count Start####################################################

                try:
                    surveyor_id_val = data["surveyor_name"].split("-")[0]
                    
                except Exception as e:
                    surveyor_id_val = data["surveyor_name"].split("(")[1][:len(data["surveyor_name"].split("(")[1])-1]

                # surveyor_id_val = data["surveyor_name"].split("-")[0]

                # print(surveyor_id_val,"====idd====",project_id_val)


                count_total = 0
                if(len(data["surveyor_name"].split("-"))>1 and "interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                    # print("surrrrrrr:::",dates_arr)
                    if(len(dates_arr)>0):
                        for dateVal in dates_arr:
                            # print(dateVal)
                            if(project_id_val!=0):
                                # print(Employee.objects.get(employee_id=surveyor_id_val),"======valll")

                                sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}% AND `mainapp_surveyresponse`.`project_id` = {project_id_val})'
                                mycursor.execute(sql)
                                survey_response_obj = mycursor.fetchcall()
                                
                                count_total = count_total + survey_response_obj[0][0]
                                # print(count_total,"count_total")
                            else:
                                # print("callling elsee*")
                                # dateVal = dateVal.date()
                                dateVal = dateVal.date()
                                # dateVal = dateVal.split(" ")[0]
                                sql = f'SELECT COUNT(DISTINCT `mainapp_surveyresponse`.`uid`) FROM `mainapp_surveyresponse` WHERE (`mainapp_surveyresponse`.`surveyor_id` = {surveyor_id_val} AND `mainapp_surveyresponse`.`params` LIKE %{dateVal}%'
                                mycursor.execute(sql)
                                survey_response_obj = mycursor.fetchcall()
                                count_total = count_total + survey_response_obj[0][0]
                                # count_total = count_total + survey_response_obj.count()
                                # print(count_total,"count_total>>>")

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

            workbook.close()
            output.seek(0)

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
        # print(data)
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
                    # print(hourlyData.created_at.hour)
                    if(hourlyData.created_at.hour in hour_count.keys()):
                        hour_count[hourlyData.created_at.hour] = hour_count[hourlyData.created_at.hour]+1;
                    else:
                        hour_count[hourlyData.created_at.hour] = 1;
                # print(hour_count)

                for x in hour_count.keys():
                    # print(hour_count[x],"====hour::",x,"   col:::",hourlyData.created_at.hour+2)
                    worksheet.write(row, x+2 , int(str(hour_count[x])))

            row = row + 1

        


        workbook.close();
        output.seek(0)

        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={selected_date}_hourly.xlsx'
        import gc
        gc.collect()

        return response
    

     #### exportdata supercheck    
    def exportData_supercheck(self,data,quality_aud):
        output = io.BytesIO()  # Use BytesIO for binary data, which is required for xlsxwriter
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('output')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#87CEEB',  # Sky blue
            'align': 'center',
            'valign': 'vcenter'
        })

        row = 0
        col = 0
        
        worksheet.write(0,1, "Supercheck Date".title(), header_format)
        worksheet.write(0,2, "Superchecker Name".title(), header_format)
        worksheet.write(0,3, "UID".title(), header_format)
        worksheet.write(0,4, "Project_Name".title(), header_format)
        worksheet.write(0,5, "Surveyor_Name".title(), header_format)
        worksheet.write(0,6, "FR_Name".title(), header_format)
        worksheet.write(0,7, "Interview_Date".title(), header_format)
        worksheet.write(0,8, "Interview_Duration".title(), header_format)
        worksheet.write(0,9, "quality_auditor".title(), header_format)
        worksheet.write(0,10, "auditor_date".title(), header_format)
        worksheet.write(0,11, "Question Skipping/ Incomplete Recording".title(), header_format)
        worksheet.write(0,12, "remarks_Question Skipping/ Incomplete Recording_reason".title(), header_format)
        worksheet.write(0,13, "remarks_A_1".title(), header_format)
        worksheet.write(0,14, "remarks_A_2".title(), header_format)
        worksheet.write(0,15, "Questionnaire / Subject Knowledge".title(), header_format)
        worksheet.write(0,16, "remarks_Questionnaire / Subject Knowledge_reason".title(), header_format)
        worksheet.write(0,17, "remarks_B_1".title(), header_format)
        worksheet.write(0,18, "remarks_B_2".title(), header_format)
        worksheet.write(0,19, "Voice Clarity".title(), header_format)
        worksheet.write(0,20, "Voice Clarity_reason".title(), header_format)
        worksheet.write(0,21, "remarks_C_voice_clarity_1".title(), header_format)
        worksheet.write(0,22, "remarks_C_voice_clarity_2".title(), header_format)
        worksheet.write(0,23, "Questioning Technique".title(), header_format)
        worksheet.write(0,24, "Questioning Technique_reason".title(), header_format)
        worksheet.write(0,25, "remarks_C_question_technique_1".title(), header_format)
        worksheet.write(0,26, "remarks_C_question_technique_2".title(), header_format)
        worksheet.write(0,27, "Convincing skills".title(), header_format)
        worksheet.write(0,28, "Convincing skills_reason".title(), header_format)
        worksheet.write(0,29, "remarks_C_convencing_skills_1".title(), header_format)
        worksheet.write(0,30, "remarks_C_convencing_skills_2".title(), header_format)
        worksheet.write(0,31, "Being Polite & courteous".title(), header_format)
        worksheet.write(0,32, "Being Polite & courteous_reason".title(), header_format)
        worksheet.write(0,33, "remarksSection_D_polite_courteous_1".title(), header_format)
        worksheet.write(0,34, "remarksSection_D_polite_courteous_2".title(), header_format)
        worksheet.write(0,35, "Rate of Speech".title(), header_format)
        worksheet.write(0,36, "Rate of Speech_reason".title(), header_format)
        worksheet.write(0,37, "remarksSection_D_rate_of_speech_1".title(), header_format)
        worksheet.write(0,38, "remarksSection_D_rate_of_speech_2".title(), header_format)
        worksheet.write(0,39, "Professionalism/ Energetic/Enthusiastic".title(), header_format)
        worksheet.write(0,40, "Professionalism/ Energetic/Enthusiastic_reason".title(), header_format)
        worksheet.write(0,41, "remarksSection_D_professionalism_energetic_enthusiastic_1".title(), header_format)
        worksheet.write(0,42, "remarksSection_D_professionalism_energetic_enthusiastic_2".title(), header_format)
        worksheet.write(0,43, "variation".title(), header_format)
        worksheet.write(0,44, "variation_reason".title(), header_format)
        worksheet.write(0,45, "remarksSectionE_variation_1".title(), header_format)
        worksheet.write(0,46, "survey".title(), header_format)
        worksheet.write(0,47, "survey_reason".title(), header_format)
        worksheet.write(0,48, "remarksSectionE_force_survey_1".title(), header_format)
        worksheet.write(0,49, "movement".title(), header_format)
        worksheet.write(0,50, "tagging".title(), header_format)
        worksheet.write(0,51, "fake".title(), header_format)
        worksheet.write(0,52, "remarks_D".title(), header_format)
        worksheet.write(0,53, "total_score".title(), header_format)
        worksheet.write(0,54, "created_date".title(), header_format)
        worksheet.write(0,55, "auditor_id".title(), header_format)

        row = row + 1
        col = 0

    

        ### data for loopsssss report       
        for data in data:
            for audit_data in quality_aud:
                if data.uid != audit_data[1]:
                    pass
                else:
                    ### Auditors_data
                    worksheet.write(row,1, str(""))
                    worksheet.write(row,2, str(""))
                    worksheet.write(row,3, str(audit_data[1]))
                    worksheet.write(row,4, str(audit_data[2]))
                    worksheet.write(row,5, str(audit_data[3]))
                    worksheet.write(row,6, str(audit_data[4]))
                    worksheet.write(row,7, str(audit_data[5]))
                    worksheet.write(row,8, str(audit_data[6]))
                    worksheet.write(row,9, str(audit_data[7]))
                    worksheet.write(row,10, str(audit_data[8]))
                    worksheet.write(row,11, round(float(str(audit_data[37])),2))
                    worksheet.write(row,12, str(audit_data[40]))
                    worksheet.write(row,13, str(audit_data[38]))
                    worksheet.write(row,14, str(audit_data[39]))
                    worksheet.write(row,15, round(float(str(audit_data[41])),2))
                    worksheet.write(row,16, str(audit_data[44]))
                    worksheet.write(row,17, str(audit_data[42]))
                    worksheet.write(row,18, str(audit_data[43]))
                    worksheet.write(row,19, round(float(str(audit_data[45])),2))
                    worksheet.write(row,20, str(audit_data[48]))
                    worksheet.write(row,21, str(audit_data[46]))
                    worksheet.write(row,22, str(audit_data[47]))
                    worksheet.write(row,23, round(float(str(audit_data[49])),2))
                    worksheet.write(row,24, str(audit_data[52]))
                    worksheet.write(row,25, str(audit_data[50]))
                    worksheet.write(row,26, str(audit_data[51]))
                    worksheet.write(row,27, round(float(str(audit_data[53])),2))
                    worksheet.write(row,28, str(audit_data[56]))
                    worksheet.write(row,29, str(audit_data[54]))
                    worksheet.write(row,30, str(audit_data[55]))
                    worksheet.write(row,31, round(float(str(audit_data[57])),2))
                    worksheet.write(row,32, str(audit_data[60]))
                    worksheet.write(row,33, str(audit_data[58]))
                    worksheet.write(row,34, str(audit_data[59]))
                    worksheet.write(row,35, round(float(str(audit_data[61])),2))
                    worksheet.write(row,36, str(audit_data[64]))
                    worksheet.write(row,37, str(audit_data[62]))
                    worksheet.write(row,38, str(audit_data[63]))
                    worksheet.write(row,39, round(float(str(audit_data[65])),2))
                    worksheet.write(row,40, str(audit_data[68]))
                    worksheet.write(row,41, str(audit_data[66]))
                    worksheet.write(row,42, str(audit_data[67]))
                    worksheet.write(row,43, round(float(str(audit_data[22])),2))
                    worksheet.write(row,44, str(audit_data[24]))
                    worksheet.write(row,45, str(audit_data[25]))
                    worksheet.write(row,46, round(float(str(audit_data[23])),2))
                    worksheet.write(row,47, str(audit_data[26]))
                    worksheet.write(row,48, str(audit_data[27]))
                    worksheet.write(row,49, round(float(str(audit_data[28])),2))
                    worksheet.write(row,50, round(float(str(audit_data[29])),2))
                    worksheet.write(row,51, round(float(str(audit_data[30])),2))
                    worksheet.write(row,52, str(audit_data[31]))
                    worksheet.write(row,53, int(round(float(str(audit_data[32])))))
                    worksheet.write(row,54, str(audit_data[33]))
                    worksheet.write(row,55, str(""))



                    row = row + 1



                    ####supercheck data
                    # print(data.id,"<<<<< ")
                    # worksheet.write(row, 1, str(data.id))
                    worksheet.write(row,1, str(data.auditor_date))
                    worksheet.write(row,2, str(data.quality_auditor))
                    worksheet.write(row,3, str(data.uid))
                    worksheet.write(row,4, str(data.project_name))
                    worksheet.write(row,5, str(data.surveyor_name))
                    worksheet.write(row,6, str(data.fr_name))
                    worksheet.write(row,7, str(data.interview_date))
                    worksheet.write(row,8, str(data.interview_duration))
                    worksheet.write(row,9, str(data.quality_auditor))
                    worksheet.write(row,10, str(data.auditor_date))
                    worksheet.write(row,11, round(float(str(data.question_skipping_incomplete_recordings)),2))
                    worksheet.write(row,12, str(data.question_skipping_incomplete_recordings_reason.related_question))
                    worksheet.write(row,13, str(data.remarksSection_A_skipping_incomplete_recordings_1))
                    worksheet.write(row,14, str(data.remarksSection_A_skipping_incomplete_recordings_2))
                    worksheet.write(row,15, round(float(str(data.question_subject_knowledge)),2))
                    worksheet.write(row,16,str(data.question_subject_knowledge_reason.related_question))
                    worksheet.write(row,17, str(data.remarksSection_B_question_subject_knowledge_1))
                    worksheet.write(row,18, str(data.remarksSection_B_question_subject_knowledge_2))
                    worksheet.write(row,19, round(float(str(data.voice_clarity)),2))
                    worksheet.write(row,20, str(data.voice_clarity_reason.related_question))
                    worksheet.write(row,21, str(data.remarksSection_C_voice_clarity_1))
                    worksheet.write(row,22, str(data.remarksSection_C_voice_clarity_2))
                    worksheet.write(row,23, round(float(str(data.questioning_technique)),2))
                    worksheet.write(row,24, str(data.questioning_technique_reason.related_question))
                    worksheet.write(row,25, str(data.remarksSection_C_questioning_technique_1))
                    worksheet.write(row,26, str(data.remarksSection_C_questioning_technique_2))
                    worksheet.write(row,27, round(float(str(data.convencing_skills)),2))
                    worksheet.write(row,28, str(data.convencing_skills_reason.related_question))
                    worksheet.write(row,29, str(data.remarksSection_C_convencing_skills_1))
                    worksheet.write(row,30, str(data.remarksSection_C_convencing_skills_2))
                    worksheet.write(row,31, round(float(str(data.polite_courteous)),2))
                    worksheet.write(row,32, str(data.polite_courteous_reason.related_question))
                    worksheet.write(row,33, str(data.remarksSection_D_polite_courteous_1))
                    worksheet.write(row,34, str(data.remarksSection_D_polite_courteous_2))
                    worksheet.write(row,35, round(float(str(data.rate_of_speech)),2))
                    worksheet.write(row,36, str(data.rate_of_speech_reason.related_question))
                    worksheet.write(row,37, str(data.remarksSection_D_rate_of_speech_1))
                    worksheet.write(row,38, str(data.remarksSection_D_rate_of_speech_2))
                    worksheet.write(row,39, round(float(str(data.professionalism_energetic_enthusiastic)),2))
                    worksheet.write(row,40, str(data.professionalism_energetic_enthusiastic_reason.related_question))
                    worksheet.write(row,41, str(data.remarksSection_D_professionalism_energetic_enthusiastic_1))
                    worksheet.write(row,42, str(data.remarksSection_D_professionalism_energetic_enthusiastic_2))
                    worksheet.write(row,43, round(float(str(data.variation)),2))
                    worksheet.write(row,44, (str(data.variation_reason.related_question)))
                    worksheet.write(row,45, str(data.remarksSection_E_variation_1))
                    worksheet.write(row,46, round(float(str(data.survey)),2))
                    worksheet.write(row,47, (str(data.force_survey_reason.related_question)))
                    worksheet.write(row,48, str(data.remarksSection_E_force_survey_1))
                    worksheet.write(row,49, round(float(str(data.movement)),2))
                    worksheet.write(row,50, round(float(str(data.tagging)),2))
                    worksheet.write(row,51, round(float(str(data.fake)),2))
                    worksheet.write(row,52, str(data.remarksSection_D))
                    worksheet.write(row,53, int(round(float(str(data.totalscore)))))
                    worksheet.write(row,54, str(data.created_at))
                    worksheet.write(row,55, str(data.quality_auditor_id))



                    row = row + 1


        workbook.close()
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={datetime.date.today()}.xlsx'
        import gc
        gc.collect()

        return response


    
