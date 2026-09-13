
import psycopg2
# from geopy.distance import geodesic
import pandas as pd
import datetime

import math

import mysql.connector


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
            "choices"."respondent_answered_choices"."audio_recording", "choices"."respondent_answered_choices"."createdAt" as "endTime", "choices"."respondent_answered_choices"."start_at" as "starttime" FROM "choices"."respondent_answered_choices" 
            INNER JOIN choices.respondent_answers on "choices"."respondent_answered_choices"."id" = choices.respondent_answers.respondent_answered_choice_id  
            INNER JOIN choices.choices on "choices"."respondent_answered_choices"."choice_id" = choices.choices.id  
            INNER JOIN choices.surveyors on choices.surveyors.id = "choices"."respondent_answered_choices"."surveyor_id" 
            where "choices"."id" in (321,382,347,325,335,332,344,320,319,342,339,348,330,352,350,326,290,291) and "choices"."respondent_answered_choices"."id" >  {max_id} order by "choices"."respondent_answered_choices".id ASC""")
    

    data = cursor.fetchall()                                  ##### ACCESSING DATA FROM GCP
        
        # print(data)

    cursor.close()


    ##### inserting data in a_app_data table ####




    if len(data) != 0:
        cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


        mycursor = cnx2.cursor()

        query ="INSERT INTO `search_a_app_data` (choice_id,id1,surveyor_name,surveyor_id,Respondent_Name,question_name,question_title,Response,mobile_no,survey_Name,area,lat,lon,audio_recording,end_time,starttime) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"

        for i in data:

            val = (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14],i[15])

            mycursor.execute(query,val)

            print(i[0],">>>>>>",i[1])

            print("ok")
            cnx2.commit()
            

    else:

        print('no data')
                
    cnx2.close()


except Exception as e:
    print(f"Error: {str(e)}")



