import pandas as pd

import math

import mysql.connector


df = pd.read_csv("C:/venv/qualityreview3/13-12/Cti_Hindi_13_12_7pm.csv")                ###### replace with filename

# df.fillna("null")

listed = list(df.values.tolist())

# print(listed)




cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


mycursor = cnx2.cursor()

query ="INSERT INTO `search_a_app_data` (id,choice_id,id1,surveyor_name,surveyor_id,Respondent_Name,question_name,question_title,Response,mobile_no,Survey_Name,area,lat,lon,audio_recording,Date_Time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"


for i in listed:


    if pd.isna(i[8]) == "True":

        i[8] == "null"

    val = (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14],i[15])

    mycursor.execute(query,val)

    # print(i[0])

    # print("ok")
    cnx2.commit()

   


cnx2.close()



# for index, row in df[0:3].iterrows():

# # each row is returned as a pandas series

#     print(row["id"])


