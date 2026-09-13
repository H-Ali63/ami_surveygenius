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
from django.http import HttpResponse
from django.conf import settings
# from mainapp.tasks import *
from search.models import *
from random import randint
from difflib import SequenceMatcher
from datetime import datetime, date
from math import sin, cos, sqrt, atan2, radians
import json
import MySQLdb
import csv
import ast
from datetime import timedelta

logger = logging.getLogger(__name__)


@method_decorator(login_required(login_url='/login'), name='dispatch')
class QualityDash(TemplateView):
    def get(self, request):
        self.daterange = date.today() - timedelta(days=0)
        self.date_yesterday = '%s-%02d-%02d' % (self.daterange.year, self.daterange.month, self.daterange.day)

        try:
            data = {
                'user': request.user.user_employee,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                # 'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'a_app_templates/a_app_qualitydashboard.html',
                'maindata': [],
                'today_str': self.date_yesterday,
                'notification': None
            }
        except Exception as e:
            logger.exception(
                            "Error while preparing user dashboard data"
                        )
            
            data = {
                            'first_name': "-",
                            'last_name': "-",
                            'userrole': "-",
                            'department': "-",
            
                            'htmlfilename':
                                'a_app_templates/a_app_qualitydashboard.html',
            
                            'maindata': [],
                            'today_str': self.date_yesterday,
                            'notification': None
                        }
            
        data['projects'] = Project.objects.filter(active=True).order_by('-pk')              ## get projects here in descending order

        if 'project' in request.GET.keys():
            try:
                data['requested_project'] = Project.objects.get(pk=request.GET['project'])
            except Exception as e:
                data['requested_project'] = None
        else:
            data['requested_project'] = None

        if data['requested_project']:
            try:
                final_dict = {}
                # print (data['requested_project'])
                project = data['requested_project']

                from_date = datetime.strptime(request.GET['from_date'], '%Y-%m-%d').date()
                to_date = datetime.strptime(request.GET['to_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError, KeyError):
        
                        logger.exception(
                            "Invalid or missing from_date/to_date"
                        )
        
                        from_date = date.today()
                        to_date = date.today()

            dates_range = []


            ## for loop from all responses from that project from surveyreponses

            for surveyor in SurveyResponse.objects.filter(project=project, project__active=True,response_date__range=(from_date, to_date)).values('surveyor__employee_id').distinct():  
                # print(surveyor)
                if surveyor['surveyor__employee_id'] is not None:
                    ## employee id of particular surveyor
                    employee_id = surveyor['surveyor__employee_id']
                    ## surveyor full name with id
                    surveyor_name_id = '%s - (%s %s)' % (employee_id, User.objects.get(user_employee__employee_id=employee_id).first_name, User.objects.get(user_employee__employee_id=employee_id).last_name)

                    try:
                        final_dict[surveyor_name_id] = {}
                    except Exception as e:
                        pass

                    for resp in SurveyResponse.objects.filter(surveyor__employee_id=employee_id, project=project,response_date__range=(from_date, to_date)).select_related('verification_status').order_by('pk'):
                        ## loop through all responses from that partcular surveyor of that project
                        try:
                        
                            params = json.loads(
                                                    resp.params or '{}'
                                                )
                        
                        except (ValueError, TypeError):
                        
                            logger.warning(
                                                    "Invalid JSON params for SurveyResponse UID %s",
                                                    resp.uid
                                                )
                            params = {}
                        # print(params)

                        date_param = resp.response_date

                        if not date_param:
                            continue
                        dates_range.append(date_param)


                        if (
                                                resp.verification_status
                                                and resp.verification_status.name == 'Verified'
                            ):
                                verification_status = 1
                        else:
                            verification_status = 0

                        # try:
                        #     date_param = datetime.strptime(resp.response_date, '%Y-%m-%d').date()          ## get date of that particular reponse
                        #     print(date_param)
                        # except Exception as e:
                        #     continue
                        # print("from",from_date,"to",to_date)
                        # if date_param < from_date or date_param > to_date:                  ## here validation of date happen
                        #     continue

                        # dates_range.append(date_param)
                        # dates_range = sorted(list(set(dates_range)), reverse=True)          ## dates in descending

                        # if resp.verification_status.name == 'Verified':                     ## Get verification status name
                        #     verification_status = 1
                        # else:
                        #     verification_status = 0

                        if 'tldetails' in params.keys():                            ## if fr name in that response
                            teamleader = params['tldetails']
                        else:
                            teamleader = None
                            # print('--------11')


                        # =================================================
                        # INITIAL SURVEYOR + DATE ENTRY
                        # =================================================
                        
                        if final_dict[surveyor_name_id] == {}:
                        
                                                final_dict[surveyor_name_id][date_param] = {
                        
                                                    'teamleader': teamleader,
                        
                                                    'totalforms': 1,
                        
                                                    'assigned_for_qc':
                                                        project.verification_percent / 100,
                        
                                                    'verified_by_qc':
                                                        verification_status,
                        
                                                    'pending_for_qc':
                                                        max(
                                                            (
                                                                project.verification_percent / 100
                                                            ) - verification_status,
                                                            0
                                                        ),
                        
                                                    'percent_verified':
                                                        (verification_status / 1) * 100
                                                }
                        
                                            # =================================================
                                            # EXISTING DATE ENTRY
                                            # =================================================
                        
                        else:
                        
                                                if (
                                                    date_param
                                                    in final_dict[surveyor_name_id]
                                                ):
                        
                                                    # =========================================
                                                    # UPDATE TEAM LEADER
                                                    # =========================================
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ]['teamleader'] = teamleader
                        
                                                    # =========================================
                                                    # TOTAL FORMS
                                                    # =========================================
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ]['totalforms'] += 1
                        
                                                    totalforms = (
                                                        final_dict[
                                                            surveyor_name_id
                                                        ][
                                                            date_param
                                                        ]['totalforms']
                                                    )
                        
                                                    # =========================================
                                                    # ASSIGNED FOR QC
                                                    # =========================================
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ]['assigned_for_qc'] = (
                                                        (project.verification_percent / 100)
                                                        * totalforms
                                                    )
                        
                                                    # =========================================
                                                    # VERIFIED BY QC
                                                    # =========================================
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ]['verified_by_qc'] += (
                                                        verification_status
                                                    )
                        
                                                    verified_by_qc = (
                                                        final_dict[
                                                            surveyor_name_id
                                                        ][
                                                            date_param
                                                        ]['verified_by_qc']
                                                    )
                        
                                                    # =========================================
                                                    # PENDING FOR QC
                                                    # =========================================
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ]['pending_for_qc'] = max(
                                                        (
                                                            (
                                                                project.verification_percent
                                                            ) / 100
                                                            * totalforms
                                                        ) - verified_by_qc,
                                                        0
                                                    )
                        
                                                    # =========================================
                                                    # PERCENT VERIFIED
                                                    # =========================================
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ]['percent_verified'] = (
                                                        (
                                                            verified_by_qc
                                                            / totalforms
                                                        ) * 100
                                                    )
                        
                                                # =============================================
                                                # NEW DATE FOR EXISTING SURVEYOR
                                                # =============================================
                        
                                                else:
                        
                                                    final_dict[
                                                        surveyor_name_id
                                                    ][
                                                        date_param
                                                    ] = {
                        
                                                        'teamleader': teamleader,
                        
                                                        'totalforms': 1,
                        
                                                        'assigned_for_qc':
                                                            project.verification_percent / 100,
                        
                                                        'verified_by_qc':
                                                            verification_status,
                        
                                                        'pending_for_qc':
                                                            max(
                                                                (
                                                                    project.verification_percent / 100
                                                                ) - verification_status,
                                                                0
                                                            ),
                        
                                                        'percent_verified':
                                                            (
                                                                verification_status / 1
                                                            ) * 100
                                                    }
                        
                                    # =========================================================
                                    # SORT DATES DESCENDING
                                    # =========================================================
                        
            dates_range = sorted(list(set(dates_range)),reverse=True)
                        
            # =========================================================
            # SEND DATA TO TEMPLATE
            # =========================================================
                        
            data['final_dict'] = final_dict
            data['dates_range'] = dates_range
                        
                                # =========================================================
                                # RENDER DASHBOARD
                                # =========================================================
                        
        return render(request,'index.html',data)
                        
        #                 if final_dict[surveyor_name_id] == {}:
        #                     final_dict[surveyor_name_id][date_param] = {
        #                         'teamleader': teamleader,
        #                         'totalforms': 1,
        #                         'assigned_for_qc': project.verification_percent / 100,
        #                         'verified_by_qc': verification_status,
        #                         'pending_for_qc': max((project.verification_percent / 100) - verification_status, 0),
        #                         'percent_verified': (verification_status / 1) * 100
        #                     }
        #                 else:
        #                     if date_param in final_dict[surveyor_name_id].keys():
        #                         final_dict[surveyor_name_id][date_param]['teamleader'] = teamleader
        #                         final_dict[surveyor_name_id][date_param]['totalforms'] += 1
        #                         final_dict[surveyor_name_id][date_param]['assigned_for_qc'] = ((project.verification_percent) / 100 * (final_dict[surveyor_name_id][date_param]['totalforms']))
        #                         final_dict[surveyor_name_id][date_param]['verified_by_qc'] += verification_status
        #                         final_dict[surveyor_name_id][date_param]['pending_for_qc'] = max((project.verification_percent) / 100 * (final_dict[surveyor_name_id][date_param]['totalforms']) - final_dict[surveyor_name_id][date_param]['verified_by_qc'], 0)
        #                         final_dict[surveyor_name_id][date_param]['percent_verified'] = (((final_dict[surveyor_name_id][date_param]['verified_by_qc']) / (final_dict[surveyor_name_id][date_param]['totalforms'])) * 100)
        #                     else:
        #                         final_dict[surveyor_name_id][date_param] = {
        #                             'teamleader': teamleader,
        #                             'totalforms': 1,
        #                             'assigned_for_qc': ((project.verification_percent) / 100),
        #                             'verified_by_qc': verification_status,
        #                             'pending_for_qc': max((project.verification_percent / 100) - verification_status, 0),
        #                             'percent_verified': ((verification_status / 1) * 100)
        #                         }
                            
        #                     print(final_dict,"final_dict")

        #     data['final_dict'] = final_dict
        #     data['dates_range'] = dates_range

        # return render(request, 'index.html', data)
