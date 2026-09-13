# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from mainapp.models import *
import MySQLdb
import csv
import datetime
from datetime import timedelta
from datetime import date
from time import mktime
from mainapp.tasks import *
import io
#from p##print() import p##print()
from random import randint
from mainapp.tasks import *
import os
import ast
import json
import xlsxwriter
from mainapp.additionalviews.nccssampling import *
from dateutil.parser import parse
from django.db.models import Q
from dateutil import tz
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3



import sys
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#print(BASE_DIR)

class ExportData(TemplateView):
    def __init__(self):
        self.checkpoint_ids = []
        self.answers = {}
        self.finaloutput = []

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
            'htmlfilename': 'exportdata.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'employee_pic': request.user.user_employee.get_profile_pic(),
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

        #print(request.GET.keys())

        if 'export' in request.GET.keys() and \
            (request.user.user_employee.designation.name == "Manager" or \
            request.user.user_employee.designation.department.name == 'Training' or \
            request.user.user_employee.designation.department.name == "Finance" or \
            request.user.user_employee.designation.department.name == "HR" or \
            request.user.user_employee.designation.department.name == "HR Analytics" or \
            request.user.user_employee.designation.department.name == "Data Analysis" or \
            request.user.user_employee.designation.department.name == "Accounts" or \
            request.user.user_employee.designation.department.name == "Quality" or \
            (request.user.user_employee.designation.department.name == 'Operations' and \
            (request.user.user_employee.designation.name in ['Executive', 'Head', 'Assistant_Manager', 'OPERATIONS COORDINATOR', 'Senior executive', 'Senior executive-Quality Assurance']) or (request.user.user_employee.designation.name == 'Manager')) or \
            request.user.user_employee.designation.department.name == "Management" or \
            request.user.user_employee.designation.department.name == "PMS") :          ### added for dinesh rajan
            if request.GET['export'] == 'text':
                #print(request.GET.items())
                if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis' or request.user.user_employee.designation.department.name == 'Training':    ### added for dinesh rajan
                    # Direct download
                    # self.fetchcheckpointtextdata()
                    # self.data_to_csv('textoutput')
                    # return self.exporttocsv(request, self.finaloutput)

                    # Add to dump
                    # exportdataview(self.checklist_id, self.checkpoint_ids)
                    # exportdataview.delay(self.checklist_id, self.checkpoint_ids)
                    
                    return self.exporttocsvfromdump(request, projectobj)

            elif request.GET['export'] == 'code':
                if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'Operations' or request.user.user_employee.designation.department.name == 'Data Analysis':
                    # self.fetchcheckpointcodedata()
                    # self.data_to_csv('codeoutput')
                    # return self.exporttocsv(request, self.finaloutput)
                    return self.exporttocsvfromdump(request, projectobj)
            elif request.GET['export'] == 'qualitybackcheck':
                if request.user.user_employee.designation.department.name == 'Product' or request.user.user_employee.designation.department.name == 'IT':
                    return self.exportbackchecktocsvfromdump(request, projectobj)
            elif request.GET['export'] == 'quality':
                return self.fetchqualityreports(projectid)
            elif request.GET['export'] == 'qualitysummary':
                return self.fetchqualitysummaryreports(projectid)
            elif request.GET['export'] == 'qualitysummaryinternal':
                return self.fetchqualitysummaryreportsinternal(request, projectid)
            elif request.GET['export'] == 'surveyors':
                return self.exportsurveyorcodes()
            elif request.GET['export'] == 'employeecodes':
                return self.exportemployeecodes()
            elif request.GET['export'] == 'otpverification':
                otpuids = self.fetchotprawdata(request)
                return self.exportotpuids(otpuids)
            elif request.GET['export'] == 'otpreports':
                otpreportsarray = self.fetchotpreports(request)
                return self.exportotpreports(otpreportsarray, request)
            elif request.GET['export'] == 'otpoverallreports':
                otpreportsarray = self.fetchotpoverallreports(request)
                return self.exportotpoverallreports(otpreportsarray, request)
            elif request.GET['export'] == 'qcempreports':
                qcanalylistarray = self.fetchqcanalystreports(request)
                return self.exportqcanalystreports(qcanalylistarray, request)
            elif request.GET['export'] == 'timeseries':
                ##print() ('in the hourly report')
                timeseriesarray = self.fetchtimeseriesreports(request)
                return self.exporttimeseriesreports(timeseriesarray, request)
            elif request.GET['export'] == 'hourlyreport':
                hourlyarray = self.fetchhourlyreports(request)
                return self.exporthourlyreports(hourlyarray, request)
            elif request.GET['export'] == 'attendance':
                attendance_dict = self.fetchattendancereports(request)
                return self.exportattendancereport(attendance_dict, request)
            elif request.GET['export'] == 'haltwisereports':
                halt_dict = self.fetchhaltwisereports(request, data['project'])
                return self.exporthaltwisereport(request, halt_dict)
            elif request.GET['export'] == 'breaktime':
                attendance_dict = self.fetchbreaktime(request)
                return self.exportbreaktime(attendance_dict, request)
            elif request.GET['export'] == 'gpsreports':
                gpsdict = self.fetchgpsreports(request)
                return self.exportgpsreports(gpsdict, request)
            elif request.GET['export'] == 'productivityreports':
                productivitydict, surveyorlist = self.fetchproductivityreport(request)
                return self.exportproductivityreport(productivitydict, surveyorlist, request)
            elif request.GET['export'] == 'googlereports':
                return self.exportgpsanalysisreport(request)
            elif request.GET['export'] == 'inventorytracking':
                fetchinventoryreports()
                # fetchinventoryreports.delay()

                return self.exportinventorytrackingreport(request)

        if 'export' in request.GET.keys() and request.GET['export'] == 'pmsreports':
            return self.exportpmsreport2(request)
            # return self.exportpmsreports(request)
            # return self.exportpmsreports_akhil(request)

        return render(request, 'index.html', data)

    def exportpmsreports_akhil(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventorytrackingreports.csv"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Count of A+', 'Count of A', 'Count of B', 'Count of C', 'Task Not Filled For The Day'])

        task_grades = {}

        try:
            #for task in Task.objects.filter(updated_on__lte=date(2'01'9, 03, 31)):
                user_name = '%s %s' % (task.assigned_to.user.first_name, task.assigned_to.user.last_name)
                if task.name == "Task not filled for the day":
                    taskrating = "Not Filled"
                else:
                    taskrating = task.rating

                if user_name in task_grades.keys():
                    if taskrating in task_grades[user_name].keys():
                        task_grades[user_name][taskrating] += 1
                    else:
                        task_grades[user_name][taskrating] = 1
                else:
                    task_grades[user_name] = {
                        taskrating: 1
                    }
        except:
            pass

        for key in task_grades.keys():
            try:
                A_plus_grade = task_grades[key]['A_plus']
            except Exception as e:
                A_plus_grade = 0

            try:
                A_grade = task_grades[key]['A']
            except Exception as e:
                A_grade = 0

            try:
                B_grade = task_grades[key]['B']
            except Exception as e:
                B_grade = 0

            try:
                C_grade = task_grades[key]['C']
            except Exception as e:
                C_grade = 0
            try:
                NotFilled_grade = task_grades[key]['Not Filled']
            except Exception as e:
                NotFilled_grade = 0

            writer.writerow([key, A_plus_grade,A_grade,B_grade,C_grade,NotFilled_grade])

        return response

    def exportinventorytrackingreport(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventorytrackingreports.csv"'

        writer = csv.writer(response)

        writer.writerow(['Sr. No.', 'User', 'Asset Code', 'IMEI', 'Last Login', 'Last form time', 'Forms since last login', 'OS', 'Model', 'Last location'])

        cnt = 1
        for tab in InventoryStatus.objects.all():
            try:
                tabuser = tab.user.employee_id
            except Exception as e:
                tabuser = '-'

            writer.writerow([cnt, tabuser, tab.asset.asset_code, tab.asset.imei, tab.last_login, tab.last_form_time, tab.forms_since_last_login, tab.os, tab.model, tab.last_form_location])
            cnt += 1

        return response

    def exportpmsreports(self, request):
        from_date = datetime.strptime('%s %s' % (request.GET['from_date'], '00:00:00'), '%Y-%m-%d %H:%M:%S').date()
        to_date = datetime.strptime('%s %s' % (request.GET['to_date'], '23:59:59'), '%Y-%m-%d %H:%M:%S').date()

        date_range = (to_date - from_date).days
        date_array = []
        task_array = []
        final_array = []

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pmsreports.csv"'

        writer = csv.writer(response)

        count = 0

        for i in range(0, date_range+1):
            date_array.append(from_date + timedelta(days=i))

            for task in Task.objects.filter(
                    assigned_to__designation__department=request.user.user_employee.designation.department,
                    updated_on__gte=(from_date + timedelta(days=i)),
                    updated_on__lte=(from_date + timedelta(days=i+1))
                ):
                task_array.append(task)

        date_array = sorted(date_array)

        ##print() task_array, date_array

        temparray = ['']
        for dateobj in date_array:
            temparray.append(dateobj)

        final_array.append(temparray)

        for task in task_array:
            temparray = [task.name]
            for date_obj in date_array:
                if task.updated_on.date() >= date_obj and task.updated_on.date() < (date_obj + timedelta(days=1)):
                    temparray.append(task.actual)
                else:
                    temparray.append('')

            final_array.append(temparray)

        for array_obj in final_array:
            writer.writerow(array_obj)

        return response

    def fetchhaltwisereports(self, request, project):
        daysreq = int(request.GET['days'])

        if project != None:
            surveyresponses = SurveyResponse.objects.all().order_by(('-pk'))[:30000]
            # surveyresponses = SurveyResponse.objects.filter(project=project)
        else:
            return None

        fr_dict = {}

        respcount = surveyresponses.count()

        # for resp in surveyresponses:
        for i in range(0, respcount):
            resp = surveyresponses[i]
            params = json.loads(resp.params)

            if 'meta' in params and params['meta']['datetime'] == 0:
                continue

            try:
                respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
            except Exception as e:
                continue

            if resp.surveyor == None:
               surv = '-'
            else:
               surv = resp.surveyor.employee_id

            if respdate.date() != date.today() - timedelta(days=daysreq):
                continue
            elif surv in fr_dict.keys():
                fr_dict[surv].append(
                    [
                        resp.uid,
                        params['date'],
                        params['time'],
                        params['surveyor'],
                        params['tldetails'],
                        params['movement'],
                        params['village'],
                        params['actualaddress'],
                        params['village_distance'],
                        resp.project.name
                    ]
                )
            else:
                fr_dict[surv] = [
                    [
                        resp.uid,
                        params['date'],
                        params['time'],
                        params['surveyor'],
                        params['tldetails'],
                        params['movement'],
                        params['village'],
                        params['actualaddress'],
                        params['village_distance'],
                        resp.project.name
                    ]
                ]

        return fr_dict

    def exporthaltwisereport(self, request, halt_dict):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="haltwisereports.csv"'

        writer = csv.writer(response)

        writer.writerow([
            'uid',
            'date',
            'time',
            'surveyor',
            'tldetails',
            'movement',
            'village',
            'actualaddress',
            'village distance',
            'project'
        ])

        for surveyorobj in halt_dict.keys():
            for obj in halt_dict[surveyorobj]:
                writer.writerow(
                    obj
                )

        return response

    def exportpmsreport2(self, request):
        dayreq = 0
        if 'days' in request.GET:
            dayreq = int(request.GET['days'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pmsreports.csv"'

        writer = csv.writer(response)

        count = 0

        writer.writerow(
            [
                'Sr.No.',
                'Reporting Manager',
                'Department',
                'Assigned To',
                'Core Task',
                'Sub Task',
                'Start Date',
                'Deadline Date',
                'Target',
                'Actual',
                'Status',
                'Remarks',
                'Completion Date',
                'Updated On'
            ]
        )

        emp_list = []
        task_list = []
        todo_list = []

        import datetime as dt_pms

        if (request.user.user_employee.designation.department.name == "Product") or \
            (request.user.user_employee.designation.department.name == "PMS"):
            for task in Task.objects.all().order_by('assigned_to'):
                try:
                    # if ((dt_pms.date.today()-timedelta(days=dayreq)) != task.updated_on.date()):
                    if ((dt_pms.date.today()-timedelta(days=dayreq))> task.enddate) or ((dt_pms.date.today()-timedelta(days=dayreq))< task.startdate):
                        continue
                except Exception as e:
                    continue

                count += 1

                emp_list.append(task.assigned_to.employee_id)

                try:
                    office_location = task.assigned_to.office_location.name
                except Exception as e:
                    office_location = '-'

                try:
                    reportingmanager = task.assigned_to.reporting_manager.get().manager.user.first_name+' '+task.assigned_to.reporting_manager.get().manager.user.last_name
                except Exception as e:
                    reportingmanager = '-'

                try:
                    tagged_users = [tagtask.tagged_user.user.first_name+' '+tagtask.tagged_user.user.last_name for tagtask in TagTask.objects.filter(task=task)]
                    tagged_users = ','.join(tagged_users)
                except Exception as e:
                    tagged_users = None

                try:
                    taskstatus = task.status.name
                except Exception as e:
                    taskstatus = '-'

                if task.pk not in task_list:
                    task_list.append(task.pk)

                    writer.writerow(
                        [
                            count,
                            reportingmanager,
                            task.assigned_to.designation.department.name,
                            task.assigned_to.user.first_name+' '+task.assigned_to.user.last_name,
                            task.name,
                            "",
                            task.startdate,
                            task.enddate,
                            task.target,
                            task.actual,
                            taskstatus,
                            task.justification,
                            task.completiondate,
                            task.updated_on.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.tzlocal())
                        ]
                    )

                for todo in ToDo.objects.filter(task=task):
                    count += 1

                    if todo.pk not in todo_list:
                        todo_list.append(todo.pk)

                        writer.writerow(
                            [
                                count,
                                reportingmanager,
                                todo.assigned_to.designation.department.name,
                                todo.assigned_to.user.first_name+' '+todo.assigned_to.user.last_name,
                                task.name,
                                todo.name,
                                todo.startdate,
                                todo.enddate,
                                todo.target,
                                todo.actual,
                                todo.status.name,
                                todo.justification,
                                todo.completiondate,
                                todo.updated_on.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.tzlocal())
                            ]
                        )

            emp_list=list(set(emp_list))

        else:
            for task in Task.objects.filter(Q(assigned_to=request.user.user_employee) | Q(created_by=request.user.user_employee)):
                count += 1

                try:
                    reportingmanager = task.assigned_to.reporting_manager.get().manager.user.first_name+' '+task.assigned_to.reporting_manager.get().manager.user.last_name
                except Exception as e:
                    reportingmanager = '-'

                try:
                    office_location = task.assigned_to.office_location.name
                except Exception as e:
                    office_location = '-'

                try:
                    taskstatus = task.status.name
                except Exception as e:
                    taskstatus = '-'

                if task.pk not in task_list:
                    task_list.append(task.pk)

                    writer.writerow(
                        [
                            count,
                            reportingmanager,
                            task.assigned_to.designation.department.name,
                            task.assigned_to.user.first_name+' '+task.assigned_to.user.last_name,
                            task.name,
                            "",
                            task.startdate,
                            task.enddate,
                            task.target,
                            task.actual,
                            taskstatus,
                            task.justification,
                            task.completiondate,
                            task.updated_on.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.tzlocal())
                        ]
                    )

                for todo in ToDo.objects.filter(task=task):
                    count += 1

                    if todo.pk not in todo_list:
                        todo_list.append(todo.pk)

                        writer.writerow(
                            [
                                count,
                                reportingmanager,
                                todo.assigned_to.designation.department.name,
                                todo.assigned_to.user.first_name+' '+todo.assigned_to.user.last_name,
                                task.name,
                                todo.name,
                                todo.startdate,
                                todo.enddate,
                                todo.target,
                                todo.actual,
                                todo.status.name,
                                todo.justification,
                                todo.completiondate,
                                todo.updated_on.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.tzlocal())
                            ]
                        )

            reportees = [reportingmanager.user for reportingmanager in ReportingManager.objects.filter(manager=request.user.user_employee)]

            for reportee in reportees:
                for task in Task.objects.filter(assigned_to=reportee):
                    count += 1

                    try:
                        reportingmanager = task.assigned_to.reporting_manager.get().manager.user.first_name+' '+task.assigned_to.reporting_manager.get().manager.user.last_name
                    except Exception as e:
                        reportingmanager = '-'

                    try:
                        office_location = task.assigned_to.office_location.name
                    except Exception as e:
                        office_location = '-'

                    try:
                        taskstatus = task.status.name
                    except Exception as e:
                        taskstatus = '-'

                    if task.pk not in task_list:
                        task_list.append(task.pk)

                        writer.writerow(
                            [
                                count,
                                reportingmanager,
                                task.assigned_to.designation.department.name,
                                task.assigned_to.user.first_name+' '+task.assigned_to.user.last_name,
                                task.name,
                                "",
                                task.startdate,
                                task.enddate,
                                task.target,
                                task.actual,
                                taskstatus,
                                task.justification,
                                task.completiondate,
                                task.updated_on.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.tzlocal())
                            ]
                        )

                    if todo.pk not in todo_list:
                        todo_list.append(todo.pk)

                        for todo in ToDo.objects.filter(task=task):
                            count += 1

                            writer.writerow(
                                [
                                    count,
                                    reportingmanager,
                                    todo.assigned_to.designation.department.name,
                                    todo.assigned_to.user.first_name+' '+todo.assigned_to.user.last_name,
                                    task.name,
                                    todo.name,
                                    todo.startdate,
                                    todo.enddate,
                                    todo.target,
                                    todo.actual,
                                    todo.status.name,
                                    todo.justification,
                                    todo.completiondate,
                                    todo.updated_on.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.tzlocal())
                                ]
                            )

        return response

    def exportproductivityreport(self, productivitydict, surveyorlist, request):
        response = HttpResponse(content_type='text/csv')
        projectname = Project.objects.get(pk=request.GET['project']).name
        response['Content-Disposition'] = 'attachment; filename="productivity-%s.csv"' % (projectname)

        dateslist = sorted(productivitydict.keys())
        finalsurveyorslist = list(set(surveyorlist))

        writer = csv.writer(response)

        writer.writerow([projectname])
        writer.writerow([])

        writer.writerow(['Surveyor/Team Leader'] + dateslist)

        for surveyor in finalsurveyorslist:
            finallist = []
            finallist.append(surveyor)
            # finallist.append('-')
            # teamleader = '-'

            for dl in dateslist:
                if surveyor in productivitydict[dl].keys():
                    # if teamleader == '-':
                    #     teamleader = productivitydict[dl][surveyor]['teamleader']

                    finallist.append(productivitydict[dl][surveyor]['count'])
                else:
                    finallist.append('-')

            # finallist[1] = teamleader

            writer.writerow(finallist)

        return response

    def fetchproductivityreport(self, request):
        project = request.GET['project']

        projectobj = Project.objects.get(pk=project)

        surveyresponses = SurveyResponse.objects.filter(project=projectobj)
        surveyorlist = []
        finalresult = {}

        for resp in surveyresponses:
            params = json.loads(resp.params)

            if params['time'] != None:
                respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
            elif params['date'] != None:
                respdate = datetime.strptime('%s %s' % (params['date'], "0:0:0"), '%d-%b-%Y %H:%M:%S')
            else:
                respdate = datetime.now() - timedelta(days=365*1111)

            if 'tldetails' in params.keys():
                tldetails = params['tldetails']
            else:
                tldetails = '-'

            try:
                surveyortl = resp.surveyor.employee_id + '/' + tldetails
            except Exception as e:
                continue

            if respdate.date() in finalresult.keys():
                try:
                    surveyorlist.append(surveyortl)

                    if surveyortl in finalresult[respdate.date()].keys():
                        finalresult[respdate.date()][surveyortl]['count'] += 1
                    else:
                        finalresult[respdate.date()][surveyortl] = {
                                'count': 1
                            }
                except Exception as e:
                    continue

            else:
                try:
                    surveyorlist.append(surveyortl)

                    finalresult[respdate.date()] = {
                        surveyortl: {
                            'count': 1
                        },
                    }
                except Exception as e:
                    continue

        return finalresult, surveyorlist

    def fetchgpsreports(self, request):
        daysreq = int(request.GET['days'])
        surveyresponses = SurveyResponse.objects.all()
        surveyordict = {}

        for resp in surveyresponses:
            params = json.loads(resp.params)
            try:
                tldetails = params['tldetails']
            except Exception as e:
                tldetails = '-'

            try:
                respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
                if respdate.date() != date.today() - timedelta(days=daysreq):
                    respdate = None
            except Exception as e:
                respdate = None

            if respdate != None:
                params['startlat'] = 0 if params['startlat'] == None else params['startlat']
                params['startlong'] = 0 if params['startlong'] == None else params['startlong']
                params['endlat'] = 0 if params['endlat'] == None else params['endlat']
                params['endlong'] = 0 if params['endlong'] == None else params['endlong']

                try:
                    emp = resp.surveyor.employee_id
                except Exception as e:
                    emp = resp.surveyor

                if emp in surveyordict.keys():
                    if int(params['startlat']) == 0 and int(params['startlong']) == 0 and \
                        int(params['endlat']) == 0 and int(params['endlong']) == 0:
                        surveyordict[emp]['gpsoff'] += 1
                    surveyordict[emp]['totalforms'] += 1
                else:
                    if int(params['startlat']) == 0 and int(params['startlong']) == 0 and \
                        int(params['endlat']) == 0 and int(params['endlong']) == 0:
                        surveyordict[emp] = {
                            'gpsoff': 1,
                            'tldetails': tldetails,
                            'surveyor': params['surveyor'],
                            'totalforms': 1
                        }
                    else:
                        surveyordict[emp] = {
                            'gpsoff': 0,
                            'tldetails': tldetails,
                            'surveyor': params['surveyor'],
                            'totalforms': 1
                        }

        return surveyordict

    def exportgpsreports(self, gpsdict, request):
        response = HttpResponse(content_type='text/csv')
        dateobj = date.today()-timedelta(days=int(request.GET['days']))
        response['Content-Disposition'] = 'attachment; filename="gps_%s-%s-%s.csv"' % (dateobj.day, dateobj.month, dateobj.year)

        writer = csv.writer(response)

        writer.writerow(['Date: %s-%s-%s' % (dateobj.day, dateobj.month, dateobj.year)])
        writer.writerow([])
        writer.writerow(['Surveyor', 'Team Leader', 'Total Forms', 'GPS off', 'Percent OFF'])

        for resp in gpsdict.keys():
            temparray = []
            breaktime = None
            ctime = None

            temparray.append(gpsdict[resp]['surveyor'])
            temparray.append(gpsdict[resp]['tldetails'])
            temparray.append(gpsdict[resp]['totalforms'])
            temparray.append(gpsdict[resp]['gpsoff'])
            temparray.append(round((gpsdict[resp]['gpsoff'] / gpsdict[resp]['totalforms']) * 100, 2))

            writer.writerow(temparray)

        return response

    def fetchbreaktime(self, request):
        daysreq = int(request.GET['days'])
        surveyresponses = SurveyResponse.objects.all()
        surveyordict = {}

        for resp in surveyresponses:
            params = json.loads(resp.params)
            try:
                tldetails = params['tldetails']
            except Exception as e:
                tldetails = '-'

            try:
                respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
                if respdate.date() != date.today() - timedelta(days=daysreq):
                    respdate = None
            except Exception as e:
                respdate = None

            if respdate != None:
                try:
                    emp = resp.surveyor.employee_id
                except Exception as e:
                    emp = resp.surveyor

                if emp in surveyordict.keys():
                    surveyordict[emp]['timings'].append(respdate.time())
                    surveyordict[emp]['totalforms'] += 1
                else:
                    surveyordict[emp] = {
                        'timings': [respdate.time()],
                        'tldetails': tldetails,
                        'surveyor': params['surveyor'],
                        'totalforms': 1
                    }

        return surveyordict

    def exportbreaktime(self, attendance_dict, request):
        response = HttpResponse(content_type='text/csv')
        dateobj = date.today()-timedelta(days=int(request.GET['days']))
        response['Content-Disposition'] = 'attachment; filename="breaktime_%s-%s-%s.csv"' % (dateobj.day, dateobj.month, dateobj.year)

        writer = csv.writer(response)

        writer.writerow(['Date: %s-%s-%s' % (dateobj.day, dateobj.month, dateobj.year)])
        writer.writerow([])
        writer.writerow(['Surveyor', 'Team Leader', 'Total Forms', 'Biggest Gap', 'Time Range'])

        for resp in attendance_dict.keys():
            temparray = []
            breaktime = None
            ctime = None
            timings = sorted(attendance_dict[resp]['timings'])

            temparray.append(attendance_dict[resp]['surveyor'])
            temparray.append(attendance_dict[resp]['tldetails'])
            temparray.append(attendance_dict[resp]['totalforms'])

            try:
                temparray.append(breaktime)
                temparray.append('-')
                for i in range(0, len(timings) - 2):
                    if (datetime(year=1900, month='01', day='01', minute=timings[i+1].minute, hour=timings[i+1].hour, second=timings[i+1].second) - \
                        datetime(year=1900, month='01', day='01', minute=timings[i].minute, hour=timings[i].hour, second=timings[i].second)).total_seconds() \
                         > breaktime:
                        breaktime = (datetime(year=1900, month='01', day='01', minute=timings[i+1].minute, hour=timings[i+1].hour, second=timings[i+1].second) - \
                            datetime(year=1900, month='01', day='01', minute=timings[i].minute, hour=timings[i].hour, second=timings[i].second)).total_seconds()
                        ctime = '%s - %s' % (timings[i], timings[i+1])

                if breaktime != None:
                    temparray[3] = int(breaktime / 60)
                    temparray[4] = ctime
                else:
                    temparray[3] = breaktime
                    temparray[4] = ctime
            except Exception as e:
                ##print() (Exception, e)
                pass

            writer.writerow(temparray)

        return response

    def exportattendancereport(self, attendance_dict, request):
        response = HttpResponse(content_type='text/csv')
        dateobj = date.today()-timedelta(days=int(request.GET['days']))
        response['Content-Disposition'] = 'attachment; filename="attendance_%s-%s-%s.csv"' % (dateobj.day, dateobj.month, dateobj.year)

        writer = csv.writer(response)

        writer.writerow(['Date: %s-%s-%s' % (dateobj.day, dateobj.month, dateobj.year)])
        writer.writerow([])
        writer.writerow(['Surveyor', 'Team Leader', 'Project', 'Total Forms', 'First Form', 'Second Form', 'Third Form', 'Third Last Form', 'Second Last Form', 'Last Form'])

        for resp in attendance_dict.keys():

            temparray = []
            timings = sorted(attendance_dict[resp]['timings'])
            temparray.append(attendance_dict[resp]['surveyor'])
            temparray.append(attendance_dict[resp]['tldetails'])
            temparray.append(attendance_dict[resp]['project'])
            temparray.append(attendance_dict[resp]['totalforms'])
            try:
                temparray.append(timings[0])
            except Exception as e:
                temparray.append('-')

            try:
                temparray.append(timings[1])
            except Exception as e:
                temparray.append('-')

            try:
                temparray.append(timings[2])
            except Exception as e:
                temparray.append('-')

            try:
                temparray.append(timings[-3])
            except Exception as e:
                temparray.append('-')

            try:
                temparray.append(timings[-2])
            except Exception as e:
                temparray.append('-')

            try:
                temparray.append(timings[-1])
            except Exception as e:
                temparray.append('-')

            writer.writerow(temparray)

        return response

    def fetchattendancereports(self, request):
        daysreq = int(request.GET['days'])
        surveyresponses = SurveyResponse.objects.all()
        surveyordict = {}

        for resp in surveyresponses:
            params = json.loads(resp.params)

            try:
                respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
                if respdate.date() != date.today() - timedelta(days=daysreq):
                    respdate = None
            except Exception as e:
                respdate = None

            if respdate != None:
                try:
                    emp = resp.surveyor.employee_id
                except Exception as e:
                    emp = resp.surveyor


                if daysreq == 0 and respdate.time() > datetime.now().time() and emp in surveyordict.keys():
                    surveyordict[emp]['totalforms'] += 1
                elif daysreq == 0 and respdate.time() > datetime.now().time():
                    surveyordict[emp] = {
                        'timings': [],
                        'tldetails': params['tldetails'],
                        'surveyor': params['surveyor'],
                        'project': resp.project.name,
                        'totalforms': 1
                    }
                elif emp in surveyordict.keys() and 'meta' in params.keys() and params['meta']['datetime'] == 1:
                    surveyordict[emp]['timings'].append(respdate.time())
                    surveyordict[emp]['totalforms'] += 1
                elif emp in surveyordict.keys() and 'meta' in params.keys() and params['meta']['datetime'] == 0:
                    surveyordict[emp]['totalforms'] += 1
                elif 'meta' in params.keys() and params['meta']['datetime'] == 1:
                    surveyordict[emp] = {
                        'timings': [respdate.time()],
                        'tldetails': params['tldetails'],
                        'surveyor': params['surveyor'],
                        'project': resp.project.name,
                        'totalforms': 1
                    }
                else:
                    surveyordict[emp] = {
                        'timings': [],
                        'tldetails': params['tldetails'],
                        'surveyor': params['surveyor'],
                        'project': resp.project.name,
                        'totalforms': 1
                    }

        return surveyordict

    def exportotpoverallreports(self, otpreportsarray, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="otpreport_overall.csv"'

        writer = csv.writer(response)

        writer.writerow([])
        writer.writerow(['Surveyor', 'Total Verified', 'Total Forms', 'Team Leader', 'Verification Percent'])

        for otpreport in otpreportsarray:
            writer.writerow(otpreport)

        return response

    def fetchotpoverallreports(self, request):
        otpreportsarray = []

        reportsdict = {}

        if 'days' in request.GET.keys():
            dayreq = int(request.GET['days'])
        else:
            dayreq = None

        if int(request.GET['status']) == 0:
            for resp in SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project'])):
                if dayreq != None and datetime.strptime(json.loads(resp.params)['date'], '%d-%b-%Y').date() != date.today() - timedelta(days=dayreq):
                    continue
                elif str(json.loads(resp.params)['surveyor']) in reportsdict.keys():
                    if resp.otp_verified:
                        verified = 1
                    else:
                        verified = 0

                    total = 1
                    percent_verified = (reportsdict[str(json.loads(resp.params)['surveyor'])][1] + verified) / \
                                        (reportsdict[str(json.loads(resp.params)['surveyor'])][2] + total) * 100

                    try:
                        tldetails = str(json.loads(resp.params)['tldetails'])
                    except Exception as e:
                        tldetails = '-'

                    reportsdict[str(json.loads(resp.params)['surveyor'])] = [
                        str(json.loads(resp.params)['surveyor']),
                        reportsdict[str(json.loads(resp.params)['surveyor'])][1] + verified,
                        reportsdict[str(json.loads(resp.params)['surveyor'])][2] + total,
                        tldetails,
                        round(percent_verified, 2)
                    ]
                else:
                    if resp.otp_verified:
                        verified = 1
                    else:
                        verified = 0

                    total = 1
                    percent_verified = verified / total * 100

                    reportsdict[str(json.loads(resp.params)['surveyor'])] = [
                        str(json.loads(resp.params)['surveyor']),
                        verified,
                        total,
                        round(percent_verified, 2)
                    ]
        elif int(request.GET['status']) == 1:
            for resp in SurveyResponse.objects.filter(project__active=True):
                if dayreq != None and json.loads(resp.params)['date'] != None and datetime.strptime(json.loads(resp.params)['date'], '%d-%b-%Y').date() != date.today() - timedelta(days=dayreq):
                    continue
                elif str(json.loads(resp.params)['surveyor']) in reportsdict.keys():
                    if resp.otp_verified:
                        verified = 1
                    else:
                        verified = 0

                    total = 1
                    percent_verified = (reportsdict[str(json.loads(resp.params)['surveyor'])][1] + verified) / \
                                        (reportsdict[str(json.loads(resp.params)['surveyor'])][2] + total) * 100

                    try:
                        tldetails = str(json.loads(resp.params)['tldetails'])
                    except Exception as e:
                        tldetails = '-'

                    reportsdict[str(json.loads(resp.params)['surveyor'])] = [
                        str(json.loads(resp.params)['surveyor']),
                        reportsdict[str(json.loads(resp.params)['surveyor'])][1] + verified,
                        reportsdict[str(json.loads(resp.params)['surveyor'])][2] + total,
                        tldetails,
                        round(percent_verified, 2)
                    ]
                else:
                    if resp.otp_verified:
                        verified = 1
                    else:
                        verified = 0

                    total = 1
                    percent_verified = verified / total * 100

                    reportsdict[str(json.loads(resp.params)['surveyor'])] = [
                        str(json.loads(resp.params)['surveyor']),
                        verified,
                        total,
                        round(percent_verified, 2)
                    ]

        for resp in reportsdict.keys():
            otpreportsarray.append(reportsdict[resp])

        return otpreportsarray

    def exporttimeseriesreports(self, timeseriesarray, request):
        dayreq = int(request.GET['days'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="timeseriesreport_%s.csv"' % (date.today() - timedelta(days=dayreq))

        writer = csv.writer(response)

        writer.writerow([date.today() - timedelta(days=dayreq)])
        writer.writerow([])
        writer.writerow([])
        writer.writerow([
            'SurveyorName',
            'TeamLeader',
            'Total Interviews',
            'Min0To1',
            'Min1To2',
            'Min2To3',
            'Min3To4',
            'Min4To5',
            'Min5To7',
            'Min7To8',
            'Min8To10',
            'Min10To15',
            'Min15ToAbove',
            'TimeIssue'
        ])

        for row in timeseriesarray:
            writer.writerow(row)

        return response

    def fetchtimeseriesreports(self, request):
        timeseriesarray = []
        dayreq = int(request.GET['days'])

        today_year = date.today().year
        today_month = date.today().month
        today_day = date.today().day
        today_date = date.today()

        responsesdict = {}
        for resp in SurveyResponse.objects.filter(project=request.GET['project']):
            respdict = json.loads(resp.params)

            if respdict['date'] != None:
                try:
                    respdict['timedifference'] = int(str(respdict['timedifference']).split(' ')[0])/60
                except Exception as e:
                    pass

                if date.today() - datetime.strptime(str(respdict['date']), '%d-%b-%Y').date() == timedelta(days=dayreq):
                    if respdict['surveyor'] in  responsesdict.keys():
                        try:
                            tldetails = respdict['tldetails']
                        except Exception as e:
                            tldetails = '-'

                        if respdict['timedifference'] == None or respdict['timedifference'] == '-':
                            responsesdict[respdict['surveyor']]['TotalFormFilled'] += 1
                            responsesdict[respdict['surveyor']]['TimeIssue'] += 1
                            continue

                        responsesdict[respdict['surveyor']]['TotalFormFilled'] += 1

                        if respdict['timedifference'] >= 0 and respdict['timedifference'] < 1:
                            responsesdict[respdict['surveyor']]['Min0ToLessThan1'] += 1
                        elif respdict['timedifference'] >= 1 and respdict['timedifference'] < 2:
                            responsesdict[respdict['surveyor']]['Min1ToLessThan2'] += 1
                        elif respdict['timedifference'] >= 2 and respdict['timedifference'] < 3:
                            responsesdict[respdict['surveyor']]['Min2ToLessThan3'] += 1
                        elif respdict['timedifference'] >= 3 and respdict['timedifference'] < 4:
                            responsesdict[respdict['surveyor']]['Min3ToLessThan4'] += 1
                        elif respdict['timedifference'] >= 4 and respdict['timedifference'] < 5:
                            responsesdict[respdict['surveyor']]['Min4ToLessThan5'] += 1
                        elif respdict['timedifference'] >= 5 and respdict['timedifference'] < 7:
                            responsesdict[respdict['surveyor']]['Min5ToLessThan7'] += 1
                        elif respdict['timedifference'] >= 7 and respdict['timedifference'] < 8:
                            responsesdict[respdict['surveyor']]['Min7ToLessThan8'] += 1
                        elif respdict['timedifference'] >= 8 and respdict['timedifference'] < 10:
                            responsesdict[respdict['surveyor']]['Min8ToLessThan10'] += 1
                        elif respdict['timedifference'] >= 10 and respdict['timedifference'] < 15:
                            responsesdict[respdict['surveyor']]['Min10ToLessThan15'] += 1
                        else:
                            responsesdict[respdict['surveyor']]['Min15ToAbove'] += 1

                    else:
                        try:
                            tldetails = respdict['tldetails']
                        except Exception as e:
                            tldetails = '-'

                        if respdict['timedifference'] == None or respdict['timedifference'] == '-':
                            responsesdict[respdict['surveyor']] = {}
                            responsesdict[respdict['surveyor']]['tldetails'] = tldetails
                            responsesdict[respdict['surveyor']]['Surveyor'] = respdict['surveyor']
                            responsesdict[respdict['surveyor']]['TotalFormFilled'] = 1
                            responsesdict[respdict['surveyor']]['Min0ToLessThan1'] = 0
                            responsesdict[respdict['surveyor']]['Min1ToLessThan2'] = 0
                            responsesdict[respdict['surveyor']]['Min2ToLessThan3'] = 0
                            responsesdict[respdict['surveyor']]['Min3ToLessThan4'] = 0
                            responsesdict[respdict['surveyor']]['Min4ToLessThan5'] = 0
                            responsesdict[respdict['surveyor']]['Min5ToLessThan7'] = 0
                            responsesdict[respdict['surveyor']]['Min7ToLessThan8'] = 0
                            responsesdict[respdict['surveyor']]['Min8ToLessThan10'] = 0
                            responsesdict[respdict['surveyor']]['Min10ToLessThan15'] = 0
                            responsesdict[respdict['surveyor']]['Min15ToAbove'] = 0
                            responsesdict[respdict['surveyor']]['TimeIssue'] = 1
                            continue

                        responsesdict[respdict['surveyor']] = {}
                        responsesdict[respdict['surveyor']]['Surveyor'] = respdict['surveyor']
                        responsesdict[respdict['surveyor']]['tldetails'] = tldetails
                        responsesdict[respdict['surveyor']]['TotalFormFilled'] = 1
                        responsesdict[respdict['surveyor']]['Min0ToLessThan1'] = 0
                        responsesdict[respdict['surveyor']]['Min1ToLessThan2'] = 0
                        responsesdict[respdict['surveyor']]['Min2ToLessThan3'] = 0
                        responsesdict[respdict['surveyor']]['Min3ToLessThan4'] = 0
                        responsesdict[respdict['surveyor']]['Min4ToLessThan5'] = 0
                        responsesdict[respdict['surveyor']]['Min5ToLessThan7'] = 0
                        responsesdict[respdict['surveyor']]['Min7ToLessThan8'] = 0
                        responsesdict[respdict['surveyor']]['Min8ToLessThan10'] = 0
                        responsesdict[respdict['surveyor']]['Min10ToLessThan15'] = 0
                        responsesdict[respdict['surveyor']]['Min15ToAbove'] = 0
                        responsesdict[respdict['surveyor']]['TimeIssue'] = 0

                        if respdict['timedifference'] >= 0 and respdict['timedifference'] < 1:
                            responsesdict[respdict['surveyor']]['Min0ToLessThan1'] += 1
                        elif respdict['timedifference'] >= 1 and respdict['timedifference'] < 2:
                            responsesdict[respdict['surveyor']]['Min1ToLessThan2'] += 1
                        elif respdict['timedifference'] >= 2 and respdict['timedifference'] < 3:
                            responsesdict[respdict['surveyor']]['Min2ToLessThan3'] += 1
                        elif respdict['timedifference'] >= 3 and respdict['timedifference'] < 4:
                            responsesdict[respdict['surveyor']]['Min3ToLessThan4'] += 1
                        elif respdict['timedifference'] >= 4 and respdict['timedifference'] < 5:
                            responsesdict[respdict['surveyor']]['Min4ToLessThan5'] += 1
                        elif respdict['timedifference'] >= 5 and respdict['timedifference'] < 7:
                            responsesdict[respdict['surveyor']]['Min5ToLessThan7'] += 1
                        elif respdict['timedifference'] >= 7 and respdict['timedifference'] < 8:
                            responsesdict[respdict['surveyor']]['Min7ToLessThan8'] += 1
                        elif respdict['timedifference'] >= 8 and respdict['timedifference'] < 10:
                            responsesdict[respdict['surveyor']]['Min8ToLessThan10'] += 1
                        elif respdict['timedifference'] >= 10 and respdict['timedifference'] < 15:
                            responsesdict[respdict['surveyor']]['Min10ToLessThan15'] += 1
                        else:
                            responsesdict[respdict['surveyor']]['Min15ToAbove'] += 1

        for resp in responsesdict.keys():
            timeseriesarray.append([
                responsesdict[resp]['Surveyor'],
                responsesdict[resp]['tldetails'],
                responsesdict[resp]['TotalFormFilled'],
                responsesdict[resp]['Min0ToLessThan1'],
                responsesdict[resp]['Min1ToLessThan2'],
                responsesdict[resp]['Min2ToLessThan3'],
                responsesdict[resp]['Min3ToLessThan4'],
                responsesdict[resp]['Min4ToLessThan5'],
                responsesdict[resp]['Min5ToLessThan7'],
                responsesdict[resp]['Min7ToLessThan8'],
                responsesdict[resp]['Min8ToLessThan10'],
                responsesdict[resp]['Min10ToLessThan15'],
                responsesdict[resp]['Min15ToAbove'],
                responsesdict[resp]['TimeIssue']
            ])

        return timeseriesarray

    def exporthourlyreports(self, hourlyarray, request):
        dayreq = int(request.GET['days'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hourlyreport_%s.csv"' % (date.today() - timedelta(days=dayreq))

        writer = csv.writer(response)

        writer.writerow([date.today() - timedelta(days=dayreq)])
        writer.writerow([])
        writer.writerow([])
        writer.writerow([
            'Surveyor Name',
            'Team Leader',
            'Total Interviews',
            '12AM-1AM',
            '1AM-2AM',
            '2AM-3AM',
            '3AM-4AM',
            '4AM-5AM',
            '5AM-6AM',
            '6AM-7AM',
            '7AM-8AM',
            '8AM-9AM',
            '9AM-10AM',
            '10AM-11AM',
            '11AM-12PM',
            '12PM-1PM',
            '1PM-2PM',
            '2PM-3PM',
            '3PM-4PM',
            '4PM-5PM',
            '5PM-6PM',
            '6PM-7PM',
            '7PM-8PM',
            '8PM-9PM',
            '9PM-10PM',
            '10PM-11PM',
            '11PM-12AM',
            'Time Issue',
            'Project Name'
        ])

        for row in hourlyarray:
            writer.writerow(row)

        return response

    def fetchhourlyreports(self, request):
        hourlyarray = []

        dayreq = int(request.GET['days'])

        today_year = date.today().year
        today_month = date.today().month
        today_day = date.today().day
        today_date = date.today()

        responsesdict = {}

        for proj in Project.objects.filter(active=True).values('name').distinct():
            responsesdict[proj['name']] = {}

        # for resp in SurveyResponse.objects.filter(project=request.GET['project']):
        for resp in SurveyResponse.objects.filter(project__active=True):
            respdict = json.loads(resp.params)

            if respdict['date'] != None:
                try:
                    respdict['time'] = int(str(respdict['time']).split(':')[0])
                except Exception as e:
                    pass

            try:
                project_name = resp.project.name
            except Exception as e:
                project_name = "-"

            if date.today() - datetime.strptime(str(respdict['date']), '%d-%b-%Y').date() == timedelta(days=dayreq):
                if respdict['surveyor'] in  responsesdict[project_name].keys():
                    try:
                        tldetails = respdict['tldetails']
                    except Exception as e:
                        tldetails = '-'


                    if respdict['time'] == None or respdict['time'] == '-':
                        responsesdict[project_name][respdict['surveyor']]['TotalFormFilled'] += 1
                        responsesdict[project_name][respdict['surveyor']]['TimeIssue'] += 1
                        continue

                    responsesdict[project_name][respdict['surveyor']]['TotalFormFilled'] += 1

                    if respdict['time'] >= 0 and respdict['time'] < 1:
                        responsesdict[project_name][respdict['surveyor']]['12ToLessThan1AM'] += 1
                    elif respdict['time'] >= 1 and respdict['time'] < 2:
                        responsesdict[project_name][respdict['surveyor']]['1ToLessThan2AM'] += 1
                    elif respdict['time'] >= 2 and respdict['time'] < 3:
                        responsesdict[project_name][respdict['surveyor']]['2ToLessThan3AM'] += 1
                    elif respdict['time'] >= 3 and respdict['time'] < 4:
                        responsesdict[project_name][respdict['surveyor']]['3ToLessThan4AM'] += 1
                    elif respdict['time'] >= 4 and respdict['time'] < 5:
                        responsesdict[project_name][respdict['surveyor']]['4ToLessThan5AM'] += 1
                    elif respdict['time'] >= 5 and respdict['time'] < 6:
                        responsesdict[project_name][respdict['surveyor']]['5ToLessThan6AM'] += 1
                    elif respdict['time'] >= 6 and respdict['time'] < 7:
                        responsesdict[project_name][respdict['surveyor']]['6ToLessThan7AM'] += 1
                    elif respdict['time'] >= 7 and respdict['time'] < 8:
                        responsesdict[project_name][respdict['surveyor']]['7ToLessThan8AM'] += 1
                    elif respdict['time'] >= 8 and respdict['time'] < 9:
                        responsesdict[project_name][respdict['surveyor']]['8ToLessThan9AM'] += 1
                    elif respdict['time'] >= 9 and respdict['time'] < 10:
                        responsesdict[project_name][respdict['surveyor']]['9ToLessThan10AM'] += 1
                    elif respdict['time'] >= 10 and respdict['time'] < 11:
                        responsesdict[project_name][respdict['surveyor']]['10ToLessThan11AM'] += 1
                    elif respdict['time'] >= 11 and respdict['time'] < 12:
                        responsesdict[project_name][respdict['surveyor']]['11ToLessThan12PM'] += 1
                    elif respdict['time'] >= 12 and respdict['time'] < 13:
                        responsesdict[project_name][respdict['surveyor']]['12ToLessThan1PM'] += 1
                    elif respdict['time'] >= 13 and respdict['time'] < 14:
                        responsesdict[project_name][respdict['surveyor']]['1ToLessThan2PM'] += 1
                    elif respdict['time'] >= 14 and respdict['time'] < 15:
                        responsesdict[project_name][respdict['surveyor']]['2ToLessThan3PM'] += 1
                    elif respdict['time'] >= 15 and respdict['time'] < 16:
                        responsesdict[project_name][respdict['surveyor']]['3ToLessThan4PM'] += 1
                    elif respdict['time'] >= 16 and respdict['time'] < 17:
                        responsesdict[project_name][respdict['surveyor']]['4ToLessThan5PM'] += 1
                    elif respdict['time'] >= 17 and respdict['time'] < 18:
                        responsesdict[project_name][respdict['surveyor']]['5ToLessThan6PM'] += 1
                    elif respdict['time'] >= 18 and respdict['time'] < 19:
                        responsesdict[project_name][respdict['surveyor']]['6ToLessThan7PM'] += 1
                    elif respdict['time'] >= 19 and respdict['time'] < 20:
                        responsesdict[project_name][respdict['surveyor']]['7ToLessThan8PM'] += 1
                    elif respdict['time'] >= 20 and respdict['time'] < 21:
                        responsesdict[project_name][respdict['surveyor']]['8ToLessThan9PM'] += 1
                    elif respdict['time'] >= 21 and respdict['time'] < 22:
                        responsesdict[project_name][respdict['surveyor']]['9ToLessThan10PM'] += 1
                    elif respdict['time'] >= 22 and respdict['time'] < 23:
                        responsesdict[project_name][respdict['surveyor']]['10ToLessThan11PM'] += 1
                    else:
                        responsesdict[project_name][respdict['surveyor']]['11ToLessThan12AM'] += 1

                else:
                    try:
                        tldetails = respdict['tldetails']
                    except Exception as e:
                        tldetails = '-'

                    if respdict['time'] == None or respdict['time'] == '-':
                        responsesdict[project_name][respdict['surveyor']] = {}
                        responsesdict[project_name][respdict['surveyor']]['tldetails'] = tldetails
                        responsesdict[project_name][respdict['surveyor']]['Surveyor'] = respdict['surveyor']
                        responsesdict[project_name][respdict['surveyor']]['TotalFormFilled'] = 1
                        responsesdict[project_name][respdict['surveyor']]['12ToLessThan1AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['1ToLessThan2AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['2ToLessThan3AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['3ToLessThan4AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['4ToLessThan5AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['5ToLessThan6AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['6ToLessThan7AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['7ToLessThan8AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['8ToLessThan9AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['9ToLessThan10AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['10ToLessThan11AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['11ToLessThan12PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['12ToLessThan1PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['1ToLessThan2PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['2ToLessThan3PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['3ToLessThan4PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['4ToLessThan5PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['5ToLessThan6PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['6ToLessThan7PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['7ToLessThan8PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['8ToLessThan9PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['9ToLessThan10PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['10ToLessThan11PM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['11ToLessThan12AM'] = 0
                        responsesdict[project_name][respdict['surveyor']]['TimeIssue'] = 1
                        continue

                    responsesdict[project_name][respdict['surveyor']] = {}
                    responsesdict[project_name][respdict['surveyor']]['Surveyor'] = respdict['surveyor']
                    responsesdict[project_name][respdict['surveyor']]['tldetails'] = tldetails
                    responsesdict[project_name][respdict['surveyor']]['TotalFormFilled'] = 1
                    responsesdict[project_name][respdict['surveyor']]['12ToLessThan1AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['1ToLessThan2AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['2ToLessThan3AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['3ToLessThan4AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['4ToLessThan5AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['5ToLessThan6AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['6ToLessThan7AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['7ToLessThan8AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['8ToLessThan9AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['9ToLessThan10AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['10ToLessThan11AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['11ToLessThan12PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['12ToLessThan1PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['1ToLessThan2PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['2ToLessThan3PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['3ToLessThan4PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['4ToLessThan5PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['5ToLessThan6PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['6ToLessThan7PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['7ToLessThan8PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['8ToLessThan9PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['9ToLessThan10PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['10ToLessThan11PM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['11ToLessThan12AM'] = 0
                    responsesdict[project_name][respdict['surveyor']]['TimeIssue'] = 0

                    if respdict['time'] >= 0 and respdict['time'] < 1:
                        responsesdict[project_name][respdict['surveyor']]['12ToLessThan1AM'] += 1
                    elif respdict['time'] >= 1 and respdict['time'] < 2:
                        responsesdict[project_name][respdict['surveyor']]['1ToLessThan2AM'] += 1
                    elif respdict['time'] >= 2 and respdict['time'] < 3:
                        responsesdict[project_name][respdict['surveyor']]['2ToLessThan3AM'] += 1
                    elif respdict['time'] >= 3 and respdict['time'] < 4:
                        responsesdict[project_name][respdict['surveyor']]['3ToLessThan4AM'] += 1
                    elif respdict['time'] >= 4 and respdict['time'] < 5:
                        responsesdict[project_name][respdict['surveyor']]['4ToLessThan5AM'] += 1
                    elif respdict['time'] >= 5 and respdict['time'] < 6:
                        responsesdict[project_name][respdict['surveyor']]['5ToLessThan6AM'] += 1
                    elif respdict['time'] >= 6 and respdict['time'] < 7:
                        responsesdict[project_name][respdict['surveyor']]['6ToLessThan7AM'] += 1
                    elif respdict['time'] >= 7 and respdict['time'] < 8:
                        responsesdict[project_name][respdict['surveyor']]['7ToLessThan8AM'] += 1
                    elif respdict['time'] >= 8 and respdict['time'] < 9:
                        responsesdict[project_name][respdict['surveyor']]['8ToLessThan9AM'] += 1
                    elif respdict['time'] >= 9 and respdict['time'] < 10:
                        responsesdict[project_name][respdict['surveyor']]['9ToLessThan10AM'] += 1
                    elif respdict['time'] >= 10 and respdict['time'] < 11:
                        responsesdict[project_name][respdict['surveyor']]['10ToLessThan11AM'] += 1
                    elif respdict['time'] >= 11 and respdict['time'] < 12:
                        responsesdict[project_name][respdict['surveyor']]['11ToLessThan12PM'] += 1
                    elif respdict['time'] >= 12 and respdict['time'] < 13:
                        responsesdict[project_name][respdict['surveyor']]['12ToLessThan1PM'] += 1
                    elif respdict['time'] >= 13 and respdict['time'] < 14:
                        responsesdict[project_name][respdict['surveyor']]['1ToLessThan2PM'] += 1
                    elif respdict['time'] >= 14 and respdict['time'] < 15:
                        responsesdict[project_name][respdict['surveyor']]['2ToLessThan3PM'] += 1
                    elif respdict['time'] >= 15 and respdict['time'] < 16:
                        responsesdict[project_name][respdict['surveyor']]['3ToLessThan4PM'] += 1
                    elif respdict['time'] >= 16 and respdict['time'] < 17:
                        responsesdict[project_name][respdict['surveyor']]['4ToLessThan5PM'] += 1
                    elif respdict['time'] >= 17 and respdict['time'] < 18:
                        responsesdict[project_name][respdict['surveyor']]['5ToLessThan6PM'] += 1
                    elif respdict['time'] >= 18 and respdict['time'] < 19:
                        responsesdict[project_name][respdict['surveyor']]['6ToLessThan7PM'] += 1
                    elif respdict['time'] >= 19 and respdict['time'] < 20:
                        responsesdict[project_name][respdict['surveyor']]['7ToLessThan8PM'] += 1
                    elif respdict['time'] >= 20 and respdict['time'] < 21:
                        responsesdict[project_name][respdict['surveyor']]['8ToLessThan9PM'] += 1
                    elif respdict['time'] >= 21 and respdict['time'] < 22:
                        responsesdict[project_name][respdict['surveyor']]['9ToLessThan10PM'] += 1
                    elif respdict['time'] >= 22 and respdict['time'] < 23:
                        responsesdict[project_name][respdict['surveyor']]['10ToLessThan11PM'] += 1
                    else:
                        responsesdict[project_name][respdict['surveyor']]['11ToLessThan12AM'] += 1


        for key in responsesdict.keys():
            for resp in responsesdict[key].keys():
                hourlyarray.append([
                    responsesdict[key][resp]['Surveyor'],
                    responsesdict[key][resp]['tldetails'],
                    responsesdict[key][resp]['TotalFormFilled'],
                    responsesdict[key][resp]['12ToLessThan1AM'],
                    responsesdict[key][resp]['1ToLessThan2AM'],
                    responsesdict[key][resp]['2ToLessThan3AM'],
                    responsesdict[key][resp]['3ToLessThan4AM'],
                    responsesdict[key][resp]['4ToLessThan5AM'],
                    responsesdict[key][resp]['5ToLessThan6AM'],
                    responsesdict[key][resp]['6ToLessThan7AM'],
                    responsesdict[key][resp]['7ToLessThan8AM'],
                    responsesdict[key][resp]['8ToLessThan9AM'],
                    responsesdict[key][resp]['9ToLessThan10AM'],
                    responsesdict[key][resp]['10ToLessThan11AM'],
                    responsesdict[key][resp]['11ToLessThan12PM'],
                    responsesdict[key][resp]['12ToLessThan1PM'],
                    responsesdict[key][resp]['1ToLessThan2PM'],
                    responsesdict[key][resp]['2ToLessThan3PM'],
                    responsesdict[key][resp]['3ToLessThan4PM'],
                    responsesdict[key][resp]['4ToLessThan5PM'],
                    responsesdict[key][resp]['5ToLessThan6PM'],
                    responsesdict[key][resp]['6ToLessThan7PM'],
                    responsesdict[key][resp]['7ToLessThan8PM'],
                    responsesdict[key][resp]['8ToLessThan9PM'],
                    responsesdict[key][resp]['9ToLessThan10PM'],
                    responsesdict[key][resp]['10ToLessThan11PM'],
                    responsesdict[key][resp]['11ToLessThan12AM'],
                    responsesdict[key][resp]['TimeIssue'],
                    key
                ])


        return hourlyarray


    def fetchqcanalystreports(self, request):
        dayreq = int(request.GET['days'])
        reportsarray = []

        reportsdict = {}
        for resp in SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project']), \
                        verification_date__gte=date.today() - timedelta(days=dayreq), \
                        verification_date__lte=date.today() - timedelta(days=dayreq-1), \
                        verification_status=VerificationStatus.objects.get(name='Verified')):
            full_name = resp.user.user.first_name+' '+resp.user.user.last_name

            if full_name in reportsdict.keys():
                continue

            verified_count = SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project']), \
                            verification_date__gte=date.today() - timedelta(days=dayreq), \
                            verification_date__lte=date.today() - timedelta(days=dayreq-1), \
                            user=resp.user,
                            verification_status=VerificationStatus.objects.get(name='Verified')).count()

            reportsdict[full_name] = [full_name, verified_count, resp.verification_date.date()]

        for rep in reportsdict.keys():
            reportsarray.append(reportsdict[rep])

        return reportsarray

    def exportqcanalystreports(self, qcanalylistarray, request):
        dayreq = int(request.GET['days'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="qcanalystreport_%s.csv"' % (date.today() - timedelta(days=dayreq))

        writer = csv.writer(response)

        writer.writerow([date.today() - timedelta(days=dayreq)])
        writer.writerow([])
        # Pending forms
        writer.writerow([
            "Pending Forms For QA",
            SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project']), user=None).count() * 23 / 100
        ])
        writer.writerow([
            "Total Forms verified by QA",
            SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project'])).exclude(user=None).count()
        ])
        writer.writerow([])
        writer.writerow(['Analyst', 'Verifed', 'Date'])

        for analystreport in qcanalylistarray:
            writer.writerow(analystreport)

        return response

    def exportotpreports(self, otpreportsarray, request):
        dayreq = int(request.GET['days'])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="otpreport_%s.csv"' % (date.today() - timedelta(days=dayreq))

        writer = csv.writer(response)

        writer.writerow([date.today() - timedelta(days=dayreq)])
        writer.writerow([])
        writer.writerow(['Surveyor', 'Total Verified', 'Total Forms', 'Team Leader', 'Verification Percent'])

        for otpreport in otpreportsarray:
            writer.writerow(otpreport)

        return response

    def fetchotpreports(self, request):
        # for i in SurveyResponse.objects.all():
        #     try:
        #         ##print() datetime.strptime(json.loads(i.params)['date'], '%d-%b-%Y').date()
        #     except Exception as e:
        #         pass
        #
        #     ##print() date.today()
        #     ##print() date.today() - timedelta(days=1)
        #     ##print() date.today() - timedelta(days=2)
        #     ##print() date.today() - timedelta(days=3)
        #     ##print() date.today() - timedelta(days=4)
        #     ##print() date.today() - timedelta(days=5)
        #     ##print() date.today() - timedelta(days=6)
        #     ##print() date.today() - timedelta(days=7)
        #     ##print() i.otp_verified, json.loads(i.params)['surveyor'], json.loads(i.params)['date']

        dayreq = int(request.GET['days'])

        otpreportsarray = []

        reportsdict = {}
        for resp in SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project'])):
            if json.loads(resp.params)['date'] == None:
                continue
            elif datetime.strptime(json.loads(resp.params)['date'], '%d-%b-%Y').date() != date.today() - timedelta(days=dayreq):
                continue
            elif str(json.loads(resp.params)['surveyor']) in reportsdict.keys():
                if resp.otp_verified:
                    verified = 1
                else:
                    verified = 0

                total = 1
                percent_verified = (reportsdict[str(json.loads(resp.params)['surveyor'])][1] + verified) / \
                                    (reportsdict[str(json.loads(resp.params)['surveyor'])][2] + total) * 100

                try:
                    tldetails = str(json.loads(resp.params)['tldetails'])
                except Exception as e:
                    tldetails = '-'

                reportsdict[str(json.loads(resp.params)['surveyor'])] = [
                    str(json.loads(resp.params)['surveyor']),
                    reportsdict[str(json.loads(resp.params)['surveyor'])][1] + verified,
                    reportsdict[str(json.loads(resp.params)['surveyor'])][2] + total,
                    tldetails,
                    round(percent_verified, 2)
                ]
            else:
                if resp.otp_verified:
                    verified = 1
                else:
                    verified = 0

                total = 1
                percent_verified = verified / total * 100

                try:
                    tldetails = str(json.loads(resp.params)['surveyor'])
                except Exception as e:
                    tldetails = '-'

                reportsdict[str(json.loads(resp.params)['surveyor'])] = [
                    str(json.loads(resp.params)['surveyor']),
                    verified,
                    total,
                    tldetails,
                    round(percent_verified, 2)
                ]

        for resp in reportsdict.keys():
            otpreportsarray.append(reportsdict[resp])

        return otpreportsarray

    def fetchotprawdata(self, request):
        otpverification_array = []

        for resp in SurveyResponse.objects.filter(project=Project.objects.get(id=request.GET['project'])):
            otpverification_array.append([resp.uid, resp.otp_verified, json.loads(resp.params)['surveyor']])

        return otpverification_array

    def exportotpuids(self, otpuids):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="otpuids.csv"'

        writer = csv.writer(response)

        writer.writerow(['uid', 'verification_status', 'surveyor'])
        for uid in otpuids:
            writer.writerow(uid)

        return response

    def exportsurveyorcodes(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="surveyorcodes.csv"'

        writer = csv.writer(response)

        surveyors = Employee.objects.filter(designation__department__name='Operations')

        writer.writerow(["Employee ID", "First Name", "Surname", "Old Code", "Phone Number", "Last Project"])
        for surveyor in surveyors:
            try:
                phone_number = surveyor.phone_number
            except Exception as e:
                phone_number = ''

            try:
                last_project = UserToProject.objects.filter(user=surveyor.surveyor).order_by(('-pk'))[0].project.name
            except Exception as e:
                last_project = ''

            writer.writerow([surveyor.employee_id, surveyor.user.first_name, surveyor.user.last_name, surveyor.old_code,  phone_number, last_project])

        return response

    def exportemployeecodes(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employeecodes.csv"'

        writer = csv.writer(response)

        employees = Employee.objects.all()[:10]

        writer.writerow(["Employee ID", "First Name", "Surname", "Email", "Department", "Designation", "Old Code", "Phone Number", "Joining Date", "State", "District", "Reporting Manager"])
        for employee in employees:
            try:
                phone_number = employee.phone_number
            except Exception as e:
                phone_number = ''

            try:
                last_project = UserToProject.objects.filter(user=employee.employee).order_by(('-pk'))[0].project.name
            except Exception as e:
                last_project = ''

            try:
                department = employee.designation.department.name
                designation = employee.designation.name
            except Exception as e:
                department = '-'
                designation = '-'

            try:
                reporting_to = ReportingManager.objects.get(user=employee).manager.user.first_name+' '+ReportingManager.objects.get(user=employee).manager.user.last_name
            except Exception as e:
                reporting_to = '-'

            writer.writerow([employee.employee_id, employee.user.first_name, employee.user.last_name, employee.user.email, department, designation, employee.old_code,  phone_number, employee.joining_date, reporting_to])

        return response


    def removejunkcolumns(self, request, data):
        project = Project.objects.get(id=request.GET['project'])
        finaldata = data

        merge = MergeColumns.objects.filter(project=project)
        #print('mergecolumns',(merge.query))
        #print("merge",merge)

        #print(type(merge))

        #print("count",MergeColumns.objects.filter(project=project).count())

        #print(type(MergeColumns.objects.filter(project=project).count()))

        if MergeColumns.objects.filter(project=project).count() > 0:
            mergeobj = MergeColumns.objects.filter(project=project)

            #print("mergeobj",mergeobj)

            #print(type(mergeobj))

            validcoldata = '-'

            start_cols = []
            all_cols = []
            outputs = []

            for mergeo in mergeobj:
                start_cols.append(int(mergeo.startcol))
                for i in range(int(mergeo.startcol), int(mergeo.endcol) + 1):
                    all_cols.append(int(i))

                for op in data[int(mergeo.startcol):(int(mergeo.endcol) + 1)]:
                    if str(op) != '-':
                        validcoldata = str(op)
                        # if validcoldata != '-':
                        #     validcoldata = '%s/%s' % (validcoldata, str(op))
                    else:
                        pass

                outputs.append(validcoldata)
                validcoldata = '-'

            finaldata = []

            for i, d in enumerate(data):
                if i in start_cols:
                    finaldata.append(outputs[start_cols.index(i)])
                elif i in all_cols:
                    pass
                else:
                    finaldata.append(d)

        finaldata2 = []


        SimilarColumn = SimilarColumns.objects.filter(project=project)
        #print("similarcolumn", SimilarColumn.query)

        if SimilarColumns.objects.filter(project=project).count() > 0:
            similarcolumnobj = SimilarColumns.objects.filter(project=project)[0]

            tempcols = []
            colnos = []

            for col in json.loads(similarcolumnobj.cols):
                temp = '-'

                for subcol in col:
                    try:
                        temp = finaldata[subcol] if finaldata[subcol] != '-' else temp
                        colnos.append(int(subcol))
                    except Exception as e:
                        continue

                tempcols.append(temp)

            for i, d in enumerate(finaldata):
                if i not in colnos:
                    tempcols.append(d)

            finaldata = tempcols

        return finaldata

    def exporttocsvfromdump(self, request, projectobj):
        output = io.BytesIO()
        #output = StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        row = 0

        # data = AllDataDump.objects.filter(project=projectobj).order_by(('-pk'))
        data = (AllDataDump.objects.filter(project=projectobj).order_by(('-pk'))[:15500])

        print("data",data)
        

        # Headers
        cp = data[0]
        print("cp",cp.uid)
        print(len(data))
        listdr =  json.loads(cp.checkpoints)   #only one data checkpoints
        #print("listdr1",listdr)
        listdr = self.removejunkcolumns(request, listdr)
        #print("listdr",listdr)

        col = 0

        worksheet.write(row, col, "UID")
        col+=1
        worksheet.write(row, col, "Datetime")
        col+=1

        # nccs headers

        if Project.objects.get(pk=request.GET['project']).nccs == True:
            durables_cols, durables_count, education_col = getnccsheaders(request.GET['project'], listdr)
            worksheet.write(row, col, "NCCS")
            col+=1
            worksheet.write(row, col, "Number of durables owned - calculated")
            col+=1
        else:
            durables_cols, education_col, durables_count = None, None, None
        # end of nccs headers

        # Write headers
        for q in listdr:
            worksheet.write(row, col, q)            #write headers
            col += 1
        row += 1

        # Split data into chunks
        # for dr in data.iterator():
        # Raw data
        for i in range(0, data.count()):
            dr = data[i]
            
            listdr =  json.loads(dr.rawdata)

            # ##print() listdr[-9]
            listdr = self.removejunkcolumns(request, listdr)

            col = 0

            skip = False

            try:
                if '-' in str(listdr[-9]):
                    worksheet.write(row, col, listdr[-10])
                    col+=1
                    worksheet.write(row, col, listdr[-9])
                    col+=1
                else:
                    worksheet.write(row, col, listdr[-9])
                    col+=1
                    worksheet.write(row, col, listdr[-8])
                    col+=1
            except Exception as e:
                continue

            # nccs headers
            if Project.objects.get(pk=request.GET['project']).nccs == True:
                nccs_result, durables_count_calculated = getnccsresults(listdr, durables_cols, education_col, durables_count)
                ##print(nccs_result, durables_count_calculated)
                worksheet.write(row, col, nccs_result)
                col+=1
                worksheet.write(row, col, durables_count_calculated)
                col+=1
            # end of nccs headers

            for dc in listdr:
                if col == 0:
                    if dc == '-':
                        row -= 1
                        dr.delete()
                        break
                try:

                    if request.GET['export'] == 'code':
                        if '-' in str(dc) and str(str(dc).split('-')[0]) not in ["2022", "2021", "2020", "2'01'9"]:
                            worksheet.write(row, col, dc.split('-')[0])
                        else:
                            worksheet.write(row, col, dc)
                    else:
                        worksheet.write(row, col, dc)



                    # if request.GET['export'] == 'code':
                        # if '-' in str(dc('utf-8')) and str(str(dc('utf-8')).split('-')[0]) not in ["2022", "2021", "2020", "2'01'9"]:
                            # worksheet.write(row, col, dc('utf-8').split('-')[0])
                        # else:
                            # worksheet.write(row, col, dc('utf-8'))
                    # else:
                        # worksheet.write(row, col, dc('utf-8'))

                except Exception as e:
                    if request.GET['export'] == 'code':
                        if '-' in str(dc) and str(str(dc).split('-')[0]) not in ["2022", "2021", "2020", "2'01'9"]:
                            
                            worksheet.write(row, col, dc.split('-')[0])
                        else:
                            worksheet.write(row, col, dc)
                    else:
                        worksheet.write(row, col, dc)

                col += 1
            row += 1

        workbook.close()


        

        fname = Project.objects.get(pk=request.GET['project']).name
        ##print(fname)
        output.seek(0)
        response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % (fname)

        import gc
        gc.collect()

        return response

    def exportbackchecktocsvfromdump(self, request, projectobj):
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        row = 0

        # data = AllDataDump.objects.filter(project=projectobj).order_by(('-pk'))
        uids_to_dump = []
        data = []

        sr_obj = SurveyResponse.objects.filter(project=projectobj, verification_status__name="Backcheck verification")

        for survey in sr_obj:
            uids_to_dump.append(survey.uid)

        for form in AllDataDump.objects.filter(project=projectobj, uid__in=uids_to_dump).order_by(('-pk')):
            if 'date' in request.GET.keys() and parse(json.loads(form.rawdata)) == parse(request.GET['date']):
                data.append(form)
            else:
                data.append(form)

        # Headers
        cp = data[0]
        listdr =  json.loads(cp.checkpoints)
        listdr = self.removejunkcolumns(request, listdr)

        col = 0

        worksheet.write(row, col, "UID")
        col+=1
        worksheet.write(row, col, "Datetime")
        col+=1

        # nccs headers
        if Project.objects.get(pk=request.GET['project']).nccs == True:
            durables_cols, durables_count, education_col = getnccsheaders(request.GET['project'], listdr)
            worksheet.write(row, col, "NCCS")
            col+=1
            worksheet.write(row, col, "Number of durables owned - calculated")
            col+=1
        else:
            durables_cols, education_col, durables_count = None, None, None
        # end of nccs headers

        for q in listdr:
            worksheet.write(row, col, q)
            col += 1
        row += 1

        # Split data into chunks
        # for dr in data.iterator():
        # Raw data
        for i in range(0, len(data)):
            dr = data[i]
            listdr =  json.loads(dr.rawdata)
            # ##print() listdr[-9]
            listdr = self.removejunkcolumns(request, listdr)
            col = 0

            skip = False

            try:
                if '-' in str(listdr[-9]):
                    worksheet.write(row, col, listdr[-10])
                    col+=1
                    worksheet.write(row, col, listdr[-9])
                    col+=1
                else:
                    worksheet.write(row, col, listdr[-9])
                    col+=1
                    worksheet.write(row, col, listdr[-8])
                    col+=1
            except Exception as e:
                continue

            # nccs headers
            if Project.objects.get(pk=request.GET['project']).nccs == True:
                nccs_result, durables_count_calculated = getnccsresults(listdr, durables_cols, education_col, durables_count)
                worksheet.write(row, col, nccs_result)
                col+=1
                worksheet.write(row, col, durables_count_calculated)
                col+=1
            # end of nccs headers

            for dc in listdr:
                if col == 0:
                    if dc == '-':
                        row -= 1
                        dr.delete()
                        break
                try:
                    if request.GET['export'] == 'code':
                        if '-' in str(dc('utf-8')) and str(str(dc('utf-8')).split('-')[0]) not in ["2020", "2021", "2022"]:
                            worksheet.write(row, col, dc('utf-8').split('-')[0])
                        else:
                            worksheet.write(row, col, dc('utf-8'))
                    else:
                        worksheet.write(row, col, dc('utf-8'))
                except Exception as e:
                    if request.GET['export'] == 'code':
                        if '-' in str(dc) and str(str(dc).split('-')[0]) not in ["2020", "2021", "2022"]:
                            worksheet.write(row, col, dc.split('-')[0])
                        else:
                            worksheet.write(row, col, dc)
                    else:
                        worksheet.write(row, col, dc)

                col += 1
            row += 1

        workbook.close()

        fname = Project.objects.get(pk=request.GET['project']).name
        output.seek(0)
        response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % ('fname')
        # response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % (fname)

        import gc
        gc.collect()

        return response

    def exporttocsv(self, request, data):
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

        # writer = csv.writer(response)
        #
        # for d in data:
        #     writer.writerow(d)
        #
        # return response

        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')
        row = 0

        for dr in data:
            dr = self.removejunkcolumns(request, dr)
            col = 0

            skip = False
            for dc in dr:
                if col == 0:
                    if dc == '-':
                        row -= 1
                        break
                try:
                    worksheet.write(row, col, dc('utf-8'))
                except Exception as e:
                    worksheet.write(row, col, dc)

                col += 1
            row += 1

        workbook.close()

        fname = Project.objects.get(pk=request.GET['project']).name
        output.seek(0)
        response = HttpResponse(output.read(), content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % (fname)

        return response

    def fetchallcheckpoints(self):
        # execute SQL query using execute() method.
        sql = """SELECT CHECKPOINT_ID FROM CHECKLIST_MASTER WHERE CHECKLIST_ID LIKE %s""" % (self.checklist_id)

        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        # Fetch checkpoint ids from checklist
        for d in data:
            for qids in d[0].replace(' ', '').split(','):
                self.checkpoint_ids.append(str(qids))

                sql = """SELECT CHECKPOINT_NAME, CHECKPOINT1_ID FROM CHECKPOINT1"""
                self.cursor.execute(sql)
                cp1_data = self.cursor.fetchall()

                for cpd in cp1_data:
                    if str(cpd[1].split('.')[0]) == str(qids):
                        self.checkpoint_ids.append(str(cpd[1]))

        # self.checkpoint_ids.append(107)

    def tackle_multiple(self, d, multipleans, cpid):
        answer = ['-' for i in range(len(multipleans))]
        for data in d[5].split(','):
            if data in multipleans:
                x = multipleans.index(data)
                answer[x] = 'Y'
        answer = ','.join(answer)
        return answer

    def fetchcheckpointtextdata(self):
        # Fetch relevant data for the given checkpoints
        datacount = 0

        for cpid in self.checkpoint_ids:

            # Check if question is multiple answer question
            if '.' in str(cpid):
                cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT1 WHERE CHECKPOINT1_ID LIKE '%s'""" % (cpid)
            else:
                cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (cpid)
            self.cursor.execute(cp_sql)

            cp_data = self.cursor.fetchall()

            try:
                if int(cp_data[0][0]) == 5:
                    multipleans = list(cp_data[0][1].split(','))
                else:
                    multipleans = None
            except Exception as e:
                multipleans = None


            from datetime import datetime as dt
            sql = """SELECT * FROM SAVE_SURVEY WHERE CHECKPOINT_ID LIKE '%s' \
                    AND DATETIME > '%s'""" % (cpid, dt.now()-timedelta(days=5))
            self.cursor.execute(sql)

            data = self.cursor.fetchall()

            uids = []

            for d in data:
                try:
                    if d[-2] in self.answers.keys():
                        if cpid in self.answers[d[-2]].keys():

                            if multipleans:

                                # trial
                                # temp = '%s-%s' % (d[-2], d[4])
                                # if temp in uids:
                                #     ##print() self.tackle_multiple(d, multipleans, cpid), ' - ', d[-2], ' - ', d[4]
                                #     uids.append('%s-%s' % (d[-2], d[4]))
                                # end of trial

                                self.answers[d[-2]][cpid].append(self.tackle_multiple(d, multipleans, cpid))
                            else:
                                if str(d[5])('utf-8') == "Other":
                                    self.answers[d[-2]][cpid].append("Other-"+d[6])
                                else:
                                    self.answers[d[-2]][cpid].append(d[5].replace(',', ' '))

                            self.answers[d[-2]]['datetime'].append(d[11])
                            self.answers[d[-2]]['filledby'].append(d[1])
                            self.answers[d[-2]]['uid'].append(d[-2])
                        else:
                            if multipleans:
                                self.answers[d[-2]][cpid] = [self.tackle_multiple(d, multipleans, cpid)]
                            else:
                                if str(d[5])('utf-8') == "Other":
                                    self.answers[d[-2]][cpid] = ["Other-"+d[6]]
                                else:
                                    self.answers[d[-2]][cpid] = [d[5].replace(',', ' ')]

                            self.answers[d[-2]]['datetime'] = [d[11]]
                            self.answers[d[-2]]['filledby'] = [d[1]]
                            self.answers[d[-2]]['uid'] = [d[-2]]
                    else:
                        if multipleans:
                            self.answers[d[-2]] = {
                                cpid: [self.tackle_multiple(d, multipleans, cpid)],
                                'datetime': [d[11]],
                                'filledby': [d[1]],
                                'uid': [d[-2]]
                            }
                        else:
                            if str(d[5])('utf-8') == "Other":
                                self.answers[d[-2]] = {
                                    cpid: ["Other-"+d[6]],
                                    'datetime': [d[11]],
                                    'filledby': [d[1]],
                                    'uid': [d[-2]]
                                }
                            else:
                                self.answers[d[-2]] = {
                                    cpid: [d[5]],
                                    'datetime': [d[11]],
                                    'filledby': [d[1]],
                                    'uid': [d[-2]]
                                }
                        datacount += 1
                except Exception as e:
                    # Exception if Hindi characters are compared to "Other"
                    if d[-2] in self.answers.keys():
                        if cpid in self.answers[d[-2]].keys():
                            if multipleans:
                                self.answers[d[-2]][cpid].append(self.tackle_multiple(d, multipleans, cpid))
                            else:
                                self.answers[d[-2]][cpid].append(d[5].replace(',', ' '))

                            self.answers[d[-2]]['datetime'].append(d[11])
                            self.answers[d[-2]]['filledby'].append(d[1])
                            self.answers[d[-2]]['uid'].append(d[-2])
                        else:
                            if multipleans:
                                self.answers[d[-2]][cpid] = [self.tackle_multiple(d, multipleans, cpid)]
                            else:
                                self.answers[d[-2]][cpid] = [d[5].replace(',', ' ')]

                            self.answers[d[-2]]['datetime'] = [d[11]]
                            self.answers[d[-2]]['filledby'] = [d[1]]
                            self.answers[d[-2]]['uid'] = [d[-2]]
                    else:
                        if multipleans:
                            self.answers[d[-2]] = {
                                cpid: [self.tackle_multiple(d, multipleans, cpid)],
                                'datetime': [d[11]],
                                'filledby': [d[1]],
                                'uid': [d[-2]]
                            }
                        else:
                            self.answers[d[-2]] = {
                                cpid: [d[5]],
                                'datetime': [d[11]],
                                'filledby': [d[1]],
                                'uid': [d[-2]]
                            }
                        datacount += 1

        for ids in self.answers.keys():
            for cpid in self.checkpoint_ids:
                if cpid not in self.answers[ids].keys():
                    # Check if question is multiple answer question
                    if '.' in str(cpid):
                        cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT1 WHERE CHECKPOINT1_ID LIKE '%s'""" % (cpid)
                    else:
                        cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (cpid)
                    self.cursor.execute(cp_sql)

                    cp_data = self.cursor.fetchall()

                    try:
                        if int(cp_data[0][0]) == 5:
                            multipleans = list(cp_data[0][1].split(','))
                        else:
                            multipleans = None
                    except Exception as e:
                        multipleans = None

                    if multipleans:
                        answer = ['-' for i in range(len(multipleans))]
                        answer = ','.join(answer)
                        self.answers[ids][cpid] = [answer]

    def fetchcheckpointcodedata(self):
        # Fetch relevant data for the given checkpoints
        datacount = 0
        self.answers = {}

        for cpid in self.checkpoint_ids:

            # Check if question is multiple answer question
            if '.' in str(cpid):
                cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT1 WHERE CHECKPOINT1_ID LIKE '%s'""" % (cpid)
            else:
                cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (cpid)
            self.cursor.execute(cp_sql)

            cp_data = self.cursor.fetchall()

            try:
                if int(cp_data[0][0]) == 5:
                    multipleans = list(cp_data[0][1].split(','))
                else:
                    multipleans = None
            except Exception as e:
                multipleans = None


            # Fetch responses
            from datetime import datetime as dt
            sql = """SELECT * FROM SAVE_SURVEY WHERE CHECKPOINT_ID LIKE '%s' \
                    AND DATETIME > '%s'""" % (cpid, dt.now()-timedelta(days=5))
            self.cursor.execute(sql)

            data = self.cursor.fetchall()

            for d in data:
                try:
                    if d[-2] in self.answers.keys():
                        if cpid in self.answers[d[-2]].keys():

                            if multipleans:
                                self.answers[d[-2]][cpid].append(self.tackle_multiple(d, multipleans, cpid))
                            else:
                                if str(d[5])('utf-8') == "Other":
                                    self.answers[d[-2]][cpid].append("Other-"+d[6])
                                else:
                                    if int(cp_data[0][0]) == 15:
                                        self.answers[d[-2]][cpid].append(d[5].split('-')[0])
                                    else:
                                        self.answers[d[-2]][cpid].append(d[5])

                            self.answers[d[-2]]['datetime'].append(d[11])
                            self.answers[d[-2]]['filledby'].append(d[1])
                            self.answers[d[-2]]['uid'].append(d[-2])
                        else:
                            if multipleans:
                                self.answers[d[-2]][cpid] = [self.tackle_multiple(d, multipleans, cpid)]
                            else:
                                if str(d[5])('utf-8') == "Other":
                                    self.answers[d[-2]][cpid] = ["Other-"+d[6]]
                                else:
                                    if int(cp_data[0][0]) == 15:
                                        self.answers[d[-2]][cpid] = [d[5].split('-')[0]]
                                    else:
                                        self.answers[d[-2]][cpid] = [d[5]]

                            self.answers[d[-2]]['datetime'] = [d[11]]
                            self.answers[d[-2]]['filledby'] = [d[1]]
                            self.answers[d[-2]]['uid'] = [d[-2]]
                    else:
                        if multipleans:
                            self.answers[d[-2]] = {
                                cpid: [self.tackle_multiple(d, multipleans, cpid)],
                                'datetime': [d[11]],
                                'filledby': [d[1]],
                                'uid': [d[-2]]
                            }
                        else:
                            if str(d[5])('utf-8') == "Other":
                                self.answers[d[-2]] = {
                                    cpid: ["Other-"+d[6]],
                                    'datetime': [d[11]],
                                    'filledby': [d[1]],
                                    'uid': [d[-2]]
                                }
                            else:
                                if int(cp_data[0][0]) == 15:
                                    self.answers[d[-2]] = {
                                        cpid: [d[5].split('-')[0]],
                                        'datetime': [d[11]],
                                        'filledby': [d[1]],
                                        'uid': [d[-2]]
                                    }
                                else:
                                    self.answers[d[-2]] = {
                                        cpid: [d[5]],
                                        'datetime': [d[11]],
                                        'filledby': [d[1]],
                                        'uid': [d[-2]]
                                    }
                        datacount += 1
                except Exception as e:
                    # Exception if Hindi characters are compared to "Other"
                    if d[-2] in self.answers.keys():
                        if cpid in self.answers[d[-2]].keys():
                            if multipleans:
                                self.answers[d[-2]][cpid].append(self.tackle_multiple(d, multipleans, cpid))
                            else:
                                self.answers[d[-2]][cpid].append(d[5])

                            self.answers[d[-2]]['datetime'].append(d[11])
                            self.answers[d[-2]]['filledby'].append(d[1])
                            self.answers[d[-2]]['uid'].append(d[-2])
                        else:
                            if multipleans:
                                self.answers[d[-2]][cpid] = [self.tackle_multiple(d, multipleans, cpid)]
                            else:
                                self.answers[d[-2]][cpid] = [d[5]]

                            self.answers[d[-2]]['datetime'] = [d[11]]
                            self.answers[d[-2]]['filledby'] = [d[1]]
                            self.answers[d[-2]]['uid'] = [d[-2]]
                    else:
                        if multipleans:
                            self.answers[d[-2]] = {
                                cpid: [self.tackle_multiple(d, multipleans, cpid)],
                                'datetime': [d[11]],
                                'filledby': [d[1]],
                                'uid': [d[-2]]
                            }
                        else:
                            self.answers[d[-2]] = {
                                cpid: [d[5]],
                                'datetime': [d[11]],
                                'filledby': [d[1]],
                                'uid': [d[-2]]
                            }
                        datacount += 1

        for ids in self.answers.keys():
            for cpid in self.checkpoint_ids:
                if cpid not in self.answers[ids].keys():
                    # Check if question is multiple answer question
                    if '.' in str(cpid):
                        cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT1 WHERE CHECKPOINT1_ID LIKE '%s'""" % (cpid)
                    else:
                        cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (cpid)
                    self.cursor.execute(cp_sql)

                    cp_data = self.cursor.fetchall()

                    try:
                        if int(cp_data[0][0]) == 5:
                            multipleans = list(cp_data[0][1].split(','))
                        else:
                            multipleans = None
                    except Exception as e:
                        multipleans = None

                    if multipleans:
                        answer = ['-' for i in range(len(multipleans))]
                        answer = ','.join(answer)
                        self.answers[ids][cpid] = [answer]

    def duplicate_ids(self):
        # Deal with duplicates in id1
        tempflag = False
        ind = 0
        while tempflag is False:
            try:
                for idx in self.answers.keys():
                    if len(self.answers[idx][self.checkpoint_ids[ind]]) > 1:
                        for i in range(1, len(self.answers[idx][self.checkpoint_ids[ind]])):
                            salt = str(idx)+str(randint(0, 9999))
                            for cpid in self.checkpoint_ids:
                                try:
                                    if cpid in self.answers[idx].keys():
                                        if salt not in self.answers.keys():
                                            self.answers[salt] = {}
                                        self.answers[salt][cpid] = [self.answers[idx][cpid][i]]
                                        self.answers[salt]['datetime'] = [self.answers[idx]['datetime'][i]]
                                        self.answers[salt]['filledby'] = [self.answers[idx]['filledby'][i]]
                                        self.answers[salt]['uid'] = [self.answers[idx]['uid'][i]]
                                except Exception as e:
                                    pass
                tempflag = True
            except Exception as e:
                ind += 1

        #End of duplicates

    def data_to_csv(self, fname):
        appended = []
        output = []

        # Headers
        for question in self.checkpoint_ids:
            if '.' in str(question):
                sql = """SELECT CHECKPOINT_NAME, TYPE_ID, SIZE, VALUE FROM CHECKPOINT1 WHERE CHECKPOINT1_ID LIKE '%s'""" % (question)
            else:
                sql = """SELECT CHECKPOINT_NAME, TYPE_ID, SIZE, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (question)
            self.cursor.execute(sql)
            data = self.cursor.fetchall()

            # Appending question to headers
            if self.checkpoint_ids.count(question) > 1:
                if question in appended:
                    try:
                        if int(data[appended.count(question)][1]) == 5:
                            self.add_multiple(data[appended.count(question)], output, question, appended)
                        else:
                            output.append(data[appended.count(question)][0]('utf-8').replace('\n', ' '))
                    except Exception as e:
                        output.append('-')
                else:
                    if int(data[0][1]) == 5:
                        self.add_multiple(data[0], output, question, appended)
                    else:
                        output.append(data[0][0]('utf-8').replace('\n', ' '))

                appended.append(question)
            else:
                try:
                    if int(data[0][1]) == 5:
                        self.add_multiple(data[0], output, question, appended)
                    else:
                        output.append(data[0][0]('utf-8').replace('\n', ' '))
                except Exception as e:
                    output.append('-')

            # for d in data:
            #     if int(d[1]) == 5:
            #         self.add_multiple(d, output)
            #     else:
            #         output.append(d[0]('utf-8').replace('\n', ' '))

        output.append('uid')
        output.append('datetime')
        output.append('filledby')
        output.append('starttime')
        output.append('endtime')
        output.append('startlat')
        output.append('startlong')
        output.append('endlat')
        output.append('endlong')
        # csvwriter.writerow(output)
        self.finaloutput.append(output)

        # End of Headers

        # Raw data
        for datainstance in self.answers.keys():
            output = []
            for question in self.checkpoint_ids:
                try:
                    if ',' in str(self.answers[datainstance][question][0])('utf-8'):
                        op = str(self.answers[datainstance][question][0])('utf-8').split(',')
                        for singleop in op:
                            output.append(singleop)
                        # output.append(str(self.answers[datainstance][question][0])('utf-8'))
                    else:
                        output.append(str(self.answers[datainstance][question][0])('utf-8'))
                except Exception as e:
                    if question in self.answers[datainstance].keys():
                        output.append(self.answers[datainstance][question][0]('utf-8'))
                    else:
                        output.append('-')

            try:
                output.append(self.answers[datainstance]['uid'][0])
                output.append(self.answers[datainstance]['datetime'][0].strftime("%Y-%m-%d %H:%M:%S"))
                output.append(self.answers[datainstance]['filledby'][0])
            except Exception as e:
                # duplicates exception
                output.append('-')
                output.append('-')

            # fetch movement
            try:
                sql = """SELECT SURVEY_ID, LATITUDE, LONGITUDE, DEVICE_DATETIME, SERVER_DATETIME FROM MOVEMENT WHERE \
                        SURVEY_ID LIKE %s AND STATUS LIKE %s"""
                self.cursor.execute(sql, (self.answers[datainstance]['uid'][0], 'START', ))
                data = self.cursor.fetchall()[0]
                output.append(data[3])
                sql2 = """SELECT SURVEY_ID, LATITUDE, LONGITUDE, DEVICE_DATETIME, SERVER_DATETIME FROM MOVEMENT WHERE \
                        SURVEY_ID LIKE %s AND STATUS LIKE %s"""
                self.cursor.execute(sql2, (self.answers[datainstance]['uid'][0], 'END', ))
                data2 = self.cursor.fetchall()[0]

                output.append(data2[3])

                output.append(data[1])
                output.append(data[2])
                output.append(data2[1])
                output.append(data2[2])
            except Exception as e:
                sql = """SELECT SURVEY_ID, LATITUDE, LONGITUDE, DEVICE_DATETIME, SERVER_DATETIME FROM MOVEMENT WHERE \
                        SURVEY_ID LIKE %s"""
                self.cursor.execute(sql, (self.answers[datainstance]['uid'][0], ))
                data = self.cursor.fetchall()
                output.append("-")
                output.append("-")
                output.append("-")
                output.append("-")
                output.append("-")
                output.append("-")

            self.finaloutput.append(output)

    def add_multiple(self, d, output, question, appended):
        for data in d[3].split(','):
            try:
                output.append(d[0]('utf-8').replace('\n', ' ')+" "+data('utf-8'))
            except Exception as e:
                output.append(''.join(i for i in d[0]('utf-8') if ord(i)<128).replace('\n', ' ')+" "+''.join(i for i in data('utf-8') if ord(i)<128).replace('\n', ' '))

    def fetchqualityreports(self, projectid):
        projectobj = Project.objects.get(id=projectid)
        qualityparams = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='Verified')
                        )

        qualitydict = {}

        for param in qualityparams:
            remarksdict = json.loads(param.remarks)
            paramsdict = json.loads(param.params)
            if remarksdict['uid'] in qualitydict.keys():
                pass
            else:
                qualitydict[remarksdict['uid']] = {}
                qualitydict[remarksdict['uid']]['uid'] = remarksdict['uid']
                qualitydict[remarksdict['uid']]['surveyor'] = remarksdict['surveyor']
                qualitydict[remarksdict['uid']]['auditor'] = "%s %s" % (param.user.user.first_name, param.user.user.last_name)

                try:
                    qualitydict[remarksdict['uid']]['teamleader'] = paramsdict['tldetails']
                except Exception as e:
                    qualitydict[remarksdict['uid']]['teamleader'] = '-'

                qualitydict[remarksdict['uid']]['date'] = parse(paramsdict['date']).date()
                qualitydict[remarksdict['uid']]['time'] = parse(paramsdict['time']).time()
                qualitydict[remarksdict['uid']]['geocodes'] = remarksdict['geocodes']
                qualitydict[remarksdict['uid']]['comments'] = remarksdict['comments']
                qualitydict[remarksdict['uid']]['verification_date'] = param.verification_date.date()
                qualitydict[remarksdict['uid']]['verification_time'] = param.verification_date.time()

                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    try:
                        qualitydict[remarksdict['uid']][str(key)] = remarksdict[str(key)]
                        qualitydict[remarksdict['uid']]['%s_remarks' % (str(key))] = remarksdict['%s_remarks' % (str(key))]
                    except Exception as e:
                        pass

                qualitydict[remarksdict['uid']]['interviewduration'] = remarksdict['interviewduration']

                qualitydict[remarksdict['uid']]['movement'] = remarksdict['movement']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="qualityreport.csv"'
        writer = csv.writer(response)

        # qckeys = list(remarksdict.keys())
        cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
        checkpoints = json.loads(cps.cplist).keys()
        cp_remarks = ['%s_remarks' % (i) for i in checkpoints]
        qckeys = [
            'uid',
            'surveyor',
            'auditor'
            'teamleader',
            'date',
            'time'
        ] + checkpoints + cp_remarks + ['interviewduration', 'movement', 'geocodes', 'comments', 'verification_date', 'verification_time']


        temp = []
        for key in qckeys:
            temp.append(key)

        writer.writerow(temp)

        for key in qualitydict:
            try:
                temp = []
                for qck in qckeys:
                    try:
                        temp.append(qualitydict[key][qck])
                    except Exception as e:
                        temp.append('-')
                writer.writerow(temp)
            except Exception as e:
                pass

        return response

    def fetchqualitysummaryreports(self, projectid):
        projectobj = Project.objects.get(id=projectid)
        qualityparams = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='Verified')
                        )

        qualitydict = {}

        surveyor_dict = {}

        for param in qualityparams:
            remarksdict = json.loads(param.remarks)

            if remarksdict['surveyor'] in surveyor_dict.keys():
                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    try:
                        if remarksdict[str(key)] == 'Variation':
                            surveyor_dict[remarksdict['surveyor']][str(key)] += 1
                    except Exception as e:
                        pass

                if remarksdict['interviewduration'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['interviewduration'] += 1

                if remarksdict['geocodes'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['geocodes'] += 1

                if remarksdict['movement'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['movement'] += 1

                surveyor_dict[remarksdict['surveyor']]['totalverified'] += 1

            else:
                surveyor_dict[remarksdict['surveyor']] = {}
                surveyor_dict[remarksdict['surveyor']]['surveyor'] = remarksdict['surveyor']
                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    surveyor_dict[remarksdict['surveyor']][str(key)] = 0

                surveyor_dict[remarksdict['surveyor']]['interviewduration'] = 0
                surveyor_dict[remarksdict['surveyor']]['geocodes'] = 0
                surveyor_dict[remarksdict['surveyor']]['movement'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalverified'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalformsfilled'] = 0

                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    try:
                        if remarksdict[str(key)] == 'Variation':
                            surveyor_dict[remarksdict['surveyor']][str(key)] += 1
                    except Exception as e:
                        pass

                if remarksdict['interviewduration'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['interviewduration'] += 1

                if remarksdict['geocodes'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['geocodes'] += 1

                if remarksdict['movement'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['movement'] += 1

                surveyor_dict[remarksdict['surveyor']]['totalverified'] += 1

        totalcountobj = SurveyResponse.objects.filter(
                            project=projectobj
                        )

        for objkey in totalcountobj:
            respdict = json.loads(objkey.params)
            if respdict['surveyor'] in surveyor_dict.keys():
                if objkey.otp_verified:
                    if 'otpverified' in surveyor_dict[respdict['surveyor']].keys():
                        surveyor_dict[respdict['surveyor']]['otpverified'] += 1
                    else:
                        surveyor_dict[respdict['surveyor']]['otpverified'] = 1
                else:
                    if 'otpverified' in surveyor_dict[respdict['surveyor']].keys():
                        surveyor_dict[respdict['surveyor']]['otpverified'] += 0
                    else:
                        surveyor_dict[respdict['surveyor']]['otpverified'] = 0
                surveyor_dict[respdict['surveyor']]['totalformsfilled'] += 1
            else:
                surveyor_dict[respdict['surveyor']] = {}
                surveyor_dict[respdict['surveyor']]['surveyor'] = respdict['surveyor']
                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    surveyor_dict[respdict['surveyor']][str(key)] = 0

                if objkey.otp_verified:
                    surveyor_dict[respdict['surveyor']]['otpverified'] = 1
                else:
                    surveyor_dict[respdict['surveyor']]['otpverified'] = 0

                surveyor_dict[respdict['surveyor']]['interviewduration'] = 0
                surveyor_dict[respdict['surveyor']]['geocodes'] = 0
                surveyor_dict[respdict['surveyor']]['movement'] = 0
                surveyor_dict[respdict['surveyor']]['totalverified'] = 0
                surveyor_dict[respdict['surveyor']]['totalformsfilled'] = 1

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="qualitysummaryreport.csv"'
        writer = csv.writer(response)

        # qckeys = list(surveyor_dict[remarksdict['surveyor']].keys())
        cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
        checkpoints = json.loads(cps.cplist).keys()

        qckeys = [
            'surveyor'
            ] + checkpoints + [
            'interviewduration',
            'movement',
            'geocodes',
            'totalverified',
            'otpverified',
            'totalformsfilled'
        ]

        temp = []
        for key in qckeys:
            temp.append(key)

        writer.writerow(temp)

        for key in surveyor_dict:
            temp = []
            for qck in qckeys:
                temp.append(surveyor_dict[key][qck])
            writer.writerow(temp)

        return response

    def fetchqualitysummaryreportsinternal(self, request, projectid):
        projectobj = Project.objects.get(id=projectid)

        if 'days' in request.GET.keys():
            qcparams = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='Verified')
                            )

            qualityparams = []
            for param in qcparams:
                try:
                    params = json.loads(param.params)

                    respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
                    if respdate.date() == date.today() - timedelta(days=int(request.GET['days'])):
                        qualityparams.append(param.remarks)
                    else:
                        continue
                except Exception as e:
                    continue

        elif 'from_date' in request.GET.keys() and 'to_date' in request.GET.keys():
            qcparams = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='Verified')
                            )

            from_date = datetime.strptime('%s %s' % (request.GET['from_date'], '00:00:00'), '%d-%m-%Y %H:%M:%S')
            to_date = datetime.strptime('%s %s' % (request.GET['to_date'], '23:59:59'), '%d-%m-%Y %H:%M:%S')

            qualityparams = []
            for param_obj in qcparams:
                try:
                    params = json.loads(param_obj.params)

                    respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')

                    if respdate >= from_date and respdate <= to_date:
                        qualityparams.append(param_obj.remarks)
                    else:
                        continue
                except Exception as e:
                    continue

        else:
            qualityparams = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='Verified')
                            )

        qualitydict = {}

        surveyor_dict = {}

        for param in qualityparams:
            if 'days' in request.GET.keys() or 'from_date' in request.GET.keys():
                remarksdict = json.loads(param)
            else:
                remarksdict = json.loads(param.remarks)

            variation = False
            no_recording = False
            not_audible = False
            language_barrier = False
            technical_issues = False
            na = False

            if remarksdict['surveyor'] in surveyor_dict.keys():
                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    try:
                        if remarksdict[str(key)] == 'Variation':
                            surveyor_dict[remarksdict['surveyor']][str(key)] += 1
                            variation = True
                        elif remarksdict[str(key)] == 'No_recording':
                            no_recording = True
                        elif remarksdict[str(key)] == 'Not_audible':
                            not_audible = True
                        elif remarksdict[str(key)] == 'NA':
                            na = True
                        elif remarksdict[str(key)] == 'Language_barrier':
                            language_barrier = True
                        elif remarksdict[str(key)] == 'Technical_issues':
                            technical_issues = True
                    except Exception as e:
                        print(e)

                if remarksdict['interviewduration'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['interviewduration'] += 1

                if remarksdict['geocodes'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['geocodes'] += 1

                if remarksdict['movement'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['movement'] += 1

                surveyor_dict[remarksdict['surveyor']]['totalverified'] += 1

                if variation:
                    surveyor_dict[remarksdict['surveyor']]['totalvariation'] += 1

                if no_recording:
                    surveyor_dict[remarksdict['surveyor']]['no_recording'] += 1

                if not_audible:
                    surveyor_dict[remarksdict['surveyor']]['not_audible'] += 1

                if na:
                    surveyor_dict[remarksdict['surveyor']]['na'] += 1

                if language_barrier:
                    surveyor_dict[remarksdict['surveyor']]['language_barrier'] += 1

                if technical_issues:
                    surveyor_dict[remarksdict['surveyor']]['technical_issues'] += 1

            else:
                surveyor_dict[remarksdict['surveyor']] = {}
                surveyor_dict[remarksdict['surveyor']]['surveyor'] = remarksdict['surveyor']
                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    surveyor_dict[remarksdict['surveyor']][str(key)] = 0

                surveyor_dict[remarksdict['surveyor']]['interviewduration'] = 0
                surveyor_dict[remarksdict['surveyor']]['geocodes'] = 0
                surveyor_dict[remarksdict['surveyor']]['movement'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalverified'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalformsfilled'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalvariation'] = 0
                surveyor_dict[remarksdict['surveyor']]['no_recording'] = 0
                surveyor_dict[remarksdict['surveyor']]['not_audible'] = 0
                surveyor_dict[remarksdict['surveyor']]['language_barrier'] = 0
                surveyor_dict[remarksdict['surveyor']]['technical_issues'] = 0
                surveyor_dict[remarksdict['surveyor']]['na'] = 0

                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()

                no_recordings_count = 0

                for key in checkpoints:
                    try:
                        if remarksdict[str(key)] == 'Variation':
                            surveyor_dict[remarksdict['surveyor']][str(key)] += 1
                            variation = True
                        elif remarksdict[str(key)] == 'No_recording':
                            no_recording = True
                        elif remarksdict[str(key)] == 'Not_audible':
                            not_audible = True
                        elif remarksdict[str(key)] == 'NA':
                            na = True
                        elif remarksdict[str(key)] == 'Language_barrier':
                            language_barrier = True
                        elif remarksdict[str(key)] == 'Technical_issues':
                            technical_issues = True
                    except Exception as e:
                        pass

                if remarksdict['interviewduration'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['interviewduration'] += 1

                if remarksdict['geocodes'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['geocodes'] += 1

                if remarksdict['movement'] == 'Yes':
                    surveyor_dict[remarksdict['surveyor']]['movement'] += 1

                if variation:
                    surveyor_dict[remarksdict['surveyor']]['totalvariation'] += 1

                if no_recording:
                    surveyor_dict[remarksdict['surveyor']]['no_recording'] += 1

                if not_audible:
                    surveyor_dict[remarksdict['surveyor']]['not_audible'] += 1

                if na:
                    surveyor_dict[remarksdict['surveyor']]['na'] += 1

                if technical_issues:
                    surveyor_dict[remarksdict['surveyor']]['technical_issues'] += 1

                surveyor_dict[remarksdict['surveyor']]['totalverified'] += 1


        totalcountobj = SurveyResponse.objects.filter(
                            project=projectobj
                        )

        # If forms not verified yet
        for objkey in totalcountobj:
            if 'days' in request.GET.keys() or 'from_date' in request.GET.keys():
                params = json.loads(objkey.params)
                respdate = datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')

                if 'days' in request.GET and respdate.date() != date.today() - timedelta(days=int(request.GET['days'])):
                    continue
                elif 'from_date' in request.GET and (respdate < from_date or respdate > to_date):
                    continue

            respdict = json.loads(objkey.params)
            if respdict['surveyor'] in surveyor_dict.keys():
                if objkey.otp_verified:
                    if 'otpverified' in surveyor_dict[respdict['surveyor']].keys():
                        surveyor_dict[respdict['surveyor']]['otpverified'] += 1
                    else:
                        surveyor_dict[respdict['surveyor']]['otpverified'] = 1
                else:
                    if 'otpverified' in surveyor_dict[respdict['surveyor']].keys():
                        surveyor_dict[respdict['surveyor']]['otpverified'] += 0
                    else:
                        surveyor_dict[respdict['surveyor']]['otpverified'] = 0
                surveyor_dict[respdict['surveyor']]['totalformsfilled'] += 1
            else:
                surveyor_dict[respdict['surveyor']] = {}
                surveyor_dict[respdict['surveyor']]['surveyor'] = respdict['surveyor']
                cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
                checkpoints = json.loads(cps.cplist).keys()
                for key in checkpoints:
                    surveyor_dict[respdict['surveyor']][str(key)] = 0

                if objkey.otp_verified:
                    surveyor_dict[respdict['surveyor']]['otpverified'] = 1
                else:
                    surveyor_dict[respdict['surveyor']]['otpverified'] = 0

                surveyor_dict[respdict['surveyor']]['interviewduration'] = 0
                surveyor_dict[respdict['surveyor']]['geocodes'] = 0
                surveyor_dict[respdict['surveyor']]['movement'] = 0
                surveyor_dict[respdict['surveyor']]['totalverified'] = 0
                surveyor_dict[respdict['surveyor']]['totalvariation'] = 0
                surveyor_dict[respdict['surveyor']]['no_recording'] = 0
                surveyor_dict[respdict['surveyor']]['not_audible'] = 0
                surveyor_dict[respdict['surveyor']]['na'] = 0
                surveyor_dict[respdict['surveyor']]['technical_issues'] = 0
                surveyor_dict[respdict['surveyor']]['language_barrier'] = 0
                surveyor_dict[respdict['surveyor']]['totalformsfilled'] = 1

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="internalqualitysummaryreport.csv"'
        writer = csv.writer(response)

        # qckeys = list(surveyor_dict[remarksdict['surveyor']].keys())
        cps = AudioCheckpoints.objects.get(project=Project.objects.get(pk=projectid))
        checkpoints = json.loads(cps.cplist).keys()
        qckeys = [
            'surveyor'
        ] + checkpoints + \
        [
            'totalvariation',
            'no_recording',
            'not_audible',
            'na',
            'technical_issues',
            'language_barrier',
            'interviewduration',
            'movement',
            'geocodes',
            'totalverified',
            'otpverified',
            'totalformsfilled',
        ]

        temp = []
        for key in qckeys:
            temp.append(key)

        writer.writerow(temp)

        for key in surveyor_dict:
            temp = []
            for qck in qckeys:
                temp.append(surveyor_dict[key][qck])
            writer.writerow(temp)

        return response

    def exportgpsanalysisreport(self, request):
        cnt=0
        googleapis_dist=[]
        googleapis_average = 0
        googleapis_count = 0
        googleapis_nonothers = 0
        google_actual = 0

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="googlemaps.csv"'

        writer = csv.writer(response)

        writer.writerow(['cnt', 'source', 'date', 'village_distance', 'village', 'actualaddress'])
        for resp in SurveyResponse.objects.all().order_by('-pk')[:10000]:
            if json.loads(resp.params)['village_distance'] != 'GPS issue' and json.loads(resp.params)['startlat']!=None:
                cnt+=1
                # dist.append(int(json.loads(resp.params)['village_distance'].replace(','','')))

                googleapis_dist.append(int(json.loads(resp.params)['village_distance'].replace(',','')))
                writer.writerow([cnt, 'googleapis', json.loads(resp.params)['date'], json.loads(resp.params)['village_distance'].replace(',', ''), json.loads(resp.params)['village'], json.loads(resp.params)['actualaddress']])

                if ') -' in json.loads(resp.params)['village'] or ') (' in json.loads(resp.params)['village']:
                    googleapis_nonothers += 1


                try:
                    if str(json.loads(resp.params)['actualaddress']) == 'GPS issue':
                        continue

                    if json.loads(resp.params)['village'] != None and ') -' in json.loads(resp.params)['village'] \
                        and (str(json.loads(resp.params)['village'].split(') - ')[1]).lower() in json.loads(resp.params)['actualaddress'].lower() \
                        or str(json.loads(resp.params)['village'].split('-')[1].split('(')[0]).lower() in json.loads(resp.params)['actualaddress'].lower()):
                        google_actual += 1
                    elif json.loads(resp.params)['village'] != None and ') (' in json.loads(resp.params)['village'] and str(json.loads(resp.params)['village'].split('(')[0].split('-')[1].split(' ')[0]).lower() in json.loads(resp.params)['actualaddress'].lower():
                        google_actual += 1
                    elif json.loads(resp.params)['village'] != None and str(json.loads(resp.params)['village']).lower() in json.loads(resp.params)['actualaddress'].lower():
                        google_actual += 1
                    elif json.loads(resp.params)['actualaddress'] != None and str(json.loads(resp.params)['actualaddress'].replace(' ', '')) != '':
                        ##print( json.loads(resp.params)['village'], '------', json.loads(resp.params)['actualaddress'], '\n\n')
                        pass                
                except Exception as e:
                    pass


        lessthan100m = 0
        lessthan1km = 0
        lessthan5km = 0
        lessthan10km = 0
        lessthan25km = 0
        lessthan50km = 0
        lessthan100km = 0
        greaterthan100km = 0

        for dist in googleapis_dist:
            if int(dist) < 100:
                lessthan100m += 1
            elif int(dist) < 1000 and int(dist) > 100:
                lessthan1km += 1
            elif int(dist) < 5000 and int(dist) > 1000:
                lessthan5km += 1
            elif int(dist) < 10000 and int(dist) > 5000:
                lessthan10km += 1
            elif int(dist) < 25000 and int(dist) > 10000:
                lessthan25km += 1
            elif int(dist) < 50000 and int(dist) > 25000:
                lessthan50km += 1
            elif int(dist) < 100000 and int(dist) > 50000:
                lessthan100km += 1
            elif int(dist) > 100000:
                greaterthan100km += 1

        writer.writerow([])
        writer.writerow([])
        writer.writerow(['Source', '<100 m', '<1 km', '<5 km', '<10 km', '<25 km', '<50 km', '<100 km', '>100 km', 'Non Others', 'Actual address matching'])

        writer.writerow(['Google', lessthan100m, lessthan1km, lessthan5km, lessthan10km, lessthan25km, lessthan50km, lessthan100km, greaterthan100km, googleapis_nonothers, google_actual])

        googleapis_average = sum(googleapis_dist) / len(googleapis_dist)

        writer.writerow([])
        writer.writerow([])
        writer.writerow(['Google Average', googleapis_average])

        return response
