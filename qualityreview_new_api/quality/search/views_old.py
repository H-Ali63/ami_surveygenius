
from __future__ import unicode_literals
from django.shortcuts import render,HttpResponse

from django.db.models import Q
import mysql.connector

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from .models import *
import requests
from django.conf import settings 
from django.db.models import FloatField, F, Sum, Count, ExpressionWrapper, Value, Case, When,Q
from django.db.models.functions import Cast

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
            return HttpResponseRedirect('/login')
        
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
        elif request.user.user_employee.designation.department.name == 'Finance':
            return HttpResponseRedirect('/expenses')
        else:
            return HttpResponseRedirect('/surveyors')
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

    def post(self, request):
        data = {'flag': True, 'message': 'Please enter your Credentials'}
        print (request.POST,'================data')
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        #print "user===",user
        if user is not None:
            login(request, user)
            #print "User::"
            #print user.user_employee.user_role
            # if user.user_employee.user_role == "client":
            #     return HttpResponseRedirect('/client_dashboard')
            # else:
            #     if user.user_employee.designation.name == "Verifier":
            #         return HttpResponseRedirect('/bulkrecording_test')
            #     else:
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


def user_upload(request):

    token = settings.API_KEY
       
    headers = {"Authorization":token,"accept":"application/json","locale":"en"}

    # dict_of_surveyors_with_surveyid = defaultdict(list)

    
    surveyors_url = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/surveyor-list?page=1&size=600"
    response = requests.get(surveyors_url, headers=headers, timeout=20)

    # query ="select username from auth_user where date_joined > 2024-08-29 10:47:12.000000"

    # mycursor.execute(query)

    # mylist = mycursor.fetchall()
    surveyor_data = response.json()
    list_of_values  = A_app_surveyors.objects.values_list('a_app_id')
    surveyor_name_aapp = ''
    surveyor_mobileno_aapp=''
    # print(mylist)
    for surveyor in surveyor_data['data']['list']:
        print(surveyor)
        surveyor_name_aapp = surveyor.get('name', '')
        
        surveyor_id_aapp = surveyor.get('id', None)
        if surveyor_id_aapp not in list_of_values:
            try:
                splitted_id = (surveyor_name_aapp.split("(")[1][0:-1]).strip()
                surveyor_name_aapp = surveyor.get('name', '')
                surveyor_id_aapp = surveyor.get('id', None)
                surveyor_mobileno_aapp = surveyor.get('mobileNumber', '')
                emp = Employee.objects.get(employee_id=splitted_id)

                A_app_surveyors.objects.create(a_app_id=surveyor_id_aapp,
                                                                                            surveyor_name=surveyor_name_aapp,
                                                                                            mobile_number=surveyor_mobileno_aapp,
                                                                                            emp_id=emp)
            except Exception as e:
                print("error",e)
        

   
    return HttpResponse('<h1>donnnnnnnnnn</h1>')

