
from __future__ import unicode_literals

from django.db.models import FloatField, ExpressionWrapper, F, Q

# from StringIO import StringIO
import io
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
import mysql.connector
import uuid
import hashlib
# Create your views here.
import xlsxwriter

#from urllib2 import urlopen
from io import BytesIO
import json,datetime
from datetime import date,time
from .models import *
# from quality.models import *
import xlsxwriter
from django.db.models import Count,Case,When,Sum

cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


mycursor = cnx2.cursor()


sq3_list = []

value_list = SurveyResponse.objects.filter(~Q(uid__in=QualityReview.objects.values_list('uid', flat=True).all()))

# print(len(value_list))

for i in value_list:
	sq3_list.append(i.uid)

# print(len(sq3_list))
# 

qs1 = SurveyResponse.objects.values_list('uid').distinct()

# print(len(qs1))

qs2 = QualityReview.objects.values_list('uid').distinct()


sq1_list = []

sq2_list = []

# for qs in qs2:
# 	sq1_list.append(str(*qs))

# print(sq1_list)

# for qs in qs1:
# 	sq2_list.append(*qs)

# print(sq2_list)




query ="select uid from quality.search_surveyresponse"

mycursor.execute(query)

mylist = mycursor.fetchall()

value = list()

		# print(len(value))

for i in mylist:
	value.append(*i)

cnx2.close()

class SearchV2(TemplateView):
	def __init__(self):

		pass

	def get(self,request):

		

		# print(value)

		# print(len(value))

		data1 = []

		done_uids = QualityReview.objects.all()
		
		for i in done_uids:
			# print(i.uid)
			if str(i.uid) in value:
				ind = value.index(str(i.uid))
				# print(ind)
				value[ind] = " "
		
		if request.user.username == '101745':
			for i in range(25):

				
				data1.append(value[i])
		
		if request.user.username == 101855:
			for i in range(26,51):
				data1.append(value[i])
		
		if request.user.username == 101935:
			for i in range(51,101):
				data1.append(value[i])
		
		if request.user.username == 101940:
			for i in range(101,126):
				data1.append(value[i])
		
		if request.user.username == 102326:
			for i in range(126,151):
				data1.append(value[i])
		
		if request.user.username == 102327:
			for i in range(151,176):
				data1.append(value[i])
		
		if request.user.username == 102411:
			for i in range(176,201):
				data1.append(value[i])
		
		if request.user.username == 102414:
			for i in range(201,226):
				data1.append(value[i])
		
		if request.user.username == 104480:
			for i in range(226,251):
				data1.append(value[i])
		
		if request.user.username == 104892:
			for i in range(251,276):
				data1.append(value[i])
		
		if request.user.username == 104481:
			for i in range(276,301):
				data1.append(value[i])
		
		if request.user.username == 109032:
			for i in range(301,326):
				data1.append(value[i])
		
		if request.user.username == 106712:
			for i in range(326,351):
				data1.append(value[i])
		
		if request.user.username == 109033:
			for i in range(351,376):
				data1.append(value[i])
		
		if request.user.username == 109034:
			for i in range(376,401):
				data1.append(value[i])

		if request.user.username == '102405':
			for i in range(326,351):
				# print(value[376])
				data1.append(value[i])

		
		# print(data1)
		max_val = 5

		# print("searchv222")
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
		if (request.user.user_employee.designation.department.name == "Quality" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance", "Manager"]) or \
			(request.user.user_employee.designation.department.name == "DRC" and request.user.user_employee.designation.name in ["Assistant_Manager", "Quality Assurance", "Senior executive-Quality Assurance"]) or \
			(request.user.user_employee.designation.department.name == "Product" and request.user.user_employee.designation.name == "Manager"):
			quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max)).values("quality_auditor") \
				.annotate(Count('project_name'))
			auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max)).count()
			# print(quality_project_wise_records, "><<<")
		else:
			quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),
					quality_auditor_id=request.user.user_employee.employee_id).values("project_name").annotate(Count('project_name'))
			auditor_count = QualityReview.objects.filter(created_at__range=(today_min, today_max),
														 quality_auditor_id=request.user.user_employee.employee_id).count()
			# print(quality_project_wise_records)

		###################################################



		# print(request.GET)
		if("filter" not in request.GET.keys() and "uid" in request.GET.keys() and request.GET["uid"]!=""):
			# print("if calledddd")
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
					"data":data1
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
					"data":data1
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

						qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate, enddate],
																	  project_name__icontains=request.GET[
																		  "auditor_project_name"],
																	  quality_auditor__icontains=request.GET[
																		  "quality_auditor_name"]).values(
							"surveyor_name") \
							.annotate(Count('surveyor_name', output_field=FloatField()),
				 
									  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (max_val * Count('surveyor_name'))) * 100,
									  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
									  alisectionAPercent=((
															(Sum("question_skipping_incomplete_recordings") / (max_val * Count('surveyor_name'))) * 100
														   # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
														   # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
														   # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
														) / 100) * 100,

									  alisectionBskills=(Sum("question_subject_knowledge") / (max_val * Count('surveyor_name'))) * 100,
									  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
									  alisectionBPercent=((
														   (Sum("question_subject_knowledge") / (max_val * Count('surveyor_name'))) * 100
														   # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
														   # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionCpolite=(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCspeech=(Sum("questioning_technique") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCprofessional=(Sum("convencing_skills") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCPercent=((
														   (Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100 +
														   (Sum("questioning_technique") / (max_val * Count('surveyor_name'))) * 100 +
														   (Sum("convencing_skills") / (max_val * Count('surveyor_name'))) * 100
														   ) / 300) * 100,


									  alisectionDpolitecourteous=(Sum("polite_courteous")/ (max_val * Count('surveyor_name'))) * 100,
									  alisectionDrateofspeech=(Sum("rate_of_speech")/ (max_val * Count('surveyor_name'))) * 100,
									  alisectionDprofessionalismenergeticenthusiastic=(Sum("professionalism_energetic_enthusiastic")/ (max_val * Count('surveyor_name'))) * 100,
									  alisectionDPercent=((
																  (Sum("polite_courteous") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("rate_of_speech") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("professionalism_energetic_enthusiastic") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alitotalABCD=(
												   Sum("question_skipping_incomplete_recordings") +
												   Sum("question_subject_knowledge") +
												   Sum("voice_clarity") +
												   Sum("questioning_technique") +
												   Sum("convencing_skills") +
												   Sum("polite_courteous") +
												   Sum("rate_of_speech") +
												   Sum("professionalism_energetic_enthusiastic")
												   # Sum("answer") +
												   # Sum("convince") +
												   # Sum("polite") +
												   # Sum("speech") +
												   # Sum("professional")
												),

									  alisectionEvariation=Sum("variation"),
									  alisectionEsurvey=Sum("survey"),
									  alisectionEmovement=Sum("movement"),
									  alisectionEtagging=Sum("tagging"),
									  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

									  alisectionABCDE_diff=Sum("totalscore"),
									  test1=(1 * max_val) * Count('surveyor_name'),
									  test2=(1 * max_val) * Count('surveyor_name'),
									  test3=(3 * max_val) * Count('surveyor_name'),
									  test4=(3 * max_val) * Count('surveyor_name'),
									  qualityPercent=((Sum("totalscore")) /
													  ((1 * max_val) * Count('surveyor_name') +
													   (1 * max_val) * Count('surveyor_name') +
													   (3 * max_val) * Count('surveyor_name') +
													   (3 * max_val) * Count('surveyor_name')) * 40),
									  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1))))

						# print(qualityRecords.count(),"*****************************************")
						# return self.exportData(qualityRecords)
						return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
					elif(request.GET["auditor_project_name"]!="default" and request.GET["quality_auditor_name"]!="default" and request.GET["startdate"]=="" and request.GET["enddate"]==""):


						# print(request.GET["interview_startdate"], "======2=====", request.GET["interview_enddate"])



						qualityRecords = QualityReview.objects.filter(
							project_name__icontains=request.GET["auditor_project_name"],
							quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
							.annotate(Count('surveyor_name', output_field=FloatField()),
									  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (max_val * Count('surveyor_name'),)) * 100,
									  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
									  alisectionAPercent=((
															(Sum("question_skipping_incomplete_recordings") / (max_val * Count('surveyor_name'))) * 100
														   # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
														   # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
														   # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionBskills=(Sum("question_subject_knowledge") / (max_val * Count('surveyor_name'))) * 100,
									  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
									  alisectionBPercent=((
															(Sum("question_subject_knowledge") / (max_val * Count('surveyor_name'))) * 100
														   # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
														   # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
														   ) / 100) * 100,

									  alisectionCpolite=(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCspeech=(Sum("questioning_technique") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCprofessional=(Sum("convencing_skills") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCPercent=((
															(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100 +
														   (Sum("questioning_technique") / (max_val * Count('surveyor_name'))) * 100 +
														   (Sum("convencing_skills") / (max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alisectionDpolitecourteous=(Sum("polite_courteous") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDrateofspeech=(Sum("rate_of_speech") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDprofessionalismenergeticenthusiastic=(Sum(
										  "professionalism_energetic_enthusiastic") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDPercent=((
																  (Sum("polite_courteous") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("rate_of_speech") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("professionalism_energetic_enthusiastic") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alitotalABCD=(
										  Sum("question_skipping_incomplete_recordings") +
										  Sum("question_subject_knowledge") +
										  Sum("voice_clarity") +
										  Sum("questioning_technique") +
										  Sum("convencing_skills") +
										  Sum("polite_courteous") +
										  Sum("rate_of_speech") +
										  Sum("professionalism_energetic_enthusiastic")
										  # Sum("answer") +
										  # Sum("convince") +
										  # Sum("polite") +
										  # Sum("speech") +
										  # Sum("professional")
									  ),

									  alisectionEvariation=Sum("variation"),
									  alisectionEsurvey=Sum("survey"),
									  alisectionEmovement=Sum("movement"),
									  alisectionEtagging=Sum("tagging"),
									  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

									  alisectionABCDE_diff=Sum("totalscore"),
									  test1=(1 * max_val) * Count('surveyor_name'),
									  test2=(1 * max_val) * Count('surveyor_name'),
									  test3=(3 * max_val) * Count('surveyor_name'),
									  test4=(3 * max_val) * Count('surveyor_name'),
									  qualityPercent=((Sum("totalscore")) /
													  (
															  (1 * max_val) * Count('surveyor_name') + (1 * max_val) * Count(
														  'surveyor_name') +
															  (3 * max_val) * Count('surveyor_name') + (3 * max_val) * Count(
														  'surveyor_name')
													  ) * 40),
									  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1))))
						# print(qualityRecords)
						# return self.exportData(qualityRecords)
						return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
					elif (request.GET["auditor_project_name"] != "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

						enddate=None
						startdate=None
						# print(request.GET["interview_startdate"], "======3=====", request.GET["interview_enddate"])

						enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
						startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
						qualityRecords = QualityReview.objects.filter(
							project_name__icontains=request.GET["auditor_project_name"],
							auditor_date__range=[startdate,enddate]).values("surveyor_name") \
							.annotate(Count('surveyor_name', output_field=FloatField()),
									  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (
												  max_val * Count('surveyor_name'))) * 100,
									  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
									  alisectionAPercent=((
																  (Sum("question_skipping_incomplete_recordings") / (
																			  max_val * Count('surveyor_name'))) * 100
															  # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionBskills=(Sum("question_subject_knowledge") / (
												  max_val * Count('surveyor_name'))) * 100,
									  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
									  alisectionBPercent=((
																  (Sum("question_subject_knowledge") / (
																			  max_val * Count('surveyor_name'))) * 100
															  # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionCpolite=(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCspeech=(Sum("questioning_technique") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionCprofessional=(Sum("convencing_skills") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionCPercent=((
																  (Sum("voice_clarity") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("questioning_technique") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("convencing_skills") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alisectionDpolitecourteous=(Sum("polite_courteous") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionDrateofspeech=(Sum("rate_of_speech") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionDprofessionalismenergeticenthusiastic=(Sum(
										  "professionalism_energetic_enthusiastic") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionDPercent=((
																  (Sum("polite_courteous") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("rate_of_speech") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("professionalism_energetic_enthusiastic") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alitotalABCD=(
										  Sum("question_skipping_incomplete_recordings") +
										  Sum("question_subject_knowledge") +
										  Sum("voice_clarity") +
										  Sum("questioning_technique") +
										  Sum("convencing_skills") +
										  Sum("polite_courteous") +
										  Sum("rate_of_speech") +
										  Sum("professionalism_energetic_enthusiastic")
										  # Sum("answer") +
										  # Sum("convince") +
										  # Sum("polite") +
										  # Sum("speech") +
										  # Sum("professional")
									  ),

									  alisectionEvariation=Sum("variation"),
									  alisectionEsurvey=Sum("survey"),
									  alisectionEmovement=Sum("movement"),
									  alisectionEtagging=Sum("tagging"),
									  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging"),

									  alisectionABCDE_diff=Sum("totalscore"),
									  test1=(1 * max_val) * Count('surveyor_name'),
									  test2=(1 * max_val) * Count('surveyor_name'),
									  test3=(3 * max_val) * Count('surveyor_name'),
									  test4=(3 * max_val) * Count('surveyor_name'),
									  qualityPercent=((Sum("totalscore")) /
													  (
														(1 * max_val) * Count('surveyor_name') + (1 * max_val) * Count('surveyor_name') +
														(3 * max_val) * Count('surveyor_name') + (3 * max_val) * Count('surveyor_name')
													  ) * 40),
									  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1))))
						# print(qualityRecords)
						# return self.exportData(qualityRecords)
						return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
					elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):
						# print("*********************************")

						enddate = None
						startdate = None
						# print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])


						enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
						startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
						qualityRecords = QualityReview.objects.filter(
							auditor_date__range=[startdate,enddate],
							quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
							.annotate(Count('surveyor_name',output_field=FloatField()),
									  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (
												  max_val * Count('surveyor_name'))) * 100,
									  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
									  alisectionAPercent=((
																  (Sum("question_skipping_incomplete_recordings") / (
																			  max_val * Count('surveyor_name'))) * 100
															  # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionBskills=(Sum("question_subject_knowledge") / (
												  max_val * Count('surveyor_name'))) * 100,
									  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
									  alisectionBPercent=((
																  (Sum("question_subject_knowledge") / (
																			  max_val * Count('surveyor_name'))) * 100
															  # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionCpolite=(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCspeech=(Sum("questioning_technique") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionCprofessional=(Sum("convencing_skills") / (
												  max_val * Count('surveyor_name'))) * 100,
									  alisectionCPercent=((
																  (Sum("voice_clarity") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("questioning_technique") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("convencing_skills") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alisectionDpolitecourteous=(Sum("polite_courteous") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDrateofspeech=(Sum("rate_of_speech") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDprofessionalismenergeticenthusiastic=(Sum(
										  "professionalism_energetic_enthusiastic") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDPercent=((
																  (Sum("polite_courteous") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("rate_of_speech") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("professionalism_energetic_enthusiastic") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alitotalABCD=(
										  Sum("question_skipping_incomplete_recordings") +
										  Sum("question_subject_knowledge") +
										  Sum("voice_clarity") +
										  Sum("questioning_technique") +
										  Sum("convencing_skills") +
										  Sum("polite_courteous") +
										  Sum("rate_of_speech") +
										  Sum("professionalism_energetic_enthusiastic")
										  # Sum("answer") +
										  # Sum("convince") +
										  # Sum("polite") +
										  # Sum("speech") +
										  # Sum("professional")
									  ),

									  alisectionEvariation=Sum("variation"),
									  alisectionEsurvey=Sum("survey"),
									  alisectionEmovement=Sum("movement"),
									  alisectionEtagging=Sum("tagging"),
									  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum(
										  "tagging"),

									  alisectionABCDE_diff=Sum("totalscore"),
									  test1=(1 * max_val) * Count('surveyor_name'),
									  test2=(1 * max_val) * Count('surveyor_name'),
									  test3=(3 * max_val) * Count('surveyor_name'),
									  test4=(3 * max_val) * Count('surveyor_name'),
									  qualityPercent=((Sum("totalscore")) /
													  (
															  (1 * max_val) * Count('surveyor_name') +
															  (1 * max_val) * Count('surveyor_name') +
															  (3 * max_val) * Count('surveyor_name') +
															  (3 * max_val) * Count('surveyor_name')
													  ) * 40),
									  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1))))
						# print(qualityRecords)
						# return self.exportData(qualityRecords)
						return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
					elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] == "default" and request.GET["startdate"] != "" and request.GET["enddate"] != ""):

						enddate = None
						startdate = None
						# print(request.GET["interview_startdate"], "======5=====", request.GET["interview_enddate"])

						enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
						startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
						qualityRecords = QualityReview.objects.filter(
							auditor_date__range=[startdate,enddate]).values("surveyor_name") \
						.annotate(Count('surveyor_name',output_field=FloatField()),
								  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (
											  max_val * Count('surveyor_name'))) * 100,
								  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
								  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
								  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
								  alisectionAPercent=((
															  (Sum("question_skipping_incomplete_recordings") / (
																		  max_val * Count('surveyor_name'))) * 100
														  # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
														  # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
														  # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
													  ) / 100) * 100,

								  alisectionBskills=(Sum("question_subject_knowledge") / (
											  max_val * Count('surveyor_name'))) * 100,
								  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
								  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
								  alisectionBPercent=((
															  (Sum("question_subject_knowledge") / (
																		  max_val * Count('surveyor_name'))) * 100
														  # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
														  # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
													  ) / 100) * 100,

								  alisectionCpolite=(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100,
								  alisectionCspeech=(Sum("questioning_technique") / (
											  max_val * Count('surveyor_name'))) * 100,
								  alisectionCprofessional=(Sum("convencing_skills") / (
											  max_val * Count('surveyor_name'))) * 100,
								  alisectionCPercent=((
															  (Sum("voice_clarity") / (
																		  max_val * Count('surveyor_name'))) * 100 +
															  (Sum("questioning_technique") / (
																		  max_val * Count('surveyor_name'))) * 100 +
															  (Sum("convencing_skills") / (
																		  max_val * Count('surveyor_name'))) * 100
													  ) / 300) * 100,

								  alisectionDpolitecourteous=(Sum("polite_courteous") / (max_val * Count('surveyor_name'))) * 100,
								  alisectionDrateofspeech=(Sum("rate_of_speech") / (max_val * Count('surveyor_name'))) * 100,
								  alisectionDprofessionalismenergeticenthusiastic=(Sum(
									  "professionalism_energetic_enthusiastic") / (max_val * Count('surveyor_name'))) * 100,
								  alisectionDPercent=((
															  (Sum("polite_courteous") / (
																		  max_val * Count('surveyor_name'))) * 100 +
															  (Sum("rate_of_speech") / (
																		  max_val * Count('surveyor_name'))) * 100 +
															  (Sum("professionalism_energetic_enthusiastic") / (
																		  max_val * Count('surveyor_name'))) * 100
													  ) / 300) * 100,

								  alitotalABCD=(
									  Sum("question_skipping_incomplete_recordings") +
									  Sum("question_subject_knowledge") +
									  Sum("voice_clarity") +
									  Sum("questioning_technique") +
									  Sum("convencing_skills") +
									  Sum("polite_courteous") +
									  Sum("rate_of_speech") +
									  Sum("professionalism_energetic_enthusiastic")
									  # Sum("answer") +
									  # Sum("convince") +
									  # Sum("polite") +
									  # Sum("speech") +
									  # Sum("professional")
								  ),

								  alisectionEvariation=Sum("variation"),
								  alisectionEsurvey=Sum("survey"),
								  alisectionEmovement=Sum("movement"),
								  alisectionEtagging=Sum("tagging"),
								  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum(
									  "tagging"),

								  alisectionABCDE_diff=Sum("totalscore"),
								  test1=(1 * max_val) * Count('surveyor_name'),
								  test2=(1 * max_val) * Count('surveyor_name'),
								  test3=(3 * max_val) * Count('surveyor_name'),
								  test4=(3 * max_val) * Count('surveyor_name'),
								  qualityPercent=((Sum("totalscore")) /
												  (
														  (1 * max_val) * Count('surveyor_name') + (1 * max_val) * Count('surveyor_name') +
														  (3 * max_val) * Count('surveyor_name') + (3 * max_val) * Count('surveyor_name')
												  ) * 40),
								  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1))))

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
							qualityRecords = QualityReview.objects.filter(
								project_name__icontains=request.GET["auditor_project_name"],interview_date__range=[startdate,enddate]).values("surveyor_name") \
								.annotate(Count('surveyor_name',output_field=FloatField()),
										  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (
													  max_val * Count('surveyor_name'))) * 100,
										  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
										  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
										  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
										  alisectionAPercent=((
																	  (Sum(
																		  "question_skipping_incomplete_recordings") / (
																				   max_val * Count('surveyor_name'))) * 100
																  # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
																  # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
																  # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
															  ) / 100) * 100,

										  alisectionBskills=(Sum("question_subject_knowledge") / (
													  max_val * Count('surveyor_name'))) * 100,
										  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
										  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
										  alisectionBPercent=((
																	  (Sum("question_subject_knowledge") / (
																				  max_val * Count('surveyor_name'))) * 100
																  # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
																  # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
															  ) / 100) * 100,

										  alisectionCpolite=(Sum("voice_clarity") / (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionCspeech=(Sum("questioning_technique") / (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionCprofessional=(Sum("convencing_skills") / (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionCPercent=((
																	  (Sum("voice_clarity") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("questioning_technique") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("convencing_skills") / (
																				  max_val * Count('surveyor_name'))) * 100
															  ) / 300) * 100,

										  alisectionDpolitecourteous=(Sum("polite_courteous")/ (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionDrateofspeech=(Sum("rate_of_speech")/ (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionDprofessionalismenergeticenthusiastic=(Sum(
											  "professionalism_energetic_enthusiastic")/ (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionDPercent=((
																	  (Sum("polite_courteous") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("rate_of_speech") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("professionalism_energetic_enthusiastic") / (
																				  max_val * Count('surveyor_name'))) * 100
															  ) / 300) * 100,

										  alitotalABCD=(
											  Sum("question_skipping_incomplete_recordings") +
											  Sum("question_subject_knowledge") +
											  Sum("voice_clarity") +
											  Sum("questioning_technique") +
											  Sum("convencing_skills") +
											  Sum("polite_courteous") +
											  Sum("rate_of_speech") +
											  Sum("professionalism_energetic_enthusiastic")
											  # Sum("answer") +
											  # Sum("convince") +
											  # Sum("polite") +
											  # Sum("speech") +
											  # Sum("professional")
										  ),

										  alisectionEvariation=Sum("variation"),
										  alisectionEsurvey=Sum("survey"),
										  alisectionEmovement=Sum("movement"),
										  alisectionEtagging=Sum("tagging"),
										  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum(
											  "tagging"),

										  alisectionABCDE_diff=Sum("totalscore"),
										  test1=(1 * max_val) * Count('surveyor_name'),
										  test2=(1 * max_val) * Count('surveyor_name'),
										  test3=(3 * max_val) * Count('surveyor_name'),
										  test4=(3 * max_val) * Count('surveyor_name'),
										  qualityPercent=((Sum("totalscore")) /
														  (
																  (1 * max_val) * Count('surveyor_name') + (
																	  1 * max_val) * Count(
															  'surveyor_name') +
																  (3 * max_val) * Count('surveyor_name') + (
																			  3 * max_val) * Count(
															  'surveyor_name')
														  ) * 40),
										  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1)))

										  )
						else:


							qualityRecords = QualityReview.objects.filter(
								project_name__icontains=request.GET["auditor_project_name"]).values("surveyor_name") \
								.annotate(Count('surveyor_name',output_field=FloatField()),
										  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (
													  max_val * Count('surveyor_name'))) * 100,
										  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
										  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
										  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
										  alisectionAPercent=((
																	  (Sum(
																		  "question_skipping_incomplete_recordings") / (
																				   max_val * Count('surveyor_name'))) * 100
																  # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
																  # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
																  # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
															  ) / 100) * 100,

										  alisectionBskills=(Sum("question_subject_knowledge") / (
													  max_val * Count('surveyor_name'))) * 100,
										  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
										  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
										  alisectionBPercent=((
																	  (Sum("question_subject_knowledge") / (
																				  max_val * Count('surveyor_name'))) * 100
																  # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
																  # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
															  ) / 100) * 100,

										  alisectionCpolite=(Sum("voice_clarity") / (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionCspeech=(Sum("questioning_technique") / (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionCprofessional=(Sum("convencing_skills") / (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionCPercent=((
																	  (Sum("voice_clarity") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("questioning_technique") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("convencing_skills") / (
																				  max_val * Count('surveyor_name'))) * 100
															  ) / 300) * 100,

										  alisectionDpolitecourteous=(Sum("polite_courteous")/ (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionDrateofspeech=(Sum("rate_of_speech")/ (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionDprofessionalismenergeticenthusiastic=(Sum(
											  "professionalism_energetic_enthusiastic")/ (
													  max_val * Count('surveyor_name'))) * 100,
										  alisectionDPercent=((
																	  (Sum("polite_courteous") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("rate_of_speech") / (
																				  max_val * Count('surveyor_name'))) * 100 +
																	  (Sum("professionalism_energetic_enthusiastic") / (
																				  max_val * Count('surveyor_name'))) * 100
															  ) / 300) * 100,

										  alitotalABCD=(
											  Sum("question_skipping_incomplete_recordings") +
											  Sum("question_subject_knowledge") +
											  Sum("voice_clarity") +
											  Sum("questioning_technique") +
											  Sum("convencing_skills") +
											  Sum("polite_courteous") +
											  Sum("rate_of_speech") +
											  Sum("professionalism_energetic_enthusiastic")
											  # Sum("answer") +
											  # Sum("convince") +
											  # Sum("polite") +
											  # Sum("speech") +
											  # Sum("professional")
										  ),

										  alisectionEvariation=Sum("variation"),
										  alisectionEsurvey=Sum("survey"),
										  alisectionEmovement=Sum("movement"),
										  alisectionEtagging=Sum("tagging"),
										  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum(
											  "tagging"),

										  alisectionABCDE_diff=Sum("totalscore"),
											test1=(1*max_val)*Count('surveyor_name'),
										  test2=(1 * max_val) * Count('surveyor_name'),
										  test3=(3 * max_val) * Count('surveyor_name'),
										  test4=(3 * max_val) * Count('surveyor_name'),
										  qualityPercent=((Sum("totalscore")) /
														  (
																  (1 * max_val) * Count('surveyor_name') + (
																	  1 * max_val) * Count(
															  'surveyor_name') +
																  (3 * max_val) * Count('surveyor_name') + (
																			  3 * max_val) * Count(
															  'surveyor_name')
														  ) * 40),
										  sectionEfakeForms = Count(Case(When(is_fake_form=True, then=1)))

										  )
							# print(qualityRecords)
						# return self.exportData(qualityRecords)
						return self.exportData_auditor(qualityRecords,request.GET["selected_form"],request)
					elif (request.GET["auditor_project_name"] == "default" and request.GET["quality_auditor_name"] != "default" and request.GET["startdate"] == "" and request.GET["enddate"] == ""):

						enddate = None
						startdate = None
						# print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])

						qualityRecords = QualityReview.objects.filter(
							quality_auditor__icontains=request.GET["quality_auditor_name"]).values("surveyor_name") \
							.annotate(Count('surveyor_name',output_field=FloatField()),
									  alisectionAskipping=(Sum("question_skipping_incomplete_recordings") / (
												  max_val * Count('surveyor_name'))) * 100,
									  # alisectionAknowledge=(Sum("knowledge") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionArecordings=(Sum("recordings") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionAvoice=(Sum("voice") / (10 * Count('surveyor_name'))) * 100,
									  alisectionAPercent=((
																  (Sum("question_skipping_incomplete_recordings") / (
																			  max_val * Count('surveyor_name'))) * 100
															  # (Sum("knowledge") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("recordings") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("voice") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionBskills=(Sum("question_subject_knowledge") / (
												  max_val * Count('surveyor_name'))) * 100,
									  # alisectionBknowledge=(Sum("answer") / (10 * Count('surveyor_name'))) * 100,
									  # alisectionBrecordings=(Sum("convince") / (10 * Count('surveyor_name'))) * 100,
									  alisectionBPercent=((
																  (Sum("question_subject_knowledge") / (
																			  max_val * Count('surveyor_name'))) * 100
															  # (Sum("answer") / (10 * Count('surveyor_name'))) * 100 +
															  # (Sum("convince") / (10 * Count('surveyor_name'))) * 100
														  ) / 100) * 100,

									  alisectionCpolite=(Sum("voice_clarity") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionCspeech=(Sum("questioning_technique") / (
											  max_val * Count('surveyor_name'))) * 100,
									  alisectionCprofessional=(Sum("convencing_skills") / (
											  max_val * Count('surveyor_name'))) * 100,
									  alisectionCPercent=((
																  (Sum("voice_clarity") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("questioning_technique") / (
																			  max_val * Count('surveyor_name'))) * 100 +
																  (Sum("convencing_skills") / (
																			  max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alisectionDpolitecourteous=(Sum("polite_courteous") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDrateofspeech=(Sum("rate_of_speech") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDprofessionalismenergeticenthusiastic=(Sum(
										  "professionalism_energetic_enthusiastic") / (max_val * Count('surveyor_name'))) * 100,
									  alisectionDPercent=((
															  (Sum("polite_courteous") / (max_val * Count('surveyor_name'))) * 100 +
															  (Sum("rate_of_speech") / (max_val * Count('surveyor_name'))) * 100 +
															  (Sum("professionalism_energetic_enthusiastic") / (max_val * Count('surveyor_name'))) * 100
														  ) / 300) * 100,

									  alitotalABCD=(
										  Sum("question_skipping_incomplete_recordings") +
										  Sum("question_subject_knowledge") +
										  Sum("voice_clarity") +
										  Sum("questioning_technique") +
										  Sum("convencing_skills") +
										  Sum("polite_courteous") +
										  Sum("rate_of_speech") +
										  Sum("professionalism_energetic_enthusiastic")
										  # Sum("answer") +
										  # Sum("convince") +
										  # Sum("polite") +
										  # Sum("speech") +
										  # Sum("professional")
									  ),

									  alisectionEvariation=Sum("variation"),
									  alisectionEsurvey=Sum("survey"),
									  alisectionEmovement=Sum("movement"),
									  alisectionEtagging=Sum("tagging"),
									  alisectionEtotal=Sum("variation") + Sum("survey") + Sum("movement") + Sum(
										  "tagging"),

									  alisectionABCDE_diff=Sum("totalscore"),
									  test1=(1 * max_val) * Count('surveyor_name'),
									  test2=(1 * max_val) * Count('surveyor_name'),
									  test3=(3 * max_val) * Count('surveyor_name'),
									  test4=(3 * max_val) * Count('surveyor_name'),
									  qualityPercent=((Sum("totalscore")) /
													  (
															  (1 * max_val) * Count('surveyor_name') + (1 * max_val) * Count(
														  'surveyor_name') +
															  (3 * max_val) * Count('surveyor_name') + (3 * max_val) * Count(
														  'surveyor_name')
													  ) * 40),
									  sectionEfakeForms=Count(Case(When(is_fake_form=True, then=1))))
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
						qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate,enddate],project_name__icontains=request.GET["auditor_project_name"])
					else:
						# print("****1234****")
						if(request.GET["enddate"]!="" and request.GET["startdate"]!="" and request.GET["auditor_project_name"]=="default"):

							enddate = None
							startdate = None
							# print(request.GET["interview_startdate"], "======4=====", request.GET["interview_enddate"])


							enddate = datetime.datetime.strptime(str(request.GET["enddate"]), "%Y-%m-%d")
							startdate = datetime.datetime.strptime(str(request.GET["startdate"]), "%Y-%m-%d")
							qualityRecords = QualityReview.objects.filter(auditor_date__range=[startdate, enddate])
						else:
							qualityRecords = QualityReview.objects.filter(project_name__icontains=request.GET["auditor_project_name"])
					# print(qualityRecords.count(),"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<counttt")
					return self.exportData(qualityRecords)


			elif("quality_auditor_id" in request.GET.keys()):

				# print("getQualityFilter:::",request.GET["quality_auditor_id"],"======",request.GET["auditor_date"])
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
								"data":data1
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
						"data":data1
					}
					return render(request, "index.html", data)

			# if("quality_auditor_name" in request.GET.keys()):
			    # print("quality_auditor_name:::", request.GET["quality_auditor_name"])
			#     qualityRecords = QualityReview.objects.filter(quality_auditor__icontains=request.GET["quality_auditor_name"])
			    # print(qualityRecords.count())
			#     return self.exportData(qualityRecords)

			# if("startdate" in request.GET.keys()):
			    # print("start date====end date::::",type(request.GET["startdate"]),"=======",type(request.GET["enddate"]))
			    # print(datetime.datetime.strptime(str(request.GET["enddate"]),"%Y-%m-%d"))
			#     try:
			#         enddate = datetime.datetime.strptime(str(request.GET["enddate"]),"%Y-%m-%d")
			#         startdate = datetime.datetime.strptime(str(request.GET["startdate"]),"%Y-%m-%d")
			        # print(enddate,"====",startdate)
			#         qualityRecords = QualityReview.objects.filter(interview_date__range=[startdate,enddate]).values("surveyor_name")\
			#             .annotate(Sum("skipping"),Sum("knowledge"),Sum("recordings"),Sum("voice"),
			#                       Sum("skills"), Sum("answer"), Sum("convince"),
			#                       Sum("polite"), Sum("speech"), Sum("professional"),
			#                       Sum("variation"), Sum("survey"), Sum("movement"), Sum("tagging"),Sum("fake"),
			#                       aliquots=(Sum("skipping")+Sum("knowledge")+Sum("recordings")+Sum("voice"))/4.0,
			#                       alisectionB=(Sum("skills") + Sum("answer") + Sum("convince"))/3.0,
			#                       alisectionC=(Sum("polite") + Sum("speech") + Sum("professional"))/3.0,
			#                       alisectionD=(Sum("variation") + Sum("survey") + Sum("movement") + Sum("tagging")+Sum("fake"))/5.0)
			        # print(qualityRecords)
			#         # return self.exportData(qualityRecords)
			#         return self.exportData_auditor(qualityRecords)
			#     except Exception as exception:
			        # print(exception,"<<<<<<<<<<<<excep")
			#         data = {
			#             'user': request.user.user_employee,
			#             'first_name': request.user.first_name,
			#             'last_name': request.user.last_name,
			#             #'employee_pic': request.user.user_employee.get_profile_pic(),
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
			# print(request.GET["hourly_auditor_name"],"<<<<<<<<hourly auditor")
			params = None
			if(request.GET["hourly_auditor_name"] != "default"):
				params = request.GET["hourly_auditor_name"].split("$-$")[1]
			else:
				params = request.GET["hourly_auditor_name"]
			# print(request.GET)
			return self.hourlyReports(params,request.GET["Pickdate"])

		else:
			# print("pppf calledddd*v2")
			# print(data1)
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
					"data":data1

			}
			return render(request, "index.html", data)


	def post(self,request):


		cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


		mycursor = cnx2.cursor()


		query ="select uid from quality.search_surveyresponse"

		mycursor.execute(query)

		mylist = mycursor.fetchall()

		value = list()

		# print(len(value))

		for i in mylist:
			value.append(*i)

		# print(value)

		# print(len(value))

		data1 = []

		done_uids = QualityReview.objects.all()
		
		for i in done_uids:
			# print(i.uid)
			if str(i.uid) in value:
				ind = value.index(str(i.uid))
				# print(ind)
				value[ind] = " "
		
		if request.user.username == '101745':
			for i in range(25):
				data1.append(value[i])
		
		if request.user.username == 101855:
			for i in range(26,51):
				data1.append(value[i])
		
		if request.user.username == 101935:
			for i in range(51,101):
				data1.append(value[i])
		
		if request.user.username == 101940:
			for i in range(101,126):
				data1.append(value[i])
		
		if request.user.username == 102326:
			for i in range(126,151):
				data1.append(value[i])
		
		if request.user.username == 102327:
			for i in range(151,176):
				data1.append(value[i])
		
		if request.user.username == 102411:
			for i in range(176,201):
				data1.append(value[i])
		
		if request.user.username == 102414:
			for i in range(201,226):
				data1.append(value[i])
		
		if request.user.username == 104480:
			for i in range(226,251):
				data1.append(value[i])
		
		if request.user.username == 104892:
			for i in range(251,276):
				data1.append(value[i])
		
		if request.user.username == 104481:
			for i in range(276,301):
				data1.append(value[i])
		
		if request.user.username == 109032:
			for i in range(301,326):
				data1.append(value[i])
		
		if request.user.username == 106712:
			for i in range(326,351):
				data1.append(value[i])
		
		if request.user.username == 109033:
			for i in range(351,376):
				data1.append(value[i])
		
		if request.user.username == 109034:
			for i in range(376,401):
				data1.append(value[i])

		if request.user.username == '102405':
			for i in range(326,351):
				# print(value[376])
				data1.append(value[i])

		cnx2.close()


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
				# print("duplicate entryyy")
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


			isFake = False

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
		if isFake==True:
			score_D=0
		else:
			score_D = float(J) + float(K) + float(L) + float(M) + float(N) + float(O) + float(P) + float(Q)

			total_score = ((score_A_B_C + score_D)/40)*100
			# print("total scoreee",datetime.datetime.now(),"========")

			# print(datetime.datetime.now() - datetime.timedelta(hours=1))

			# ================================================================= #
			# present_date = datetime.datetime.now()
			# hourly_based_data_arr = []
			# for x in range(0,24):
			#     hourlyJson = {}
			#     result_date = present_date - datetime.timedelta(hours=1)
			#     hourlyJson["starting_hour"] = result_date
			#     hourlyJson["ending_hour"] = present_date
			#     hourlyBasedData = QualityReview.objects.filter(created_at__range=(result_date, present_date), auditor_date=date.today())
			    # print(hourlyBasedData.count())
			#     hourly_uids = []
			#     if(hourlyBasedData.count()>0):
			#         for hour_data in hourlyBasedData:
			            # print(hour_data.uid)
			#             hourly_uids.append(hour_data.uid)
			#         hourlyJson["hourly_uids"] = hourly_uids
			#
			#     else:
			        # print("elseeeee")
			#         hourlyJson["hourly_uids"] = []
			#     hourly_based_data_arr.append(hourlyJson)
			#     present_date = result_date
			# print(hourly_based_data_arr)
			# return self.exportHourlyBased( hourly_based_data_arr)
			# ================================================================= #



			if(QualityReview.objects.filter(uid=int(request.POST["uid_id"])).count()==0):
				# print(request.POST)
				QualityReview.objects.create(
					uid=int(request.POST["uid_id"]),
					project_name=request.POST["project_name"],
					surveyor_name=request.POST["surveyor_id"]+"-"+request.POST["surveyor_name"],
					fr_name=request.POST["fr_name"],

					interview_date = request.POST["interview_date"][:10],
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
		# print(auditor_count)
		quality_project_wise_records = QualityReview.objects.filter(created_at__range=(today_min, today_max),quality_auditor_id=request.user.user_employee.employee_id).values("project_name") \
			.annotate(Count('project_name',output_field=FloatField()))
		active_projects_list = QualityReview.objects.values("project_name").distinct()
		auditor_list = QualityReview.objects.values("quality_auditor", "quality_auditor_id").distinct()
		sectionAIssueList = IssueList.objects.filter(section="section_A").values("issue_id", "issues","related_question")
		sectionBIssueList = IssueList.objects.filter(section="section_B").values("issue_id", "issues","related_question")
		sectionCIssueList = IssueList.objects.filter(section="section_C").values("issue_id", "issues","related_question")
		sectionDIssueList = IssueList.objects.filter(section="section_D").values("issue_id", "issues","related_question")
		sectionEIssueList = IssueList.objects.filter(section="section_E").values("issue_id", "issues","related_question")
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
			"data":data1
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
		
		worksheet.write(0,1,"ID".title().encode('utf-8'))
		worksheet.write(0, 2, "UID".title().encode('utf-8'))
		worksheet.write(0, 3, "Project_Name".title().encode('utf-8'))
		worksheet.write(0,4,"Surveyor_Name".title().encode('utf-8'))
		worksheet.write(0, 5, "FR_Name".title().encode('utf-8'))
		worksheet.write(0, 6, "Interview_Date".title().encode('utf-8'))
		worksheet.write(0, 7, "Interview_Duration".title().encode('utf-8'))
		worksheet.write(0, 8, "quality_auditor".title().encode('utf-8'))
		worksheet.write(0, 9, "auditor_date".title().encode('utf-8'))


		worksheet.write(0, 10, "Question Skipping/ Incomplete Recording".title().encode('utf-8'))
		# worksheet.write(0, 11, "knowledge".title().encode('utf-8'))
		# worksheet.write(0, 12, "recordings".title().encode('utf-8'))
		# worksheet.write(0, 13, "voice".title().encode('utf-8'))
		worksheet.write(0, 11, "remarks_Question Skipping/ Incomplete Recording_reason".title().encode('utf-8'))
		worksheet.write(0, 12, "remarks_A_1".title().encode('utf-8'))
		worksheet.write(0, 13, "remarks_A_2".title().encode('utf-8'))

		worksheet.write(0, 14, "Questionnaire / Subject Knowledge".title().encode('utf-8'))
		# worksheet.write(0, 16, "answer".title().encode('utf-8'))
		# worksheet.write(0, 17, "convince".title().encode('utf-8'))
		worksheet.write(0, 15, "remarks_Questionnaire / Subject Knowledge_reason".title().encode('utf-8'))
		worksheet.write(0, 16, "remarks_B_1".title().encode('utf-8'))
		worksheet.write(0, 17, "remarks_B_2".title().encode('utf-8'))

		worksheet.write(0, 18, "Voice Clarity".title().encode('utf-8'))
		worksheet.write(0, 19, "Voice Clarity_reason".title().encode('utf-8'))
		worksheet.write(0, 20, "remarks_C_voice_clarity_1".title().encode('utf-8'))
		worksheet.write(0, 21, "remarks_C_voice_clarity_2".title().encode('utf-8'))
		worksheet.write(0, 22, "Questioning Technique".title().encode('utf-8'))
		worksheet.write(0, 23, "Questioning Technique_reason".title().encode('utf-8'))
		worksheet.write(0, 24, "remarks_C_question_technique_1".title().encode('utf-8'))
		worksheet.write(0, 25, "remarks_C_question_technique_2".title().encode('utf-8'))
		worksheet.write(0, 26, "Convincing skills".title().encode('utf-8'))
		worksheet.write(0, 27, "Convincing skills_reason".title().encode('utf-8'))
		worksheet.write(0, 28, "remarks_C_convencing_skills_1".title().encode('utf-8'))
		worksheet.write(0, 29, "remarks_C_convencing_skills_2".title().encode('utf-8'))

		worksheet.write(0, 30, "Being Polite & courteous".title().encode('utf-8'))
		worksheet.write(0, 31, "Being Polite & courteous_reason".title().encode('utf-8'))
		worksheet.write(0, 32, "remarksSection_D_polite_courteous_1".title().encode('utf-8'))
		worksheet.write(0, 33, "remarksSection_D_polite_courteous_2".title().encode('utf-8'))
		worksheet.write(0, 34, "Rate of Speech".title().encode('utf-8'))
		worksheet.write(0, 35, "Rate of Speech_reason".title().encode('utf-8'))
		worksheet.write(0, 36, "remarksSection_D_rate_of_speech_1".title().encode('utf-8'))
		worksheet.write(0, 37, "remarksSection_D_rate_of_speech_2".title().encode('utf-8'))
		worksheet.write(0, 38, "Professionalism/ Energetic/Enthusiastic".title().encode('utf-8'))
		worksheet.write(0, 39, "Professionalism/ Energetic/Enthusiastic_reason".title().encode('utf-8'))
		worksheet.write(0, 40, "remarksSection_D_professionalism_energetic_enthusiastic_1".title().encode('utf-8'))
		worksheet.write(0, 41, "remarksSection_D_professionalism_energetic_enthusiastic_2".title().encode('utf-8'))

		worksheet.write(0, 42, "variation".title().encode('utf-8'))
		worksheet.write(0, 43, "variation_reason".title().encode('utf-8'))
		worksheet.write(0, 44, "remarksSectionE_variation_1".title().encode('utf-8'))
		worksheet.write(0, 45, "survey".title().encode('utf-8'))
		worksheet.write(0, 46, "survey_reason".title().encode('utf-8'))
		worksheet.write(0, 47, "remarksSectionE_force_survey_1".title().encode('utf-8'))
		worksheet.write(0, 48, "movement".title().encode('utf-8'))
		worksheet.write(0, 49, "tagging".title().encode('utf-8'))
		worksheet.write(0, 50, "fake".title().encode('utf-8'))
		worksheet.write(0, 51, "remarks_D".title().encode('utf-8'))

		worksheet.write(0, 52, "total_score".title().encode('utf-8'))
		worksheet.write(0, 53, "created_date".title().encode('utf-8'))
		worksheet.write(0, 54, "auditor_id".title().encode('utf-8'))

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

			worksheet.write(row, 10, round(float(str(data.question_skipping_incomplete_recordings).encode('utf-8')),2))
			# worksheet.write(row, 11, int(round(float(str(data.knowledge).encode('utf-8')))))
			# worksheet.write(row, 12, int(round(float(str(data.recordings).encode('utf-8')))))
			# worksheet.write(row, 13, int(round(float(str(data.voice).encode('utf-8')))))
			worksheet.write(row, 11, str(data.question_skipping_incomplete_recordings_reason.related_question).encode('utf-8'))
			worksheet.write(row, 12, str(data.remarksSection_A_skipping_incomplete_recordings_1).encode('utf-8'))
			worksheet.write(row, 13, str(data.remarksSection_A_skipping_incomplete_recordings_2).encode('utf-8'))

			worksheet.write(row, 14, round(float(str(data.question_subject_knowledge).encode('utf-8')),2))
			# worksheet.write(row, 16, int(round(float(str(data.answer).encode('utf-8')))))
			# worksheet.write(row, 17, int(round(float(str(data.convince).encode('utf-8')))))
			worksheet.write(row, 15,str(data.question_subject_knowledge_reason.related_question).encode('utf-8'))
			worksheet.write(row, 16, str(data.remarksSection_B_question_subject_knowledge_1).encode('utf-8'))
			worksheet.write(row, 17, str(data.remarksSection_B_question_subject_knowledge_2).encode('utf-8'))

			worksheet.write(row, 18, round(float(str(data.voice_clarity).encode('utf-8')),2))
			worksheet.write(row, 19, str(data.voice_clarity_reason.related_question).encode('utf-8'))
			worksheet.write(row, 20, str(data.remarksSection_C_voice_clarity_1).encode('utf-8'))
			worksheet.write(row, 21, str(data.remarksSection_C_voice_clarity_2).encode('utf-8'))
			worksheet.write(row, 22, round(float(str(data.questioning_technique).encode('utf-8')),2))
			worksheet.write(row, 23, str(data.questioning_technique_reason.related_question).encode('utf-8'))
			worksheet.write(row, 24, str(data.remarksSection_C_questioning_technique_1).encode('utf-8'))
			worksheet.write(row, 25, str(data.remarksSection_C_questioning_technique_2).encode('utf-8'))
			worksheet.write(row, 26, round(float(str(data.convencing_skills).encode('utf-8')),2))
			worksheet.write(row, 27, str(data.convencing_skills_reason.related_question).encode('utf-8'))
			worksheet.write(row, 28, str(data.remarksSection_C_convencing_skills_1).encode('utf-8'))
			worksheet.write(row, 29, str(data.remarksSection_C_convencing_skills_2).encode('utf-8'))

			worksheet.write(row, 30, round(float(str(data.polite_courteous).encode('utf-8')),2))
			worksheet.write(row, 31, str(data.polite_courteous_reason.related_question).encode('utf-8'))
			worksheet.write(row, 32, str(data.remarksSection_D_polite_courteous_1).encode('utf-8'))
			worksheet.write(row, 33, str(data.remarksSection_D_polite_courteous_2).encode('utf-8'))
			worksheet.write(row, 34, round(float(str(data.rate_of_speech).encode('utf-8')),2))
			worksheet.write(row, 35, str(data.rate_of_speech_reason.related_question).encode('utf-8'))
			worksheet.write(row, 36, str(data.remarksSection_D_rate_of_speech_1).encode('utf-8'))
			worksheet.write(row, 37, str(data.remarksSection_D_rate_of_speech_2).encode('utf-8'))
			worksheet.write(row, 38, round(float(str(data.professionalism_energetic_enthusiastic).encode('utf-8')),2))
			worksheet.write(row, 39, str(data.professionalism_energetic_enthusiastic_reason.related_question).encode('utf-8'))
			worksheet.write(row, 40, str(data.remarksSection_D_professionalism_energetic_enthusiastic_1).encode('utf-8'))
			worksheet.write(row, 41, str(data.remarksSection_D_professionalism_energetic_enthusiastic_2).encode('utf-8'))



			worksheet.write(row, 42, round(float(str(data.variation).encode('utf-8')),2))
			worksheet.write(row, 43, (str(data.variation_reason.related_question).encode('utf-8')))
			worksheet.write(row, 44, str(data.remarksSection_E_variation_1).encode('utf-8'))
			worksheet.write(row, 45, round(float(str(data.survey).encode('utf-8')),2))
			worksheet.write(row, 46, (str(data.force_survey_reason.related_question).encode('utf-8')))
			worksheet.write(row, 47, str(data.remarksSection_E_force_survey_1).encode('utf-8'))
			worksheet.write(row, 48, round(float(str(data.movement).encode('utf-8')),2))
			worksheet.write(row, 49, round(float(str(data.tagging).encode('utf-8')),2))
			worksheet.write(row, 50, round(float(str(data.fake).encode('utf-8')),2))
			worksheet.write(row, 51, str(data.remarksSection_D).encode('utf-8'))


			worksheet.write(row, 52, int(round(float(str(data.totalscore).encode('utf-8')))))
			worksheet.write(row, 53, str(data.created_at).encode('utf-8'))
			worksheet.write(row, 54, str(data.quality_auditor_id).encode('utf-8'))

			row = row + 1


		workbook.close()
		output.seek(0)
		response = HttpResponse(output, content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = f'attachment filename={str(date.today())}.xlsx'
		import gc
		gc.collect()

		return response






	def exportData_auditor(self,data,type,request):
		output = io.StringIO()
		workbook = xlsxwriter.Workbook(output)
		worksheet = workbook.add_worksheet('output')
		# print(type,"<<<<,type")
		if(type=="fetch"):
			row = 0
			col = 0
			worksheet.write(0, 1, "surveyor_name".encode('utf-8'))
			worksheet.write(0, 2, "Question Skipping/ Incomplete Recording".encode('utf-8'))
			# worksheet.write(0, 3, "Thorough Knowledge of Questionnaire".encode('utf-8'))
			# worksheet.write(0, 4, "No Incomplete Recordings".encode('utf-8'))
			# worksheet.write(0, 5, "Respondent voice can be heard clearly/Background noises".encode('utf-8'))
			worksheet.write(0, 3, "Section - A Subject Knowledge (Questionnaire) & Tab Knowledge/Handling Skills".encode('utf-8'))

			worksheet.write(0, 4, "Questionnaire / Subject Knowledge ".encode('utf-8'))
			# worksheet.write(0, 8, "Prompting Answer/ Options".encode('utf-8'))
			# worksheet.write(0, 9, "Good Convincing Skills".encode('utf-8'))
			worksheet.write(0, 5, "Section - B Survey Handling Skills".encode('utf-8'))

			worksheet.write(0, 6, "Voice Clarity".encode('utf-8'))
			worksheet.write(0, 7, "Questioning Skills".encode('utf-8'))
			worksheet.write(0, 8, "Convincing skills".encode('utf-8'))
			worksheet.write(0, 9, "Section - C Survey Handling Skills".encode('utf-8'))

			worksheet.write(0, 10, "Being Polite & courteous".encode('utf-8'))
			worksheet.write(0, 11, "Rate of Speech".encode('utf-8'))
			worksheet.write(0, 12, "Professionalism/ Energetic/Enthusiastic".encode('utf-8'))
			worksheet.write(0, 13, "Section - D Soft Skills".encode('utf-8'))

			worksheet.write(0, 14, "Variation".encode('utf-8'))
			worksheet.write(0, 15, "Force Survey/False Promises/False Information".encode('utf-8'))
			worksheet.write(0, 16, "Movement During Interview".encode('utf-8'))
			worksheet.write(0, 17, "Geo Tagging".encode('utf-8'))
			worksheet.write(0, 18, "Fake Forms Count".encode('utf-8'))
			worksheet.write(0, 19, "Section - E Fatal Errors".encode('utf-8'))

			worksheet.write(0, 20, "total_forms_verified".encode('utf-8'))

			worksheet.write(0, 21, "quality_score % ".encode('utf-8'))
			worksheet.write(0, 22, "total_quality_score % ".encode('utf-8'))

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
				# print(surveyor_id_val, "====idd")

				count_total = 0
				if (len(data["surveyor_name"].split("-")) > 1   and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
					if (len(dates_arr) > 0):
						for dateVal in dates_arr:
							if (project_id_val != 0):
								# print("calling surveyresponse*******1")
								survey_response_obj = SurveyResponse.objects.filter(
									surveyor=Employee.objects.get(employee_id=surveyor_id_val),
									params__icontains=dateVal,
									project=Project.objects.get(pk=project_id_val)
								).values('uid').distinct()
								count_total = count_total + survey_response_obj.count()
							else:
								# print("calling surveyresponse*******2")
								survey_response_obj = SurveyResponse.objects.filter(
									surveyor=Employee.objects.get(employee_id=surveyor_id_val),
									params__icontains=dateVal
								).values('uid').distinct()
								count_total = count_total + survey_response_obj.count()

				################################################ For Surveyor_Count END####################################################

				worksheet.write(row, 1, str(data["surveyor_name"]).encode('utf-8'))

				worksheet.write(row, 2, round(float(str(data["alisectionAskipping"]).encode('utf-8')),2))
				# worksheet.write(row, 3, int(round(float(str(data["alisectionAknowledge"]).encode('utf-8')))))
				# worksheet.write(row, 4, int(round(float(str(data["alisectionArecordings"]).encode('utf-8')))))
				# worksheet.write(row, 5, int(round(float(str(data["alisectionAvoice"]).encode('utf-8')))))
				worksheet.write(row, 3, round(float(str(data["alisectionAPercent"]).encode('utf-8')),2))


				worksheet.write(row, 4, round(float(str(data["alisectionBskills"]).encode('utf-8')),2))
				# worksheet.write(row, 8, int(round(float(str(data["alisectionBknowledge"]).encode('utf-8')))))
				# worksheet.write(row, 9, int(round(float(str(data["alisectionBrecordings"]).encode('utf-8')))))
				worksheet.write(row, 5, round(float(str(data["alisectionBPercent"]).encode('utf-8')),2))


				worksheet.write(row, 6, round(float(str(data["alisectionCpolite"]).encode('utf-8')),2))
				worksheet.write(row, 7, round(float(str(data["alisectionCspeech"]).encode('utf-8')),2))
				worksheet.write(row, 8, round(float(str(data["alisectionCprofessional"]).encode('utf-8')),2))
				worksheet.write(row, 9, round(float(str(data["alisectionCPercent"]).encode('utf-8')),2))


				worksheet.write(row, 10, round(float(str(data["alisectionDpolitecourteous"]).encode('utf-8')),2))
				worksheet.write(row, 11, round(float(str(data["alisectionDrateofspeech"]).encode('utf-8')),2))
				worksheet.write(row, 12, round(float(str(data["alisectionDprofessionalismenergeticenthusiastic"]).encode('utf-8')),2))
				worksheet.write(row, 13, round(float(str(data["alisectionDPercent"]).encode('utf-8')),2))


				worksheet.write(row, 14, round(float(str(data["alisectionEvariation"]).encode('utf-8')),2))
				worksheet.write(row, 15, round(float(str(data["alisectionEsurvey"]).encode('utf-8')),2))
				worksheet.write(row, 16, round(float(str(data["alisectionEmovement"]).encode('utf-8')),2))
				worksheet.write(row, 17, round(float(str(data["alisectionEtagging"]).encode('utf-8')),2))
				worksheet.write(row, 18, round(float(str(data["sectionEfakeForms"]).encode('utf-8')),2))
				worksheet.write(row, 19, round(float(str(data["alisectionEtotal"]).encode('utf-8')),2))

				worksheet.write(row, 20, round(float(str(data["surveyor_name__count"]).encode('utf-8')),2))
				worksheet.write(row, 21, int(round(float(str(data["qualityPercent"]).encode('utf-8')))))
				worksheet.write(row, 22, int(round(float(str(100).encode('utf-8')))))
				# worksheet.write(row,24, str(data["surveyor_name"]).encode('utf-8'))
				worksheet.write(row, 23, int(round(float(str(count_total).encode('utf-8')))))
				# worksheet.write(row, 24, str(data["alisectionAPercent"]).encode('utf-8'))
				# worksheet.write(row, 25, str(data["alisectionBPercent"]).encode('utf-8'))
				# worksheet.write(row, 26, str(data["alisectionCPercent"]).encode('utf-8'))




				row = row + 1


			workbook.close()
			output.seek(0)
		elif(type=="detailed_summary"):
			# print("shortttttt:::",request)
			row = 0
			col = 0
			worksheet.write(0, 1, "surveyor_name".encode('utf-8'))
			# worksheet.write(0, 2, "No Questions Skipping".encode('utf-8'))
			# worksheet.write(0, 3, "Thorough Knowledge of Questionnaire".encode('utf-8'))
			# worksheet.write(0, 4, "No Incomplete Recordings".encode('utf-8'))
			# worksheet.write(0, 5, "Respondent voice can be heard clearly/Background noises".encode('utf-8'))
			worksheet.write(0, 2,"Section - A Behavioural Aspect ".encode(
								'utf-8'))

			# worksheet.write(0, 7, "Good probing or questioning Skills".encode('utf-8'))
			# worksheet.write(0, 8, "Prompting Answer/ Options".encode('utf-8'))
			# worksheet.write(0, 9, "Good Convincing Skills".encode('utf-8'))
			worksheet.write(0, 3, "Section - B Subject Knowledge".encode('utf-8'))

			# worksheet.write(0, 11, "Being polite and courteous during survey".encode('utf-8'))
			# worksheet.write(0, 12, "Good rate of speech".encode('utf-8'))
			# worksheet.write(0, 13, "Professional / Enthusiastic / Energetic".encode('utf-8'))
			worksheet.write(0, 4, "Section - C Survey Handling Skills".encode('utf-8'))

			worksheet.write(0, 5, "Section - D Soft skills".encode('utf-8'))

			# worksheet.write(0, 15, "Variation".encode('utf-8'))
			# worksheet.write(0, 16, "Force Survey/False Promises/False Information".encode('utf-8'))
			# worksheet.write(0, 17, "Movement During Interview".encode('utf-8'))
			worksheet.write(0, 6, "Geo Tagging".encode('utf-8'))
			worksheet.write(0, 7, "Fake Forms Count".encode('utf-8'))
			worksheet.write(0, 8, "Section - E Fatal Errors".encode('utf-8'))

			worksheet.write(0, 9, "total_forms_verified".encode('utf-8'))

			worksheet.write(0, 10, "quality_score % ".encode('utf-8'))
			worksheet.write(0, 11, "total_quality_score % ".encode('utf-8'))

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
				# print(surveyor_id_val,"====idd====",project_id_val)

				count_total = 0
				if(len(data["surveyor_name"].split("-"))>1 and "interview_startdate" in request.GET.keys() and "interview_enddate" in request.GET.keys() and request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
					# print("surrrrrrr:::",dates_arr)
					if(len(dates_arr)>0):
						for dateVal in dates_arr:
							if(project_id_val!=0):
								# print(Employee.objects.get(employee_id=surveyor_id_val),"======valll")
								survey_response_obj = SurveyResponse.objects.filter(
									surveyor=Employee.objects.get(employee_id=surveyor_id_val),
									params__icontains=dateVal,
									project=Project.objects.get(pk=project_id_val)
								).values('uid').distinct()
								count_total =count_total + survey_response_obj.count()
							else:
								# print("callling elsee*")
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
				worksheet.write(row, 2, round(float(str(data["alisectionAPercent"]).encode('utf-8')),2))

				# worksheet.write(row, 7, str(data["alisectionBskills"]).encode('utf-8'))
				# worksheet.write(row, 8, str(data["alisectionBknowledge"]).encode('utf-8'))
				# worksheet.write(row, 9, str(data["alisectionBrecordings"]).encode('utf-8'))
				worksheet.write(row, 3, round(float(str(data["alisectionBPercent"]).encode('utf-8')),2))

				# worksheet.write(row, 11, str(data["alisectionCpolite"]).encode('utf-8'))
				# worksheet.write(row, 12, str(data["alisectionCspeech"]).encode('utf-8'))
				# worksheet.write(row, 13, str(data["alisectionCprofessional"]).encode('utf-8'))
				worksheet.write(row, 4, round(float(str(data["alisectionCPercent"]).encode('utf-8')),2))

				worksheet.write(row, 5, round(float(str(data["alisectionDPercent"]).encode('utf-8')),2))

				# worksheet.write(row, 15, str(data["alisectionDvariation"]).encode('utf-8'))
				# worksheet.write(row, 16, str(data["alisectionDsurvey"]).encode('utf-8'))
				# worksheet.write(row, 17, str(data["alisectionDmovement"]).encode('utf-8'))
				worksheet.write(row, 6, round(float(str(data["alisectionEtagging"]).encode('utf-8')),2))
				worksheet.write(row, 7, round(float(str(data["sectionEfakeForms"]).encode('utf-8')),2))
				worksheet.write(row, 8, round(float(str(data["alisectionEtotal"]).encode('utf-8')),2))

				worksheet.write(row, 9, round(float(str(data["surveyor_name__count"]).encode('utf-8')),2))
				worksheet.write(row, 10, int(round(float(str(data["qualityPercent"]).encode('utf-8')))))
				worksheet.write(row, 11, (float(str(100).encode('utf-8'))))
				# worksheet.write(row, 24, str(data["surveyor_name"]).encode('utf-8'))

				# worksheet.write(row, 24, str(data["alisectionAPercent"]).encode('utf-8'))
				# worksheet.write(row, 25, str(data["alisectionBPercent"]).encode('utf-8'))
				# worksheet.write(row, 26, str(data["alisectionCPercent"]).encode('utf-8'))
				if(request.GET["interview_enddate"]!="" and request.GET["interview_startdate"]!=""):
					worksheet.write(row, 16, (float(str(count_total).encode('utf-8'))))

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





	# def exportHourlyBased(self,data,auditor_arr,selected_date):
	# 	output = io.StringIO()
		# print(dir(output))
		# print(output.seek(0))
	# 	workbook = xlsxwriter.Workbook(output)
	# 	worksheet = workbook.add_worksheet('output')

	# 	row = 0
	# 	col = 0

	# 	# worksheet.write(0, 0, "Date".encode('utf-8'))
	# 	worksheet.write(0, 1, "Name".encode('utf-8'))
	# 	worksheet.write(0, 2, "00.00 - 01.00".encode('utf-8'))
	# 	worksheet.write(0, 3, "01.00 - 02.00".encode('utf-8'))
	# 	worksheet.write(0, 4, "02.00 - 03.00".encode('utf-8'))
	# 	worksheet.write(0, 5, "03.00 - 04.00".encode('utf-8'))
	# 	worksheet.write(0, 6, "04.00 - 05.00".encode('utf-8'))
	# 	worksheet.write(0, 7, "05.00 - 06.00".encode('utf-8'))
	# 	worksheet.write(0, 8, "06.00 - 07.00".encode('utf-8'))
	# 	worksheet.write(0, 9, "07.00 - 08.00".encode('utf-8'))
	# 	worksheet.write(0, 10, "08.00 - 09.00".encode('utf-8'))
	# 	worksheet.write(0, 11, "09.00 - 10.00".encode('utf-8'))
	# 	worksheet.write(0, 12, "10.00 - 11.00".encode('utf-8'))
	# 	worksheet.write(0, 13, "11.00 - 12.00".encode('utf-8'))
	# 	worksheet.write(0, 14, "12.00 - 13.00".encode('utf-8'))
	# 	worksheet.write(0, 15, "13.00 - 14.00".encode('utf-8'))
	# 	worksheet.write(0, 16, "14.00 - 15.00".encode('utf-8'))
	# 	worksheet.write(0, 17, "15.00 - 16.00".encode('utf-8'))
	# 	worksheet.write(0, 18, "16.00 - 17.00".encode('utf-8'))
	# 	worksheet.write(0, 19, "17.00 - 18.00".encode('utf-8'))
	# 	worksheet.write(0, 20, "18.00 - 19.00".encode('utf-8'))
	# 	worksheet.write(0, 21, "19.00 - 20.00".encode('utf-8'))
	# 	worksheet.write(0, 22, "20.00 - 21.00".encode('utf-8'))
	# 	worksheet.write(0, 23, "21.00 - 22.00".encode('utf-8'))
	# 	worksheet.write(0, 24, "22.00 - 23.00".encode('utf-8'))
	# 	worksheet.write(0, 25, "23.00 - 00.00".encode('utf-8'))

	# 	worksheet.write(0, 27, "Total Count".encode('utf-8'))


	# 	row = row + 1
	# 	col = 0
		# print(data)
	# 	for hrdata in auditor_arr:
			# print(hrdata)
	# 		if("name" in hrdata.keys()):
	# 			# worksheet.write(row, 0, str(selected_date).encode('utf-8'))
	# 			worksheet.write(row, 1, str(hrdata["name"]).encode('utf-8'))
	# 			worksheet.write(row, 2, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 3, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 4, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 5, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 6, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 7, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 8, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 9, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 10, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 11, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 12, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 13, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 14, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 15, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 16, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 17, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 18, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 19, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 20, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 21, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 22, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 23, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 24, int(str(0).encode('utf-8')))
	# 			worksheet.write(row, 25, int(str(0).encode('utf-8')))

	# 			worksheet.write(row, 27, int(str(len(hrdata["obj"])).encode('utf-8')))




				# print(hrdata["obj"],"=====",hrdata["name"])
	# 			hour_count={}
	# 			for hourlyData in hrdata["obj"]:
					# print(hourlyData.created_at.hour)
	# 				if(hourlyData.created_at.hour in hour_count.keys()):
	# 					hour_count[hourlyData.created_at.hour] = hour_count[hourlyData.created_at.hour]+1
	# 				else:
	# 					hour_count[hourlyData.created_at.hour] = 1
				# print(hour_count)

	# 			for x in hour_count.keys():
					# print(hour_count[x],"====hour::",x,"   col:::",hourlyData.created_at.hour+2)
	# 				worksheet.write(row, x+2 , int(str(hour_count[x]).encode('utf-8')))

	# 		row = row + 1

	# 	# for data in data:
		    # print(data)
		    # print(data["starting_hour"],"======",data["ending_hour"]," count::",len(data["hourly_uids"]))
	# 	#     date_time_obj = data["starting_hour"]
	# 	#     date_time_obj = data["ending_hour"]
	# 	#     d=(date_time_obj.date())
	# 	#
	# 	#
	# 	#     a = (date_time_obj.time())
	# 	#     h=(a.hour)
		    # print(h)
	# 	#
	# 	#
		    # print(data["hourly_uids"],"<<<<hourly auditor ids::::",h)
	# 	#
	# 	#     worksheet.write(1, col, str(d).encode('utf-8'))
	# 	#
	# 	#     worksheet.write(1, h+2, str(len(data["hourly_uids"])).encode('utf-8'))
	# 	#     worksheet.write(1,27,str(data["hourly_auditor_ids"]).encode('utf-8'))
	# 	#
	# 	#     row = row + 1
	# 	#
	# 	#
	# 	#
	# 	#
	# 	#
	# 	#
	# 	#     # worksheet.write(row, 1, str(data["starting_hour"]).encode('utf-8'))
	# 	#     # worksheet.write(row, 2, str(data["ending_hour"]).encode('utf-8'))
	# 	#     # worksheet.write(row, 3, str(len(data["hourly_uids"])).encode('utf-8'))
	# 	#     # worksheet.write(row, 4, ",".join(map(str,data["hourly_uids"])).encode('utf-8'))
	# 	#     #row = row + 1


        
	# 	workbook.close()
		
		# print(output.seek(0))

	# 	response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	# 	response['Content-Disposition'] = 'attachment filename='+str(selected_date)+'_hourly.xlsx'
	# 	import gc
	# 	gc.collect()

	# 	return response
	
	def exportHourlyBased(self, data, auditor_arr, selected_date):
		output = io.BytesIO()  # Use BytesIO for binary data, which is required for xlsxwriter
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		worksheet = workbook.add_worksheet('output')

		row = 0
		col = 0

		# Write headers
		headers = [
			"Name", "00.00 - 01.00", "01.00 - 02.00", "02.00 - 03.00", "03.00 - 04.00",
			"04.00 - 05.00", "05.00 - 06.00", "06.00 - 07.00", "07.00 - 08.00", "08.00 - 09.00",
			"09.00 - 10.00", "10.00 - 11.00", "11.00 - 12.00", "12.00 - 13.00", "13.00 - 14.00",
			"14.00 - 15.00", "15.00 - 16.00", "16.00 - 17.00", "17.00 - 18.00", "18.00 - 19.00",
			"19.00 - 20.00", "20.00 - 21.00", "21.00 - 22.00", "22.00 - 23.00", "23.00 - 00.00",
			"Total Count"
		]

		for col, header in enumerate(headers):
			worksheet.write(row, col, header)

		row += 1

		# Write data
		for hrdata in auditor_arr:
			if "name" in hrdata.keys():
				worksheet.write(row, 1, hrdata["name"])
				total_count = len(hrdata.get("obj", []))
				worksheet.write(row, 25, total_count)

				hour_count = {}
				for hourlyData in hrdata.get("obj", []):
					hour = hourlyData.created_at.hour
					hour_count[hour] = hour_count.get(hour, 0) + 1

				for hour, count in hour_count.items():
					worksheet.write(row, hour + 2, count)

				row += 1

		workbook.close()
		output.seek(0)  # Go to the start of the BytesIO buffer

		response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = f'attachment; filename={selected_date}_hourly.xlsx'

		return response
