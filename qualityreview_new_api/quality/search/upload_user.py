# from django.contrib.auth.models import User

import mysql.connector

conn = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


mycursor = conn.cursor()

query = ("SELECT max(id) FROM quality.auth_user;")

mycursor.execute(query)

maxid = mycursor.fetchall()[0][0]

query2 = (f"SELECT username FROM quality.auth_user where id = {maxid};")

mycursor.execute(query2)

username = mycursor.fetchall()[0][0]

print(maxid)
print(username)

conn.close()


cnx = mysql.connector.connect(user='root', password='axis@123',
                              host='192.168.1.32',
                              database='surveygeniusdb')


mycursor = cnx.cursor()

query  = (f"SELECT id FROM `auth_user` WHERE `username` = {username}")   


mycursor.execute(query)

myresult = mycursor.fetchall()[0][0]

print(myresult)

query1 = (f"SELECT * FROM `auth_user` WHERE `id` > {myresult} ORDER BY `id` ASC")                  ### select max id from surveygeniusdb from user table and paste in where clause


mycursor.execute(query1)

myresult1 = mycursor.fetchall()

print(myresult1)

# listed = []

# for i in myresult1:
#     listed.append(*i)
#     print(*i)


# print(listed)

# for username in listed:

#     user = User.objects.create(username = username,password = "axis@123")
#     user.save()


cnx.close()



cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality')


mycursor = cnx2.cursor()

query = ("SELECT username FROM auth_user where username <> '300%' ORDER BY `id` ASC")


mycursor.execute(query)

value = mycursor.fetchall()

listed = []

for i in value:
    listed.append(*i)
    # print(*i)
print(listed)

query ="INSERT INTO quality.auth_user (password,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) VALUES (%s, %s, %s,%s,%s, %s, %s,%s,%s)"

for x in myresult1:
    print(x)

    


    val = (x[1],x[3],x[10],x[4],x[5],x[6],x[7],x[8],str(x[9]))

    mycursor.execute(query,val)

    print("ok")
    cnx2.commit()


cnx2.close()



#### for employee upload




cnx = mysql.connector.connect(user='root', password='axis@123',
                              host='192.168.1.32',
                              database='surveygeniusdb')


mycursor = cnx.cursor()

# query ="SELECT * from mainapp_designation"

query =f"SELECT id,gender,employee_id,date_of_birth,address,user_role,designation_id,user_id,location_id,office_location_id from mainapp_employee WHERE `user_id` > {myresult} ORDER BY `id` ASC"     ### select max id from surveygeniusdb from user table and paste in where clause 

# query ="SELECT * from mainapp_language"

# query ="SELECT * from quality_issuelist"




# query = ("SELECT * from mainapp_employee where designation_id <> 203 and id > 4387 and designation_id <> 204 and designation_id <> 206 and designation_id <> 207")


mycursor.execute(query)

myresult = mycursor.fetchall()

print(myresult)



cnx.close()

cnx2 = mysql.connector.connect(user='root', password='axis@123',
                              host='localhost',
                              database='quality',auth_plugin='mysql_native_password')


mycursor = cnx2.cursor()

query = (f"SELECT id FROM auth_user where username <> '300%' and id > {maxid} ORDER BY `id` ASC")     ### select last id from quality auth user

mycursor.execute(query)

value = mycursor.fetchall()

listed = []



for i in value:
    listed.append(*i)
    # print(*i)
print(listed)
# query = "INSERT INTO search_location (id,state_id,name) values(%s,%s,%s)"

# query = "INSERT INTO search_department (id,name,hod) values(%s,%s,%s)"

# query = "INSERT INTO search_designation (id,name,layer_id,department_id) values(%s,%s,%s,%s)"

# query = "INSERT INTO search_employee (id,gender,employee_id,date_of_birth,address,user_role,designation_id,user_id,location_id,office_location_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


# query = "INSERT INTO search_verificationstatus (id,name) values(%s,%s)"


# query = "INSERT INTO search_issuelist (id,issue_id,section,issues,related_question) values(%s,%s,%s,%s,%s)"



# query = "INSERT INTO search_state (id,name) values(%s,%s)"



query ="INSERT INTO search_employee (gender,employee_id,date_of_birth,address,user_role,designation_id,user_id,office_location_id) VALUES ( %s, %s,%s, %s, %s,%s, %s, %s)"

for index,x in enumerate(myresult):
    print(x)

    # if x[0] == 1:
    #     continue

    
    # val = (x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9])

    # val = (x[0],x[1],x[2],x[3],x[4])

    val = (x[1],x[2],x[3],x[4],x[5],3,listed[index],x[9])

    mycursor.execute(query,val)

    print("ok")
    cnx2.commit()


cnx2.close()




