import pandas as pd

import mysql.connector

df = pd.read_csv("C:/venv/qualityreview3/19_09/book.csv")

id1_list = df.Survey_Name.tolist()

choiceid_list1 = df.choice_id.tolist()

choiceid_list = []

for i in choiceid_list1:
    if i not in choiceid_list:
        choiceid_list.append(i)

id1 = []

for i in id1_list:
    if i not in id1:
        id1.append(i)

new_list = [id1,choiceid_list]

print(new_list)



# cnx2 = mysql.connector.connect(user='root', password='axis@123',
#                               host='localhost',
#                               database='quality')


# mycursor = cnx2.cursor()

# query ="INSERT INTO `search_a_app_data` (id,choice_id,id1,surveyor_name,surveyor_id,Respondent_Name,question_name,question_title,Response,mobile_no,Survey_Name,area,lat,lon,audio_recording,Date_Time) values (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, )"


# for i in range (len(new_list[0])):

#     val = (i+1,new_list[0][i],new_list[1][i],1,100,0,1,23,4)

#     mycursor.execute(query,val)

#     print("ok")
#     cnx2.commit()


# cnx2.close()


cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


mycursor = cnx2.cursor()

query ="INSERT INTO search_project (name,capi_checklist_id,active,verification_percent,verification_percent_backcheck,pull_data,language_id,state_id) values (%s, %s, %s, %s, %s, %s, %s, %s)"


for i in range (len(new_list[0])):

    val = (new_list[0][i],new_list[1][i],1,100,0,1,23,4)

    mycursor.execute(query,val)

    print("ok")
    cnx2.commit()


cnx2.close()
        

# # responsesdict= {}

# # for val in id1:

# #     responsesdict[val] = {
# #                     'surveyor': None,
# #                     'date': None,
# #                     'time': None,
# #                     'id1': val,
# #                     'village': None,
# #                     'village_latitude': None,
# #                     'village_longitude': None,
# #                     'startlat': None,
# #                     'endlat': None,
# #                     'startlong': None,
# #                     'endlong': None,
# #                     'movement': None,
# #                     'village_distance': None,
# #                     'timedifference': None,
# #                     'otpstatus': None,
# #                     'audiourls': None,
# #                     'audioanswers': None,
# #                     'actualaddress': None,
# #                     'tldetails': None,
# #                     'vflag': ""
# #                 }
    

# # print(responsesdict)