# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect  # type:ignore
from django.utils.decorators import method_decorator  # type:ignore
from django.views.generic import TemplateView  # type:ignore
from django.shortcuts import HttpResponseRedirect  # type:ignore
from django.contrib.auth import authenticate, login, logout  # type:ignore
from django.contrib.auth.models import User  # type:ignore
from django.http import HttpResponse  # type:ignore
from django.conf import settings  # type:ignore

from search.tasks import *
from search.models import *
from random import randint
from difflib import SequenceMatcher
from datetime import datetime, date
from math import sin, cos, sqrt, atan2, radians
import json
import MySQLdb  # type:ignore
import csv
import ast
# from celery.task.control import inspect
from dateparser import parse  # type:ignore

logger = logging.getLogger(__name__)


from quality.ratelimit import rate_limit, get_client_ip  #type: ignore


@method_decorator(login_required(login_url='/login'), name='dispatch')
@method_decorator(
    rate_limit(limit=30, window_seconds=60, scope='geomismatch',
               key_func=lambda r: f"{r.user.pk if r.user.is_authenticated else get_client_ip(r)}"),
    name='dispatch',
)
class GeoMismatchView(TemplateView):
    def __init__(self):
        pass

        timeslots = ['4:00:01 am to 10:00 am', '10:00:01 am to 1:00 pm', '1:00:01 pm to 4:00 pm', '4:00:01 pm to 8:00 pm']
        self.map_timebuckets(timeslots)

    def map_timebuckets(self, timeslots):
        self.timeslots = []

        for slot in timeslots:
            split_slot = slot.split('to')
            # print(split_slot,"slotttt")

            self.timeslots.append([parse(split_slot[0]), parse(split_slot[1])])
        
        # print(self.timeslots,"timeslots")

    def get(self, request):
        try:
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                # 'employee_pic': request.user.user_employee.get_profile_pic(),
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
        # print(projectid)
        data['projectid'] = projectid

        if Project.objects.filter(pk=projectid).count() == 0:
            data['error'] = True
            data['error_message'] = "Project does not exist in CAPI."
            return render(request, 'a_app_templates/a_app_geomismatch.html', data)
        else:
            # Check if project is nccs project
            data['error'] = False

        fordate = request.GET.get('fordate', '').strip()
        surveyor_req = request.GET.get('surveyor_req', '').strip()
        data['fordate'] = fordate
        data['surveyor_req'] = surveyor_req

        if not fordate:
            data['error'] = True
            data['error_message'] = "Please select a date before submitting."
            return render(request, 'a_app_templates/a_app_geomismatch.html', data)

        try:
            datetime.strptime(fordate, '%Y-%m-%d')
        except ValueError:
            data['error'] = True
            data['error_message'] = "Please enter a valid date."
            return render(request, 'a_app_templates/a_app_geomismatch.html', data)

        capi_checklist_id = Project.objects.filter(pk=projectid)[0].capi_checklist_id

        # print(capi_checklist_id,"capi_c_id")

        if request.user.is_active:
            self.fetchdata(request, data, capi_checklist_id)



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

    def fetchdata(self, request, data, capi_checklist_id):
        self.maxaudios = 0
        # print('request.get',request.GET)

        requested_time = '"date": "%s"' % (datetime.strptime(request.GET['fordate'], '%Y-%m-%d').strftime('%d-%b-%Y'))  ## here we get requested date in 16-oct-2024 
           
        # print(requested_time,"requested time")
        projectobj = Project.objects.get(id=data['projectid'])
        # print("request.GET.keys()",request.GET.keys())
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

            # print('employee_get',Employee.objects.get(user=request.user))

            # print('coutn',SurveyResponse.objects.filter(
            #                 project=projectobj,
            #                 verification_status=VerificationStatus.objects.get(name='Verifying'),
            #                 user = Employee.objects.get(user=request.user),
            #                 params__icontains=requested_time,
            #             ).count())

            ####if count is greater than 0 then return only one surveyresponse###

            
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

                # print('surveyresponse',surveyresponse.id)

                ### get json data of that params of that surveyresponse in responseparams###

                responseparams = json.loads(surveyresponse.params.replace('103.226.1.242:8888','192.168.1.251').replace('pnndsrvctvt.com:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251'))

                # print(responseparams,"responseparams")  

                data['maindata'].append(responseparams)   ##append that responseparams in data maindata 

                # print(data,"data")

                return data

            #if we search for first time that day and count is zero

            surveyors = SurveyResponse.objects.filter(
                            project=projectobj,
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params__icontains=requested_time,
                            # otp_verified=True
                        ).values('surveyor').distinct()
            # print(surveyors,"surveyors")

        percent_verified_surveyor = 100                             ## verification percent changes after each iteration
        final_surveyor = None
        tempsurveyor = None

        # print(surveyors,"surveyors")

        for surveyor in surveyors:
            if surveyor['surveyor'] == None:
                continue

            try:

                #### verified urls count of that particular surveyor on that day###
                verifiedcount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    verification_status=VerificationStatus.objects.get(name='Verified'),
                                    surveyor=Employee.objects.get(pk=surveyor['surveyor']),
                                    params__icontains=requested_time,
                                    # otp_verified=True
                                ).count()


                # print(verifiedcount,'verified coutn')

                ### total count of that surveyor of that day 

                totalcount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    params__icontains=requested_time,
                                    surveyor=Employee.objects.get(pk=surveyor['surveyor']),
                                    # otp_verified=True
                                ).count()

                # print('totalcount',totalcount)

                # print('perce',percent_verified_surveyor)

                # print(verifiedcount/totalcount * 100 < percent_verified_surveyor,'pp')

                if totalcount == 0:
                    continue

                # The surveyor with lowest verification percentage will get the highest priority
                if verifiedcount/totalcount * 100 < percent_verified_surveyor:

                    
                    percent_verified_surveyor = verifiedcount/totalcount * 100              ## here percent verified count change

                    # print('loopperce',percent_verified_surveyor)

                    tempsurveyor = surveyor['surveyor']

                    # final_surveyor = surveyor['surveyor']
                    # Set upper limit of 23%
                    if data['surveyor_req'] != "":
                        final_surveyor = surveyor['surveyor']
                    elif percent_verified_surveyor <= int(projectobj.verification_percent):
                        final_surveyor = surveyor['surveyor']
                    # print(final_surveyor,'final')                       ### surveyor get here with lowest verification percentage
            except Exception as e:
                pass

        # Remove capping
        # if final_surveyor == None:
        #     final_surveyor = tempsurveyor

        # filter(params__icontains='"datetime": 1') in querycount and surveyresponse

        # Select form to be loaded
        try:
            querycount = SurveyResponse.objects.filter(
                                project=projectobj,
                                verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                                params__icontains=requested_time,
                                surveyor=Employee.objects.get(pk=final_surveyor),
                                # otp_verified=True
                            ).count()      
                                                                 ###count of surveys which not yet verified of that particular surveyor on that day
        except Exception as e:
            # print(e)
            querycount = 0
        # print(querycount,'querycount')

        individual_slots_unverified = [0 for _ in range(len(self.timeslots))]
        individual_sids_unverified = [[] for _ in range(len(self.timeslots))]
        individual_slots_verified = [0 for _ in range(len(self.timeslots))]
        individual_sids_verified = [[] for _ in range(len(self.timeslots))]

        # print('individual_slots_unverified',individual_slots_unverified)
        # print('individual_sids_unverified',individual_sids_unverified)

        # print('individual_slots_verified',individual_slots_verified)

        # print('individual_sids_verified',individual_sids_verified)



        ### get verified and unverified surveys of that particular surveyor of that day

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
                        individual_slots_unverified[index] += 1                                             ## per time slot count appending
                        individual_sids_unverified[index].append(resp)

            for resp in filtered_surveyresponses_verified:
                params = json.loads(resp.params)
                if params['audiourls'] == []:
                    continue

                for index, value in enumerate(self.timeslots):
                    if parse(params['time']) > value[0] and parse(params['time']) < value[1]:
                        individual_slots_verified[index] += 1
                        individual_sids_verified[index].append(resp)

            # print('individual_slots_unverified',individual_slots_unverified)
            # print('individual_sids_unverified',individual_sids_unverified)

            # print('individual_slots_verified',individual_slots_verified)

            # print('individual_sids_verified',individual_sids_verified)

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
            #     print('resp_percentage',resp_percentage)
            #     print('resp_index = index',resp_index)

            # print('individual_slots_unverified',individual_slots_unverified)
            # print('individual_sids_unverified',individual_sids_unverified)

            # print('individual_slots_verified',individual_slots_verified)

            # print('individual_sids_verified',individual_sids_verified)

            try:
                surveyresponse = individual_sids_unverified[resp_index][0]
            except Exception as e:
                return data
            # print('surveyresponse',surveyresponse)
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

        # cps = AudioCheckpoints.objects.get(project=projectobj)              ## Here we get audio questions
        # checkpoints = json.loads(cps.cplist).keys()

        # If technical issue, do not mark as verified
        technical_issue = False

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
            # print("enter in elseeeee")
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
                
                # print(surveyresponse,"surveyorresponseee")

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
            
            # print("surveyors_here",surveyors) ### from here need to be check

        percent_verified_surveyor = 100
        final_surveyor = None
        tempsurveyor = None

        if surveyors:
            for surveyor in surveyors:
                # print(surveyor,"surveyorsssssssssssssssssss")
                if surveyor['surveyor'] == None:
                    # print('checkkkkkkk')
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
                    
                    # print(verifiedcount,"verifiedcounttttt")
                    # print(totalcount,"totalcountttttttt")


                    if totalcount == 0:
                        continue

                    # The surveyor with lowest verification percentage will get the highest priority
                    if verifiedcount/totalcount * 100 < percent_verified_surveyor:
                        percent_verified_surveyor = verifiedcount/totalcount * 100

                        # print(tempsurveyor,"tempsurveyorrrrrrrrr")
                        tempsurveyor = surveyor['surveyor']
                        # print(tempsurveyor,"tempsurveyorrrrrrrrrssssss")
                        # final_surveyor = surveyor['surveyor']

                        # Set upper limit of 23%
                        if data['surveyor_req'] != "":
                            final_surveyor = surveyor['surveyor']
                        elif percent_verified_surveyor <= int(projectobj.verification_percent):
                            # print(final_surveyor,"final_surveyorsssssss")
                            final_surveyor = surveyor['surveyor']
                except Exception as e:
                    pass
        
            
        # Remove capping
        # if final_surveyor == None:
        #     final_surveyor = tempsurveyor

        # print(final_surveyor,"exitttttttttt")

        # Select form to be loaded
        if final_surveyor is not None:
            try:
                querycount = SurveyResponse.objects.filter(
                                    project=projectobj,
                                    verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                                    surveyor=Employee.objects.get(pk=final_surveyor),
                                    params__icontains=requested_time,
                                    # otp_verified=True
                                ).count()
            except Exception as e:
                print(e,"some error occured in fetching querycount")
        else:
            querycount = 0

        # print(querycount,"querycounttttttttt")

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
            'htmlfilename': 'a_app_templates/a_app_geomismatch.html',
            'maindata': []
        }

        projectid = request.GET['project']
        data['fordate'] = request.POST['fordate']

        data['projectid'] = projectid

        if Project.objects.filter(pk=projectid).count() == 0:
            data['error'] = True
            return render(request, 'a_app_templates/a_app_geomismatch.html', data)
        else:
            # Check if project is nccs project
            data['error'] = False

        capi_checklist_id = Project.objects.filter(pk=projectid)[0].capi_checklist_id

        data = self.postdata(request, data, capi_checklist_id)
        data['maindata'].reverse()
        maxa = []

        return render(request, 'index.html', data)
