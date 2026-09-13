# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
import requests
from random import randint
from difflib import SequenceMatcher
from datetime import datetime, date
from math import sin, cos, sqrt, atan2, radians
import json
import MySQLdb
import csv
import ast

from dateparser import parse

class GeoMismatchView(TemplateView):


    def get(self, request):
        try:
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'employee_pic': request.user.user_employee.get_profile_pic(),
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'a_app_templates/a_app_qualitydashboard.html',
                'maindata': [],
                'added_bye':None,
                'added_time':None
            }
        except Exception as e:
            data = {
                'first_name': "-",
                'last_name': "-",
                'userrole': "-",
                'department': "-",
                'htmlfilename': 'a_app_templates/a_app_qualitydashboard.html',
                'maindata': [],
                'added_bye':None,
                'added_time':None
                
            }

        projectid = request.GET['project']
        print(projectid)
        data['projectid'] = projectid

        if projectid == '':
            data['error'] = True
            return render(request, 'a_app_templates/a_app_qualitydashboard.html', data)
        else:
            # Check if project is nccs project
            data['error'] = False

    

        if request.user.is_active:
            self.fetchdata(request, data)

     



        if not request.user.is_active:
            return HttpResponseRedirect('/login')

        
        return render(request, 'index.html', data)


    ####### showing report data #########

    def fetchdata(self, request, data):
        self.maxaudios = 0
        
        client_id = "1000.Q860LP648ERMIBPKJHIFAE4QKRWIMI";
        client_secret = "a6f0a2abbba58ea1cbecb81f8504230c0ddad07e1d";
        refresh_token = "1000.d3a8eca69745b36a7729e746f8a21e19.8979ba5d21ac79ab36bd1ba5259009d2";
        url = "https://accounts.zoho.in/oauth/v2/token";
        parameters = {"grant_type":"refresh_token","client_id":client_id,"client_secret":client_secret,"refresh_token":refresh_token}

        r = requests.post(url,data=parameters)
        access_token = r.json()['access_token']

        headers = {"Authorization":"Zoho-oauthtoken " + access_token}

        url2 = "https://people.zoho.in/people/api/forms/PMS1/getRecords?sIndex=1&limit=100"

        r2 = requests.get(url2,headers=headers)

        test = list(r2.json()['response']['result'])

        if 'project' in request.GET.keys():
            data['project'] = request.GET['project']
            
            for i,value in enumerate (test):
                for j in value:
                    if value[j][0]['Added_By'] == request.GET['project'] and datetime.today().strftime('%d-%m-%Y') in value[j][0]['AddedTime']:
                        
                            employee_data = value[j][0]['tabularSections']['Tasks']
                            employee_all_data = value[j][0]
                            print(employee_data)
                            
            data['added_bye'] = employee_all_data['Added_By']
            
            data['added_time'] = employee_all_data['AddedTime']
            
            data['maindata'] = employee_data
                            
                
        return data