# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils import timezone
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
import datetime
from datetime import timedelta
from datetime import date
from time import mktime
# from mainapp.tasks import *
import io
from random import randint
import os
import ast
import json
import xlsxwriter
from dateutil.parser import parse
from django.db.models import Q, Count
from dateutil import tz
import requests

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from quality.ratelimit import rate_limit, get_client_ip  #type: ignore


@method_decorator(login_required(login_url='/login'), name='dispatch')
@method_decorator(
    rate_limit(limit=10, window_seconds=60, scope='exportdata',
               key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}"),
    name='dispatch',
)
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
                   
                    return self.exporttocsvfromdump(request, projectobj)
           
            elif request.GET['export'] == 'quality':
                return self.fetchqualityreports(projectid)
            elif request.GET['export'] == 'qualitysummary':
                return self.fetchqualitysummaryreports(projectid)
            elif request.GET['export'] == 'qualitysummaryinternal':
                return self.fetchqualitysummaryreportsinternal(request, projectid)
            
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
          
            elif request.GET['export'] == 'productivityreports':
                productivitydict, surveyorlist = self.fetchproductivityreport(request)
                return self.exportproductivityreport(productivitydict, surveyorlist, request)
                # fetchinventoryreports.delay()

                return self.exportinventorytrackingreport(request)

        if 'export' in request.GET.keys() and request.GET['export'] == 'pmsreports':
            return self.exportpmsreport2(request)
            # return self.exportpmsreports(request)
            # return self.exportpmsreports_akhil(request)

        return render(request, 'index.html', data)


    

    def fetchhaltwisereports(self, request, project):
        
        daysreq = int(request.GET['days'])
        print(daysreq,"ddddd")
        if project != None:
            surveyresponses = SurveyResponse.objects.all().order_by(('-pk'))[:3000]
            # surveyresponses = SurveyResponse.objects.filter(project=project)
        else:
            return None

        fr_dict = {}

        respcount = surveyresponses.count()
        # print(resp)
        # for resp in surveyresponses:
        for i in range(0, respcount):
            print(i)
            resp = surveyresponses[i]
            params = json.loads(resp.params)

            if 'meta' in params and params['meta']['datetime'] == 0:
                continue

            try:
                respdate = datetime.datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
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
                respdate = datetime.datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
            elif params['date'] != None:
                respdate = datetime.datetime.strptime('%s %s' % (params['date'], "0:0:0"), '%d-%b-%Y %H:%M:%S')
            else:
                respdate = datetime.datetime.now() - timedelta(days=365*1111)

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
                respdate = datetime.datetime.strptime('%s %s' % (params['date'], params['time']), '%d-%b-%Y %H:%M:%S')
                if respdate.date() != date.today() - timedelta(days=daysreq):
                    respdate = None
            except Exception as e:
                respdate = None

            if respdate != None:
                try:
                    emp = resp.surveyor.employee_id
                except Exception as e:
                    emp = resp.surveyor


                if daysreq == 0 and respdate.time() > datetime.datetime.now().time() and emp in surveyordict.keys():
                    surveyordict[emp]['totalforms'] += 1
                elif daysreq == 0 and respdate.time() > datetime.datetime.now().time():
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

                if date.today() - datetime.datetime.strptime(str(respdict['date']), '%d-%b-%Y').date() == timedelta(days=dayreq):
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

            if date.today() - datetime.datetime.strptime(str(respdict['date']), '%d-%b-%Y').date() == timedelta(days=dayreq):
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
        start_date = timezone.make_aware(datetime.datetime.combine(
            date.today() - timedelta(days=dayreq),
            datetime.time.min,
        ))
        end_date = timezone.make_aware(datetime.datetime.combine(
            date.today() - timedelta(days=dayreq - 1),
            datetime.time.max,
        ))
        rows = (
            SurveyResponse.objects
            .filter(
                project_id=request.GET['project'],
                verification_date__gte=start_date,
                verification_date__lte=end_date,
                verification_status__name='Verified',
            )
            .values(
                'user__user__first_name',
                'user__user__last_name',
            )
            .annotate(verified_count=Count('id'))
        )
        return [
            [
                f"{row['user__user__first_name']} {row['user__user__last_name']}",
                row['verified_count'],
                start_date.date(),
            ]
            for row in rows
        ]

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




    def exporttocsvfromdump(self, request, projectobj):
        print(request.GET['from_date'] , request.GET['to_date'],"1122")
        
        if request.GET['from_date'] and request.GET['to_date']:
            start_date = request.GET['from_date']
            end_date = request.GET['to_date']

            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            day_diff = (end_date - start_date).days
    
            if day_diff < 0:
                return JsonResponse({"error": "End date cannot be before start date."}, status=400)
            if day_diff > 7:
                return JsonResponse({"error": "The difference between the dates should not exceed 7 days."}, status=400)
            print(projectobj)
            
            prj = Project.objects.filter(id = projectobj.id).values_list('name',flat=True)
            import zipfile
            import xml.etree.ElementTree as ET
            import io
            
            token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyQ29kZSI6InFjYXVkaXQiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczODE0NjIwOCwiZXhwIjoxNzM4NzUxMDA4fQ.6BPFxKM3m42DSWM2TzGeLH5FeicNB8lvKrotxi2YJ9E"
            headers = {"Authorization":token,"accept":"application/json","locale":"en"}
            Export_data_api = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-download/download-range/340?format=excel&download=true&startDate={start_date}&endDate={end_date}"

            try:
                response = requests.get(Export_data_api, headers=headers)
                response.raise_for_status()  # Raise HTTPError for bad responses
                data = response.json().get('data', {})
            except Exception as e:
                print(e)
            
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
        

    def _project_checkpoints(self, projectid):
        latest_response = (
            SurveyResponse.objects
            .filter(project_id=projectid)
            .only('params')
            .order_by('-id')
            .first()
        )
        if not latest_response:
            return []
        return [
            checkpoint[1]
            for checkpoint in json.loads(latest_response.params).get('audioanswers', [])
        ]

    def fetchqualityreports(self, projectid):
        projectobj = Project.objects.get(id=projectid)
        checkpoints = self._project_checkpoints(projectid)
        qualityparams = SurveyResponse.objects.filter(
            project=projectobj,
            verification_status__name='Verified',
        ).select_related('user__user').iterator()

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
        cp_remarks = ['%s_remarks' % (i) for i in checkpoints]
        qckeys = [
            'uid',
            'surveyor',
            'auditor',
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
        checkpoints = self._project_checkpoints(projectid)
        qualityparams = SurveyResponse.objects.filter(
            project=projectobj,
            verification_status__name='Verified',
        ).iterator()

        qualitydict = {}

        surveyor_dict = {}

        for param in qualityparams:
            remarksdict = json.loads(param.remarks)

            if remarksdict['surveyor'] in surveyor_dict.keys():
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
                for key in checkpoints:
                    surveyor_dict[remarksdict['surveyor']][str(key)] = 0

                surveyor_dict[remarksdict['surveyor']]['interviewduration'] = 0
                surveyor_dict[remarksdict['surveyor']]['geocodes'] = 0
                surveyor_dict[remarksdict['surveyor']]['movement'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalverified'] = 0
                surveyor_dict[remarksdict['surveyor']]['totalformsfilled'] = 0

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

        totalcountobj = SurveyResponse.objects.filter(project=projectobj).iterator()

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
        checkpoints = self._project_checkpoints(projectid)

        if 'days' in request.GET.keys():
            qcparams = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status__name='Verified'
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
                                verification_status__name='Verified'
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
                                verification_status__name='Verified'
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