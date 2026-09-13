# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings

# from mainapp.tasks import *
from search.models import *    #changes
from random import randint
from difflib import SequenceMatcher
from datetime import datetime, date
from math import sin, cos, sqrt, atan2, radians
import json
import MySQLdb
import csv
import ast
# from celery.task.control import inspect
from dateparser import parse


class GeoMismatchView(TemplateView):
    def __init__(self):
        # Open database connection
        # db_config = json.dumps(settings.CELERY_DATABASE_CONFIG);

        # # making db_config
        # self.db_config_host = str(json.loads(db_config)['host']);
        # self.db_config_user = str(json.loads(db_config)['user']);
        # self.db_config_port = str(json.loads(db_config)['port']);
        # self.db_config_pass = str(json.loads(db_config)['pass']);
        # self.db_config_database = str(json.loads(db_config)['database']);

        # # commented becoz of configuring
        # # self.db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
        # self.db = MySQLdb.connect(self.db_config_host, self.db_config_user, self.db_config_pass, self.db_config_database, charset='utf8', use_unicode=True)
        # self.cursor = self.db.cursor()

        timeslots = ['6:30 am to 10:00 am', '10:00:01 am to 1:00 pm', '1:00:01 pm to 4:00 pm', '4:00:01 pm to 8:00 pm']
        self.map_timebuckets(timeslots)

    def map_timebuckets(self, timeslots):
        self.timeslots = []

        for slot in timeslots:
            split_slot = slot.split('to')

            self.timeslots.append([parse(split_slot[0]), parse(split_slot[1])])

    def get(self, request):
        try:
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'a_app_templates/a_app_geomismatch.html',
                'maindata': []
            }
        except Exception as e:
            data = {
                'first_name': "-",
                'last_name': "-",
                'userrole': "-",
                'department': "-",
                'htmlfilename': 'a_app_templates/a_app_geomismatch.html',
                'maindata': []
            }

        projectid = request.GET['project']
        print(projectid)
        data['projectid'] = projectid
        print(projectid,">>>>")

        if Project.objects.filter(pk=projectid).count() == 0:
            data['error'] = True
            return render(request, 'a_app_templates/a_app_geomismatch.html', data)
        else:
            # Check if project is nccs project
            data['error'] = False

        capi_checklist_id = Project.objects.filter(pk=projectid)[0].capi_checklist_id

        if request.user.is_active:
            self.fetchdata(request, data, capi_checklist_id)

        # from quality.settings import application_version
        # i = inspect()


        # for proj in Project.objects.filter(pk=529).order_by(('-pk')):
        #     operationsdashcron(proj.capi_checklist_id)

#         if len(i.active()[i.active().keys()[0]]) <= 1:
#             for proj in Project.objects.filter(pull_data=True, frpmdashboard_flag=True).order_by(('-pk')):
#                 operationsdashcron.delay(proj.capi_checklist_id)

#             for proj in Project.objects.filter(pull_data=True).order_by(('-pk')):
#                 fetchdatacron.delay(proj.capi_checklist_id)
#                 exportdatacron.delay(proj.capi_checklist_id)

#             if datetime.now().hour > 19 or datetime.now().hour < 6:
#                 for proj in Project.objects.filter(pull_data=True, is_gas_activity=False).order_by(('-pk')):
#                     fetchbackcheckdatacron.delay(proj.pk)

        if not request.user.is_active:
            return HttpResponseRedirect('/login')

        data['fordate'] = request.GET['fordate']

        # self.db.close()

        return render(request, 'index.html', data)


    ####### showing report data #########

    def fetchdata(self, request, data, capi_checklist_id):
        self.maxaudios = 0
        print(request.GET['fordate'])

        requested_time = '"date": "%s"' % (datetime.strptime(request.GET['fordate'], '%Y-%m-%d').strftime('%d-%b-%Y'))

        # requested_time = request.GET['fordate']
        print(requested_time)
        projectobj = Project.objects.get(id=data['projectid'])
        if 'surveyor_req' in request.GET.keys() and str(request.GET['surveyor_req']) != "000000":
            data['surveyor_req'] = request.GET['surveyor_req']
            surveyors = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params__icontains=requested_time,
                            surveyor__employee_id=request.GET['surveyor_req']
                        ).values('surveyor').distinct()
        else:
            data['surveyor_req'] = ""

            if SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='Verifying'),
                            user = Employee.objects.get(user=request.user),
                            params__icontains=requested_time,
                        ).count() > 0:
                surveyresponse = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='Verifying'),
                                user = Employee.objects.get(user=request.user),
                                params__icontains=requested_time,
                            )[0]

                responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

                data['maindata'].append(responseparams)

                return data

            surveyors = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params__icontains=requested_time,
                            # otp_verified=True
                        ).values('surveyor').distinct()

        percent_verified_surveyor = 100
        final_surveyor = None
        tempsurveyor = None
        print(surveyors)

        for surveyor in surveyors:
            if surveyor['surveyor'] == None:
                continue

            try:
                verifiedcount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    verification_status=VerificationStatus.objects.get(name='Verified'),
                                    surveyor=Employee.objects.get(pk=surveyor['surveyor']),
                                    params__icontains=requested_time,
                                    # otp_verified=True
                                ).count()

                totalcount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    params__icontains=requested_time,
                                    surveyor=Employee.objects.get(pk=surveyor['surveyor']),
                                    # otp_verified=True
                                ).count()

                print(totalcount,"totttttt")
                if totalcount == 0:
                    continue

                # The surveyor with lowest verification percentage will get the highest priority
                if verifiedcount/totalcount * 100 < percent_verified_surveyor:
                    percent_verified_surveyor = verifiedcount/totalcount * 100

                    tempsurveyor = surveyor['surveyor']

                    # final_surveyor = surveyor['surveyor']
                    # Set upper limit of 23%
                    if data['surveyor_req'] != "":
                        final_surveyor = surveyor['surveyor']
                    elif percent_verified_surveyor <= int(projectobj.verification_percent):
                        final_surveyor = surveyor['surveyor']
            except Exception as e:
                pass

        # Remove capping
        # if final_surveyor == None:
        #     final_surveyor = tempsurveyor

        # filter(params__icontains='"datetime": 1') in querycount and surveyresponse
        print(final_surveyor)
        # Select form to be loaded
        # print(Employee.objects.get(pk=final_surveyor),"emp")s

        #### changes need to  be done
        try:
            querycount = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                                params__icontains=requested_time,
                                surveyor=Employee.objects.get(pk=final_surveyor)
                                # otp_verified=True
                            ).count()
        except ValueError as e:
                # Handle the error
                print(e)
                querycount = 0
        #### changes need to  be done

        print(querycount)

        individual_slots_unverified = [0 for _ in range(len(self.timeslots))]
        individual_sids_unverified = [[] for _ in range(len(self.timeslots))]
        individual_slots_verified = [0 for _ in range(len(self.timeslots))]
        individual_sids_verified = [[] for _ in range(len(self.timeslots))]

        if querycount > 0 and final_surveyor != None:
            filtered_surveyresponses_unverified = SurveyResponse.objects.filter(
                                project=projectobj,
                                surveyor=Employee.objects.get(pk=final_surveyor),
                                verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                                params__icontains=requested_time,
                                # otp_verified=True
                            ).order_by('-pk',)

            filtered_surveyresponses_verified = SurveyResponse.objects.filter(
                                project=projectobj,
                                surveyor=Employee.objects.get(pk=final_surveyor),
                                verification_status=VerificationStatus.objects.get(name='Verified'),
                                params__icontains=requested_time,
                                # otp_verified=True
                            )

            # Enter form into a timeslot
            for resp in filtered_surveyresponses_unverified:
                params = json.loads(resp.params)
                # if params['audiourls'] == []:
                #     continue

                for index, value in enumerate(self.timeslots):
                    if parse(params['time']) > value[0] and parse(params['time']) < value[1]:
                        individual_slots_unverified[index] += 1
                        individual_sids_unverified[index].append(resp)

            for resp in filtered_surveyresponses_verified:
                params = json.loads(resp.params)
                if params['audiourls'] == []:
                    continue

                for index, value in enumerate(self.timeslots):
                    if parse(params['time']) > value[0] and parse(params['time']) < value[1]:
                        individual_slots_verified[index] += 1
                        individual_sids_verified[index].append(resp)

            if individual_slots_unverified == []:
                SurveyResponse.objects.filter(
                                project=projectobj,
                                surveyor=Employee.objects.get(pk=final_surveyor),
                                verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                                params__icontains=requested_time,
                                # otp_verified=True
                            ).delete()

            # Calculate verification percentage in timeslots
            resp_percentage = 1
            resp_index = 0
            for index, value in enumerate(self.timeslots):
                if (individual_slots_unverified[index]+individual_slots_verified[index]) == 0:
                    continue

                if individual_slots_verified[index]/(individual_slots_unverified[index]+individual_slots_verified[index]) < resp_percentage:
                    resp_percentage = individual_slots_verified[index]/(individual_slots_unverified[index]+individual_slots_verified[index])
                    resp_index = index

            try:
                surveyresponse = individual_sids_unverified[resp_index][0]
            except Exception as e:
                return data

            # SurveyResponse.objects.filter(user__pk=final_surveyor, verification_status__name="Verifying").update(verification_status=VerificationStatus.objects.get(name='To Be Verified'))
            surveyresponse.user = Employee.objects.get(user=request.user)
            surveyresponse.verification_status = VerificationStatus.objects.get(name='Verifying')
            surveyresponse.save()

            responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

            # responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

            data['maindata'].append(responseparams)

        return data

    def postdata(self, request, data, capi_checklist_id):
        remarksdict = {}
        uid = request.POST['uid']
        projectobj = Project.objects.get(pk=request.GET['project'])

        remarksdict['uid'] = uid
        remarksdict['surveyor'] = request.POST['surveyor']
        data['surveyor_req'] = request.POST['surveyor_req']
        requested_time = '"date": "%s"' % (datetime.strptime(request.GET['fordate'], '%Y-%m-%d').strftime('%d-%b-%Y'))

        # requested_time = request.GET['fordate']

        try:
            remarksdict['geocodes'] = request.POST['geocodes']
        except Exception as e:
            remarksdict['geocodes'] = 'NA'

        remarksdict['comments'] = request.POST['comments']
        try:
            if request.POST['send_to_surveyor'] == 'Yes':
                remarksdict['send_to_surveyor'] = True
            else:
                remarksdict['send_to_surveyor'] = False
        except Exception as e:
            remarksdict['send_to_surveyor'] = False

        # cps = AudioCheckpoints.objects.get(project=projectobj) #### need to be done changes
        # checkpoints = json.loads(cps.cplist).keys()     #### need to be done changes

        # If technical issue, do not mark as verified
        technical_issue = False


        ### need to be done changes

        # for key in checkpoints:
        #     try:
        #         remarksdict[str(key)] = request.POST[str(key)]

        #         remarksdict['%s' % (str(key))] = request.POST['%s' % (str(key))]

        #         if str(request.POST['%s' % (str(key))]) == "Technical_issues":
        #             technical_issue = True
        #     except Exception as e:
        #         pass

        remarksdict['interviewduration'] = request.POST['interviewduration']
        remarksdict['movement'] = request.POST['movement']

        surveyresponse = SurveyResponse.objects.get(uid=uid)
        surveyresponse.remarks = json.dumps(remarksdict)
        surveyresponse.send_to_surveyor = remarksdict['send_to_surveyor']
        surveyresponse.verification_date = datetime.now()

        # if technical_issue == True:
        #     surveyresponse.verification_status = VerificationStatus.objects.get(name='Technical Issue')
        # else:
        #     surveyresponse.verification_status = VerificationStatus.objects.get(name='Verified')

        surveyresponse.verification_status = VerificationStatus.objects.get(name='Verified')

        surveyresponse.user = Employee.objects.get(user=request.user)
        surveyresponse.save()

        self.maxaudios = 0

        if data['surveyor_req'] != "":
            surveyors = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params__icontains=requested_time,
                            surveyor__employee_id=data['surveyor_req']
                        ).values('surveyor').distinct()
        else:
            if SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='Verifying'),
                            user = Employee.objects.get(user=request.user),
                            params__icontains=requested_time,
                        ).count() > 0:
                surveyresponse = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='Verifying'),
                                user = Employee.objects.get(user=request.user),
                                params__icontains=requested_time,
                            )[0]

                responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

                # responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

                data['maindata'].append(responseparams)

                return data

            surveyors = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params__icontains=requested_time,
                            # otp_verified=True
                        ).values('surveyor').distinct()

        percent_verified_surveyor = 100
        final_surveyor = None
        tempsurveyor = None

        for surveyor in surveyors:
            if surveyor['surveyor'] == None:
                continue

            try:
                verifiedcount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    verification_status=VerificationStatus.objects.get(name='Verified'),
                                    surveyor=Employee.objects.get(pk=surveyor['surveyor']),
                                    params__icontains=requested_time,
                                    # otp_verified=True
                                ).count()

                totalcount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    surveyor=Employee.objects.get(pk=surveyor['surveyor']),
                                    params__icontains=requested_time,
                                    # otp_verified=True
                                ).count()

                print(totalcount,"total")
                if totalcount == 0:
                    continue

                # The surveyor with lowest verification percentage will get the highest priority
                if verifiedcount/totalcount * 100 < percent_verified_surveyor:
                    percent_verified_surveyor = verifiedcount/totalcount * 100

                    tempsurveyor = surveyor['surveyor']

                    # final_surveyor = surveyor['surveyor']

                    # Set upper limit of 23%
                    if data['surveyor_req'] != "":
                        final_surveyor = surveyor['surveyor']
                    elif percent_verified_surveyor <= int(projectobj.verification_percent):
                        final_surveyor = surveyor['surveyor']
            except Exception as e:
                pass

        # Remove capping
        # if final_surveyor == None:
        #     final_surveyor = tempsurveyor

        # Select form to be loaded
        querycount = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            surveyor=Employee.objects.get(pk=final_surveyor),
                            params__icontains=requested_time,
                            # otp_verified=True
                        ).count()

        individual_slots_unverified = [0 for _ in range(len(self.timeslots))]
        individual_sids_unverified = [[] for _ in range(len(self.timeslots))]
        individual_slots_verified = [0 for _ in range(len(self.timeslots))]
        individual_sids_verified = [[] for _ in range(len(self.timeslots))]

        if querycount > 0 and final_surveyor != None:
            filtered_surveyresponses_unverified = SurveyResponse.objects.filter(
                                project=projectobj,
                                surveyor=Employee.objects.get(pk=final_surveyor),
                                verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                                params__icontains=requested_time,
                                # otp_verified=True
                            ).order_by('-pk',)

            filtered_surveyresponses_verified = SurveyResponse.objects.filter(
                                project=projectobj,
                                surveyor=Employee.objects.get(pk=final_surveyor),
                                verification_status=VerificationStatus.objects.get(name='Verified'),
                                params__icontains=requested_time,
                                # otp_verified=True
                            )

            # Enter form into a timeslot
            for resp in filtered_surveyresponses_unverified:
                params = json.loads(resp.params)
                if params['audiourls'] == []:
                    continue

                for index, value in enumerate(self.timeslots):
                    if parse(params['time']) > value[0] and parse(params['time']) < value[1]:
                        individual_slots_unverified[index] += 1
                        individual_sids_unverified[index].append(resp)

            for resp in filtered_surveyresponses_verified:
                params = json.loads(resp.params)
                if params['audiourls'] == []:
                    continue

                for index, value in enumerate(self.timeslots):
                    if parse(params['time']) > value[0] and parse(params['time']) < value[1]:
                        individual_slots_verified[index] += 1
                        individual_sids_verified[index].append(resp)

            # Calculate verification percentage in timeslots
            resp_percentage = 1
            resp_index = 0
            for index, value in enumerate(self.timeslots):
                if (individual_slots_unverified[index]+individual_slots_verified[index]) == 0:
                    continue

                if individual_slots_verified[index]/(individual_slots_unverified[index]+individual_slots_verified[index]) < resp_percentage:
                    resp_percentage = individual_slots_verified[index]/(individual_slots_unverified[index]+individual_slots_verified[index])
                    resp_index = index

            try:
                surveyresponse = individual_sids_unverified[resp_index][0]
            except Exception as e:
                return data

            # SurveyResponse.objects.filter(user=surveyresponse.user, verification_status__name="Verifying").update(verification_status=VerificationStatus.objects.get(name='To Be Verified'))
            surveyresponse.user = Employee.objects.get(user=request.user)
            surveyresponse.verification_status = VerificationStatus.objects.get(name='Verifying')
            surveyresponse.save()

            responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

            # responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.0.212'))

            data['maindata'].append(responseparams)

        return data

    def post(self, request):
        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            'htmlfilename': 'a_app_templates/a_app_search_quality.html',
            'maindata': []
        }

        projectid = request.GET['project']
        data['fordate'] = request.POST['fordate']

        data['projectid'] = projectid

        if Project.objects.filter(pk=projectid).count() == 0:
            data['error'] = True
            return render(request, 'a_app_templates/a_app_search_quality.html', data)
        else:
            # Check if project is nccs project
            data['error'] = False

        capi_checklist_id = Project.objects.filter(pk=projectid)[0].capi_checklist_id

        data = self.postdata(request, data, capi_checklist_id)
        data['maindata'].reverse()
        maxa = []

        return render(request, 'index.html', data)
