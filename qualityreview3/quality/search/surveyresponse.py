# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from celery import shared_task, task

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from .models import *
from random import randint
from difflib import SequenceMatcher
from datetime import datetime, date, timedelta
from math import sin, cos, sqrt, atan2, radians
import json
import MySQLdb
import csv
import ast
import requests
from mainapp.additionalviews.exporttask import *
from mainapp.additionalviews.frpmdashboard_task import *
from mainapp.additionalviews.exporttasknormal import *
from mainapp.additionalviews.fetchbackchecktask import *
from celery.task.control import inspect

from analytics.models import OperationsDashboard

# db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
# cursor = db.cursor()
# start for priority_wise_task #


import logging
log = logging.getLogger(__name__)


# def notify_fetchdatacron(capi_checklist_id,priority_task_id):
#     try:
#         arg_name = Project.objects.get(capi_checklist_id=capi_checklist_id).name
#         log.debug('fetching started for==>%s '% (arg_name))
#         fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, '', capi_checklist_id)
#         log.debug('fetch done for==>%s ',(Project.objects.get(capi_checklist_id=capi_checklist_id).name))
#     except Exception as e:
#         #print()('before entering fetch exception::' ," for==> ", str(Project.objects.get(capi_checklist_id=capi_checklist_id).name))
#         pass

#     notify_export(capi_checklist_id,priority_task_id)

# def notify_export(capi_checklist_id,priority_task_id):
#     try:
#         log.debug('export started for==>%s ',(Project.objects.get(capi_checklist_id=capi_checklist_id).name))
#         checkpoint_ids = []
#         #print()(capi_checklist_id,"<<<<<<<<<capi_checklist_id")
#         checkpoint_ids = fetchallcheckpoints(capi_checklist_id)
#         #print()(checkpoint_ids,"<<<<<<<<<<<checkpoint_ids")
#         exportdataview(capi_checklist_id, checkpoint_ids)
#         log.debug('export done for =%s ',(Project.objects.get(capi_checklist_id=capi_checklist_id).name))
#         # PriorityTasksSchedulesID.objects.get(pk=priority_task_id).delete() #commented becoz of changes in scheduler
#         log.debug("deleted priority id::::=%s ",(str(priority_task_id)))
#         #print()("deleting from priority task")
#     except Exception as e:
#         #print()(' before entering export ', capi_checklist_id)
#         pass

# end of priority_wise_task #

# @task(name='fetchinventoryreports')
# def fetchinventoryreports():
#     db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

#     # making db_config
#     db_config_host = str(json.loads(db_config)['host'])
#     db_config_pass = str(json.loads(db_config)['pass'])
#     db_config_user = str(json.loads(db_config)['user'])
#     db_config_port = str(json.loads(db_config)['port'])
#     db_config_database = str(json.loads(db_config)['database'])

#     db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
#     #db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database,charset='utf8', use_unicode=True)
#     cursor = db.cursor()

#     sql = "SELECT EMP_ID, DEVICE_MODEL, IMEI, OS, UPDATETIME FROM DEVICES"
#     cursor.execute(sql)

#     results = cursor.fetchall()

#     for res in results:
#         sql = "SELECT Address, DEVICE_DATETIME FROM MOVEMENT WHERE EMP_ID='%s' ORDER BY DEVICE_DATETIME DESC LIMIT 1" % (res[0])
#         cursor.execute(sql)

#         movement_results = cursor.fetchall()

#         tablet, created_tab = TabInventory.objects.get_or_create(imei=res[2])

#         if len(movement_results) > 0:
#             invstatus, created_status = InventoryStatus.objects.get_or_create(asset=tablet)
#             try:
#                 invstatus.user = Employee.objects.get(employee_id=res[0])
#             except Exception as e:
#                 pass

#             sql = "SELECT COUNT(*) FROM MOVEMENT WHERE DEVICE_DATETIME > '%s' AND EMP_ID='%s'" % (res[4], res[0])
#             cursor.execute(sql)

#             cnt = int(cursor.fetchall()[0][0])/2

#             invstatus.last_login = res[4]
#             invstatus.os = res[3]
#             invstatus.model = res[1]
#             invstatus.last_form_location = movement_results[0][0]
#             invstatus.last_form_time = movement_results[0][1]
#             invstatus.forms_since_last_login = cnt
#             invstatus.save()

#     db.close()

# @task(name='operationsdashcron')
# def operationsdashcron(capi_checklist_id):
#     try:
#         #print() 'fetch ops -------- %s' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#         fetchdata_ops(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, '', capi_checklist_id)
#         #print() 'fetch ops -------- %s done' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#     except Exception as e:
#         #print() '%s %s before entering fetch %s' % (Exception, e, Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#         pass

# @task(name='fetchdatacron')
# def fetchdatacron(capi_checklist_id):
#     try:
#         #print() 'fetch -------- %s' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#         fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, '', capi_checklist_id)
#         #print() 'fetch -------- %s done' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#     except Exception as e:
#         #print() '%s %s before entering fetch %s' % (Exception, e, Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#         pass

# @task(name='fetchbackcheckdatacron')
# def fetchbackcheckdatacron(pk):
#     projectobj = Project.objects.get(pk=pk)
#     try:
#         #print() 'fetch backcheck -------- %s' % (projectobj.name)
#         fetch_backcheck_data(projectobj)
#         #print() 'fetch backcheck -------- %s done' % (projectobj.name)
#     except Exception as e:
#         #print() '%s %s before entering fetch %s' % (Exception, e, projectobj.name)
#         pass

# @task(name='exportdatacron')
# def exportdatacron(capi_checklist_id):
#     try:
#         #print() 'export -------- %s' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#         checkpoint_ids = []
#         checkpoint_ids = fetchallcheckpoints(capi_checklist_id)
#         #print() '%s (exportdata)' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#         exportdataview(capi_checklist_id, checkpoint_ids)
#         #print() '%s (exportdata done)' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#     except Exception as e:
#         #print() e, ' before entering export ', capi_checklist_id
#         pass

# @task(name='all_crons')
# def allcrons(data):
#     for proj in Project.objects.filter(active=True).order_by(('-pk')):
#         capi_checklist_id = proj.capi_checklist_id

#         from surveygenius.settings import application_version

#         if application_version == 'development':
#             try:
#                 i = inspect()
#                 if len(i.active()[i.active().keys()[0]]) <= 4:
#                     fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#             except Exception as e:
#                 fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#         else:
#             # Just one task
#             try:
#                 i = inspect()
#                 if len(i.active()[i.active().keys()[0]]) <= 4:
#                     #print() '%s (fetchdata)' % (Project.objects.get(capi_checklist_id=capi_checklist_id).name)
#                     fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#             except Exception as e:
#                 fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)

# @task(name='all_crons2')
# def allcrons2(data):
#     for proj in Project.objects.filter(active=True).order_by(('-pk')):
#         capi_checklist_id = proj.capi_checklist_id

#         from surveygenius.settings import application_version

#         if application_version == 'development':
#             try:
#                 i = inspect()
#                 if len(i.active()[i.active().keys()[0]]) <= 4:
#                     checkpoint_ids = []
#                     checkpoint_ids = fetchallcheckpoints(capi_checklist_id)
#                     exportdataview(capi_checklist_id, checkpoint_ids)
#             except Exception as e:
#                 print(e, ' before entering')

#             # fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#         else:
#             # fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#             # Just one task
#             try:
#                 i = inspect()
#                 if len(i.active()[i.active().keys()[0]]) <= 4:
#                     checkpoint_ids = []
#                     checkpoint_ids = fetchallcheckpoints(capi_checklist_id)
#                     #print() '%s (exportdata)' % (proj.name)
#                     exportdataview(capi_checklist_id, checkpoint_ids)
#             except Exception as e:
#                 #print() e, ' before entering'
#                  pass

# @task(name='normaldataexportcron')
# def normaldataexportcron(data):
#     for proj in Project.objects.filter(active=True).order_by(('-pk')):
#         capi_checklist_id = proj.capi_checklist_id

#         from surveygenius.settings import application_version

#         if application_version == 'development':
#             try:
#                 i = inspect()
#                 if len(i.active()[i.active().keys()[0]]) <= 4:
#                     checkpoint_ids = []
#                     checkpoint_ids = fetchallcheckpoints(capi_checklist_id)
#                     exportnormaldataview(capi_checklist_id, checkpoint_ids)
#             except Exception as e:
#                 #print() e
#                  pass
#             # fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#         else:
#             # fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, data, capi_checklist_id)
#             # Just one task
#             try:
#                 i = inspect()
#                 if len(i.active()[i.active().keys()[0]]) <= 4:
#                     checkpoint_ids = []
#                     checkpoint_ids = fetchallcheckpoints(capi_checklist_id)
#                     #print() '%s (exportdatanormal)' % (proj.name)
#                     exportnormaldataview(capi_checklist_id, checkpoint_ids)
#             except Exception as e:
#                 #print() e
#                  pass

def fetchallcheckpoints(capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    # execute SQL query using execute() method.
    # sql = """SELECT CHECKPOINT_ID FROM CHECKLIST_MASTER WHERE CHECKLIST_ID=%s""" % (capi_checklist_id)
    sql = """SELECT CHECKPOINT_ID FROM NCCS_NEW WHERE CHECKLIST_ID=%s""" % (capi_checklist_id)
    checkpoint_ids = []

    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()

    # Fetch checkpoint ids from checklist
    for d in data:

        for qids in d[0].replace(' ', '').split(','):
            db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

            db_config_host = str(json.loads(db_config)['host'])
            db_config_pass = str(json.loads(db_config)['pass'])
            db_config_user = str(json.loads(db_config)['user'])
            db_config_port = str(json.loads(db_config)['port'])
            db_config_database = str(json.loads(db_config)['database'])

            db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
            # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
            cursor = db.cursor()

            checkpoint_ids.append(str(qids))

            sql = """SELECT CHECKPOINT_NAME, CHECKPOINT1_ID FROM CHECKPOINT1"""
            cursor.execute(sql)
            cp1_data = cursor.fetchall()

            for cpd in cp1_data:
                if str(cpd[1].split('.')[0]) == str(qids):
                    checkpoint_ids.append(str(cpd[1]))
            db.close()

    return checkpoint_ids


@task(name='fetch_data')
def fetchdata2(project, data, capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    # sql = """DELETE FROM SAVE_SURVEY WHERE DATETIME < '%s'""" % (datetime.now()-timedelta(days=20))

    # cursor.execute(sql)
    # db.commit()


    # Fetch which checkpoints have phone number
    try:
        number_cp = fetchnumbercheckpoint(capi_checklist_id)
    except Exception as e:
        number_cp = None

    # Fetch task IDs
    tasks = fetchtasks(capi_checklist_id)
    # Fetch OTP checkpoint
    try:
        otp_cpnumber = fetchotpcpnumber(capi_checklist_id)
    except Exception as e:
        otp_cpnumber = None

    # Location checkpoint
    villages_list = fetchlocation(capi_checklist_id)

    used_ids = []
    maxaudios = 0
    responsesdict = {}
    vflag = 0

    # Fetch response data
    alreadythere=[]
    for i in SurveyResponse.objects.filter(project__capi_checklist_id=capi_checklist_id).order_by(('-pk')):
        alreadythere.append(i.uid)
    alreadythere=','.join(alreadythere)

    # sql = """SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER FROM SAVE_SURVEY WHERE TASK_ID IN (%s) \
    #         AND DATETIME > '%s' AND id1 NOT IN (%s) ORDER BY SID DESC""" % (tasks, datetime.now()-timedelta(days=2), alreadythere)

    # sql = """SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER FROM SAVE_SURVEY WHERE TASK_ID IN (%s) \
    #         AND DATETIME > '%s' AND id1 NOT IN (%s) ORDER BY SID DESC""" % (tasks, datetime.now()-timedelta(hours=2), alreadythere)

    # sql = '''SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER FROM SAVE_SURVEY WHERE TASK_ID IN (%s) AND id1 NOT IN (%s) \
    #          AND DATETIME < '%s' ORDER BY SID DESC''' % (tasks, alreadythere, datetime.now()-timedelta(hours=1))

    try:
        sql = """SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER, TASK_ID FROM SAVE_SURVEY WHERE TASK_ID IN (%s) AND id1 NOT IN (%s) \
                    AND DATETIME > '%s' AND DATETIME < '%s' ORDER BY SID DESC""" % (tasks, alreadythere, datetime.now() - timedelta(days=220), datetime.now() - timedelta(minutes='05'))

        # sql = """SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER, TASK_ID FROM SAVE_SURVEY WHERE TASK_ID IN (%s) \
        #             AND DATETIME > '%s' AND DATETIME < '%s' ORDER BY SID DESC LIMIT 300""" % (tasks, datetime.now() - timedelta(days=10), datetime.now() - timedelta(minutes=20))

        # sql = "SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER FROM SAVE_SURVEY WHERE id1 in (5815423,5815485,5815419,5815465) ORDER BY SID DESC"

        # #print()(sql, "<<<<<<<<<<,,sqlll")
        cursor.execute(sql)
        sqldata = cursor.fetchall()

        # #print()(sqldata, "<<<<sqldata2222")
    except Exception as e:
        sql = """SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER, TASK_ID FROM SAVE_SURVEY WHERE TASK_ID IN (%s) \
                    AND DATETIME > '%s' AND DATETIME < '%s' ORDER BY SID DESC""" % (tasks, datetime.now() - timedelta(days=220), datetime.now() - timedelta(minutes='05'))

        # sql = """SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER, TASK_ID FROM SAVE_SURVEY WHERE TASK_ID IN (%s) \
        #             AND DATETIME > '%s' AND DATETIME < '%s' ORDER BY SID DESC LIMIT 300""" % (tasks, datetime.now() - timedelta(days=10), datetime.now() - timedelta(minutes=01))

        # sql = "SELECT VALUE, EMP_ID, UPDATETIME, id1, CHECKPOINT_ID, OTHER FROM SAVE_SURVEY WHERE id1 in (5815423,5815485,5815419,5815465) ORDER BY SID DESC"
        # #print()(sql, "<<<<<<<<<<,,sqlll")
        cursor.execute(sql)
        sqldata = cursor.fetchall()
        # #print()(sqldata, "<<<<<<sqldata33333")

    # Set vflag if geocodes are available
    if Project.objects.get(id=project).geocodes_available:
        vflag = 1
    else:
        vflag = 0

    for d in sqldata:

        #print() '%s -> %s (fetchdata)' % (d[3], Project.objects.get(capi_checklist_id=capi_checklist_id).name)
        if datetime.now() - timedelta(minutes=10) < d[2]:
            continue
        if d[3] in responsesdict.keys():
            pass
        elif SurveyResponse.objects.filter(uid=d[3]).count() > 0:
            deleted_flag = False
            # try:
            #     if json.loads(SurveyResponse.objects.get(uid=d[3]).params)["audiourls"] == []:
            #         params = json.loads(SurveyResponse.objects.get(uid=d[3]).params)
            #         params['audiourls'], params['audioanswers'] = fetchaudiourls(request, d[3], maxaudios)
            #         resp = SurveyResponse.objects.get(uid=d[3])
            #         resp.params = params
            #         resp.verification_status = VerificationStatus.objects.get('To Be Verified')
            #         resp.save()
            # except Exception as e:
            #     SurveyResponse.objects.get(uid=d[3]).delete()
            #     deleted_flag = True
            if deleted_flag:
                responsesdict[d[3]] = {
                    'surveyor': None,
                    'date': None,
                    'time': None,
                    'id1': d[3],
                    'village': None,
                    'village_latitude': None,
                    'village_longitude': None,
                    'startlat': None,
                    'endlat': None,
                    'startlong': None,
                    'endlong': None,
                    'movement': None,
                    'village_distance': None,
                    'timedifference': None,
                    'otpstatus': None,
                    'audiourls': None,
                    'audioanswers': None,
                    'actualaddress': None,
                    'tldetails': None,
                    'vflag': vflag
                }
            else:
                continue
        else:
            responsesdict[d[3]] = {
                'surveyor': None,
                'date': None,
                'time': None,
                'id1': d[3],
                'village': None,
                'village_latitude': None,
                'village_longitude': None,
                'startlat': None,
                'endlat': None,
                'startlong': None,
                'endlong': None,
                'movement': None,
                'village_distance': None,
                'timedifference': None,
                'otpstatus': None,
                'audiourls': None,
                'audioanswers': None,
                'actualaddress': None,
                'tldetails': None,
                'vflag': vflag
            }

        # Fetch Village
        if responsesdict[d[3]]['village'] == None:
            if float(d[4]) in villages_list:
                if d[5] != '' and d[5] != None:
                    # Check if village is in others
                    village = d[5]
                    responsesdict[d[3]]['village'] = d[5]
                else:
                    try:
                        village = d[0].split('-')[1].split('(')[0].replace(' ', '')
                    except Exception as e:
                        village = d[0]

                    responsesdict[d[3]]['village'] = d[0]

                if Village.objects.filter(name__iexact=village).count() > 0:
                    responsesdict[d[3]]['vflag'] = vflag
                    villageobj = Village.objects.filter(name__iexact=village)[0]
                    responsesdict[d[3]]['village_latitude'] = villageobj.latitude
                    village_latitude = villageobj.latitude
                    responsesdict[d[3]]['village_longitude'] = villageobj.longitude
                    village_longitude = villageobj.longitude
                else:
                    village, state, lat, lng = extractvillagegeocodes(village, project)

                    responsesdict[d[3]]['vflag'] = vflag
                    responsesdict[d[3]]['village_latitude'] = lat
                    village_latitude = lat
                    responsesdict[d[3]]['village_longitude'] = lng
                    village_longitude = lng

        # Fetch surveyor name
        if responsesdict[d[3]]['surveyor'] == None:
            surveyorname = getsurveyorname(d[1])
            responsesdict[d[3]]['surveyor'] = '%s - (%s)' % (d[1], surveyorname)

        # Fetch datetime and geocode details
        if responsesdict[d[3]]['date'] == None:
            responsesdict = fetchdatetime(responsesdict, d)

        # Fetch OTP status
        try:
            if float(d[4]) == float(otp_cpnumber):
                otpstatus_flag = fetchotpstatus(otp_cpnumber, d, capi_checklist_id, number_cp)
                responsesdict[d[3]]['otpstatus'] = otpstatus_flag
        except Exception as e:
            otpstatus_flag = None
            responsesdict[d[3]]['otpstatus'] = None

        # Fetch audios
        if responsesdict[d[3]]['audiourls'] == None:
            audiourls, audioanswers = fetchaudiourls(d[3], maxaudios, Project.objects.get(capi_checklist_id=capi_checklist_id).pk)
            responsesdict[d[3]]['audiourls'] = audiourls
            responsesdict[d[3]]['audioanswers'] = audioanswers

        # Fetch TL Details
        if responsesdict[d[3]]['tldetails'] == None:
            responsesdict[d[3]]['tldetails'] = fetchtldetails(d, capi_checklist_id)

        # Fetch Distance and Movement
        if responsesdict[d[3]]['village_distance'] == None or responsesdict[d[3]]['movement'] == None:
            if Project.objects.get(id=project).geocodes_available:
                geocodes_available = True
            else:
                geocodes_available = False

            responsesdict = fetchdistanceandmovement(capi_checklist_id, responsesdict, d, responsesdict[d[3]]['startlat'], responsesdict[d[3]]['startlong'], responsesdict[d[3]]['endlat'], responsesdict[d[3]]['endlong'])
        else:
            if Project.objects.get(id=project).geocodes_available:
                geocodes_available = True
            else:
                geocodes_available = False

            responsesdict = fetchdistanceandmovement(capi_checklist_id, responsesdict, d, responsesdict[d[3]]['startlat'], responsesdict[d[3]]['startlong'], responsesdict[d[3]]['endlat'], responsesdict[d[3]]['endlong'])

        responsesdict[d[3]]['task_id'] = d[6]

    for key in responsesdict.keys():
        #print() 'Pre populate %s %s' % (key, Project.objects.get(pk=project).name)
        populateSurveyResponse(key, responsesdict, data, project)

    db.close()

def fetchtldetails(d, capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    project = Project.objects.get(capi_checklist_id=capi_checklist_id)
    try:
        tlcheckpoint = ProjectSpecificCheckpoints.objects.filter(project=project)[0].tlcodecheckpoint
    except Exception as e:
        return None

    tlcode = '''SELECT VALUE, OTHER FROM SAVE_SURVEY WHERE id1="%s" AND CHECKPOINT_ID="%s"''' \
                % (d[3], tlcheckpoint)
    # tlcode = '''SELECT VALUE, OTHER FROM SAVE_SURVEY WHERE id1 LIKE "%s" AND CHECKPOINT_ID LIKE "%s"''' \
    #             % (d[3], tlcheckpoint)
    cursor.execute(tlcode)
    try:
        tlcode = cursor.fetchall()[0][0]
    except Exception as e:
        tlcode = None

    db.close()
    return tlcode

# def project_surveyor_list(data, capi_checklist_id):
#     db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
#     cursor = db.cursor()
#
#     sql = '''SELECT EMP_ID FROM ASSIGNED_SURVEY WHERE CHECKLIST_ID=%s''' % (capi_checklist_id)
#     cursor.execute(sql)
#     surveyorlist = cursor.fetchall()
#     surveyors = [surveyor[0] for surveyor in surveyorlist]
#
#     db.close()
#     return surveyors

def audiofiles(d, capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    sql = '''SELECT VALUE, AUDIO_URL, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE AUDIO_URL IS NOT NULL AND id1=%s''' % (d[3])
    # sql = '''SELECT VALUE, AUDIO_URL, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE AUDIO_URL IS NOT NULL AND id1 LIKE %s''' % (d[3])
    cursor.execute(sql)
    audiosql = cursor.fetchall()

    if len(audiosql) > maxaudios:
        maxaudios = len(audiosql)

    audiourls = []
    if len(audiosql) > 0:
        for urls in audiosql:
            sql = '''SELECT CHECKPOINT_NAME FROM CHECKPOINT WHERE CHECKPOINT_ID=%s''' % (urls[3])
            # sql = '''SELECT CHECKPOINT_NAME FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE %s''' % (urls[3])
            cursor.execute(sql)
            cp_sql = cursor.fetchall()[0][0]

            try:
                if urls[0] == 'Other':
                    audiourls.append([urls[2].encode('utf-8'), urls[1], cp_sql.encode('utf-8')])
                else:
                    audiourls.append([urls[0].encode('utf-8'), urls[1], cp_sql.encode('utf-8')])
            except Exception as e:
                pass

    db.close()
    return audiourls

def getsurveyorname(data):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    sql = '''SELECT EMP_NAME FROM EMP_MASTER WHERE EMP_ID="%s"''' % (data)
    cursor.execute(sql)
    sqldata = cursor.fetchall()

    db.close()
    return sqldata[0][0]

def fetchnumbercheckpoint(capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    # Fetch which checkpoints have phone number
    sql = '''SELECT CHECKPOINT_ID FROM NCCS_NEW WHERE CHECKLIST_ID=%s''' % (capi_checklist_id)
    # sql = '''SELECT CHECKPOINT_ID FROM CHECKLIST_MASTER WHERE CHECKLIST_ID LIKE %s''' % (capi_checklist_id)

    cursor.execute(sql)
    sqldata = cursor.fetchall()

    number_cp = None
    for cpd in sqldata:
        sql = '''SELECT CHECKPOINT_ID FROM CHECKPOINT WHERE QUESTION_CODE=1000 AND CHECKPOINT_ID IN (%s)''' % (cpd)
        # sql = '''SELECT CHECKPOINT_ID FROM CHECKPOINT WHERE QUESTION_CODE LIKE 1000 AND CHECKPOINT_ID IN (%s)''' % (cpd)

        cursor.execute(sql)
        insqldata = cursor.fetchall()

        if len(insqldata) != 0:
            number_cp = insqldata[0][0]

    db.close()
    return number_cp

def fetchotpcpnumber(capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    # Fetch which checkpoints have phone number
    sql = '''SELECT CHECKPOINT_ID FROM NCCS_NEW WHERE CHECKLIST_ID=%s''' % (capi_checklist_id)
    # sql = '''SELECT CHECKPOINT_ID FROM CHECKLIST_MASTER WHERE CHECKLIST_ID LIKE %s''' % (capi_checklist_id)

    cursor.execute(sql)
    sqldata = cursor.fetchall()

    number_cp = None
    otp_cpnumber = None
    for cpd in sqldata:
        sql = '''SELECT CHECKPOINT_ID FROM CHECKPOINT WHERE CHECKPOINT_NAME IN ("Axis Number", "OTP") AND CHECKPOINT_ID IN (%s)''' % (cpd)

        cursor.execute(sql)
        insqldata = cursor.fetchall()

        if len(insqldata) != 0:
            otp_cpnumber = insqldata[0][0]

    db.close()
    return otp_cpnumber

def fetchtasks(capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    # Fetch task ID
    sql = '''SELECT TASK_ID FROM ASSIGNED_SURVEY WHERE CHECKLIST_ID=%s ORDER BY TID DESC''' % (capi_checklist_id)
    # sql = '''SELECT TASK_ID FROM ASSIGNED_SURVEY WHERE CHECKLIST_ID LIKE %s ORDER BY TID DESC''' % (capi_checklist_id)

    cursor.execute(sql)
    sqldata = cursor.fetchall()

    taskarray = []
    for d in sqldata:
        taskarray.append(str(d[0]))

    tasks = ','.join(taskarray)

    db.close()
    return tasks

def fetchlocation(capi_checklist_id):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    checkpoints = []
    subcheckpoints = []
    subcheckpoints_final = []
    villagearr = ['village', 'villages', 'district', 'address / ward number', 'village/location']
    village = None

    # Fetch checkpoints of the checklist
    sql = '''SELECT CHECKPOINT_ID FROM NCCS_NEW WHERE CHECKLIST_ID=%s''' % (capi_checklist_id)
    # sql = '''SELECT CHECKPOINT_ID FROM CHECKLIST_MASTER WHERE CHECKLIST_ID LIKE %s''' % (capi_checklist_id)
    cursor.execute(sql)
    checklistsql = cursor.fetchall()

    for checkpoint in checklistsql:
        for cp in checkpoint[0].split(','):
            if cp:
                checkpoints.append(int(cp.replace(' ', '')))

    try:
        for checkpoint in checkpoints:
            sql = '''SELECT SUBCHECKPOINT FROM CHECKPOINT WHERE CHECKPOINT_ID=%s''' % (checkpoint)
            cursor.execute(sql)
            checkpointsql = cursor.fetchall()
            for cp in checkpointsql:
                if cp[0]:
                    for subcp in cp[0].split(','):
                        if int(float(subcp.replace(' ', ''))) != 0:
                            subcheckpoints.append(float(subcp.replace(' ', '')))

        for data in subcheckpoints:
            sql = '''SELECT CHECKPOINT_NAME, CHECKPOINT1_ID FROM CHECKPOINT1 WHERE CHECKPOINT1_ID LIKE %s''' % (data)
            cursor.execute(sql)
            subcheckpointsql = cursor.fetchall()

            for subcp in subcheckpointsql:
                try:
                    if subcp[0].encode('utf-8').lower() in villagearr:
                        subcheckpoints_final.append(float(subcp[1]))
                except Exception as e:
                    pass

    except Exception as e:
        # e.g. For PMUY questionnaire
        for checkpoint in checkpoints:
            sql = '''SELECT CHECKPOINT_NAME, CHECKPOINT_ID FROM CHECKPOINT WHERE CHECKPOINT_ID=%s''' % (checkpoint)
            # sql = '''SELECT CHECKPOINT_NAME, CHECKPOINT_ID FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE %s''' % (checkpoint)
            cursor.execute(sql)
            checkpointsql = cursor.fetchall()

            for cp in checkpointsql:
                try:
                    if cp[0].encode('utf-8').lower() in villagearr:
                        subcheckpoints_final.append(float(cp[1]))
                except Exception as e:
                    pass

    db.close()
    return subcheckpoints_final

def getsurveyorname(data):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    sql = '''SELECT EMP_NAME FROM EMP_MASTER WHERE EMP_ID="%s"''' % (data)
    cursor.execute(sql)
    sqldata = cursor.fetchall()

    db.close()
    return sqldata[0][0]

def fetchdatetime(responsesdict, d):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    sql = '''SELECT STATUS, LATITUDE, LONGITUDE, DEVICE_DATETIME, Address FROM MOVEMENT WHERE SURVEY_ID=%s''' % (d[3])
    # sql = '''SELECT STATUS, LATITUDE, LONGITUDE, DEVICE_DATETIME, Address FROM MOVEMENT WHERE SURVEY_ID LIKE %s''' % (d[3])

    cursor.execute(sql)
    locationdata = cursor.fetchall()

    starttime = None
    endtime = None
    devicedate = None
    devicetime = None
    startlat = None
    startlong = None
    endlat = None
    endlong = None
    actualaddress = None

    for ld in locationdata:
        devicedate = ld[3].date
        devicetime = ld[3].time

        # Display Date
        responsesdict[d[3]]['date'] = ld[3].strftime('%d-%b-%Y')

        if ld[0] == 'START':
            startlat = float(ld[1])
            startlong = float(ld[2])
            starttime = ld[3]
            actualaddress = ld[4]
        elif ld[0] == 'END':
            endlat = float(ld[1])
            endlong = float(ld[2])
            endtime = ld[3]
            if actualaddress == None:
                actualaddress = ld[4]

    if endtime is None or starttime is None:
        timedifference = '-'
    else:
        timedifference = (datetime.combine(endtime.date(), endtime.time()) - datetime.combine(starttime.date(), starttime.time())).seconds

    # responsesdict[d[3]]['date'] = devicedate

    if starttime != None:
        responsesdict[d[3]]['meta'] = {'datetime': 1}
        responsesdict[d[3]]['time'] = starttime.strftime('%H:%M:%S')
    else:
        responsesdict[d[3]]['meta'] = {'datetime': 0}
        # responsesdict[d[3]]['time'] = starttime
        sql = '''SELECT DATETIME FROM SAVE_SURVEY WHERE id1="%s"''' % (d[3])
        # sql = '''SELECT DATETIME FROM SAVE_SURVEY WHERE id1 LIKE "%s"''' % (d[3])
        cursor.execute(sql)
        dtobj = cursor.fetchall()[0][0]
        responsesdict[d[3]]['time'] = dtobj.time().strftime('%H:%M:%S')

        if responsesdict[d[3]]['date'] == None:
            responsesdict[d[3]]['date'] = dtobj.date().strftime('%d-%b-%Y')

    responsesdict[d[3]]['startlat'] = startlat
    responsesdict[d[3]]['startlong'] = startlong
    responsesdict[d[3]]['endlat'] = endlat
    responsesdict[d[3]]['endlong'] = endlong
    responsesdict[d[3]]['timedifference'] = '%s seconds' % (timedifference)
    responsesdict[d[3]]['actualaddress'] = actualaddress

    db.close()
    return responsesdict

def fetchotpstatus(otp_cpnumber, d, capi_checklist_id, number_cp):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    # Fetch mobile number
    mobile_number = None

    try:
        sql = '''SELECT VALUE FROM SAVE_SURVEY WHERE CHECKPOINT_ID="%s" AND id1="%s"''' % (number_cp, str(d[3]))
        # sql = '''SELECT VALUE FROM SAVE_SURVEY WHERE CHECKPOINT_ID LIKE %s AND id1 LIKE %s''' % (number_cp, d[3])
        cursor.execute(sql)
        mobile_number = cursor.fetchall()[0][0]
    except Exception as e:
        return 'Wrong'

    otpstatus_flag = None
    entered_otp = d[0].lower()

    sql = '''SELECT OTP FROM OTP WHERE CHECKLIST_ID="%s" AND MOBILE="%s"''' % (capi_checklist_id, str(mobile_number))
    # sql = '''SELECT OTP FROM OTP WHERE CHECKLIST_ID LIKE %s AND MOBILE LIKE %s''' % (capi_checklist_id, mobile_number)
    cursor.execute(sql)
    otp_sql = cursor.fetchall()

    otps = []
    for otp in otp_sql:
        otps.append(otp[0].lower())

    if entered_otp in otps:
        otpstatus_flag = 'Verified'
    else:
        otpstatus_flag = 'Wrong'

    db.close()
    return otpstatus_flag

def fetchaudiourls(id1, maxaudios, project):
    db_config = json.dumps(settings.CELERY_DATABASE_CONFIG)

    db_config_host = str(json.loads(db_config)['host'])
    db_config_pass = str(json.loads(db_config)['pass'])
    db_config_user = str(json.loads(db_config)['user'])
    db_config_port = str(json.loads(db_config)['port'])
    db_config_database = str(json.loads(db_config)['database'])

    db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
    # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    sql = '''SELECT VALUE, AUDIO_URL, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE AUDIO_URL IS NOT NULL AND id1=%s''' % (id1)
    # sql = '''SELECT VALUE, AUDIO_URL, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE AUDIO_URL IS NOT NULL AND id1 LIKE %s''' % (id1)
    cursor.execute(sql)
    audiosql = cursor.fetchall()

    if len(audiosql) > maxaudios:
        maxaudios = len(audiosql)

    audiourls = []
    if len(audiosql) > 0:
        for urls in audiosql:
            sql = '''SELECT CHECKPOINT_NAME FROM CHECKPOINT WHERE CHECKPOINT_ID=%s''' % (urls[3])
            # sql = '''SELECT CHECKPOINT_NAME FROM CHECKPOINT WHERE CHECKPOINT_ID LIKE %s''' % (urls[3])
            cursor.execute(sql)
            cp_sql = cursor.fetchall()[0][0]

            try:
                if urls[0] == 'Other':
                    audiourls.append([urls[2].encode('utf-8'), urls[1], cp_sql.encode('utf-8')])
                else:
                    audiourls.append([urls[0].encode('utf-8'), urls[1], cp_sql.encode('utf-8')])
            except Exception as e:
                pass

    # Fetch political answers
    answers_political = []

    try:
        audiocpobj = AudioCheckpoints.objects.get(project=Project.objects.get(id=project))
    except Exception as e:
        return [], []

    checkpoints_political = []
    checkpoints_political_1 = []
    cpdict = {}
    cp1dict = {}
    for cp in json.loads(audiocpobj.cplist).keys():

        if '.' in str(json.loads(audiocpobj.cplist)[cp]):
            checkpoints_political_1.append(json.loads(audiocpobj.cplist)[cp])
            cp1dict[json.loads(audiocpobj.cplist)[cp]] = cp
        else:
            checkpoints_political.append(json.loads(audiocpobj.cplist)[cp])
            cpdict[json.loads(audiocpobj.cplist)[cp]] = cp

    # checkpoints_political = [int(audiocpobj.mla), int(audiocpobj.mp), int(audiocpobj.state), int(audiocpobj.center)]
    checkpoints_political = ','.join(str(cpobj) for cpobj in checkpoints_political)

    sql = '''SELECT VALUE, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE id1=%s AND CHECKPOINT_ID in (%s)''' % (id1, checkpoints_political)
    cursor.execute(sql)

    for ans in cursor.fetchall():
        try:
            answers_political.append([ans[0].encode('utf-8'), str(cpdict[int(ans[2])])])
        except Exception as e:
            pass

    db.close()

    try:
        db = MySQLdb.connect(db_config_host, db_config_user, db_config_pass, db_config_database, charset='utf8',use_unicode=True)
        # db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
        cursor = db.cursor()

        checkpoints_political_1 = ','.join(str(cpobj) for cpobj in checkpoints_political_1)

        sql = '''SELECT VALUE, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE id1=%s AND CHECKPOINT_ID in (%s)''' % (id1, checkpoints_political_1)
        cursor.execute(sql)

        for ans in cursor.fetchall():
            try:
                answers_political.append([ans[0].encode('utf-8'), str(cp1dict[float(ans[2])])])
            except Exception as e:
                pass

        db.close()
    except Exception as e:
        pass

    return audiourls, answers_political

def fetchdistanceandmovement(capi_checklist_id, responsesdict, d, startlat, startlong, endlat, endlong):
    R = 6373.0
    movement = None
    village_distance = None

    if startlat != None and startlong != None and endlat != None and endlong != None:
        dlat = radians(responsesdict[d[3]]['endlat']) - radians(responsesdict[d[3]]['startlat'])
        dlong = radians(responsesdict[d[3]]['endlong']) - radians(responsesdict[d[3]]['startlong'])

        try:
            a = (sin(dlat/2))**2 + cos((startlat)) * cos(endlat) * (sin(dlong/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            movement = '{:,}'.format(int(distance*1000))
        except Exception as e:
            pass

        try:
            if responsesdict[d[3]]['village_latitude'] != None and responsesdict[d[3]]['village_longitude'] != None:
                dvlat = radians(float(responsesdict[d[3]]['village_latitude'])) - radians(float(responsesdict[d[3]]['startlat']))
                dvlong = radians(float(responsesdict[d[3]]['village_longitude'])) - radians(float(responsesdict[d[3]]['startlong']))

                av = (sin(dvlat/2))**2 + cos((startlat)) * cos(endlat) * (sin(dvlong/2))**2
                cv = 2 * atan2(sqrt(av), sqrt(1-av))
                distancev = R * cv

                village_distance = '{:,}'.format(int(distancev*1000))
        except Exception as e:
            pass

    if responsesdict[d[3]]['movement'] == None:
        responsesdict[d[3]]['movement'] = movement

    if responsesdict[d[3]]['village_distance'] == None:
        responsesdict[d[3]]['village_distance'] = village_distance

    return responsesdict

def populateSurveyResponse(key, responsesdict, data, project):
    # Populate remarks
    responseparamdict = {}

    responseparamdict['id1'] = key
    responseparamdict['surveyor'] = responsesdict[key]['surveyor']

    # OTP flag
    if responsesdict[key]['otpstatus'] == 'Verified':
        otpstatus_flag = True
    else:
        otpstatus_flag = False


    if SurveyResponse.objects.filter(uid=key,project=Project.objects.get(id=project)).count() == 0:
        if responsesdict[key]['village_distance'] == None:
            responsesdict[key]['village_distance'] = 'GPS issue'
        if responsesdict[key]['movement'] == None:
            responsesdict[key]['movement'] = 'GPS issue'

        try:
            if responsesdict[key]['audiourls'] == []:
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='No Recordings'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'].split(' ')[0]),
                    otp_verified = otpstatus_flag
                    )
            elif responsesdict[key]['actualaddress'] != None:
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'].split(' ')[0]),
                    otp_verified = otpstatus_flag
                    )
            else:
                responsesdict[key]['actualaddress'] = 'GPS issue'
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'].split(' ')[0]),
                    otp_verified = otpstatus_flag
                    )

            #print() '%s -> %s (populate)' % (key, Project.objects.get(pk=project).name)
        except Exception as e:
            try:
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    otp_verified = otpstatus_flag
                    )

                #print() '%s -> %s (populate)' % (key, Project.objects.get(pk=project).name)
            except Exception as e:
                #print() e, ' during populate'
                pass


    return data

def extractvillagegeocodes(village, project):
    # try:
    #     base = "https://apis.mapmyindia.com/advancedmaps/v1/ztgf2xai9pexed26o3kev3zb6cfs8bjk/geo_code?"
    #     state = Project.objects.get(id=project).state.name
    #     address = village+', '+state
    #     params = "addr={address}".format(
    #         address=address
    #     )
    #
    #     url = "{base}{params}".format(base=base, params=params)
    #     response = requests.get(url)
    #     geocodes = response.json()['results'][0]
    #
    #     lat = geocodes['lat']
    #     lng = geocodes['lng']
    #
    #     return village, state, lat, lng
    # except Exception as e:
    #     #print() 'Key exhausted', e
    #     return village, None, None, None
    try:
        key = "AIzaSyBVxG-rxSrRrg1eJOO5jY311P7LUlAFORw"
        # key = "AIzaSyB_ZIG03KZ6Uj9o4ROuhIoK7NqR-SuuUJg"
        # key = "AIzaSyB-drA36Kmgr6fTzu0z8g28Sod5ZbwpJiY"
        # key = "AIzaSyDXvfMPhjz1LnaKVKoIuyfHjoMIhysfxjo"
        base = "https://maps.googleapis.com/maps/api/geocode/json?"
        state = Project.objects.get(id=project).state.name
        address = village+', '+state
        params = "address={address}&sensor={sen}&key={key}".format(
            address=address,
            sen='false',
            key=key
        )
        url = "{base}{params}".format(base=base, params=params)
        response = requests.get(url)
        geocodes = response.json()['results'][0]['geometry']['location']
        lat = geocodes['lat']
        lng = geocodes['lng']

        return village, state, lat, lng
    except Exception as e:
        return village, state, None, None
