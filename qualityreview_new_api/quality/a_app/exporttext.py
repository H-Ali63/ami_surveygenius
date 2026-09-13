
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from search.models import * #change
import MySQLdb
import csv
from django.http import JsonResponse
from datetime import datetime

from time import mktime
# from mainapp.tasks import *
import io
#from p##print() import p##print()
from random import randint
import os

from dateutil.parser import parse
from django.db.models import Q
from dateutil import tz
import requests
import zipfile
import xml.etree.ElementTree as ET
import io


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

# Rate-limit imports
from quality.ratelimit import rate_limit, get_client_ip  #type: ignore


@method_decorator(login_required(login_url='/login'), name='dispatch')
@method_decorator(
    rate_limit(limit=10, window_seconds=60, scope='export',
               key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}"),
    name='dispatch',
)
class Export_Response(TemplateView):

    def exporttocsvfromdump(self, request, projectobj):
            
            if request.GET['fromdate'] and request.GET['todate']:
                start = request.GET['fromdate']
                end = request.GET['todate']

                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
                day_diff = (end_date - start_date).days
                print(start_date,end_date)

                from django.contrib import messages
                if day_diff < 0:
                    messages.error(request, "End date cannot be before start date.")
                    return redirect('Export_Response')  # Replace 'your_view_name' with your actual view name
                if day_diff > 7:
                    messages.error(request, "The difference between the dates should not exceed 7 days.")
                    return redirect('Export_Response') 
                # if day_diff < 0:
                #     return JsonResponse({"error": "End date cannot be before start date."}, status=400)
                # if day_diff > 7:
                #     return JsonResponse({"error": "The difference between the dates should not exceed 7 days."}, status=400)
                # print(projectobj.capi_checklist_id)
                
                prj = Project.objects.filter(id = projectobj.id).values_list('name',flat=True)
                
                
                token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyQ29kZSI6InFjYXVkaXQiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczODc1MTk4NiwiZXhwIjoxNzM5MzU2Nzg2fQ.-AwonEHMH6wCXl5dBTAtvoPzYw7UJd-3JwvzslTKrRI"
                headers = {"Authorization":token,"accept":"application/json","locale":"en"}
                Export_data_api = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-download/download-range/{projectobj.capi_checklist_id}?format=excel&download=true&startDate={start}&endDate={end}"

                try:
                    response = requests.get(Export_data_api, headers=headers)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json().get('data', {})
                except Exception as e:
                    logger.exception('Export API error')
                
                print(response)
                file_like_object = io.BytesIO(response.content)

                def decode_ooxml(file_like_object):
                    # Check if the file is a valid OOXML file
                    try:
                        with zipfile.ZipFile(file_like_object) as zip_file:
                            # Check if the file contains the required XML files
                            if 'xl/_rels/workbook.xml.rels' in zip_file.namelist():
                                # Extract the workbook.xml.rels file
                                with zip_file.open('xl/_rels/workbook.xml.rels') as rels_file:
                                    # Parse the XML file
                                    rels_xml = ET.parse(rels_file)
                                    # Get the root element
                                    root = rels_xml.getroot()
                                    # Print the relationships
                                    for rel in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                                        print(f"ID: {rel.attrib['Id']}, Type: {rel.attrib['Type']}, Target: {rel.attrib['Target']}")
                            else:
                                print("Not a valid OOXML file.")
                    except zipfile.BadZipFile:
                        print("Not a valid zip file.")

                decode_ooxml(file_like_object)
                        
                        ## function for showing projects which are activ
                    
                response = HttpResponse(file_like_object.getvalue(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{prj[0]}.xlsx"'

                return response
            else:
                return JsonResponse({"error": "Both Start Date and End Date are required."}, status=400)
  
        # Open database connection
        # Open database connection

        # below is commented becoz it is not need

        # db_config = json.dumps(settings.CELERY_DATABASE_CONFIG);
        #
        # # making db_config
        # self.db_config_host = str(json.loads(db_config)['host']);
        # self.db_config_user = str(json.loads(db_config)['user']);
        # self.db_config_port = str(json.loads(db_config)['port']);
        # self.db_config_pass = str(json.loads(db_config)['pass']);
        # self.db_config_database = str(json.loads(db_config)['database']);
        #
        # # commented becoz of configuring
        # self.db = MySQLdb.connect(self.db_config_host, self.db_config_user, self.db_config_pass,self.db_config_database, charset='utf8', use_unicode=True)
        # # self.db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
        # self.cursor = self.db.cursor()

    def get(self, request):
        data = {
            'htmlfilename': 'a_app_templates/a_app_search_quality.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            }

        try:
            projectid = request.GET['project']

            projectobj = Project.objects.get(id=projectid)
            data['project'] = projectobj
            # self.checklist_id = projectobj.capi_checklist_id
            # self.fetchallcheckpoints()
        except Exception as e:
            data['project'] = None

    
                #print(request.GET.items())
        if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis' or request.user.user_employee.designation.department.name == 'Training':    ### added for dinesh rajan
     
                return self.exporttocsvfromdump(request, projectobj)
        else:
            return render(request, 'index.html', data)


    
    
    def post(self,request):
        data = {
            'htmlfilename': 'a_app_templates/a_app_search_quality.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            }

        try:
            projectid = request.GET['project']

            projectobj = Project.objects.get(id=projectid)
            data['project'] = projectobj
            # self.checklist_id = projectobj.capi_checklist_id
            # self.fetchallcheckpoints()
        except Exception as e:
            data['project'] = None

    
                #print(request.GET.items())
        if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis' or request.user.user_employee.designation.department.name == 'Training':    ### added for dinesh rajan
     
                return self.exporttocsvfromdump(request, projectobj)
        else:
            return render(request, 'index.html', data)
        













































@method_decorator(login_required(login_url='/login'), name='dispatch')
@method_decorator(
    rate_limit(limit=10, window_seconds=60, scope='export_new',
               key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}"),
    name='dispatch',
)
class Export_new_Response(TemplateView):

    def exporttocsvfromdump(self, request, projectobj):
            
            if request.GET['fromdate'] and request.GET['todate']:
                start = request.GET['fromdate']
                end = request.GET['todate']

                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
                day_diff = (end_date - start_date).days
                print(start_date,end_date)

                from django.contrib import messages
                if day_diff < 0:
                    messages.error(request, "End date cannot be before start date.")
                    return redirect('Export_Response')  # Replace 'your_view_name' with your actual view name
                if day_diff > 7:
                    messages.error(request, "The difference between the dates should not exceed 7 days.")
                    return redirect('Export_Response') 
                # if day_diff < 0:
                #     return JsonResponse({"error": "End date cannot be before start date."}, status=400)
                # if day_diff > 7:
                #     return JsonResponse({"error": "The difference between the dates should not exceed 7 days."}, status=400)
                # print(projectobj.capi_checklist_id)
                
                prj = Project.objects.filter(id = projectobj.id).values_list('name',flat=True)
                
                
                token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiQ1IxNzM4ODM2MDE1MTMwT1IiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczODgzNjAxNX0.YWpi1cSg1-PTseqUtQwP8gs8WVWZdZCDeqjy6I8Jtno"
                headers = {"Authorization":token,"accept":"application/json","locale":"en"}
                # Export_data_api = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-download/download-range/{projectobj.capi_checklist_id}?format=excel&download=true&startDate={start}&endDate={end}"
                Export_data_api = f"https://api-dev.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-download/download-range/{projectobj.capi_checklist_id}?startDate={start}&endDate={end}"

                try:
                    response = requests.get(Export_data_api, headers=headers)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json().get('data', {})
                except Exception as e:
                    logger.exception('Export API error')
                
                messages.success(request, data.get("message", "No message from API"))
                
                        ## function for showing projects which are activ
                    
                

                return render(request, "index.html")
            else:
                return JsonResponse({"error": "Both Start Date and End Date are required."}, status=400)
            

  
    from django.contrib import messages
    def get(self, request):

        data = {
            'htmlfilename': 'a_app_templates/a_app_search_quality.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'showOptionsFlag': False,
            'showDataFlag': False,
        }

        from django.contrib import messages

        

        # -------------------------
        # Get project from request
        # -------------------------
        project_id = request.GET.get('project')
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
        start = request.GET.get('fromdate')
        end = request.GET.get('todate')

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
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiQ1IxNzM4ODM2MDE1MTMwT1IiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczODgzNjAxNX0.YWpi1cSg1-PTseqUtQwP8gs8WVWZdZCDeqjy6I8Jtno"
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
            logger.exception('API Error')
            messages.error(request, "Something went wrong while calling API.")

        # data['s']

        return render(request, "index.html", data)


    
    
    def post(self,request):
        data = {
            'htmlfilename': 'a_app_templates/a_app_search_quality.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            }

        try:
            projectid = request.GET['project']

            projectobj = Project.objects.get(id=projectid)
            data['project'] = projectobj
            # self.checklist_id = projectobj.capi_checklist_id
            # self.fetchallcheckpoints()
        except Exception as e:
            data['project'] = None

    
                #print(request.GET.items())
        if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis' or request.user.user_employee.designation.department.name == 'Training':    ### added for dinesh rajan
     
                return self.exporttocsvfromdump(request, projectobj)
        else:
            return render(request, 'index.html', data)
        





@method_decorator(login_required(login_url='/login'), name='dispatch')
@method_decorator(
    rate_limit(limit=20, window_seconds=60, scope='download_status',
               key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}"),
    name='dispatch',
)
class Download_status(TemplateView):

    def get(self,request):


        data = {
            'htmlfilename': 'a_app_templates/a_app_download_status.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'maindata' : [],
            'project_name': 'unknown',
            'token':'unknown'
            }

       
        try:
            projectdata = request.GET['project']

            if "." in projectdata:
                projectid = projectdata.split('.')[0]
            else:
                projectid = projectdata

            projectobj = Project.objects.get(id=projectid)
            data['project'] = projectobj
            # self.checklist_id = projectobj.capi_checklist_id
            # self.fetchallcheckpoints()

            # -----------------------------------------
            # API Call Section
            # -----------------------------------------
            token = AccessToken.get_existing_token().token
            #token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiQ08xNjk1MjAzNzcyNjQ4RVIiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTY5NTIwMzc3Mn0.ExzW5mj7iZLOouAgHG4iVSVy60xTTIBW64jPxYrryjU"
            headers = {"Authorization": token, "accept": "application/json", "locale": "en"}

            api_url = (
                f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-download/survey-report-tasks?page=1&size=10&choiceId={projectobj.capi_checklist_id}"
            )

            data['token'] = '***'  # Never expose the token to the template/frontend

            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()  # HTTP error
                api_json = response.json()
                api_data = api_json.get('data')

                api_list = api_data.get("data")
                data['project'] = api_list['list'][0]['choiceName']
                data['maindata'] = api_list['list']

                # messages.success(request, api_message)

            except ValueError:
                logger.exception('Value Error in API response')
                # messages.error(request, "API did not return valid JSON.")
            except Exception as e:
                logger.exception('API Error')
                # messages.error(request, "Something went wrong while calling API.")

            return render(request, 'index.html', data)
        # data['s']
        except Exception as e:
            data['project'] = None
        #print(request.GET.keys())

        # if 'export' in request.GET.keys() and \
        #     (request.user.user_employee.designation.name == "Manager" or \
        #     request.user.user_employee.designation.department.name == 'Training' or \
        #     request.user.user_employee.designation.department.name == "Finance" or \
        #     request.user.user_employee.designation.department.name == "HR" or \
        #     request.user.user_employee.designation.department.name == "HR Analytics" or \
        #     request.user.user_employee.designation.department.name == "Data Analysis" or \
        #     request.user.user_employee.designation.department.name == "Accounts" or \
        #     request.user.user_employee.designation.department.name == "Quality" or \
        #     (request.user.user_employee.designation.department.name == 'Operations' and \
        #     (request.user.user_employee.designation.name in ['Executive', 'Head', 'Assistant_Manager', 'OPERATIONS COORDINATOR', 'Senior executive', 'Senior executive-Quality Assurance']) or (request.user.user_employee.designation.name == 'Manager')) or \
        #     request.user.user_employee.designation.department.name == "Management" or \
        #     request.user.user_employee.designation.department.name == "PMS") :          ### added for dinesh rajan
        #     if request.GET['export'] == 'text':
        #         #print(request.GET.items())
        #         if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis' or request.user.user_employee.designation.department.name == 'Training':    ### added for dinesh rajan
        #             # Direct download
        #             # self.fetchcheckpointtextdata()
        #             # self.data_to_csv('textoutput')
        #             # return self.exporttocsv(request, self.finaloutput)

        #             # Add to dump
        #             # exportdataview(self.checklist_id, self.checkpoint_ids)
        #             # exportdataview.delay(self.checklist_id, self.checkpoint_ids)
                    
        #             return self.exporttocsvfromdump(request, projectobj)

        #     elif request.GET['export'] == 'code':
        #         if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis':
                   
        #             return self.exporttocsvfromdump(request, projectobj)
        return render(request, 'index.html', data)

    def post(self, request):
        data = {'flag': True, 'message': 'Please enter your Credentials'}
        # data = None
        if(not request.user.is_active):
            return HttpResponseRedirect('/login');
        else:
            # tasks = PriorityTasksSchedulesID.objects.all()
            data = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    # 'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    'htmlfilename': 'a_app_templates/a_app_search_quality.html',
                    'maindata': [],
                    
                }
        return render(request, 'index.html', data);



@login_required(login_url='/login')
@rate_limit(limit=10, window_seconds=60, scope='proxy_download',
            key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}")
def proxy_download_survey(request):
    project = request.GET.get('Project')

    task_id = project.split('-')[0]

    project_name = project.split('-')[1]
    
    # Use the token from your session or hardcode if it's static
    token = AccessToken.get_existing_token().token
    
    if not task_id:
        return JsonResponse({'error': 'Missing taskId'}, status=400)

    url = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-download/download-survey-report?taskId={task_id}"
    
    headers = {
        "Authorization": token, # Add 'Bearer ' if needed
        "Accept": "application/octet-stream",
        "locale": "en"
    }

    try:
        # Make the request from your SERVER (No CORS issues here)
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 200:
            # Create a Django File Response
            django_response = HttpResponse(
                response.content, 
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            django_response['Content-Disposition'] = f'attachment; filename="{project_name}_{task_id}.xlsx"'
            return django_response
        else:
            logger.warning("proxy_download_survey upstream failure status=%s task_id=%s", response.status_code, task_id)
            return JsonResponse({'success': False, 'message': 'Could not retrieve the file. Please try again.'}, status=502)

    except Exception:
        logger.exception("proxy_download_survey failed for task_id=%s", task_id)
        return JsonResponse({'success': False, 'message': 'Something went wrong. Please try again.'}, status=500)