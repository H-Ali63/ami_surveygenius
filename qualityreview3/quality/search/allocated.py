import mysql.connector

import itertools


cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


mycursor = cnx2.cursor()

survey = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

survey_cycle = itertools.cycle(survey)


query ="select uid from quality.search_surveyresponse where allocated_survey IS NULL"

mycursor.execute(query)

mylist = mycursor.fetchall()

value = list()

for i in mylist:
    value.append(*i)

print(value)


for uid in value:
    survey = next(survey_cycle)

    query = f"update quality.search_surveyresponse set allocated_survey = {survey} where uid = {uid} and allocated_survey IS NULL"

    mycursor.execute(query)

    cnx2.commit()


# emps = (101745,101855,101935,101940,102326,102327,102411,102414,104244,104480,104481,104892,106712,109032,109033,109034)


# for i in emps:
    
#     query ="INSERT INTO quality.search_employee (allocated_survey) values() where employee_id = %s"