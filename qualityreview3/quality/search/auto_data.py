
import psycopg2
# from geopy.distance import geodesic
import pandas as pd
import datetime

import math

import mysql.connector

from search.models import *

from django.http import HttpResponse

import json

from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Populate Survey Responses'

    def handle(self, *args, **kwargs):
        print("Starting the population process...")


        cnx2 = mysql.connector.connect(user='root', password='axis@123',
                                    host='localhost',
                                    database='quality',auth_plugin='mysql_native_password')


        mycursor = cnx2.cursor()

        query = ("select max(id1) from quality.search_a_app_data;")     ### select last id from quality auth user

        mycursor.execute(query)

        max_id = mycursor.fetchone()[0]
        print(max_id)

        cnx2.close()


        ### connection of gcp ####

        database = "axismyindia"
        user =  "amiproduser"
        password = "Amiproduser@321"
        host = "localhost" 
        port = "5432"       

        connection = None

        try:

            connection = psycopg2.connect(
                dbname=database,
                user=user,
                password=password,
                host=host, 
                port=port
            )
            
            cursor = connection.cursor()
            cursor.execute(f"""SELECT "choices"."respondent_answered_choices"."choice_id", "choices"."respondent_answered_choices"."id" AS "id1", 
                    "choices"."surveyors"."name" AS "Surveyor_Name", "choices"."respondent_answered_choices"."surveyor_id", 
                    "choices"."respondent_answered_choices"."name" AS "Respondent_Name", 
                    "choices"."respondent_answers"."question_name", "choices"."respondent_answers"."question_title", 
                    "choices"."respondent_answers"."answer_display_value_string" AS "Response", "choices"."surveyors"."mobile_no", "choices"."choices"."name" AS "Survey_Name", 
                    "choices"."respondent_answered_choices"."area", "choices"."respondent_answered_choices"."lat", "choices"."respondent_answered_choices"."lon", 
                    "choices"."respondent_answered_choices"."audio_recording", "choices"."respondent_answered_choices"."createdAt" as "Time" FROM "choices"."respondent_answered_choices" 
                    INNER JOIN choices.respondent_answers on "choices"."respondent_answered_choices"."id" = choices.respondent_answers.respondent_answered_choice_id  
                    INNER JOIN choices.choices on "choices"."respondent_answered_choices"."choice_id" = choices.choices.id  
                    INNER JOIN choices.surveyors on choices.surveyors.id = "choices"."respondent_answered_choices"."surveyor_id" 
                    where ("choices"."name" LIKE '%CTI TAMIL BRAND SECTION%' OR "choices"."name" LIKE '%CTI HINDI BRAND SECTION%' OR "choices"."name" LIKE '%CTI TELUGU BRAND SECTION%')
                    and "choices"."respondent_answered_choices"."id" > {max_id} order by "choices"."respondent_answered_choices".id ASC""")
            

            data = cursor.fetchall()                                  ##### ACCESSING DATA FROM GCP
                
                # print(data)

            cursor.close()


            ##### inserting data in a_app_data table ####




            if len(data) != 0:
                cnx2 = mysql.connector.connect(user='root', password='axis@123',
                                    host='localhost',
                                    database='quality')


                mycursor = cnx2.cursor()

                query ="INSERT INTO `search_a_app_data` (choice_id,id1,surveyor_name,surveyor_id,Respondent_Name,question_name,question_title,Response,mobile_no,survey_Name,area,lat,lon,audio_recording,date_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"

                for i in data:

                    val = (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14])

                    mycursor.execute(query,val)

                    print(i[0],">>>>>>",i[1])

                    print("ok")
                    cnx2.commit()
                    

            else:

                print('no data')
                        
            cnx2.close()


        except Exception as e:
            print(f"Error: {str(e)}")



    ##### from surveyresponssssssss


        print("initaia")

        cnx = mysql.connector.connect(user='root', password='axis@123',
                                    host='localhost',
                                    database='quality')


        mycursor = cnx.cursor()

        query = ("select distinct id1 from quality.search_a_app_data where id1 > 9889")            ### here change id (neeche 2 bar aur)


        mycursor.execute(query)

        myresult = mycursor.fetchall()

        myresult2 = []

        for i in myresult:
            myresult2.append(*i)
            
        # print(myresult2)



        responsesdict = {}



        for key in myresult2:
            print(key)

            sql  = "select * from quality.search_a_app_data where id1 >= %s and id1 > 9889"       ### here change id


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





            responsesdict[key]["surveyor"] = myresult[0][3]

            print(responsesdict[key]["surveyor"])

            responsesdict[key]["date"] = myresult[0][-2]

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

                sql  = "select Response from quality.search_a_app_data where id1 >= %s and question_title like '%FR NAME%' and id1 > 9889"        ### here change id

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


