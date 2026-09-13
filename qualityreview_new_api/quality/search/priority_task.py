# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

# import datetime
import logging
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from search.models import PriorityTasksSchedulesID,Project;
from search.tasks import *
from threading import Thread
from django.contrib import messages

logger = logging.getLogger(__name__)


@method_decorator(login_required(login_url='/login'), name='dispatch')
class PriorityTasksView(TemplateView):

    def get(self,request):
        tasks = PriorityTasksSchedulesID.objects.all()
        data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'userrole': request.user.user_employee.designation.name,
                'department': request.user.user_employee.designation.department.name,
                'htmlfilename': 'a_app_templates/priotityViews.html',
                'maindata': [],
                'tasks': tasks
            }
        return render(request, 'index.html', data);

    def post(self,request):
      
        data = None
        if(request.POST.get('export_action') == 'add'):
            # print(start_date,end_date, " dateeeeeeeeeee")
            tasksObj = PriorityTasksSchedulesID(task_id=request.POST.get('export_task_id'),task_created_by=request.user.first_name,task_created_on=datetime.now());
            tasksObj.save();
            data = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    # 'employee_pic': request.user.user_employee.get_profile_pic(),
                    'userrole': request.user.user_employee.designation.name,
                    'department': request.user.user_employee.designation.department.name,
                    'htmlfilename': 'a_app_templates/priotityViews.html',
                    'maindata': [],
                    'tasks': PriorityTasksSchedulesID.objects.all()
                }
            return render(request, 'index.html',data)
    
        elif(request.POST.get('export_action') == 'delete'):
            PriorityTasksSchedulesID.objects.get(pk=request.POST.get('export_task_id')).delete();
            data = {
                            'first_name': request.user.first_name,
                            'last_name': request.user.last_name,
                            # 'employee_pic': request.user.user_employee.get_profile_pic(),
                            'userrole': request.user.user_employee.designation.name,
                            'department': request.user.user_employee.designation.department.name,
                            'htmlfilename': 'a_app_templates/priotityViews.html',
                            'maindata': [],
                            'tasks': PriorityTasksSchedulesID.objects.all()
                    }
            return render(request, 'index.html',data)



        else:
            t = None;
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            # print(start_date,"date>>>")
            for proj in PriorityTasksSchedulesID.objects.all():

                # print(proj.task_id,">>>")
                capi_checklist_id = Project.objects.filter(pk=proj.task_id)[0].capi_checklist_id;
                t = Thread(target=notify_fetchdatacron, args=(capi_checklist_id,proj.task_id,start_date,end_date))
                t.start();
                t.join();
            data = {
                        'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                        # 'employee_pic': request.user.user_employee.get_profile_pic(),
                        'userrole': request.user.user_employee.designation.name,
                        'department': request.user.user_employee.designation.department.name,
                        'htmlfilename': 'a_app_templates/priotityViews.html',
                        'maindata': [],
                        'tasks': PriorityTasksSchedulesID.objects.all()
                }
        return render(request, 'index.html',data);
