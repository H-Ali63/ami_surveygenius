
from __future__ import unicode_literals
from django.shortcuts import render

from django.db.models import Q

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from .models import *

from django.contrib.auth.models import User



# Create your views here.
class HomePage(TemplateView):
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
            return HttpResponseRedirect('/v2')

            #code for abhijeet dange

            # if request.user.user_employee.employee_id == 112498:
                
            #     projects = Project.objects.filter(Q(name__icontains="station") | Q(name__icontains="train") | Q(name__icontains="counter") | Q(name__icontains="images") )

            #     data['projects'] = []

            #     for project in projects:
            #         data['projects'].append(project)
                
            # else:
            #     data = self.showProjects(data)  

            # if 'project' in request.GET.keys():        #here we select the project from quality.html project dropdownlist
            #     self.showQualityReports(request, data)
            #     print(self.showQualityReports(request, data))
            # else:
            #     data['showOptionsFlag'] = False
            #     data['showDataFlag'] = False
        # elif request.user.user_employee.designation.department.name == 'Finance':
        #     return HttpResponseRedirect('/expenses')
        # else:
        #     return HttpResponseRedirect('/surveyors')
        return render(request, 'index.html', data)
    

    # def showProjects(self, data):
    #     projects = Project.objects.filter(active=True)
    #     # projects = Project.objects.all()
    #     data['projects'] = []

    #     for project in projects:
    #         data['projects'].append(project)

    #     return data

    # def showQualityReports(self, request, data):
    #     print(request.GET['project'])                   #project id get
    #     print(Project.objects.filter(pk=request.GET['project'])[0])  #get project name
    #     if str(request.GET['project']) == "":
    #         data['showOptionsFlag'] = False
    #         data['showDataFlag'] = False
    #         data['nccs'] = False
    #     else:
    #         if Project.objects.filter(pk=request.GET['project'])[0].nccs == True:
    #             if request.user.user_employee.designation.department.name == 'Product':
    #                 data['nccs'] = True

    #         data['project'] = request.GET['project']
    #         data['showOptionsFlag'] = True
    #         if request.user.user_employee.designation.department.name == 'Product' or \
    #             request.user.user_employee.designation.department.name == 'Data Analysis' or \
    #             request.user.user_employee.designation.department.name == 'Finance' or \
    #             request.user.user_employee.designation.department.name == 'Accounts' or \
    #             request.user.user_employee.designation.department.name == 'Management' or \
    #             (request.user.user_employee.designation.department.name == 'Operations' and \
    #             request.user.user_employee.designation.name in ['Manager', 'OPERATIONS COORDINATOR', 'Assistant_Manager', 'Head']) or \
    #             (request.user.user_employee.designation.department.name == 'Training' and \
    #             request.user.user_employee.designation.name in ['Manager', 'Assistant Manager', 'Assistant_Manager', 'Head']) or \
    #             request.user.user_employee.designation.department.name == 'HR' or \
    #             request.user.user_employee.designation.department.name == 'HR Analytics' or \
    #             (request.user.user_employee.designation.department.name == 'Quality' and \
    #             request.user.user_employee.designation.name in ['Assistant_Manager', 'Manager', 'Senior executive-Quality Assurance', 'Head', 'Senior executive']) or \
    #             (request.user.user_employee.designation.department.name == 'DRC' and \
    #             request.user.user_employee.designation.name in ['Quality Assurance', 'Manager']):
    #             data['showDataFlag'] = True

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
    

def user_data(request):
 

    import mysql.connector
    cnx = mysql.connector.connect(user='root', password='axis@123',
                                host='192.168.1.32',
                                database='surveygeniusdb')


    mycursor = cnx.cursor()

    query = ("SELECT username FROM auth_user ORDER BY `id` ASC")


    mycursor.execute(query)

    myresult = mycursor.fetchall()

    # print(myresult)

    listed = []

    for i in myresult:
        listed.append(*i)
        print(*i)


    print(listed)

    for username in listed:

        user = User.objects.create(username = username,password = "axis@123")
        user.save()


    cnx.close()

    return(request,'<h1>done</h1>')