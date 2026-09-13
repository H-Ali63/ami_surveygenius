# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db.models import Q
from django.core.exceptions import SuspiciousOperation

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.conf import settings
from django.utils import timezone
import json
import requests
from datetime import datetime,timedelta
from search.models import Project

logger = logging.getLogger(__name__)


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

def access_token():
    accept = "application/json"
    locale = "en"
    refresh_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiQU0xNzM0NjAzMTk2MDkwTUkiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczNDYwMzE5Nn0.xmlInt8oOUISSaCD5wCGpHDBIoepbx5PvT4CkjAPm_o";
    url = "https://api-uat.axismyindia.in/v1/user/partner";
    parameters = {"accept":accept,"locale":locale,"refresh_token":refresh_token}

    r = requests.patch(url,headers=parameters)
    print(r.json())
    access_token = r.json()['data']['access_token']
    print(access_token)

    return access_token
        
class HomePage(TemplateView):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % ('/login', request.path))
        
        #print(request.user)

        if request.user.user_employee.employee_id == "104489":
            myurl = "hul"
            return HttpResponseRedirect('/inventory/{}/FinalStockReports'.format(myurl))

        if request.user.user_employee.employee_id == "105726":
            myurl = "hul"
            return HttpResponseRedirect('/inventory/{}/FinalStockReports'.format(myurl))

        elif request.user.user_employee.employee_id == "105826" or request.user.user_employee.employee_id == "105726":
            myurl = "pc"
            return HttpResponseRedirect('/inventory/{}/FinalStockReports'.format(myurl))
        elif request.user.user_employee.designation.department.name == "Client" and request.user.user_employee.designation.name == "UP Client":
            return HttpResponseRedirect('/operations/clientdashboard')

        if request.user.user_employee.employee_id == '104495' or request.user.user_employee.employee_id == '104496' or  request.user.user_employee.employee_id == '104497' or request.user.user_employee.employee_id == '104498':
             return HttpResponseRedirect('/inventory/hul/ConsumptionAtCity')


        print(request.user.user_employee.employee_id,"=======",request.user.user_employee.designation.department.name)


        isGas = False
        if (request.user.user_employee.designation.department.name == 'Operations' or
                request.user.user_employee.designation.department.name == 'Product' or
                request.user.user_employee.designation.department.name == 'Data Analysis' or
                request.user.user_employee.designation.department.name =='Management' or
                request.user.user_employee.designation.department.name =='HR' or
                request.user.user_employee.designation.department.name =='HR Analytics' or
                request.user.user_employee.employee_id=='103245' or
                request.user.user_employee.employee_id=='101836' or
                request.user.user_employee.employee_id=='102534' or
                request.user.user_employee.employee_id=='103002' or
                request.user.user_employee.employee_id=='102141' or
                request.user.user_employee.employee_id=='102057'):
            isGas = True

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'showOptionsFlag': False,
            'showDataFlag': False,
            'gasDisplay' :isGas
        }

        allowed_deps = ['Accounts', 'Product', 'Quality', 'Finance', 'HR', 'HR Analytics', 'Management', 'Operations', 'Training',  'Data Analysis', 'DRC']

        

        if request.user.user_employee.designation.department.name in allowed_deps:
            data['htmlfilename'] = 'a_app_templates/a_app_search_quality.html'

            #if 'from_date' and 'to_date' in request.GET.keys():
            
            data = self.showProjects(data)   ##### here we show the projects which are active

            if 'project' in request.GET.keys():        ### here we select the project from quality.html project dropdownlist
                self.showQualityReports(request, data)
                print(self.showQualityReports(request, data))

                if request.user.user_employee.employee_id == '109955':    ### added for dinesh ranjan

                    data["showOptionsFlag"] = False

            else:
                data['showOptionsFlag'] = False
                data['showDataFlag'] = False
        elif request.user.user_employee.designation.department.name == 'Finance':
            return HttpResponseRedirect('/expenses')
        else:
            return HttpResponseRedirect('/surveyors')
        return render(request, 'index.html', data)
    

    def showProjects(self, data): 
        
        token = access_token()
        
        headers = {"Authorization":token,"accept":"application/json","locale":"en"}

        url2 = "https://api-uat.axismyindia.in/v1/admin/surveyors/qc-service/surveys?page=1&limit=10&startDate=2024-12-12&endDate=2024-12-23"

        r2 = requests.get(url2,headers=headers)
        print(r2.json())

        test = r2.json()['data']['list'][0]
        print(test)
        list_of_append = test

        '''date_value = (datetime.today()-timedelta(days=1)).strftime('%d-%m-%Y')

        list_of_append = []

        for i,value in enumerate (test):
            for j in value:
                if datetime.today().strftime('%d-%m-%Y') in value[j][0]['AddedTime']:
                    employee = value[j][0]['Added_By']
                    list_of_append.append(employee)
        print(list_of_append)'''

        
        
        ## function for showing projects which are activ
            
        
        # projects = Project.objects.all()
        data['projects'] = []

        #for project in list_of_append:
        data['projects'].append(list_of_append)

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

    def post(self, request):
        data = {'flag': True, 'message': 'Please enter your Credentials'}
        user = authenticate(username=request.POST.get('username', ''), password=request.POST['password'])
        #print "user===",user
        if user is not None:
            login(request, user)
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            if not request.session.session_key:
                request.session.save()

            #print "User::"
            #print user.user_employee.user_role
            if user.user_employee.user_role == "client":
                return HttpResponseRedirect('/client_dashboard')
            else:
                if user.user_employee.designation.name == "Verifier":
                    return HttpResponseRedirect('/bulkrecording_test')
                else:
                    return HttpResponseRedirect('/')
        else:
            data['message'] = 'Incorrect Login Credentials'
            data['flag'] = False

        return render(request, 'login.html', data)




class SurveyProjectPage(TemplateView):
    def __init__(self):
        
        pass;

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
        print('qualityreports',)
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

        
