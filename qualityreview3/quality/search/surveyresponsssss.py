from search.models import *

from django.http import HttpResponse

from datetime import datetime
import pytz
from dateutil import parser

import json
import mysql.connector

def pope(request):

    # for i in range(2812,):
    #     print(i)
















    #     x = SurveyResponse.objects.filter(id__gt=2811).values().order_by('id')p
    #     print(x)
    #     for a in x:
    #         obj = SurveyResponse.objects.get(pk=a["id"])
    #         obj.id = i
    #         obj.save()
            
            
    #         obj.save()
    #         if a["id"] == 4257:
    #                break
        
            
                
                   
              
    


    # x = duplicateSurveyResponse.objects.all()
    # x.delete()

     # x = SurveyResponse.objects.filter(allocated_survey__isnull = True)
    # x.delete()

    print("initaia")

    cnx = mysql.connector.connect(user='root', password='axis@123',
                                host='localhost',
                                database='quality')


    mycursor = cnx.cursor()

    query = ("select distinct id1 from quality.search_a_app_data where id1 > 13060")            ### here change id (neeche 2 bar aur)


    mycursor.execute(query)

    myresult = mycursor.fetchall()

    myresult2 = []

    for i in myresult:
        myresult2.append(*i)
        
    # print(myresult2)



    responsesdict = {}



    for key in myresult2:
        print(key)

        sql  = "select * from quality.search_a_app_data where id1 = %s and id1 > 13060"       ### here change id


        adr = (key, )

        mycursor.execute(sql, adr)

        myresult = mycursor.fetchall()

        # print(myresult)


        responsesdict[key] = {
                        'surveyor': None,
                        'date': None,
                        'time': None,
                        'id1': key,
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
                        'otpstatus': False,
                        'audiourls': [],
                        'audioanswers': None,
                        'actualaddress': None,
                        'tldetails': None,
                        'vflag': ""
            }


        ###end datetime
        end_datetime = myresult[0][-2]

        date_object = parser.isoparse(end_datetime)
 
        # Convert to Asia/Kolkata timezone
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        date_object_kolkata = date_object.astimezone(kolkata_tz)
        
        # Format time as desired
        time_string = date_object_kolkata.strftime('%H:%M:%S')
        
        # Format date as desired
        date_string_kolkata = date_object_kolkata.strftime('%d-%b-%Y')
        ###end datetime



        responsesdict[key]["surveyor"] = myresult[0][3]

        print(responsesdict[key]["surveyor"])

        responsesdict[key]["date"] = date_string_kolkata

        print(responsesdict[key]["date"])

        responsesdict[key]["time"] = time_string
        print(responsesdict[key]["date"])

        responsesdict[key]["startlat"] = myresult[0][12]

        print(responsesdict[key]["startlat"])

        responsesdict[key]["endlat"] = myresult[0][13]

        print(responsesdict[key]["endlat"])


        responsesdict[key]["audiourls"] = myresult[0][14]

        print(responsesdict[key]["audiourls"])


        responsesdict[key]["actualaddress"] = myresult[0][11]

        print(responsesdict[key]["actualaddress"])


        project = myresult[0][1]

        try:

            sql  = "select Response from quality.search_a_app_data where id1 = %s and question_title like '%FR NAME%' and id1 > 13060"        ### here change id

            adr = (key, )

            mycursor.execute(sql, adr)

            responses = mycursor.fetchall()

        except Exception as e:
             print(e)
             responses = None

        # print(responses)

        if responses:
            for response in responses:
                responsesdict[key]["tldetails"] = response[0]
        else:
            responsesdict[key]["tldetails"] = None


        for i in myresult:
            if i[7].startswith == "VILLAGE":

                responsesdict[key]["village"] = myresult[0][8]

            else:
                responsesdict[key]["village"] = None

        

        
        # print(project)


        # print(responsesdict)


            #print() 'Pre populate %s %s' % (key, Project.objects.get(pk=project).name)
        populateSurveyResponse(key, responsesdict, project)
    cnx.close()

    return HttpResponse('done')



def populateSurveyResponse(id1, responsesdict, project):
    # Populate remarks
    responseparamdict = {}

    responseparamdict['id1'] = id1

    responseparamdict['surveyor'] = responsesdict[id1]['surveyor']

    # print(responsesdict[id1]['surveyor'])


    # length = len(responseparamdict['surveyor'])

    ind = (responseparamdict['surveyor']).find("(")
    responseparamdict['surveyor'] = (responseparamdict['surveyor'])[ind+1:]

    if len(responseparamdict['surveyor']) == 7 and responsesdict[id1]['surveyor'] != "Prateek":
        responseparamdict['surveyor'] = responsesdict[id1]['surveyor']

        length = len(responseparamdict['surveyor'])

        ind = (responseparamdict['surveyor']).find("(")
        responseparamdict['surveyor'] = (responseparamdict['surveyor'])[ind+1:length-1]

        print('surveyors',responseparamdict['surveyor'])


    # if SurveyResponse.objects.filter(id1=id1,project=Project.objects.get(capi_checklist_id=project)).count() == 0:
    #     if responsesdict[id1]['village_distance'] == None:
    #         responsesdict[id1]['village_distance'] = 'GPS issue'
    #     if responsesdict[id1]['movement'] == None:
    #         responsesdict[id1]['movement'] = 'GPS issue'

        if not str(responseparamdict['surveyor']).startswith('300'):
   
            if responsesdict[id1]['audiourls'] == []:
                        SurveyResponse.objects.create(
                            uid=id1,
                            project=Project.objects.get(capi_checklist_id=project),
                            verification_status=VerificationStatus.objects.get(name='No Recordings'),
                            params=json.dumps(responsesdict[id1]),
                            remarks=json.dumps(responseparamdict),
                            surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor']),
                            otp_verified = True
                            )
                        
                        
            # elif responsesdict[id1]['actualaddress'] != None:                         ####comment by me
            #             SurveyResponse.objects.create(
            #                 uid=id1,
            #                 project=Project.objects.get(capi_checklist_id=project),
            #                 verification_status=VerificationStatus.objects.get(name='To Be Verified'),
            #                 params=json.dumps(responsesdict[id1]),
            #                 remarks=json.dumps(responseparamdict),
            #                 surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor']),
            #                 otp_verified = True
            #                 )
                        
            else:
                        # responsesdict[id1]['actualaddress'] = 'GPS issue'        #### comment by me
                        SurveyResponse.objects.create(
                            uid=id1,
                            project=Project.objects.get(capi_checklist_id=project),
                            verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                            params=json.dumps(responsesdict[id1]),
                            remarks=json.dumps(responseparamdict),
                            surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor']),
                            otp_verified = True
                            )
                        
                        

            print('%s -> %s (populate)' % (id1, Project.objects.get(capi_checklist_id=project).name))

        else:
            raise TypeError("username startwith 30000")
        # else:
        #         try:
        #             SurveyResponse.objects.create(
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
        #             pass


def deleted_data(request):



    entries = SurveyResponse.objects.filter(id__gt=7606)
    entries.delete()    
    
    html = "<html><body>It is now done</body></html>"
    return HttpResponse(html)
            
            