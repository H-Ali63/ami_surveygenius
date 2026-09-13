

# for duplicate
# SELECT uid, COUNT(uid) 
# FROM quality.search_surveyresponse
# GROUP BY uid
# HAVING COUNT(uid) > 1

## for delete duplicate

# DELETE FROM quality.search_surveyresponse
# WHERE id NOT IN (
#     SELECT * FROM (
#         SELECT MIN(id) AS id
#         FROM quality.search_surveyresponse
#         GROUP BY uid, params
#     ) AS temp
# );


# SELECT uid, COUNT(uid) AS DuplicateRanks
# FROM search_surveyresponse
# GROUP BY id
# HAVING COUNT(uid)>1


# SELECT MAX(CAST(uid AS SIGNED)) from search_surveyresponse WHERE uid REGEXP '^[0-9]+$';
from __future__ import unicode_literals

# from StringIO import StringIO

from io import StringIO
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
import requests as req
import MySQLdb
import uuid
import hashlib
# Create your views here.
import xlsxwriter

from urllib.request import urlopen
from io import BytesIO
import json,datetime
from datetime import date,time
# from mainapp.models import *
from .models import *
import xlsxwriter
from django.db.models import Count,Case,When,Sum

class Search(TemplateView):
    def __init__(self):

        pass

    def get(self,request):
        # print(request.user.user_employee.designation.name,"=====",request.user.user_employee.employee_id,"<<<user::::",request.user.user_employee.designation.department.name)
        active_projects_list = QualityReview.objects.values("project_name").distinct()
        auditor_list = QualityReview.objects.values("quality_auditor","quality_auditor_id").distinct()
        # print(auditor_list,"<<<<<<<<<<<<<<<<,quality_auditor")

        data = {}
        # print(request.GET.keys())

        # today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        # today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        # auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).count()
        # quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).values("project_name")\
        #     .annotate(Count('project_name'))
        #
        # print(quality_project_wise_records,"<<<<<<<quality_project_wise_records::::",auditor_count)
        # print(quality_project_wise_records)

        ###################################################
        quality_project_wise_records = None
        auditor_count = 0
        # if (request.user.user_employee.designation.department.name == "Quality" and request.user.user_employee.designation.name in ["Assistant_Manager", "Senior executive-Quality Assurance", "Manager"]) or \
        #     (request.user.user_employee.designation.department.name == "DRC" and request.user.user_employee.designation.name in ["Quality Assurance", "Senior executive-Quality Assurance"]) or \
        #     (request.user.user_employee.designation.department.name == "Product" and request.user.user_employee.designation.name == "Manager"):

        print(type(request.user.username))
        if request.user.username == "axis":
            quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max)).values("quality_auditor") \
                .annotate(Count('project_name'))
            auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max)).count()
            print(quality_project_wise_records, "><<<")
        else:
            quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                    quality_auditor_id=request.user.user_employee.employee_id).values("project_name").annotate(Count('project_name'))
            auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),
                                                         quality_auditor_id=request.user.user_employee.employee_id).count()
            print(quality_project_wise_records)

        ###################################################



        print(request.GET)
        if("filter" not in request.GET.keys() and "uid" in request.GET.keys() and request.GET["uid"]!=""):
            print("if calledddd")
            surveyResponse = SurveyResponse.objects.filter(uid=request.GET["uid"])
            # print(surveyResponse.count(),"<<<counttt")
            if(surveyResponse.count()>0):
                params = json.loads(surveyResponse[0].params)

                remarks = json.loads(surveyResponse[0].remarks)
                surveyor_id=params["surveyor"].split("-")[0]
                surveyor_name = params["surveyor"].split("-")[1]
                tl_name=params["tldetails"]

                currentdatetime=datetime.datetime.now().strftime('%Y-%m-%d')
                data={
                    'user': request.user,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'employee_pic': request.user,
                    'userrole': request.user,
                    'department': request.user,
                    "uid":request.GET["uid"],
                    "project_id":surveyResponse[0].project.id,
                    "project_name": surveyResponse[0].project.name,
                    "surveyor_name":surveyor_name,
                    "surveyor_id":int(surveyor_id),
                    "tl_name":tl_name,
                    "params":params,
                    "remarks":remarks,
                    "verification_status":surveyResponse[0].verification_status.name,
                    "audit_date":str(currentdatetime),
                    "interview_duration":params["timedifference"],
                    "interview_date":params["date"],
                    "quality_auditor_name":request.user.first_name +" "+ request.user.last_name,
                    "status":True,
                    'htmlfilename': 'search_quality.html',
                    'maindata': [],
                    'notification': None,
                    "quality_auditor_id":request.user,
                    "auditor_position":request.user,
                    "active_projects_list":active_projects_list,
                    "auditor_list":auditor_list,
                    "msg": "",
                    "auditor_count_form":auditor_count,
                    "quality_project_wise_records":quality_project_wise_records
                }
                # return render(request,"search_quality.html",data)
                return render(request, "index.html", data)
            else:
                print("if-else called calledddd")
                data = {
                    'user': request.user,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'employee_pic': request.user,
                    'userrole': request.user,
                    'department': request.user,
                    'htmlfilename': 'search_quality.html',
                    'maindata': [],
                    'notification': None,
                    "quality_auditor_id": request.user,
                    "auditor_position": request.user,
                    "active_projects_list": active_projects_list,
                    "auditor_list": auditor_list,
                    "msg": "",
                    "auditor_count_form": auditor_count,
                    "quality_project_wise_records":quality_project_wise_records
                }
                return render(request, "index.html", data)
        elif("filter" in request.GET.keys()):
            print("elif calledddd::::")
            if("auditor_project_name" in request.GET.keys() or "quality_auditor_name" in request.GET.keys() or "startdate" in request.GET.keys() or "enddate" in request.GET.keys()):

                if(request.GET["selected_form"]=="fetch" or request.GET["selected_form"]=="detailed_summary"):

                    if(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]!="" and request.GET["enddate"]!=""):

                        enddate=None
                        startdate = None
                        print(request.GET["interview_startdate"],"=====1======",request.GET["interview_enddate"])
                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")


                        print(request.GET["auditor_project_name"],"<<<<<<<<,,nameeee::::",request.GET["quality_auditor_name"])
                        qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate,enddate],project_name__icontains=request.GET["auditor_project_name"],
                                                                      quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                            .annotate(Count('surveyor_name'),
                                      alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("voice") / (
                                                                       10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                      alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("convince") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("professional") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                                          "voice") + Sum(
                                          "skills") +
                                                   Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                                                  "professional")),

                                      alisectionDvariation=Sum("variation"),
                                      alisectionDsurvey=Sum("survey"),
                                      alisectionDmovement=Sum("movement"),
                                      alisectionDtagging=Sum("tagging"),
                                      alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                      alisectionABCD_diff=Sum("totalscore"),
                                      test1=(4 * 10) * Count('surveyor_name'),
                                      test2=(3 * 10) * Count('surveyor_name'),
                                      test3=(3 * 10) * Count('surveyor_name'),
                                      qualityPercent=((Sum("totalscore")) / (
                                              (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                                              3 * 10) * Count('surveyor_name')) * 100),
                                      sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))
                        print(qualityRecords.count(),"*****************************************")
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]=="" and request.GET["enddate"]==""):


                        print(request.GET["interview_startdate"], "======2=====", request.GET["interview_enddate"])



                        qualityRecords = QualityReview.objects.filter(
                            project_name__icontains=request.GET["auditor_project_name"],
                            quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                            .annotate(Count('surveyor_name'),
                                      alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("voice") / (
                                                                       10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                      alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("convince") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("professional") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                                          "voice") + Sum(
                                          "skills") +
                                                   Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                                                  "professional")),

                                      alisectionDvariation=Sum("variation"),
                                      alisectionDsurvey=Sum("survey"),
                                      alisectionDmovement=Sum("movement"),
                                      alisectionDtagging=Sum("tagging"),
                                      alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                      alisectionABCD_diff=Sum("totalscore"),
                                      test1=(4 * 10) * Count('surveyor_name'),
                                      test2=(3 * 10) * Count('surveyor_name'),
                                      test3=(3 * 10) * Count('surveyor_name'),
                                      qualityPercent=((Sum("totalscore")) / (
                                              (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                                              3 * 10) * Count('surveyor_name')) * 100),
                                      sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))
                        print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] != "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

                        enddate=None
                        startdate=None
                        print(request.GET["interview_startdate"], "======3=====", request.GET["interview_enddate"])

                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(
                            project_name__icontains=request.GET["auditor_project_name"],
                            auditor_date__range=[startdate,enddate]).values("surveyor_name") \
                            .annotate(Count('surveyor_name'),
                                      alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("voice") / (
                                                                       10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                      alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("convince") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("professional") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                                          "voice") + Sum(
                                          "skills") +
                                                   Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                                                  "professional")),

                                      alisectionDvariation=Sum("variation"),
                                      alisectionDsurvey=Sum("survey"),
                                      alisectionDmovement=Sum("movement"),
                                      alisectionDtagging=Sum("tagging"),
                                      alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                      alisectionABCD_diff=Sum("totalscore"),
                                      test1=(4 * 10) * Count('surveyor_name'),
                                      test2=(3 * 10) * Count('surveyor_name'),
                                      test3=(3 * 10) * Count('surveyor_name'),
                                      qualityPercent=((Sum("totalscore")) / (
                                              (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                                              3 * 10) * Count('surveyor_name')) * 100),
                                      sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))
                        print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):
                        print("*********************************")

                        enddate = None
                        startdate = None
                        print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])


                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(
                            auditor_date__range=[startdate,enddate],
                            quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                            .annotate(Count('surveyor_name'),
                                      alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("voice") / (
                                                                       10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                      alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("convince") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("professional") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                                          "voice") + Sum(
                                          "skills") +
                                                   Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                                                  "professional")),

                                      alisectionDvariation=Sum("variation"),
                                      alisectionDsurvey=Sum("survey"),
                                      alisectionDmovement=Sum("movement"),
                                      alisectionDtagging=Sum("tagging"),
                                      alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                      alisectionABCD_diff=Sum("totalscore"),
                                      test1=(4 * 10) * Count('surveyor_name'),
                                      test2=(3 * 10) * Count('surveyor_name'),
                                      test3=(3 * 10) * Count('surveyor_name'),
                                      qualityPercent=((Sum("totalscore")) / (
                                              (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                                              3 * 10) * Count('surveyor_name')) * 100),
                                      sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))
                        print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

                        enddate = None
                        startdate = None
                        print(request.GET["interview_startdate"], "======5=====", request.GET["interview_enddate"])

                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(
                            auditor_date__range=[startdate,enddate]).values("surveyor_name") \
                        .annotate(Count('surveyor_name'),
                                  alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("voice") / (10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                  alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("convince") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                  alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                  alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                       (Sum("professional") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                  alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum("voice") + Sum(
                                      "skills") +
                                               Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                                              "professional")),

                                  alisectionDvariation=Sum("variation"),
                                  alisectionDsurvey=Sum("survey"),
                                  alisectionDmovement=Sum("movement"),
                                  alisectionDtagging=Sum("tagging"),
                                  alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                  alisectionABCD_diff=Sum("totalscore"),
                                  test1=(4 * 10) * Count('surveyor_name'),
                                  test2=(3 * 10) * Count('surveyor_name'),
                                  test3=(3 * 10) * Count('surveyor_name'),
                                  qualityPercent=((Sum("totalscore")) / (
                                              (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                                                  3 * 10) * Count('surveyor_name')) * 100),
                                  sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))

                        print(qualityRecords)
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
                        print(request.GET["interview_startdate"], "======6=====", request.GET["interview_enddate"])


                        if("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                            enddate = datetime.datetime.strptime(str(request.GET["interview_enddate"]), "%Y-%m-%d")
                            startdate = datetime.datetime.strptime(str(request.GET["interview_startdate"]), "%Y-%m-%d")
                            print("endDateeeeeeee called************",enddate,"=====",startdate)
                            qualityRecords = QualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"],interview_date__range=[startdate,enddate]).values("surveyor_name") \
                                .annotate(Count('surveyor_name'),
                                          alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionArecordings=(Sum("recordings") / (
                                                      10 * Count('surveyor_name'))) * 100,
                                          alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("knowledge") / (
                                                                           10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("recordings") / (
                                                                           10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("voice") / (10 * Count(
                                                                   'surveyor_name'))) * 100) / 400) * 100,

                                          alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("convince") / (10 * Count(
                                                                   'surveyor_name'))) * 100) / 300) * 100,

                                          alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionCprofessional=(Sum("professional") / (
                                                      10 * Count('surveyor_name'))) * 100,
                                          alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("professional") / (10 * Count(
                                                                   'surveyor_name'))) * 100) / 300) * 100,

                                          alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                                              "voice") + Sum("skills") +
                                                       Sum("answer") + Sum("convince") + Sum("polite") + Sum(
                                                      "speech") + Sum("professional")),

                                          alisectionDvariation=Sum("variation"),
                                          alisectionDsurvey=Sum("survey"),
                                          alisectionDmovement=Sum("movement"),
                                          alisectionDtagging=Sum("tagging"),
                                          alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum(
                                              "tagging"),

                                          alisectionABCD_diff=Sum("totalscore"),
                                          test1=(4 * 10) * Count('surveyor_name'),
                                          test2=(3 * 10) * Count('surveyor_name'),
                                          test3=(3 * 10) * Count('surveyor_name'),
                                          qualityPercent=((Sum("totalscore")) / (
                                                      (4 * 10) * Count('surveyor_name') + (3 * 10) * Count(
                                                  'surveyor_name') + (3 * 10) * Count('surveyor_name')) * 100),
                                          sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1)))

                                          )
                        else:


                            qualityRecords = QualityReview.objects.filter(
                                project_name__icontains=request.GET["auditor_project_name"]).values("surveyor_name") \
                                .annotate(Count('surveyor_name'),alisectionAskipping=(Sum("skipping")/(10*Count('surveyor_name')))*100,
                                          alisectionAknowledge=(Sum("knowledge")/(10*Count('surveyor_name')))*100,
                                          alisectionArecordings=(Sum("recordings")/(10*Count('surveyor_name')))*100,
                                          alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionAPercent=(((Sum("skipping")/(10*Count('surveyor_name')))*100 +
                                                               (Sum("knowledge")/(10*Count('surveyor_name')))*100 +
                                                               (Sum("recordings")/(10*Count('surveyor_name')))*100 +
                                                               (Sum("voice") / (10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                          alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("convince") / (10 * Count('surveyor_name'))) * 100)  / 300) * 100,

                                          alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                          alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                               (Sum("professional") / (10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                          alitotalABC = (Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum("voice") + Sum("skills") +
                                                         Sum("answer") + Sum("convince") +Sum("polite") + Sum("speech") + Sum("professional") ),



                                          alisectionDvariation=Sum("variation"),
                                          alisectionDsurvey=Sum("survey"),
                                          alisectionDmovement=Sum("movement"),
                                          alisectionDtagging=Sum("tagging"),
                                          alisectionDtotal = Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                          alisectionABCD_diff=Sum("totalscore"),
                                            test1=(4*10)*Count('surveyor_name'),
                                          test2=(3 * 10) * Count('surveyor_name'),
                                          test3=(3 * 10) * Count('surveyor_name'),
                                          qualityPercent=((Sum("totalscore"))/((4*10)*Count('surveyor_name')+(3*10)*Count('surveyor_name')+(3*10)*Count('surveyor_name'))*100),
                                          sectionDfakeForms = Count(Case(When(is_fake_form=True, then=1)))

                                          )
                            print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
                    elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] == "" and request.GET["enddate"] == ""):

                        enddate = None
                        startdate = None
                        print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])

                        qualityRecords = QualityReview.objects.filter(
                            quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
                            .annotate(Count('surveyor_name'),
                                      alisectionAskipping=(Sum("skipping") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionAPercent=(((Sum("skipping") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("voice") / (
                                                                       10 * Count('surveyor_name'))) * 100) / 400) * 100,

                                      alisectionBskills=(Sum("skills") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionBPercent=(((Sum("skills") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("convince") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alisectionCpolite=(Sum("polite") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCspeech=(Sum("speech") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCprofessional=(Sum("professional") / (10 * Count('surveyor_name'))) * 100,
                                      alisectionCPercent=(((Sum("polite") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("speech") / (10 * Count('surveyor_name'))) * 100 +
                                                           (Sum("professional") / (
                                                                   10 * Count('surveyor_name'))) * 100) / 300) * 100,

                                      alitotalABC=(Sum("skipping") + Sum("knowledge") + Sum("recordings") + Sum(
                                          "voice") + Sum(
                                          "skills") +
                                                   Sum("answer") + Sum("convince") + Sum("polite") + Sum("speech") + Sum(
                                                  "professional")),

                                      alisectionDvariation=Sum("variation"),
                                      alisectionDsurvey=Sum("survey"),
                                      alisectionDmovement=Sum("movement"),
                                      alisectionDtagging=Sum("tagging"),
                                      alisectionDtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

                                      alisectionABCD_diff=Sum("totalscore"),
                                      test1=(4 * 10) * Count('surveyor_name'),
                                      test2=(3 * 10) * Count('surveyor_name'),
                                      test3=(3 * 10) * Count('surveyor_name'),
                                      qualityPercent=((Sum("totalscore")) / (
                                              (4 * 10) * Count('surveyor_name') + (3 * 10) * Count('surveyor_name') + (
                                              3 * 10) * Count('surveyor_name')) * 100),
                                      sectionDfakeForms=Count(Case(When(is_fake_form=True, then=1))))
                        print(qualityRecords)
                        # return self.exportData(qualityRecords)
                        return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)

                else:

                    print("****123****")
                    # enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                    # startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                    # print("request.GET:::::",request.GET["auditor_project_name"])
                    qualityRecords = None
                    if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]!="default"):
                        print("12345")

                        enddate = None
                        startdate = None
                        print(request.GET["interview_startdate"], "======7=====", request.GET["interview_enddate"])


                        enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                        startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                        qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate,enddate],project_name__icontains=request.GET["auditor_project_name"])
                    else:
                        print("****1234****")
                        if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]=="default"):

                            enddate = None
                            startdate = None
                            print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])


                            enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
                            startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
                            qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate, enddate])
                        else:
                            qualityRecords = QualityReview.objects.filter(project_name__icontains=request.GET["auditor_project_name"])
                    # print(qualityRecords.count(),"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<counttt")
                    return self.exportData(qualityRecords)


            elif("quality_auditor_id" in request.GET.keys()):

                print("getQualityFilter:::",request.GET["quality_auditor_id"],"======",request.GET["auditor_date"])
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
                                'user': request.user,
                                'first_name': request.user.first_name,
                                'last_name': request.user.last_name,
                                'employee_pic': request.user,
                                'userrole': request.user,
                                'department': request.user,
                                'htmlfilename': 'search_quality.html',
                                'maindata': [],
                                'notification': None,
                                "quality_auditor_id": request.user,
                                "auditor_position": request.user,
                                "active_projects_list": active_projects_list,
                                "auditor_list": auditor_list,
                                "msg": "",
                                "auditor_count_form": auditor_count,
                                "quality_project_wise_records":quality_project_wise_records
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
                        'user': request.user,
                        'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                        'employee_pic': request.user,
                        'userrole': request.user,
                        'department': request.user,
                        'htmlfilename': 'search_quality.html',
                        'maindata': [],
                        'notification': None,
                        "quality_auditor_id": request.user,
                        "auditor_position": request.user,
                        "active_projects_list": active_projects_list,
                        "auditor_list": auditor_list,
                        "msg": "",
                        "auditor_count_form": auditor_count,
                        "quality_project_wise_records":quality_project_wise_records
                    }
                    return render(request, "index.html", data)

            # if("quality_auditor_name" in request.GET.keys()):
            #     print("quality_auditor_name:::", request.GET["quality_auditor_name"])
            #     qualityRecords = QualityReview.objects.filter(quality_auditor__icontains=request.GET["quality_auditor_name"])
            #     print(qualityRecords.count())
            #     return self.exportData(qualityRecords)

            # if("startdate" in request.GET.keys()):
            #     print("start date====end date::::",type(request.GET["startdate"]),"=======",type(request.GET["enddate"]))
            #     # print(datetime.datetime.strptime(str(request.GET["enddate"]),"%Y-%m-%d"))
            #     try:
            #         enddate = datetime.datetime.strptime(str(request.GET["enddate"]),"%Y-%m-%d")
            #         startdate = datetime.datetime.strptime(str(request.GET["startdate"]),"%Y-%m-%d")
            #         print(enddate,"====",startdate)
            #         qualityRecords = QualityReview.objects.filter(interview_date__range=[startdate,enddate]).values("surveyor_name")\
            #             .annotate(Sum("skipping"),Sum("knowledge"),Sum("recordings"),Sum("voice"),
            #                       Sum("skills"), Sum("answer"), Sum("convince"),
            #                       Sum("polite"), Sum("speech"), Sum("professional"),
            #                       Sum("variation"), Sum("survey"), Sum("movement"), Sum("tagging"),Sum("fake"),
            #                       aliquots=(Sum("skipping")+Sum("knowledge")+Sum("recordings")+Sum("voice"))/4.0,
            #                       alisectionB=(Sum("skills") + Sum("answer") + Sum("convince"))/3.0,
            #                       alisectionC=(Sum("polite") + Sum("speech") + Sum("professional"))/3.0,
            #                       alisectionD=(Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging")+Sum("fake"))/5.0)
            #         print(qualityRecords)
            #         # return self.exportData(qualityRecords)
            #         return self.exportData_auditor(qualityRecords)
            #     except Exception as exception:
            #         print(exception,"<<<<<<<<<<<<excep")
            #         data = {
            #             'user': request.user.user_employee,
            #             'first_name': request.user.first_name,
            #             'last_name': request.user.last_name,
            #             'employee_pic': request.user.user_employee.get_profile_pic(),
            #             'userrole': request.user.user_employee.designation.name,
            #             'department': request.user.user_employee.designation.department.name,
            #             'htmlfilename': 'search_quality.html',
            #             'maindata': [],
            #             'notification': None,
            #             "quality_auditor_id": request.user.user_employee.employee_id,
            #             "auditor_position": request.user.user_employee.designation.department.name,
            #             "active_projects_list": active_projects_list,
            #             "auditor_list": auditor_list
            #
            #         }
            #         return render(request, "index.html", data)
        elif("hourly_report" in request.GET.keys()):
            print(request.GET["hourly_auditor_name"],"<<<<<<<<hourly auditor")
            params = None
            if(request.GET["hourly_auditor_name"] != "default"):
                params = request.GET["hourly_auditor_name"].split("$-$")[1]
            else:
                params = request.GET["hourly_auditor_name"]
            print(request.GET)
            return self.hourlyReports(params,request.GET["Pickdate"])

        else:
            print("pppf calledddd")
            data = {
                'user': request.user,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'employee_pic': request.user,
                'userrole': request.user,
                'department': request.user,
                'htmlfilename': 'search_quality.html',
                'maindata': [],
                'notification': None,
                "quality_auditor_id": request.user,
                "auditor_position": request.user,
                "active_projects_list": active_projects_list,
                "auditor_list": auditor_list,
                "msg": "",
                "auditor_count_form": auditor_count,
                "quality_project_wise_records":quality_project_wise_records

            }
            return render(request, "index.html", data)


    def post(self,request):

        msg = ""

        if ("mis_match_uid" in request.POST.keys()):
            if (QualityReviewMismatch.objects.filter(uid=int(request.POST["mis_match_uid"])).count() == 0):
                QualityReviewMismatch.objects.create(
                    uid=int(request.POST["mis_match_uid"]),
                    project_name=request.POST["mis_project_name"],
                    surveyor_name=request.POST["mis_surveyor_id"]+"-"+request.POST["mis_surveyor_name"],
                    fr_name=request.POST["mis_tl_name"],
                    interview_date=datetime.datetime.strptime(request.POST["mis_interview_date"], '%d-%b-%Y').strftime(
                        "%Y-%m-%d"),
                    interview_duration=request.POST["mis_interview_duration"],
                    quality_auditor=request.user.first_name + " " + request.user.last_name,
                    auditor_date=request.POST["mis_audit_date"],
                    review=request.POST["mis_match_reason_review"]
                )
                msg = "Submitted"
            else:
                print("duplicate entryyy")
                msg = "Duplicated Entry Please verify"

        else:



            data = {}
            msg=""




            A = request.POST["section_A_question_skipping_"]
            B = request.POST["section_A_incomplete_recording_"]
            C = request.POST["section_A_voice_quality_"]
            knowledge = request.POST["section_A_question_knowledge_"]

            D = request.POST["section_B_questioning_skills_"]
            E = request.POST["section_B_prompt_answers_"]
            F = request.POST["section_B_convincing_skills_"]

            G = request.POST["section_C_polite_and_courteous_"]
            H = request.POST["section_C_rate_of_speech_"]
            I = request.POST["section_C_professional_"]

            J = request.POST["section_D_variation_"]
            K = request.POST["section_D_force_survey_"]
            L = request.POST["section_D_moment_during_interview_"]
            M = request.POST["section_D_geo_tagging_"]
            N = request.POST["section_D_fake_form_"]

            isFake = False

            if(int(N)<0):
                A = 0
                B = 0
                C = 0
                D = 0
                E = 0
                F = 0
                G = 0
                H = 0
                I = 0
                J = 0
                K = 0
                L = 0
                M = 0
                N = 0
                knowledge = 0
                isFake = True





            score_A_B_C =  int(A) + int(B) +  int(C) + int(knowledge) + int(D) + int(E) + int(F) + int(G) + int(H) + int(I) 
            score_D = int(J) + int(K) + int(L) + int(M) + int(N)
            total_score = score_A_B_C + score_D
            print("total scoreee",datetime.datetime.now(),"========")

            print(datetime.datetime.now() - datetime.timedelta(hours=1))

            # ================================================================= #
            # present_date = datetime.datetime.now()
            # hourly_based_data_arr = []
            # for x in range(0,24):
            #     hourlyJson = {}
            #     result_date = present_date - datetime.timedelta(hours=1)
            #     hourlyJson["starting_hour"] = result_date
            #     hourlyJson["ending_hour"] = present_date
            #     hourlyBasedData = QualityReview.objects.filter(created_at__range=(result_date, present_date), auditor_date=date.today())
            #     print(hourlyBasedData.count())
            #     hourly_uids = []
            #     if(hourlyBasedData.count()>0):
            #         for hour_data in hourlyBasedData:
            #             print(hour_data.uid)
            #             hourly_uids.append(hour_data.uid)
            #         hourlyJson["hourly_uids"] = hourly_uids
            #
            #     else:
            #         print("elseeeee")
            #         hourlyJson["hourly_uids"] = []
            #     hourly_based_data_arr.append(hourlyJson)
            #     present_date = result_date
            # print(hourly_based_data_arr)
            # return self.exportHourlyBased( hourly_based_data_arr)
            # ================================================================= #



            if(QualityReview.objects.filter(uid=int(request.POST["uid_id"])).count()==0):
                QualityReview.objects.create(
                    uid=int(request.POST["uid_id"]),
                    project_name=request.POST["project_name"],
                    surveyor_name=request.POST["surveyor_id"]+"-"+request.POST["surveyor_name"],
                    fr_name=request.POST["fr_name"],
                    interview_date=datetime.datetime.strptime(request.POST["interview_date"], '%d-%b-%Y').strftime("%Y-%m-%d"),
                    interview_duration=request.POST["interview_duration"],
                    quality_auditor=request.user.first_name +" "+ request.user.last_name,
                    auditor_date=request.POST["auditing_date"],

                    skipping=A,
                    knowledge=knowledge,
                    recordings=B,
                    voice=C,
                    remarksSection_A=request.POST["section_A_remarks_"],

                    skills=D,
                    answer=E,
                    convince=F,
                    remarksSection_B=request.POST["section_B_remarks_"],


                    polite=G,
                    speech=H,
                    professional=I,
                    remarksSection_C=request.POST["section_C_remarks_"],


                    variation= J,
                    survey=K,
                    movement=L,
                    tagging=M,
                    fake=N,
                    remarksSection_D=request.POST["section_D_remarks_"],

                    totalscore=total_score,
                    # created_at=datetime.datetime.now(),
                    quality_auditor_id = request.user,
                    is_fake_form = isFake
                )
                # print("inserted")
                msg = "Submitted"
            else:
                # print("duplicate entryyy")
                msg = "Duplicated Entry Please verify"

        active_projects_list = QualityReview.objects.values("project_name").distinct()
        auditor_list = QualityReview.objects.values("quality_auditor","quality_auditor_id").distinct()
        # auditor_count = QualityReview.objects.filter(created_at=datetime.today().strftime("%Y-%m-%d")).count()
        # print(auditor_count)
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).count()
        print(auditor_count)
        quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).values("project_name") \
            .annotate(Count('project_name'))
        data = {
            'user': request.user,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'employee_pic': request.user,
            'userrole': request.user,
            'department': request.user,
            'htmlfilename': 'search_quality.html',
            'maindata': [],
            'notification': None,
            "quality_auditor_id": request.user,
            "auditor_position": request.user,
            "active_projects_list": active_projects_list,
            "auditor_list": auditor_list,
            "msg": msg,
            "auditor_count_form":auditor_count,
            "quality_project_wise_records":quality_project_wise_records
        }
        return render(request, "index.html", data)






    def hourlyReports(self,params,selected_date):
        print(selected_date,"====",selected_date)
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
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        row = 0
        col = 0
        worksheet.write(0,1,"ID".title().encode('utf-8'))
        worksheet.write(0, 2, "UID".title().encode('utf-8'))
        worksheet.write(0, 3, "Project_Name".title().encode('utf-8'))
        worksheet.write(0,4,"Surveyor_Name".title().encode('utf-8'))
        worksheet.write(0, 5, "FR_Name".title().encode('utf-8'))
        worksheet.write(0, 6, "Interview_Date".title().encode('utf-8'))
        worksheet.write(0, 7, "Interview_Duration".title().encode('utf-8'))
        worksheet.write(0, 8, "quality_auditor".title().encode('utf-8'))
        worksheet.write(0, 9, "auditor_date".title().encode('utf-8'))
        worksheet.write(0, 10, "skipping".title().encode('utf-8'))
        worksheet.write(0, 11, "knowledge".title().encode('utf-8'))
        worksheet.write(0, 12, "recordings".title().encode('utf-8'))
        worksheet.write(0, 13, "voice".title().encode('utf-8'))
        worksheet.write(0, 14, "remarks_A".title().encode('utf-8'))
        worksheet.write(0, 15, "skills".title().encode('utf-8'))
        worksheet.write(0, 16, "answer".title().encode('utf-8'))
        worksheet.write(0, 17, "convince".title().encode('utf-8'))
        worksheet.write(0, 18, "remarks_B".title().encode('utf-8'))
        worksheet.write(0, 19, "polite".title().encode('utf-8'))
        worksheet.write(0, 20, "speech".title().encode('utf-8'))
        worksheet.write(0, 21, "professional".title().encode('utf-8'))
        worksheet.write(0, 22, "remarks_C".title().encode('utf-8'))
        worksheet.write(0, 23, "variation".title().encode('utf-8'))
        worksheet.write(0, 24, "survey".title().encode('utf-8'))
        worksheet.write(0, 25, "movement".title().encode('utf-8'))
        worksheet.write(0, 26, "tagging".title().encode('utf-8'))
        worksheet.write(0, 27, "fake".title().encode('utf-8'))
        worksheet.write(0, 28, "remarks_D".title().encode('utf-8'))
        worksheet.write(0, 29, "total_score".title().encode('utf-8'))
        worksheet.write(0, 30, "created_date".title().encode('utf-8'))
        worksheet.write(0, 31, "auditor_id".title().encode('utf-8'))

        row = row + 1
        col = 0
        for data in data:
            # print(data.id,"<<<<< ")
            worksheet.write(row, 1, str(data.id).encode('utf-8'))
            worksheet.write(row, 2, str(data.uid).encode('utf-8'))
            worksheet.write(row, 3, str(data.project_name).encode('utf-8'))
            worksheet.write(row, 4, str(data.surveyor_name).encode('utf-8'))
            worksheet.write(row, 5, str(data.fr_name).encode('utf-8'))
            worksheet.write(row, 6, str(data.interview_date).encode('utf-8'))
            worksheet.write(row, 7, str(data.interview_duration).encode('utf-8'))
            worksheet.write(row, 8, str(data.quality_auditor).encode('utf-8'))
            worksheet.write(row, 9, str(data.auditor_date).encode('utf-8'))
            worksheet.write(row, 10, int(round(float(str(data.skipping).encode('utf-8')))))
            worksheet.write(row, 11, int(round(float(str(data.knowledge).encode('utf-8')))))
            worksheet.write(row, 12, int(round(float(str(data.recordings).encode('utf-8')))))
            worksheet.write(row, 13, int(round(float(str(data.voice).encode('utf-8')))))
            worksheet.write(row, 14, str(data.remarksSection_A).encode('utf-8'))
            worksheet.write(row, 15, int(round(float(str(data.skills).encode('utf-8')))))
            worksheet.write(row, 16, int(round(float(str(data.answer).encode('utf-8')))))
            worksheet.write(row, 17, int(round(float(str(data.convince).encode('utf-8')))))
            worksheet.write(row, 18, str(data.remarksSection_B).encode('utf-8'))
            worksheet.write(row, 19, int(round(float(str(data.polite).encode('utf-8')))))
            worksheet.write(row, 20, int(round(float(str(data.speech).encode('utf-8')))))
            worksheet.write(row, 21, int(round(float(str(data.professional).encode('utf-8')))))
            worksheet.write(row, 22, str(data.remarksSection_C).encode('utf-8'))
            worksheet.write(row, 23, int(round(float(str(data.variation).encode('utf-8')))))
            worksheet.write(row, 24, int(round(float(str(data.survey).encode('utf-8')))))
            worksheet.write(row, 25, int(round(float(str(data.movement).encode('utf-8')))))
            worksheet.write(row, 26, int(round(float(str(data.tagging).encode('utf-8')))))
            worksheet.write(row, 27, int(round(float(str(data.fake).encode('utf-8')))))
            worksheet.write(row, 28, str(data.remarksSection_D).encode('utf-8'))
            worksheet.write(row, 29, int(round(float(str(data.totalscore).encode('utf-8')))))
            worksheet.write(row, 30, str(data.created_at).encode('utf-8'))
            worksheet.write(row, 31, str(data.quality_auditor_id).encode('utf-8'))

            row = row + 1


        workbook.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment filename=%s.xlsx' % str(date.today())
        import gc
        gc.collect()

        return response






    def exportData_auditor(self,data,type,request):
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        # print(type,"<<<<,type")
        if(type=="fetch"):
            row = 0
            col = 0
            worksheet.write(0, 1, "surveyor_name".encode('utf-8'))
            worksheet.write(0, 2, "No Questions Skipping".encode('utf-8'))
            worksheet.write(0, 3, "Thorough Knowledge of Questionnaire".encode('utf-8'))
            worksheet.write(0, 4, "No Incomplete Recordings".encode('utf-8'))
            worksheet.write(0, 5, "Respondent voice can be heard clearly/Background noises".encode('utf-8'))
            worksheet.write(0, 6, "Section - A Subject Knowledge (Questionnaire) & Tab Knowledge/Handling Skills".encode('utf-8'))

            worksheet.write(0, 7, "Good probing or questioning Skills".encode('utf-8'))
            worksheet.write(0, 8, "Prompting Answer/ Options".encode('utf-8'))
            worksheet.write(0, 9, "Good Convincing Skills".encode('utf-8'))
            worksheet.write(0, 10, "Section - B Survey Handling Skills".encode('utf-8'))

            worksheet.write(0, 11, "Being polite and courteous during survey".encode('utf-8'))
            worksheet.write(0, 12, "Good rate of speech".encode('utf-8'))
            worksheet.write(0, 13, "Professional / Enthusiastic / Energetic".encode('utf-8'))
            worksheet.write(0, 14, "Section - C Soft Skills".encode('utf-8'))

            worksheet.write(0, 15, "Variation".encode('utf-8'))
            worksheet.write(0, 16, "Force Survey/False Promises/False Information".encode('utf-8'))
            worksheet.write(0, 17, "Movement During Interview".encode('utf-8'))
            worksheet.write(0, 18, "Geo Tagging".encode('utf-8'))
            worksheet.write(0, 19, "Fake Forms Count".encode('utf-8'))
            worksheet.write(0, 20, "Section - D Fatal Errors".encode('utf-8'))

            worksheet.write(0, 21, "total_forms_verified".encode('utf-8'))

            worksheet.write(0, 22, "quality_score % ".encode('utf-8'))
            worksheet.write(0, 23, "total_quality_score % ".encode('utf-8'))

            # worksheet.write(0, 24, "Percent Section A total_quality_score % ".encode('utf-8'))
            # worksheet.write(0, 25, "Percent Section B total_quality_score % ".encode('utf-8'))
            # worksheet.write(0, 26, "Percent Section C total_quality_score % ".encode('utf-8'))




            row = row + 1
            col = 0

            ################################################# For Surveyor_Count Start####################################################

            interview_startdate = None
            interview_enddate = None
            dates_arr = []
            if ("interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys()   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):

                interview_startdate = str(request.GET["interview_startdate"])
                interview_enddate = str(request.GET["interview_enddate"])
                delta = datetime.datetime.strptime(interview_enddate, '%Y-%m-%d') - datetime.datetime.strptime(
                    interview_startdate, '%Y-%m-%d')  # as timedelta

                for i in range(delta.days + 1):
                    day = datetime.datetime.strptime(interview_startdate, '%Y-%m-%d') + datetime.timedelta(days=i)
                    start_vall = '"date": "%s"' % (
                        datetime.datetime.strptime(str(day.date()), '%Y-%m-%d').strftime('%d-%b-%Y'))
                    dates_arr.append(start_vall)

            project_id_val = 0
            if ("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"] != "default"):
                projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                project_id_val = projectId.id

            ################################################ For Surveyor_Count ####################################################
            for data in data:

                ################################################# For Surveyor_Count Start####################################################
                surveyor_id_val = data["surveyor_name"].split("-")[0]
                print(surveyor_id_val, "====idd")

                count_total = 0
                if (len(data["surveyor_name"].split("-")) > 1   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                    if (len(dates_arr) > 0):
                        for dateVal in dates_arr:
                            if (project_id_val != 0):
                                print("calling surveyresponse*******1")
                                survey_response_obj = SurveyResponse.objects.filter(
                                    surveyor=Employee.objects.get(employee_id=surveyor_id_val),
                                    params__icontains=dateVal,
                                    project=Project.objects.get(pk=project_id_val)
                                ).values('uid').distinct()
                                count_total = count_total + survey_response_obj.count()
                            else:
                                print("calling surveyresponse*******2")
                                survey_response_obj = SurveyResponse.objects.filter(
                                    surveyor=Employee.objects.get(employee_id=surveyor_id_val),
                                    params__icontains=dateVal
                                ).values('uid').distinct()
                                count_total = count_total + survey_response_obj.count()

                ################################################ For Surveyor_Count END####################################################

                worksheet.write(row, 1, str(data["surveyor_name"]).encode('utf-8'))

                worksheet.write(row, 2, int(round(float(str(data["alisectionAskipping"]).encode('utf-8')))))
                worksheet.write(row, 3, int(round(float(str(data["alisectionAknowledge"]).encode('utf-8')))))
                worksheet.write(row, 4, int(round(float(str(data["alisectionArecordings"]).encode('utf-8')))))
                worksheet.write(row, 5, int(round(float(str(data["alisectionAvoice"]).encode('utf-8')))))
                worksheet.write(row, 6, int(round(float(str(data["alisectionAPercent"]).encode('utf-8')))))


                worksheet.write(row, 7, int(round(float(str(data["alisectionBskills"]).encode('utf-8')))))
                worksheet.write(row, 8, int(round(float(str(data["alisectionBknowledge"]).encode('utf-8')))))
                worksheet.write(row, 9, int(round(float(str(data["alisectionBrecordings"]).encode('utf-8')))))
                worksheet.write(row, 10, int(round(float(str(data["alisectionBPercent"]).encode('utf-8')))))


                worksheet.write(row, 11, int(round(float(str(data["alisectionCpolite"]).encode('utf-8')))))
                worksheet.write(row, 12, int(round(float(str(data["alisectionCspeech"]).encode('utf-8')))))
                worksheet.write(row, 13, int(round(float(str(data["alisectionCprofessional"]).encode('utf-8')))))
                worksheet.write(row, 14, int(round(float(str(data["alisectionCPercent"]).encode('utf-8')))))


                worksheet.write(row, 15, int(round(float(str(data["alisectionDvariation"]).encode('utf-8')))))
                worksheet.write(row, 16, int(round(float(str(data["alisectionDsurvey"]).encode('utf-8')))))
                worksheet.write(row, 17, int(round(float(str(data["alisectionDmovement"]).encode('utf-8')))))
                worksheet.write(row, 18, int(round(float(str(data["alisectionDtagging"]).encode('utf-8')))))
                worksheet.write(row, 19, int(round(float(str(data["sectionDfakeForms"]).encode('utf-8')))))
                worksheet.write(row, 20, int(round(float(str(data["alisectionDtotal"]).encode('utf-8')))))

                worksheet.write(row, 21, int(round(float(str(data["surveyor_name__count"]).encode('utf-8')))))
                worksheet.write(row, 22, int(round(float(str(data["qualityPercent"]).encode('utf-8')))))
                worksheet.write(row, 23, int(round(float(str(100).encode('utf-8')))))
                # worksheet.write(row, 24, str(data["surveyor_name"]).encode('utf-8'))
                worksheet.write(row, 25, int(round(float(str(count_total).encode('utf-8')))))
                # worksheet.write(row, 24, str(data["alisectionAPercent"]).encode('utf-8'))
                # worksheet.write(row, 25, str(data["alisectionBPercent"]).encode('utf-8'))
                # worksheet.write(row, 26, str(data["alisectionCPercent"]).encode('utf-8'))




                row = row + 1


            workbook.close()
            output.seek(0)
        elif(type=="detailed_summary"):
            print("shortttttt:::",request)
            row = 0
            col = 0
            worksheet.write(0, 1, "surveyor_name".encode('utf-8'))
            # worksheet.write(0, 2, "No Questions Skipping".encode('utf-8'))
            # worksheet.write(0, 3, "Thorough Knowledge of Questionnaire".encode('utf-8'))
            # worksheet.write(0, 4, "No Incomplete Recordings".encode('utf-8'))
            # worksheet.write(0, 5, "Respondent voice can be heard clearly/Background noises".encode('utf-8'))
            worksheet.write(0, 2,"Section - A Subject Knowledge (Questionnaire) & Tab Knowledge/Handling Skills".encode(
                                'utf-8'))

            # worksheet.write(0, 7, "Good probing or questioning Skills".encode('utf-8'))
            # worksheet.write(0, 8, "Prompting Answer/ Options".encode('utf-8'))
            # worksheet.write(0, 9, "Good Convincing Skills".encode('utf-8'))
            worksheet.write(0, 3, "Section - B Survey Handling Skills".encode('utf-8'))

            # worksheet.write(0, 11, "Being polite and courteous during survey".encode('utf-8'))
            # worksheet.write(0, 12, "Good rate of speech".encode('utf-8'))
            # worksheet.write(0, 13, "Professional / Enthusiastic / Energetic".encode('utf-8'))
            worksheet.write(0, 4, "Section - C Soft Skills".encode('utf-8'))

            # worksheet.write(0, 15, "Variation".encode('utf-8'))
            # worksheet.write(0, 16, "Force Survey/False Promises/False Information".encode('utf-8'))
            # worksheet.write(0, 17, "Movement During Interview".encode('utf-8'))
            worksheet.write(0, 5, "Geo Tagging".encode('utf-8'))
            worksheet.write(0, 6, "Fake Forms Count".encode('utf-8'))
            worksheet.write(0, 7, "Section - D Fatal Errors".encode('utf-8'))

            worksheet.write(0, 8, "total_forms_verified".encode('utf-8'))

            worksheet.write(0, 9, "quality_score % ".encode('utf-8'))
            worksheet.write(0, 10, "total_quality_score % ".encode('utf-8'))

            # worksheet.write(0, 24, "Percent Section A total_quality_score % ".encode('utf-8'))
            # worksheet.write(0, 25, "Percent Section B total_quality_score % ".encode('utf-8'))
            # worksheet.write(0, 26, "Percent Section C total_quality_score % ".encode('utf-8'))

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
                    start_vall = '"date": "%s"' % (datetime.datetime.strptime(str(day.date()), '%Y-%m-%d').strftime('%d-%b-%Y'))
                    dates_arr.append(start_vall)



            project_id_val=0
            if("auditor_project_name" in request.GET.keys() and request.GET["auditor_project_name"]!="default"):
                projectId = Project.objects.get(name=request.GET["auditor_project_name"])
                project_id_val = projectId.id

            ################################################ For Surveyor_Count ####################################################

            for data in data:

                ################################################# For Surveyor_Count Start####################################################
                surveyor_id_val = data["surveyor_name"].split("-")[0]
                print(surveyor_id_val,"====idd====",project_id_val)

                count_total = 0
                if(len(data["surveyor_name"].split("-"))>1 and "interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                    print("surrrrrrr:::",dates_arr)
                    if(len(dates_arr)>0):
                        for dateVal in dates_arr:
                            if(project_id_val!=0):
                                print(Employee.objects.get(employee_id=surveyor_id_val),"======valll")
                                survey_response_obj = SurveyResponse.objects.filter(
                                    surveyor=Employee.objects.get(employee_id=surveyor_id_val),
                                    params__icontains=dateVal,
                                    project=Project.objects.get(pk=project_id_val)
                                ).values('uid').distinct()
                                count_total =count_total + survey_response_obj.count()
                            else:
                                print("callling elsee*")
                                survey_response_obj = SurveyResponse.objects.filter(
                                    surveyor=Employee.objects.get(employee_id=surveyor_id_val),
                                    params__icontains=dateVal
                                ).values('uid').distinct()
                                count_total = count_total + survey_response_obj.count()

                ################################################ For Surveyor_Count END####################################################



                worksheet.write(row, 1, str(data["surveyor_name"]).encode('utf-8'))

                # worksheet.write(row, 2, str(data["alisectionAskipping"]).encode('utf-8'))
                # worksheet.write(row, 3, str(data["alisectionAknowledge"]).encode('utf-8'))
                # worksheet.write(row, 4, str(data["alisectionArecordings"]).encode('utf-8'))
                # worksheet.write(row, 5, str(data["alisectionAvoice"]).encode('utf-8'))
                worksheet.write(row, 2, int(round(float(str(data["alisectionAPercent"]).encode('utf-8')))))

                # worksheet.write(row, 7, str(data["alisectionBskills"]).encode('utf-8'))
                # worksheet.write(row, 8, str(data["alisectionBknowledge"]).encode('utf-8'))
                # worksheet.write(row, 9, str(data["alisectionBrecordings"]).encode('utf-8'))
                worksheet.write(row, 3, int(round(float(str(data["alisectionBPercent"]).encode('utf-8')))))

                # worksheet.write(row, 11, str(data["alisectionCpolite"]).encode('utf-8'))
                # worksheet.write(row, 12, str(data["alisectionCspeech"]).encode('utf-8'))
                # worksheet.write(row, 13, str(data["alisectionCprofessional"]).encode('utf-8'))
                worksheet.write(row, 4, int(round(float(str(data["alisectionCPercent"]).encode('utf-8')))))

                # worksheet.write(row, 15, str(data["alisectionDvariation"]).encode('utf-8'))
                # worksheet.write(row, 16, str(data["alisectionDsurvey"]).encode('utf-8'))
                # worksheet.write(row, 17, str(data["alisectionDmovement"]).encode('utf-8'))
                worksheet.write(row, 5, int(round(float(str(data["alisectionDtagging"]).encode('utf-8')))))
                worksheet.write(row, 6, int(round(float(str(data["sectionDfakeForms"]).encode('utf-8')))))
                worksheet.write(row, 7, int(round(float(str(data["alisectionDtotal"]).encode('utf-8')))))

                worksheet.write(row, 8, int(round(float(str(data["surveyor_name__count"]).encode('utf-8')))))
                worksheet.write(row, 9, int(round(float(str(data["qualityPercent"]).encode('utf-8')))))
                worksheet.write(row, 10, int(round(float(str(100).encode('utf-8')))))
                # worksheet.write(row, 24, str(data["surveyor_name"]).encode('utf-8'))

                # worksheet.write(row, 24, str(data["alisectionAPercent"]).encode('utf-8'))
                # worksheet.write(row, 25, str(data["alisectionBPercent"]).encode('utf-8'))
                # worksheet.write(row, 26, str(data["alisectionCPercent"]).encode('utf-8'))
                if(request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
                    worksheet.write(row, 15, int(round(float(str(count_total).encode('utf-8')))))

                row = row + 1

            workbook.close()
            output.seek(0)
        response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment filename=%s.xlsx'  % str(date.today())
        import gc
        gc.collect()

        return response





    def exportHourlyBased(self,data,auditor_arr,selected_date):
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')

        row = 0
        col = 0

        # worksheet.write(0, 0, "Date".encode('utf-8'))
        worksheet.write(0, 1, "Name".encode('utf-8'))
        worksheet.write(0, 2, "00.00 - 01.00".encode('utf-8'))
        worksheet.write(0, 3, "01.00 - 02.00".encode('utf-8'))
        worksheet.write(0, 4, "02.00 - 03.00".encode('utf-8'))
        worksheet.write(0, 5, "03.00 - 04.00".encode('utf-8'))
        worksheet.write(0, 6, "04.00 - 05.00".encode('utf-8'))
        worksheet.write(0, 7, "05.00 - 06.00".encode('utf-8'))
        worksheet.write(0, 8, "06.00 - 07.00".encode('utf-8'))
        worksheet.write(0, 9, "07.00 - 08.00".encode('utf-8'))
        worksheet.write(0, 10, "08.00 - 09.00".encode('utf-8'))
        worksheet.write(0, 11, "09.00 - 10.00".encode('utf-8'))
        worksheet.write(0, 12, "10.00 - 11.00".encode('utf-8'))
        worksheet.write(0, 13, "11.00 - 12.00".encode('utf-8'))
        worksheet.write(0, 14, "12.00 - 13.00".encode('utf-8'))
        worksheet.write(0, 15, "13.00 - 14.00".encode('utf-8'))
        worksheet.write(0, 16, "14.00 - 15.00".encode('utf-8'))
        worksheet.write(0, 17, "15.00 - 16.00".encode('utf-8'))
        worksheet.write(0, 18, "16.00 - 17.00".encode('utf-8'))
        worksheet.write(0, 19, "17.00 - 18.00".encode('utf-8'))
        worksheet.write(0, 20, "18.00 - 19.00".encode('utf-8'))
        worksheet.write(0, 21, "19.00 - 20.00".encode('utf-8'))
        worksheet.write(0, 22, "20.00 - 21.00".encode('utf-8'))
        worksheet.write(0, 23, "21.00 - 22.00".encode('utf-8'))
        worksheet.write(0, 24, "22.00 - 23.00".encode('utf-8'))
        worksheet.write(0, 25, "23.00 - 00.00".encode('utf-8'))

        worksheet.write(0, 27, "Total Count".encode('utf-8'))


        row = row + 1
        col = 0
        print(data)
        for hrdata in auditor_arr:
            # print(hrdata)
            if("name" in hrdata.keys()):
                # worksheet.write(row, 0, str(selected_date).encode('utf-8'))
                worksheet.write(row, 1, str(hrdata["name"]).encode('utf-8'))
                worksheet.write(row, 2, int(str(0).encode('utf-8')))
                worksheet.write(row, 3, int(str(0).encode('utf-8')))
                worksheet.write(row, 4, int(str(0).encode('utf-8')))
                worksheet.write(row, 5, int(str(0).encode('utf-8')))
                worksheet.write(row, 6, int(str(0).encode('utf-8')))
                worksheet.write(row, 7, int(str(0).encode('utf-8')))
                worksheet.write(row, 8, int(str(0).encode('utf-8')))
                worksheet.write(row, 9, int(str(0).encode('utf-8')))
                worksheet.write(row, 10, int(str(0).encode('utf-8')))
                worksheet.write(row, 11, int(str(0).encode('utf-8')))
                worksheet.write(row, 12, int(str(0).encode('utf-8')))
                worksheet.write(row, 13, int(str(0).encode('utf-8')))
                worksheet.write(row, 14, int(str(0).encode('utf-8')))
                worksheet.write(row, 15, int(str(0).encode('utf-8')))
                worksheet.write(row, 16, int(str(0).encode('utf-8')))
                worksheet.write(row, 17, int(str(0).encode('utf-8')))
                worksheet.write(row, 18, int(str(0).encode('utf-8')))
                worksheet.write(row, 19, int(str(0).encode('utf-8')))
                worksheet.write(row, 20, int(str(0).encode('utf-8')))
                worksheet.write(row, 21, int(str(0).encode('utf-8')))
                worksheet.write(row, 22, int(str(0).encode('utf-8')))
                worksheet.write(row, 23, int(str(0).encode('utf-8')))
                worksheet.write(row, 24, int(str(0).encode('utf-8')))
                worksheet.write(row, 25, int(str(0).encode('utf-8')))

                worksheet.write(row, 27, int(str(len(hrdata["obj"])).encode('utf-8')))




                # print(hrdata["obj"],"=====",hrdata["name"])
                hour_count={}
                for hourlyData in hrdata["obj"]:
                    print(hourlyData.created_at.hour)
                    if(hourlyData.created_at.hour in hour_count.keys()):
                        hour_count[hourlyData.created_at.hour] = hour_count[hourlyData.created_at.hour]+1
                    else:
                        hour_count[hourlyData.created_at.hour] = 1
                print(hour_count)

                for x in hour_count.keys():
                    print(hour_count[x],"====hour::",x,"   col:::",hourlyData.created_at.hour+2)
                    worksheet.write(row, x+2 , int(str(hour_count[x]).encode('utf-8')))

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
        #     worksheet.write(1, col, str(d).encode('utf-8'))
        #
        #     worksheet.write(1, h+2, str(len(data["hourly_uids"])).encode('utf-8'))
        #     worksheet.write(1,27,str(data["hourly_auditor_ids"]).encode('utf-8'))
        #
        #     row = row + 1
        #
        #
        #
        #
        #
        #
        #     # worksheet.write(row, 1, str(data["starting_hour"]).encode('utf-8'))
        #     # worksheet.write(row, 2, str(data["ending_hour"]).encode('utf-8'))
        #     # worksheet.write(row, 3, str(len(data["hourly_uids"])).encode('utf-8'))
        #     # worksheet.write(row, 4, ",".join(map(str,data["hourly_uids"])).encode('utf-8'))
        #     #row = row + 1



        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment filename='+str(selected_date)+'_hourly.xlsx'
        import gc
        gc.collect()

        return response