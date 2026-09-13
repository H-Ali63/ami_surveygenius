# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from mainapp.tasks import *
from mainapp.models import *
from random import randint
from difflib import SequenceMatcher
from datetime import datetime, date, timedelta
from math import sin, cos, sqrt, atan2, radians
import json
import MySQLdb
import csv
import ast

class QualityAuditView(TemplateView):
    def get(self, request):
        try:
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'qualityaudit.html',
                'maindata': [],
                'count':  ""
            }
        except Exception as e:
            data = {
                'first_name': "-",
                'last_name': "-",
                'userrole': "-",
                'department': "-",
                'htmlfilename': 'qualityaudit.html',
                'maindata': []
            }

        data['count'] = None                    #count variable for cris

        data['maindata'] = None
        data['totalcount'] = None

        print("get",request.GET)

        if 'page' in request.GET.keys() and int(request.GET['page']) >= 0:
            x = int(request.GET['page']) * 100

            data['page'] = int(request.GET['page'])
            data['previous'] = int(request.GET['page']) - 1
            data['next'] = int(request.GET['page']) + 1
        else:
            x = 0
            data['page'] = 0
            data['next'] = 1
            data['previous'] = 0


        data['allfilters'] = {}

        data['allfilters']['projects'] = Project.objects.all()

        fieldresearchers = []
        # surveyors = []
        verifiedby = []

        AllSurveyResponses = SurveyResponse.objects.all().order_by('-pk')[:10000]           ## Here we get recently submitted 10000 surveyresponses

        print("allsurveyresponses",AllSurveyResponses)

        for resp in AllSurveyResponses:
            print('resp',resp)

            print("json",json.loads(resp.params).keys())                                ## Here we get params from that responses

            if 'tldetails' in json.loads(resp.params).keys():
                fieldresearchers.append(json.loads(resp.params)['tldetails'])
                fieldresearchers = list(set(fieldresearchers))                          ## Here we get list of FR from that responses

                print("fieldreserchers",fieldresearchers)

            # if resp.surveyor:
            #     surveyors.append(resp.surveyor)
            #     surveyors = list(set(surveyors))

            if resp.user:
                verifiedby.append(resp.user)
                verifiedby = list(set(verifiedby))                                     ## Here we get varified QA from that responses

        data['allfilters']['fieldresearchers'] = fieldresearchers
        # data['allfilters']['surveyors'] = surveyors
        data['allfilters']['verifiedby'] = verifiedby

        ##print("get1",request.GET)

        try:
            ## if project is selected

            if request.GET['Project'] != "":
                RespFilter = SurveyResponse.objects.filter(project__pk=request.GET['Project']) 
                ##print("respfilter",RespFilter)
            
            ## if FR is selected

            if request.GET['FieldResearcher'] != "":
                if request.GET['Project'] != "":                    ## if FR and project is selected
                    RespFilter = RespFilter.filter(params__contains=request.GET['FieldResearcher'])
                else:                                                  ## if only FR selected
                    RespFilter = SurveyResponse.objects.filter(params__contains=request.GET['FieldResearcher'])
            
            ## if surveyor is selected

            if request.GET['Surveyor'] != "":
                if request.GET['Project'] != "" or request.GET['FieldResearcher'] != "":        ## if surveyor and FR or project is selected
                    RespFilter = RespFilter.filter(surveyor__employee_id=request.GET['Surveyor'])
                    ##print("respfilter2",RespFilter)

                else:
                    RespFilter = SurveyResponse.objects.filter(surveyor__employee_id=request.GET['Surveyor'])       ## if only surveyor selected

            if request.GET['VerifiedBy'] != "":
                if request.GET['Project'] != "" or request.GET['FieldResearcher'] != "" or request.GET['Surveyor'] != "":       ## if verifiedby and FR or project or surveyor is selected
                    RespFilter = RespFilter.filter(user__pk=request.GET['VerifiedBy'])
                else:
                    RespFilter = SurveyResponse.objects.filter(user__pk=request.GET['VerifiedBy'])                      ## if only surveyor selected

            if 'verifiedflag' in request.GET.keys() and request.GET['verifiedflag'] == 'on':
                if request.GET['Project'] != "" or request.GET['FieldResearcher'] != "" or request.GET['Surveyor'] != "" or request.GET['VerifiedBy'] != "":      ## if verificationflag is on and verifiedby or FR or project or surveyor is selected
                    RespFilter = RespFilter.filter(verification_status__name='Verified')
                else:
                    RespFilter = SurveyResponse.objects.filter(verification_status__name='Verified')                    ## if only verificationflag selected


            try:
                if request.GET['fromdate'] != "" and request.GET['todate'] != "":       ## if fromdate and todate selected
                    RespFilter = RespFilter.filter(verification_date__gte=request.GET['fromdate'], verification_date__lte='%s 23:59:59' % (request.GET['todate'])).order_by('-pk')
                elif request.GET['fromdate'] != "":                             ## if fromdate selected
                    RespFilter = RespFilter.filter(verification_date__gte=request.GET['fromdate']).order_by('-pk')
                elif request.GET['todate'] != "":                               ## if todate selected
                    RespFilter = RespFilter.filter(verification_date__lte='%s 23:59:59' % (request.GET['todate'])).order_by('-pk')
            except Exception as e:
                pass

            if request.GET['uid'] != "":                                ### if uid is entered
                RespFilter = SurveyResponse.objects.filter(uid=request.GET['uid'])

            data['maindata'] = []

            db_config = json.dumps(settings.CELERY_DATABASE_CONFIG);

            # making db_config
            db_config_host = str(json.loads(db_config)['host']);
            db_config_pass = str(json.loads(db_config)['pass']);
            db_config_user = str(json.loads(db_config)['user']);
            db_config_port = str(json.loads(db_config)['port']);
            db_config_database = str(json.loads(db_config)['database']);

            #print("RespFilter",RespFilter)

            for resp in RespFilter[x:x+100]:

                #print('resp',str(resp.project)[0:4])

                #print('uid',resp.uid)

                #print('user',resp.user)

                if SuperCheckerResponse.objects.filter(surveyresponse__uid=int(resp.uid)).count() > 0:
                    spd_flag = 1
                else:
                    spd_flag = 0
                    

                #print(request.GET["Project"]) 
                
                    ##cris project code ##
                try:

                    if str(resp.project)[0:4] == "1200":

                        try:
                            db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
                        
                        except Exception as e:
                            pass

                        cursor = db.cursor()

                        cp_sql = """SELECT IMG_URL FROM SAVE_SURVEY WHERE id1='%s' AND (IMG_URL <> 'None')""" % (resp.uid)
                        # cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (cpid)

                        cursor.execute(cp_sql)

                        cp_data = cursor.fetchall()
                        #print(cp_data)

                        ##print("cp",str(cp_data[0][0]))

                        ##print(type(str(cp_data[0][0])))

                        IMG_URL = "None"
                        VIDEO_URL = "None"

                        Image_video = str(cp_data[0][0])

                        #print("slice",Image_video[-3:])

                        if Image_video[-3:] == "mp4":
                            VIDEO_URL = Image_video.replace("8888","8297")
                            #print("video",VIDEO_URL)
                        else:
                            IMG_URL = Image_video.replace("8888","8297")
                            #print("image",IMG_URL)
                            
                        data['maindata'].append({
                            'uid': resp.uid,
                            'user': resp.user,
                            'project': resp.project,
                            'verification_status': resp.verification_status,
                            'verification_date': resp.verification_date,
                            'otp_verified': resp.otp_verified,
                            'surveyor': resp.surveyor,
                            'superchecking_done': spd_flag,
                            'params': json.loads(resp.params.replace('103.226.1.242:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251')),
                            #'params': json.loads(resp.params.replace('103.226.1.242:8888', db_config_host).replace('103.218.101.38:8888',db_config_host)),
                            'remarks': json.loads(resp.remarks),
                            'img_url':IMG_URL,
                            'video_url':VIDEO_URL
                        }) 

                        data["count"] = 1 


                    ####cris project code ####

                    else: 

                        data['maindata'].append({
                            'uid': resp.uid,
                            'user': resp.user,
                            'project': resp.project,
                            'verification_status': resp.verification_status,
                            'verification_date': resp.verification_date,
                            'otp_verified': resp.otp_verified,
                            'surveyor': resp.surveyor,
                            'superchecking_done': spd_flag,
                            'params': json.loads(resp.params.replace('103.226.1.242:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251')),
                            #'params': json.loads(resp.params.replace('103.226.1.242:8888', db_config_host).replace('103.218.101.38:8888',db_config_host)),
                            'remarks': json.loads(resp.remarks)

                        })

                except Exception as e:
                    pass

            data['totalcount'] = '%s to %s out of %s' % \
                                (x+1,x+100,\
                                RespFilter.count())
                                # SurveyResponse.objects.filter(project=Project.objects.filter(pk=request.GET['firstlevel'])).count())

            getkeys = []
            for key in request.GET.keys():
                getkeys.append('%s=%s' % (key, request.GET[key]))
            
            print(getkeys)

            data['getdata'] = '&'.join(getkeys)

        except Exception as e:
            print(e)
        

        #print(data["maindata"])
        ##print(data["maindata"].video_url)
        return render(request, 'index.html', data)

    def post(self, request):
        try:
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'qualityaudit.html',
                'maindata': []
            }
        except Exception as e:
            data = {
                'first_name': "-",
                'last_name': "-",
                'userrole': "-",
                'department': "-",
                'htmlfilename': 'qualityaudit.html',
                'maindata': [],
                'count' : ""
            }


        data['count'] = None   #count variable for cris

        data['maindata'] = None
        data['totalcount'] = None

        if 'page' in request.GET.keys() and int(request.GET['page']) >= 0:
            x = int(request.GET['page']) * 100

            data['page'] = int(request.GET['page'])
            data['previous'] = int(request.GET['page']) - 1
            data['next'] = int(request.GET['page']) + 1
        else:
            x = 0
            data['page'] = 0
            data['next'] = 1
            data['previous'] = 0


        data['allfilters'] = {}

        data['allfilters']['projects'] = Project.objects.all()

        fieldresearchers = []
        # surveyors = []
        verifiedby = []

        AllSurveyResponses = SurveyResponse.objects.all().order_by('-pk')[:10000]

        #print("allsurveyresponse",AllSurveyResponses)

        for resp in AllSurveyResponses:
            if 'tldetails' in json.loads(resp.params).keys():
                fieldresearchers.append(json.loads(resp.params)['tldetails'])
                fieldresearchers = list(set(fieldresearchers))

            # if resp.surveyor:
            #     surveyors.append(resp.surveyor)
            #     surveyors = list(set(surveyors))

            if resp.user:
                verifiedby.append(resp.user)
                verifiedby = list(set(verifiedby))

        data['allfilters']['fieldresearchers'] = fieldresearchers
        # data['allfilters']['surveyors'] = surveyors
        data['allfilters']['verifiedby'] = verifiedby

        try:
            if request.GET['Project'] != "":
                RespFilter = SurveyResponse.objects.filter(project__pk=request.GET['Project'])

            if request.GET['FieldResearcher'] != "":
                if request.GET['Project'] != "":
                    RespFilter = RespFilter.filter(params__contains=request.GET['FieldResearcher'])
                else:
                    RespFilter = SurveyResponse.objects.filter(params__contains=request.GET['FieldResearcher'])

            if request.GET['Surveyor'] != "":
                if request.GET['Project'] != "" or request.GET['FieldResearcher'] != "":
                    RespFilter = RespFilter.filter(surveyor__employee_id=request.GET['Surveyor'])
                else:
                    RespFilter = SurveyResponse.objects.filter(surveyor__employee_id=request.GET['Surveyor'])

            if request.GET['VerifiedBy'] != "":
                if request.GET['Project'] != "" or request.GET['FieldResearcher'] != "" or request.GET['Surveyor'] != "":
                    RespFilter = RespFilter.filter(user__pk=request.GET['VerifiedBy'])
                else:
                    RespFilter = SurveyResponse.objects.filter(user__pk=request.GET['VerifiedBy'])

            if 'verifiedflag' in request.GET.keys() and request.GET['verifiedflag'] == 'on':
                if request.GET['Project'] != "" or request.GET['FieldResearcher'] != "" or request.GET['Surveyor'] != "" or request.GET['VerifiedBy'] != "":
                    RespFilter = RespFilter.filter(verification_status__name='Verified')
                else:
                    RespFilter = SurveyResponse.objects.filter(verification_status__name='Verified')

            try:
                if request.GET['fromdate'] != "" and request.GET['todate'] != "":
                    RespFilter = RespFilter.filter(verification_date__gte=request.GET['fromdate'], verification_date__lte='%s 23:59:59' % (request.GET['todate'])).order_by('-pk')
                elif request.GET['fromdate'] != "":
                    RespFilter = RespFilter.filter(verification_date__gte=request.GET['fromdate']).order_by('-pk')
                elif request.GET['todate'] != "":
                    RespFilter = RespFilter.filter(verification_date__lte='%s 23:59:59' % (request.GET['todate'])).order_by('-pk')
            except Exception as e:
                pass

            if request.GET['uid'] != "":
                
                RespFilter = SurveyResponse.objects.filter(uid=request.GET['uid'])

            data['maindata'] = []

            db_config = json.dumps(settings.CELERY_DATABASE_CONFIG);

            # making db_config
            db_config_host = str(json.loads(db_config)['host']);
            db_config_pass = str(json.loads(db_config)['pass']);
            db_config_user = str(json.loads(db_config)['user']);
            db_config_port = str(json.loads(db_config)['port']);
            db_config_database = str(json.loads(db_config)['database']);

            #print("RespFilter",RespFilter)

            for resp in RespFilter[x:x+100]:

                #print('uid',resp.uid)

                if SuperCheckerResponse.objects.filter(surveyresponse__uid=int(resp.uid)).count() > 0:
                    spd_flag = 1
                else:
                    spd_flag = 0

                
                    ##cris project code ##

                try:

                    if str(resp.project)[0:4] == "1200":

                        try:
                            db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
                        
                        except Exception as e:
                            pass

                        cursor = db.cursor()

                        cp_sql = """SELECT IMG_URL FROM SAVE_SURVEY WHERE id1='%s' AND (IMG_URL <> 'None')""" % (resp.uid)
                        # cp_sql = """SELECT TYPE_ID, VALUE FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE '%s'""" % (cpid)

                        cursor.execute(cp_sql)

                        cp_data = cursor.fetchall()
                        #print(cp_data)

                        ##print("cp",str(cp_data[0][0]))

                        ##print(type(str(cp_data[0][0])))

                        IMG_URL = "None"
                        VIDEO_URL = "None"

                        Image_video = str(cp_data[0][0])

                        #print("slice",Image_video[-3:])

                        if Image_video[-3:] == "mp4":
                            VIDEO_URL = Image_video.replace("8888","8297")
                            #print("video",VIDEO_URL)
                        else:
                            IMG_URL = Image_video.replace("8888","8297")
                            #print("image",IMG_URL)
                            
                        data['maindata'].append({
                            'uid': resp.uid,
                            'user': resp.user,
                            'project': resp.project,
                            'verification_status': resp.verification_status,
                            'verification_date': resp.verification_date,
                            'otp_verified': resp.otp_verified,
                            'surveyor': resp.surveyor,
                            'superchecking_done': spd_flag,
                            'params': json.loads(resp.params.replace('103.226.1.242:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251')),
                            #'params': json.loads(resp.params.replace('103.226.1.242:8888', db_config_host).replace('103.218.101.38:8888',db_config_host)),
                            'remarks': json.loads(resp.remarks),
                            'img_url':IMG_URL,
                            'video_url':VIDEO_URL
                        }) 

                        data["count"] = 1 


                    ####cris project code ####

                    else: 

                        data['maindata'].append({
                            'uid': resp.uid,
                            'user': resp.user,
                            'project': resp.project,
                            'verification_status': resp.verification_status,
                            'verification_date': resp.verification_date,
                            'otp_verified': resp.otp_verified,
                            'surveyor': resp.surveyor,
                            'superchecking_done': spd_flag,
                            'params': json.loads(resp.params.replace('103.226.1.242:8888','192.168.1.251').replace('103.218.101.38:8888','192.168.1.251')),
                            #'params': json.loads(resp.params.replace('103.226.1.242:8888', db_config_host).replace('103.218.101.38:8888',db_config_host)),
                            'remarks': json.loads(resp.remarks)

                        })

                except Exception as e:
                    pass

            data['totalcount'] = '%s to %s out of %s' % \
                                (x+1,x+100,\
                                RespFilter.count())
                                # SurveyResponse.objects.filter(project=Project.objects.filter(pk=request.GET['firstlevel'])).count())

            getkeys = []
            for key in request.GET.keys():
                getkeys.append('%s=%s' % (key, request.GET[key]))

            data['getdata'] = '&'.join(getkeys)
            print(getkeys,"getkeys")

            superchecker_obj, created = SuperCheckerResponse.objects.get_or_create(
                surveyresponse=SurveyResponse.objects.get(uid=int(request.POST['surveyresponse_uid']))
            )

            superchecker_remarks = {}

            print(request.post)

            for key, value in request.POST.items():
                if key in ["uid", "surveyresponse_uid", "csrfmiddlewaretoken", "submit"]:
                    continue

                superchecker_remarks[key] = value

            superchecker_obj.superchecker_user = request.user.user_employee
            superchecker_obj.remarks = json.dumps(superchecker_remarks)
            superchecker_obj.save()

        except Exception as e:
            print(e)

        return render(request, 'index.html', data)
