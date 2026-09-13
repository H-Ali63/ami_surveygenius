
from __future__ import unicode_literals
import logging
from django.shortcuts import render,HttpResponse #type: ignore

from django.db.models import Q #type: ignore
import mysql.connector #type: ignore

from django.shortcuts import render, redirect #type: ignore
from django.views.generic import TemplateView #type: ignore
from django.shortcuts import HttpResponseRedirect #type: ignore
from django.contrib.auth import authenticate, login, logout #type: ignore
from django.contrib.auth.models import User #type: ignore
from django.contrib.sessions.models import Session #type: ignore
from django.core.exceptions import SuspiciousOperation #type: ignore
from django.conf import settings #type: ignore
from django.utils.decorators import method_decorator #type: ignore
from django.utils import timezone #type: ignore
from django.utils.http import url_has_allowed_host_and_scheme #type: ignore
from django.db import close_old_connections #type: ignore
import hashlib
from quality.ratelimit import rate_limit, get_client_ip #type: ignore
from quality.access_control import require_staff #type: ignore
from .models import *

logger = logging.getLogger(__name__)
import requests #type: ignore
from django.db.models import FloatField, F, Sum, Count, ExpressionWrapper, Value, Case, When,Q #type: ignore
from django.db.models.functions import Cast #type: ignore
from django.http import JsonResponse #type: ignore
from datetime import datetime

from time import mktime
# from mainapp.tasks import *
import io
#from p##print() import p##print()
from random import randint
import os

from dateutil.parser import parse #type: ignore
from django.db.models import Q #type: ignore
from dateutil import tz #type: ignore
import requests #type: ignore
import zipfile
import xml.etree.ElementTree as ET
import io


def _invalidate_other_sessions(user_id, current_session_key):
    """Keep only the current session for this user.

    Corrupted or old-key sessions are silently skipped — they are already
    inaccessible and will be removed by ``clearsessions``.
    """
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_str = str(user_id)

    for session in active_sessions.iterator():
        if session.session_key == current_session_key:
            continue
        try:
            session_data = session.get_decoded()
        except SuspiciousOperation:
            # Session was signed with a different SECRET_KEY — skip silently.
            continue
        except Exception:
            continue

        if session_data.get("_auth_user_id") == user_id_str:
            session.delete()


# def access_token(): #####new changes
#     accept = "application/json"
#     locale = "en"
#     refresh_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiQU0xNzM0NjAzMTk2MDkwTUkiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczNDYwMzE5Nn0.xmlInt8oOUISSaCD5wCGpHDBIoepbx5PvT4CkjAPm_o";
#     url = "https://api-uat.axismyindia.in/v1/user/partner";
#     parameters = {"accept":accept,"locale":locale,"refresh_token":refresh_token}

#     r = requests.patch(url,headers=parameters)
#     print(r.json())
#     access_token = r.json()['data']['access_token']
#     print(access_token)

#     return access_token

# Create your views here.
class HomePage(TemplateView): ####new changes
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % ('/login', request.path))
        
        #print(request.user)


        isGas = False

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'showOptionsFlag': False,
            'showDataFlag': False,
            'gasDisplay' :isGas
        }

        allowed_deps = ['Accounts', 'Product', 'Quality', 'Finance', 'HR', 'HR Analytics', 'Management', 'Operations', 'Training',  'Data Analysis', 'DRC']

        if request.user.user_employee.designation.department.name in allowed_deps:
            data['htmlfilename'] = 'a_app_templates/a_app_search_quality.html'
            # return HttpResponseRedirect('/v2')

            data = self.showProjects(data)   ##### here we show the projects which are active

            if 'project' in request.GET.keys():        ### here we select the project from quality.html project dropdownlist
                self.showQualityReports(request, data)
                print(self.showQualityReports(request, data))

                if request.user.user_employee.employee_id == '109955':    ### added for dinesh ranjan

                    data["showOptionsFlag"] = False

            else:
                data['showOptionsFlag'] = False
                data['showDataFlag'] = False

        return render(request, 'index.html', data)



    def post(self,request):


        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % ('/login', request.path))
        
        #print(request.user)


        isGas = False

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'showOptionsFlag': False,
            'showDataFlag': False,
            'gasDisplay' :isGas
        }

        from django.contrib import messages #type: ignore

        # -------------------------
        # Get project from request
        # -------------------------
        data['htmlfilename'] = 'a_app_templates/a_app_search_quality.html'

        if request.POST.get('submit') == 'Text':
            project_id = request.GET.get('project')

            print(request.GET,"requeiwaoue")

            if project_id:
                try:
                    projectobj = Project.objects.get(id=project_id)
                    data['project'] = projectobj
                except Project.DoesNotExist:
                    messages.error(request, "Invalid project selected.")
                    data['project'] = None
            else:
                data['project'] = None

            # -----------------------------------------
            # Check department level authorization
            # -----------------------------------------
            allowed_depts = ['Product', 'Operations', 'Data Analysis', 'Training']

            if data['department'] not in allowed_depts:
                return render(request, 'index.html', data)

            # -----------------------------------------
            # Date validation
            # -----------------------------------------
            start = request.POST.get('fromdate')
            end = request.POST.get('todate')

            if not start or not end:
                messages.error(request, "Both start and end date are required.")
                return render(request, "index.html", data)

            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                messages.error(request, "Invalid date format.")
                return render(request, "index.html", data)

            day_diff = (end_date - start_date).days

            if day_diff < 0:
                messages.error(request, "End date cannot be before start date.")
                return redirect('Export_Response')

            if day_diff > 7:
                messages.error(request, "The difference between dates cannot exceed 7 days.")
                return redirect('Export_Response')

            # -----------------------------------------
            # API Call Section
            # -----------------------------------------
            token = AccessToken.get_existing_token().token
            #token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiQ1IxNzM4ODM2MDE1MTMwT1IiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczODgzNjAxNX0.YWpi1cSg1-PTseqUtQwP8gs8WVWZdZCDeqjy6I8Jtno"
            headers = {"Authorization": token, "accept": "application/json", "locale": "en"}

            api_url = (
                f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/"
                f"survey-response-download/download-range/{projectobj.capi_checklist_id}"
                f"?startDate={start}&endDate={end}"
            )

            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()  # HTTP error
                api_json = response.json()
                api_data = api_json.get('data')
                api_message = api_data.get("message", "No message from API")

                messages.success(request, api_message)

            except ValueError:
                messages.error(request, "API did not return valid JSON.")
            except Exception as e:
                print("API Error:", e)
                messages.error(request, "Something went wrong while calling API.")

            return render(request, 'index.html', data)
        # data['s']

    
        return render(request, 'index.html', data)
    

    def showProjects(self, data):
        projects = Project.objects.filter(active=True)
        # projects = Project.objects.all()
        data['projects'] = []

        for project in projects:
            data['projects'].append(project)

        return data
    
    def showQualityReports(self, request, data):
          #get project name
        if str(request.GET['project']) == "":
            data['showOptionsFlag'] = False
            data['showDataFlag'] = False
            data['nccs'] = False
        else:

            data['project'] = request.GET['project']
            data['showOptionsFlag'] = True
            if request.user.user_employee.designation.department.name == 'Product' or \
                request.user.user_employee.designation.department.name == 'Data Analysis' or \
                request.user.user_employee.designation.department.name == 'Finance' or \
                request.user.user_employee.designation.department.name == 'Accounts' or \
                request.user.user_employee.designation.department.name == 'Management' or \
                (request.user.user_employee.designation.department.name == 'Operations' and \
                request.user.user_employee.designation.name in ['Manager', 'OPERATIONS COORDINATOR', 'Assistant_Manager', 'Head']) or \
                (request.user.user_employee.designation.department.name == 'Training' and \
                request.user.user_employee.designation.name in ['Manager', 'Assistant Manager', 'Assistant_Manager', 'Head']) or \
                request.user.user_employee.designation.department.name == 'HR' or \
                request.user.user_employee.designation.department.name == 'HR Analytics' or \
                (request.user.user_employee.designation.department.name == 'Quality' and \
                request.user.user_employee.designation.name in ['Assistant_Manager', 'Manager', 'Senior executive-Quality Assurance', 'Head', 'Senior executive']) or \
                (request.user.user_employee.designation.department.name == 'DRC' and \
                request.user.user_employee.designation.name in ['Quality Assurance', 'Manager']):
                data['showDataFlag'] = True


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return redirect('/login')

class LoginPage(TemplateView):
    def get(self, request):
        return render(request, 'login.html', {})

    @method_decorator(
        rate_limit(
            limit=10,
            window_seconds=300,
            scope='login',
            key_func=lambda r: f"{get_client_ip(r)}:{r.POST.get('username', '')}",
        )
    )
    def post(self, request):
        close_old_connections()
        data = {'flag': True, 'message': 'Please enter your Credentials'}
        user = authenticate(username=request.POST.get('username', ''), password=request.POST['password'])
        #print "user===",user
        if user is not None:
            login(request, user)
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            if not request.session.session_key:
                request.session.save()
            browser_parts = [
                request.META.get("HTTP_USER_AGENT", ""),
                request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
            ]
            request.session["browser_fingerprint"] = hashlib.sha256("|".join(browser_parts).encode("utf-8")).hexdigest()
            request.session["browser_last_seen"] = timezone.now().isoformat()
            #print "User::"
            #print user.user_employee.user_role
            # if user.user_employee.user_role == "client":
            #     return HttpResponseRedirect('/client_dashboard')
            # else:
            #     if user.user_employee.designation.name == "Verifier":
            #         return HttpResponseRedirect('/bulkrecording_test')
            #     else:
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect('/v2')
        else:
            data['message'] = 'Incorrect Login Credentials'
            data['flag'] = False

        return render(request, 'login.html', data)

    
class SurveyProjectPage(TemplateView):
    def __init__(self):
        pass
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % ('/login', request.path))


        isGas = False
        if (request.user.user_employee.designation.department.name == 'Operations' or
                request.user.user_employee.designation.department.name == 'Product' or
                request.user.user_employee.designation.department.name == 'Data Analysis' or
                request.user.user_employee.designation.department.name =='Management' or
                request.user.user_employee.designation.department.name =='HR' or
                request.user.user_employee.designation.department.name =='HR Analytics' or
                request.user.user_employee.employee_id == '103245' or
                request.user.user_employee.employee_id == '101836' or
                request.user.user_employee.employee_id == '102534' or
                request.user.user_employee.employee_id == '103002' or
                request.user.user_employee.employee_id == '102141' or
                request.user.user_employee.employee_id == '102057'):
            isGas = True

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'showOptionsFlag': False,
            'showDataFlag': False,
            'gasDisplay' :isGas,

        }

        allowed_deps = ['Accounts', 'Product', 'Quality', 'Finance', 'HR', 'HR Analytics', 'Management', 'Operations', 'Training',  'Data Analysis', 'DRC']

        if request.user.user_employee.designation.department.name in allowed_deps:
            data['htmlfilename'] = 'survey_quality.html'

            data = self.showProjects(data)

            check = self.getCheckPointIds(data)
            if 'project' in request.GET.keys():
                self.showQualityReports(request, data)

            else:
                data['showOptionsFlag'] = False
                data['showDataFlag'] = False


        elif request.user.user_employee.designation.department.name == 'Finance':
            return HttpResponseRedirect('/expenses')
        else:
            return HttpResponseRedirect('/surveyors')


        return render(request, 'index.html',data)



    def showProjects(self, data):
        projects = Project.objects.filter(active=True,is_gas_activity=True)
        data['projects'] = []

        for project in projects:
            data['projects'].append(project)
        return data

    def showQualityReports(self, request, data):
        if str(request.GET['project']) == "":
            data['showOptionsFlag'] = False
            data['showDataFlag'] = False
            data['nccs'] = False
        else:
            if Project.objects.filter(pk=request.GET['project'])[0].nccs == True:
                if request.user.user_employee.designation.department.name == 'Product':
                    data['nccs'] = True

            data['project'] = request.GET['project']
            data['activity'] = request.GET['activity']
            data['showOptionsFlag'] = True
            if request.user.user_employee.designation.department.name == 'Product' or \
                request.user.user_employee.designation.department.name == 'Finance' or \
                request.user.user_employee.designation.department.name == 'Data Analysis' or \
                request.user.user_employee.designation.department.name == 'Accounts' or \
                request.user.user_employee.designation.department.name == 'Management' or \
                (request.user.user_employee.designation.department.name == 'Operations' and \
                request.user.user_employee.designation.name in ['Manager', 'OPERATIONS COORDINATOR', 'Assistant_Manager', 'Head']) or \
                (request.user.user_employee.designation.department.name == 'Training' and \
                request.user.user_employee.designation.name in ['Manager', 'Assistant Manager', 'Assistant_Manager', 'Head']) or \
                request.user.user_employee.designation.department.name == 'HR' or \
                request.user.user_employee.designation.department.name == 'HR Analytics' or \
                (request.user.user_employee.designation.department.name == 'Quality' and \
                request.user.user_employee.designation.name in ['Manager', 'Senior executive-Quality Assurance', 'Senior executive', 'Head']) or \
                (request.user.user_employee.designation.department.name == 'DRC' and \
                request.user.user_employee.designation.name in ['Quality Assurance', 'Manager']):
                data['showDataFlag'] = True

        project_id = data['project']
        activity = data['activity']

        if ("startDate" in request.GET and request.GET["startDate"] != "" and "endDate" in request.GET and request.GET["endDate"] != ""):
            startDate = request.GET["startDate"]
            endDate = request.GET["endDate"]

        data["startDate"] = startDate
        data["endDate"] = endDate



    def getCheckPointIds(self,data):
        data["list_of_activity"] = []
        activity = []
        queries_id = "SELECT DISTINCT VALUE FROM `CHECKPOINT` WHERE CHECKPOINT_NAME='Activity'"
        self.cursor.execute(queries_id);
        queries_id = self.cursor.fetchall();

        for item in queries_id:
            for terms in item:
                #print terms
                activity.append(terms)


        joined_string = ",".join(activity)
        data["list_of_activity"] = joined_string.split(',')



# def dashboard(request):

#     project_ids = SurveyResponse.objects.all().values_list('project',flat = True).distinct()

#     surveyor_count = None

#     data = {}

#     for ids in project_ids:


#         project_name = Project.objects.get(id = ids)
#         project_name = project_name.name

        

#         # for value in SurveyResponse.objects.all():
#         qualityRecords = SurveyResponse.objects.filter(project=2).values('surveyor') \
#                         .annotate(surveyor_count=Count('surveyor'))
        
#         for i in qualityRecords:
#             surveyor_name = User.objects.get(user_employee=i['surveyor']).get_full_name()
#             print(surveyor_name)
#             uid = SurveyResponse.objects.filter(surveyor=i['surveyor']).exclude(uid__in=QualityReview.objects.values_list('uid', flat=True)).values_list('uid',flat=True)[:round(int(i['surveyor_count']) * 0.3)]

#             data = {project_name: project_name, uid:uid,surveyor_name:surveyor_name,surveyor_count:i['surveyor_count']}

#             return render(request,'dashboard_quality.html',data)

    
        

#     # qualityRecords = value.aggregate(surveyor_count = Count('surveyor')).filter(project = 20).values('surveyor','surveyor_count')
# 						# .annotate(surveyor_count=Count('surveyor_name', output_field=FloatField()))

#     # print(SurveyResponse.objects.annotate(each_surveyor = Count('surveyor')).values_list('uid','surveyor')[:round(qualityRecords)])
#     # print(qualityRecords)
#     # return render(request,'search_quality.html')


@require_staff
def user_upload(request):

    cnx2 = mysql.connector.connect(user='root', password=os.environ.get('SURVEYGENIUS_DB_PASSWORD', ''),
                              host='192.168.1.32',
                              port = '9000',
                              database='surveygeniusdb')
    
    mycursor = cnx2.cursor()

    if mycursor.is_connected():
        print('connected')

    # query ="select username from auth_user where date_joined > 2024-08-29 10:47:12.000000"

    # mycursor.execute(query)

    # mylist = mycursor.fetchall()

    # print(mylist)

    mycursor.close()

    

    user_last_uploaded = User.objects.values_list('username',flat=True)
    print(user_last_uploaded)
    return HttpResponse('<h1>donnnnnnnnnn</h1>')
