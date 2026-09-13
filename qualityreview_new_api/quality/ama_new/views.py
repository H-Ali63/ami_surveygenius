from django.shortcuts import render   #type: ignore
from django.http import HttpResponse  #type: ignore
from django.views import View         #type: ignore
from .models import ama_new_data,SurveyResponse_ama, QualityReview_ama #type: ignore
import pandas as pd #type: ignore
import datetime
import json
from search.models import Project, Employee
from django.contrib.auth.models import User #type: ignore
from quality.access_control import require_staff

# Create your views here.
@require_staff
def data_insert(request):

    df = pd.read_csv("C:/venv/qualityreview3/Axis My America_25.csv")

    response_ids_db = ama_new_data.objects.values_list('response_id',flat=True)


    for index,row in df.iterrows():
        if row['Response ID'] in response_ids_db:
             continue
        print(index,'ind')
        print(row,"row")

        survey = ama_new_data(response_id=row['Response ID'],Surveyor_Name=row['Interviewer Name (Your Full Name)'],
                              Survey_name='Axis My America',Respondent_Name=row['Respondent Name'],Respondent_location=row['Respondent location'],
                              Start_time=row['Start time'],Completion_time=row['Completion time'],Time_taken=row['Time taken'],Lat =row['Location[Latitude]'],
                              Long=row['Location[Latitude]'],City = row['City'],State= row['State'], Ama_audio_Url = row['Upload Audio'],Ama_response_Url = row['Response link'])
     
    
    # Save the instance to the database
        survey.save()

    return HttpResponse("<h1>done insertion</h1>")

@require_staff
def surveyresponse_upload(request):

    responsesdict = {}
    

    all_entries = ama_new_data.objects.filter(id=132).values('response_id','Surveyor_Name','Survey_name','Respondent_Name','Start_time','Completion_time','Time_taken','Lat','Long','City','State')
    print(all_entries)

    for value in all_entries:

        response_id = value['response_id']
        Surveyor_Name = value['Surveyor_Name']
        Survey_name = value['Survey_name']
        Respondent_Name = value['Respondent_Name']
        Start_time = value['Start_time']
        Completion_time = value['Completion_time']
        Time_taken = value['Time_taken']
        Lat = value['Lat']
        Long = value['Long']
        City = value['City']
        State = value['State']


        responsesdict[response_id] = {
                        'surveyor': Surveyor_Name,
                        'date': Start_time,
                        'time': None,
                        'id1': response_id,
                        'village': City,
                        'village_latitude': None,
                        'village_longitude': None,
                        'startlat': Lat,
                        'endlat': None,
                        'startlong': Long,
                        'endlong': None,
                        'movement': None,
                        'village_distance': None,
                        'timedifference': Time_taken,
                        'otpstatus': False,
                        'audiourls': [],
                        'audioanswers': None,
                        'actualaddress': None,
                        'tldetails': None,
                        'vflag': "",
                        'project': Survey_name
            }
        
        # print(responsesdict)


        # value = User.objects.get(first_name__icontains = str(responsesdict[response_id]['surveyor']))
        # print(value)

        # print(responsesdict[response_id]['id1'])

        populateSurveyResponse(response_id, responsesdict)

    return HttpResponse("<h1>Fetch data</h1>")

    


def populateSurveyResponse(id1, responsesdict):
    # Populate remarks
    responseparamdict = {}

    responsesdict_id1  = str(responsesdict[id1]['surveyor']).strip()

    # list_responsesdict_id1 = responsesdict_id1.split(' ')

    name_parts = responsesdict_id1.strip().split()

    first_name = ""
    last_name = ""

    


    if len(name_parts) > 1:
        # If there are multiple parts, assume the last part is the last name
        if not 'Sai Srikar' == " ".join(name_parts):
            first_name = " ".join(name_parts[:-1])  # Join all but the last part as first name
            last_name = name_parts[-1]
        else:
            first_name = " ".join(name_parts)  # Join all but the last part as first name
            last_name = ""            # Last part as last name
   
    elif len(name_parts) == 1:
        # If there's only one part, treat it as the first name
        first_name = name_parts[0]
        # print('no')




    # if len(responsesdict_id1.split(' ')) == 3:
          
    #     first_name = list_responsesdict_id1[0] + " " + list_responsesdict_id1[1]
    #     last_name = list_responsesdict_id1[2]

    # elif len(responsesdict_id1.split(' ')) == 2:
          
    #     first_name = list_responsesdict_id1[0]
    #     last_name = list_responsesdict_id1[1]

    # else:
        
    #    first_name = list_responsesdict_id1[0]
    #    last_name = ''

    first_name = first_name.strip()
    print(first_name)
    print(last_name)


    if last_name == "":
        print('yes')
        if first_name == "Mohit":
            matching_users = User.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact="Sai",
                username__startswith = "3000"  # or last_name=""
            )

        elif first_name == "Nikhil":
            matching_users = User.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact="K",
                username__startswith = "3000"  # or last_name=""
            )

        elif 'Sai Srikar' in first_name:
            matching_users = User.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact="Patibanda",
                username__startswith = "3000"  # or last_name=""
            )
        
        else:
            matching_users = User.objects.filter(
                first_name__iexact=first_name,
                last_name = "",
                username__startswith = "3000"  # or last_name=""
            )

    else:


        matching_users = User.objects.filter(
            first_name__iexact=first_name,           # Case-insensitive comparison for first name
            last_name__iexact=last_name,
            username__startswith = "3000"               # Case-insensitive comparison for last name
        )

    # If last name is empty, check for users with no last name

    print(matching_users.values(),"match")
        

          
    # new_responsesdict = str(responsesdict[id1]['surveyor']).split(" ")[0]
    
    # print(User.objects.filter(first_name__iexact = first_name, last_name__iexact = last_name).values('first_name','last_name'))
    

    # new_responsesdict2 = str(responsesdict[id1]['surveyor']).split(" ")[1]
    # print("new",new_responsesdict)


    # print(User.objects.filter(first_name__iexact=first_name).values()[0]['username'])

    if str(matching_users.values()[0]['username']):
        responseparamdict['id1'] = id1

        # if User.objects.filter(first_name__iexact = first_name, last_name__iexact = last_name).values()[0]['username']:
        #     responseparamdict['surveyor'] = User.objects.filter(first_name__iexact = first_name, last_name__iexact = last_name).values()[0]['username']
        # else:
        #     responseparamdict['surveyor'] = User.objects.filter(first_name__icontains = first_name).values()

        responseparamdict['surveyor'] = matching_users.values()[0]['username']
        print(responseparamdict['surveyor'])
        # ids = responseparamdict['surveyor']

        project = 1111

        print(responsesdict[id1]['surveyor'])


        # length = len(responseparamdict['surveyor'])

        # ind = (responseparamdict['surveyor']).find("(")
        # responseparamdict['surveyor'] = (responseparamdict['surveyor'])[ind+1:]

        # if len(responseparamdict['surveyor']) == 7 and responsesdict[id1]['surveyor'] != "Prateek":
        #     responseparamdict['surveyor'] = responsesdict[id1]['surveyor']

        #     length = len(responseparamdict['surveyor'])

        #     ind = (responseparamdict['surveyor']).find("(")
        #     responseparamdict['surveyor'] = (responseparamdict['surveyor'])[ind+1:length-1]

        #     print(responseparamdict['surveyor'])


        # if SurveyResponse_ama.objects.filter(id1=id1,project=Project.objects.get(capi_checklist_id=project)).count() == 0:
        #     if responsesdict[id1]['village_distance'] == None:
        #         responsesdict[id1]['village_distance'] = 'GPS issue'
        #     if responsesdict[id1]['movement'] == None:
        #         responsesdict[id1]['movement'] = 'GPS issue'
    
        if responsesdict[id1]['audiourls'] == []:
            SurveyResponse_ama.objects.create(
                uid=id1,
                project=Project.objects.get(capi_checklist_id=project),
                # verification_status=VerificationStatus.objects.get(name='No Recordings'),
                params=json.dumps(responsesdict[id1]),
                remarks=json.dumps(responseparamdict),
                surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'])
            )
                

        elif responsesdict[id1]['actualaddress'] != None:
                        SurveyResponse_ama.objects.create(
                            uid=id1,
                            project=Project.objects.get(capi_checklist_id=project),
                            # verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params=json.dumps(responsesdict[id1]),
                            remarks=json.dumps(responseparamdict),
                            surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'])
                            # otp_verified = True
                            )
        else:
                        responsesdict[id1]['actualaddress'] = 'GPS issue'
                        SurveyResponse_ama.objects.create(
                            uid=id1,
                            project=Project.objects.get(capi_checklist_id=project),
                            # verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params=json.dumps(responsesdict[id1]),
                            remarks=json.dumps(responseparamdict),
                            surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'])
                            # otp_verified = True
                           )

        print( '%s -> %s (populate)' % (id1, Project.objects.get(capi_checklist_id=project).name))
            # else:
            #         try:
            #             SurveyResponse_ama.objects.create(
            #                 uid=id1,
            #                 project=Project.objects.get(id=project),
            #                 verification_status=VerificationStatus.objects.get(name='To Be Verified'),
            #                 params=json.dumps(responsesdict[id1]),
            #                 remarks=json.dumps(responseparamdict),
            #                 otp_verified = None
            #                 )

            #             #print() '%s -> %s (populate)' % (id1, Project.objects.get(pk=project).name)
            #         except Exception as e:
            #             #print() e, ' during populate'
            #             



@require_staff
def data_deletion(request):
    # QualityReview_ama.objects.all().delete()
    return HttpResponse('<h1>done</h1>')


@require_staff
def url_upload(request):

    df = pd.read_csv("C:/venv/qualityreview3/Axis My America.csv")

    list_of_uids = ama_new_data.objects.values_list('response_id',flat=True)

    print(list_of_uids)

    #   for index,row in df.iterrows():
    #     # print(index,'ind')
    #     # print(row['Response link'],"row")
    #     # print(list_of_uids[index])
    #     # print(row['Response ID'])

    #     if row['Response ID'] == list_of_uids[index+2]:
    #         print(row['Response ID'],list_of_uids[index+2])
    #         survey = ama_new_data.objects.get(response_id = list_of_uids[index+2])
    #         # survey = ama_new_data(Ama_audio_Url=row['Upload Audio'],Ama_response_Url=row['Response link'])
    #         survey.Ama_audio_Url=row['Upload Audio']
    #         survey.Ama_response_Url=row['Response link']

    #         survey.save()

    
    for i in list_of_uids:
        if not df[df['Response ID'] == i]['Response link'].empty:
            print(list(df[df['Response ID'] == i]['Response link'])[0])
            survey = ama_new_data.objects.get(response_id = list(df[df['Response ID'] == i]['Response ID'])[0])
            survey.Ama_audio_Url=list(df[df['Response ID'] == i]['Upload Audio'])[0]
            survey.Ama_response_Url=list(df[df['Response ID'] == i]['Response link'])[0]
            print(i)
            survey.save()

    return HttpResponse('<h1>Ursl Uploaded</h1>')




@require_staff
def employee_upload(request):
      
    ama_users = User.objects.filter(username__startswith = '300',id__gt = 19170).values()
    for i in ama_users:
        print(i)


        employeees = Employee.objects.create(gender='Male',employee_id=i['username'],user_role='user',designation_id=3,user_id = i['id'])
        employeees.save()

    return HttpResponse('<h1>done</h1>')
    # pass