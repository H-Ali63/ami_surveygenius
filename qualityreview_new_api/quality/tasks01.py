# from django.http import HttpResponse
import django
import os
from django.conf import settings
# import sys
# sys.path.append('/path/to/your/project')
# # Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality.settings')  # Replace 'quality' with your project name
django.setup()

import paramiko ### for storing in 251
# from quality.utils import refresh_api_key
from quality.utils2 import refresh_api_key

import requests
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import time
import mysql.connector
import MySQLdb
from logging.handlers import RotatingFileHandler
# import os
from urllib.parse import urlparse
from django.conf import settings                ## for audio part
from search.models import Project,SurveyResponse,VerificationStatus,Employee,A_app_surveyors
import json
import mysql.connector
import Levenshtein
from search.models import AccessToken

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Create a file handler
handler = RotatingFileHandler('logs.log', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


#Configure logger for maps.log
debug_logger = logging.getLogger('debug_logger')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler('maps.log')
debug_handler.setFormatter(formatter) # Using the same formatter
debug_logger.addHandler(debug_handler)


### connection with 251
host = "192.168.1.251"
username = "root"
password = "axis@123"


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

sftp = ssh.open_sftp()
print('connect')


def is_match_80_percent(string1, string2):
    # Calculate Levenshtein distance
    distance = Levenshtein.distance(string1, string2)
    # Calculate maximum possible length (longer string)
    max_len = max(len(string1), len(string2))
    # Calculate similarity percentage
    similarity = 1 - (distance / max_len)
    return similarity >= 0.8, similarity

## FUNCTION FOR DATA APPEND IN DATABASE ###
def emp_user_data_append():

    try:

        conn = mysql.connector.connect(user='root', password='axis@123',
                                    host='localhost',
                                    database='quality')


        mycursor = conn.cursor()

        query = ("SELECT max(id) FROM quality.auth_user where username NOT LIKE '3000%';")

        mycursor.execute(query)

        maxid = mycursor.fetchall()[0][0]

        query2 = (f"SELECT username FROM quality.auth_user where id = {maxid};")

        mycursor.execute(query2)

        username = mycursor.fetchall()[0][0]

        print(maxid)
        # print(username)

        conn.close()


        cnx = mysql.connector.connect(user='root', password='axis@123',
                                    host='192.168.1.32',
                                    database='surveygeniusdb')


        mycursor = cnx.cursor()

        query  = (f"SELECT id FROM `auth_user` WHERE `username` = {username}")   


        mycursor.execute(query)

        myresult = mycursor.fetchall()[0][0]

        # print(myresult)

        query1 = (f"SELECT * FROM `auth_user` WHERE `id` > {myresult} ORDER BY `id` ASC")                  ### select max id from surveygeniusdb from user table and paste in where clause


        mycursor.execute(query1)

        myresult1 = mycursor.fetchall()

        # print(myresult1)

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
        # print(listed)

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

        # print(myresult)



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
    except Exception as e:
        print(f'error in data append {e}')







def listofuids(capi_checklist_id):                                   ### get dictionary surveyor with uids
        """
        Fetches surveyor response IDs for a given capi_checklist_id, excluding UIDs already in the database.
        If no date range is provided, defaults to yesterday and today.

        Args:
            capi_checklist_id (int): Checklist ID to fetch responses for.
            start_date (str): Start date in "YYYY-MM-DD" format. Defaults to yesterday.
            end_date (str): End date in "YYYY-MM-DD" format. Defaults to today.
            max_retries (int): Maximum number of retry attempts.

        Returns:
            defaultdict: A dictionary with surveyor IDs as keys and response IDs as values.
        """

        # start_date='2025-01-16'
        # end_date='2025-01-16'

        # if not start_date or not end_date:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        logger.info(f"Fetching data for date range: {start_date} to {end_date}")

        token = AccessToken.get_existing_token().token
       
        headers = {"Authorization":token,"accept":"application/json","locale":"en"}

        dict_surveyorid_uid = defaultdict(list)

        # def iterate_default_dict(d: defaultdict)->None:
        #     for key, values in d.items():
        #         yield key, values

        # for projectid in projects_list:
        #         print(projectid['choiceId'])
            
            # print(project)
        base_url = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/surveyor-responses/{capi_checklist_id}"

        # Fetch UIDs already in the database
        existing_uids = get_existing_uids_from_db(capi_checklist_id)
        # print(list(existing_uids))
        page = 1
        page_size = 1000

        while True:
            print(page,">>")
            url = f"{base_url}?page={page}&size={page_size}&startDate={start_date}&endDate={end_date}"
            success = False
            attempt = 0
            delay = 2
            while attempt < 2:  # Retry logic for each page
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 401:
                        refresh_api_key()
                        listofuids(capi_checklist_id)
                    response.raise_for_status()  # Raise HTTPError for bad responses




                    
                    data = response.json().get('data', {})
                    responses = data.get('responses', [])
                    # Add responses to the dictionary if UID is not in the database
                    if responses!=[]:
                        for resp in responses:
                            print(resp['responseId'],"responseid")
                            if str(resp['responseId']) not in list(existing_uids):
                               print(resp['responseId'],"in")
                               dict_surveyorid_uid[capi_checklist_id].append(resp['responseId'])

                        success = True
                        logger.info(f"Fetched page {page} successfully with {len(responses)} responses .")

                    # Check if there are more pages
                        # if data.get('hasNext', False):  # Assuming `hasNext` indicates more pages
                        page += 1
                        # else:
                    break
                
                except requests.exceptions.RequestException as e:
                    attempt += 1
                    delay *= 2  # exponential backoff
                    logger.warning(f"Error fetching page {page} for capi_checklist_id {capi_checklist_id} (attempt {attempt}): {e}")
                    time.sleep(delay)  #Exponential backoff
                except KeyError as e:
                    logger.error(f"Key error while parsing response for capi_checklist_id {capi_checklist_id}, page {page}: {e}")
                    break  # Exit retry loop on unrecoverable error

            if not success:
                logger.error(f"Failed to fetch page {page} for capi_checklist_id {capi_checklist_id} after 3 attempts.")
                break  # Exit loop on repeated failure
        print(dict_surveyorid_uid)
        return dict_surveyorid_uid  # Return collected data even if some pages failed

        # r2 = requests.get(url2,headers=headers)
        # print(r2.json)

        # try:
        #     responses = r2.json()['data']['responses']
        # except Exception as e:
        #     responses = None
        # print(responses)

        # if responses !=None:
        #     for i in range (len(responses)):
            
        #         dict_surveyorid_uid[capi_checklist_id].append(responses[i]['responseId'])

        # # print(dict_surveyorid_uid)
        # return dict_surveyorid_uid



def get_existing_uids_from_db(capi_checklist_id):
    """
    Fetch existing UIDs from the `surveyresponse` table in the `quality` database.

    Returns:
        set: A set of UIDs already present in the database.
        
    """
    existing_uids = []
    try:
        existing_uids =  SurveyResponse.objects.filter(project__capi_checklist_id = capi_checklist_id).values_list("uid",flat= True)
        # logger.info(f"Fetched {len(existing_uids)} existing UIDs from the database.")
    except Exception as e:
        logger.warning(f"Data not fetched, connection error to database {e}")
    return existing_uids

    # mydb  = mysql.connector.connect(
    #         host="localhost",
    #         user="root",
    #         password="axis@123",
    #         database="quality"
    # )

    # mycursor = mydb.cursor()

    # existing_uids = set()
    # try:
    #     query = f"SELECT uid FROM quality.search_surveyresponse where project_id = {capi_checklist_id}"

        
    #     mycursor.execute(query)
    #     rows = mycursor.fetchall()
    #     existing_uids = {row[0] for row in rows}

    #     logger.info(f"Fetched {len(existing_uids)} existing UIDs from the database.")
    # except Exception as e:
    #     logger.warning(f"Data not fetched, connection error to database {e}")
    # return existing_uids




def getsurveyorname(surveyor_id):
    """
    Fetches a dictionary of survey IDs mapped to their respective surveyor IDs, with error handling and dynamic dates.
 
    Args:
        start_date (str): Start date in "YYYY-MM-DD" format. Defaults to yesterday.
        end_date (str): End date in "YYYY-MM-DD" format. Defaults to today.
 
    Returns:
        defaultdict: A dictionary with survey IDs as keys and lists of surveyor IDs as values.
    """
    
    token = AccessToken.get_existing_token().token
       
    headers = {"Authorization":token,"accept":"application/json","locale":"en"}

    # dict_of_surveyors_with_surveyid = defaultdict(list)

    db = MySQLdb.connect("192.168.1.251","root","axis@123","AXISMYINDIA", charset='utf8', use_unicode=True)
    cursor = db.cursor()

    ### updated

    surveyor_data = None

    try:
        surveyor_data = list(A_app_surveyors.objects.filter(a_app_id=surveyor_id).values_list('emp_id__employee_id', flat=True))

        print(surveyor_data,"sg data")

    except Exception as e:
        surveyor_data = None
        print(f"Error in fetching the A_app_surveyor table data: {e}")
        print("data not in table")

    
    page = 1
    sqldata = None
  
    surveyor_employee_id =None
    emp = None
    page_size = 100
    surveyor_found = False      #change

    if surveyor_data:
        try:
            sql = '''SELECT EMP_ID, EMP_NAME FROM EMP_MASTER WHERE EMP_ID="%s"''' % (surveyor_data[0])
            cursor.execute(sql)
            sqldata = cursor.fetchall()
            return sqldata
        except Exception as e:

            print(f"Error for fetching data from 251 emp table: {e}")

    else:
        print('gooooooo')
        
        while not surveyor_found:      #change
                print(page,"page")
                print("ok>>>>>")
                try:
                    surveyors_url = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/surveyor-list?page={page}&size={page_size}"
                    response = requests.get(surveyors_url, headers=headers, timeout=20)
                    if response.status_code == 401:  ###if error get in authentication
                        refresh_api_key()
                        getsurveyorname(surveyor_id)  # Raise HTTPError for bad responses
                        
                    elif response.status_code == 200:
                        surveyor_data = response.json()

                        if 'total' in surveyor_data['data']:
                            total_elements = surveyor_data['data']['total']
                            total_pages = -(-total_elements // page_size)  

                            print("enter",total_pages)
                                
                            # print(surveyor_data)  # Debug the whole response structure
                            if 'data' in surveyor_data and 'list' in surveyor_data['data']:
                                print("okkkk")

                                ### iterating through surveyor list
                                for surveyor in surveyor_data['data']['list']:

                                    surveyor_id_aapp = surveyor.get('id', None)
                                    surveyor_name_aapp = ''
                                    ### if surveyor id matches
                                    if surveyor_id == surveyor_id_aapp:
                                        surveyor_id_aapp = surveyor.get('id', None)
                                        # surveyor_id_aapp = surveyor.get('id', None)
                                        print(surveyor_id_aapp,"surveyorids_aapp")
                                        print(surveyor_id,"surveyor_idsssss")

                                        surveyor_name_aapp = surveyor.get('name', '')
                                        surveyor_mobileno_aapp = surveyor.get('mobileNumber', '')

                                        print(surveyor_name_aapp, ">>>>>")

                                        try:
                                            splitted_id = (surveyor_name_aapp.split("(")[1][0:-1]).strip()
                                            print(splitted_id,"spli")
                                            try:    
                                                emp = Employee.objects.get(employee_id=splitted_id)
                                                try:
                                                    Emp_Value = Employee.objects.filter(employee_id=splitted_id).values_list("employee_id",
                                                                                                        flat=True)
                                                except:
                                                    print("not get empid")
                                                    Emp_Value = []

                                                if Emp_Value != []:
                                                    surveyor_employee_id = splitted_id
                                                else:
                                                    pass

                                                try:
                                                    # print(surveyor_employee_id)
                                                    sql = '''SELECT EMP_ID, EMP_NAME FROM EMP_MASTER WHERE EMP_ID="%s"''' % (
                                                                surveyor_employee_id)
                                                    cursor.execute(sql)
                                                    sqldata = cursor.fetchall()
                                                    print(sqldata,">><<>>sqldata")
                                                except Exception as e:
                                                    print("get2")
                                                    print(f"Error fetching employee id from 251 table for {surveyor_name_aapp}: {e}")
                                            except Exception as e:
                                                print('not empid in employee',e)
                                                emp = None
                                                sqldata = surveyor_name_aapp
                                            if emp is not None:
                                                A_app_surveyors.objects.create(a_app_id=surveyor_id_aapp,
                                                                                surveyor_name=surveyor_name_aapp,
                                                                                mobile_number=surveyor_mobileno_aapp,
                                                                                emp_id=emp)
                                        except (IndexError, AttributeError) as e:
                                            print("indexerror")
                                            sql = '''SELECT EMP_ID, EMP_NAME FROM EMP_MASTER WHERE EMP_MOBILE="%s"''' % (
                                            surveyor_mobileno_aapp)
                                            cursor.execute(sql)
                                            sqldata_result = cursor.fetchall()
                                            print(sqldata_result, ">><<>>sqldatamobi")

                                            if sqldata_result:
                                                result = False
                                                # result, similarity = is_match_80_percent(str(surveyor_name_aapp), str(sqldata_result[0][1]))
                                            else:
                                                result = False
                                            print(result,"resulttttttttt")

                                            if result is True:
                                                try:
                                                    emp = Employee.objects.get(employee_id=sqldata_result[0][0])
                                                except:
                                                    emp = None
                                                if emp is not None:
                                                    A_app_surveyors.objects.create(a_app_id=surveyor_id_aapp,
                                                                                        surveyor_name=surveyor_name_aapp,
                                                                                        mobile_number=surveyor_mobileno_aapp,
                                                                                        emp_id=emp)
                                                print(f'employee id not in {surveyor_name_aapp}')
                                                sqldata = sqldata_result
                                            else:
                                                sqldata = surveyor_name_aapp
                                                print(f"Similarity percentage for {surveyor_name_aapp}: {similarity * 100:.2f}%")

                                        except Exception as e:        # If an error occurs in the except block itself
                                            print(f"An error occurred while handling the employee lookup: {e}")
                                        
                                        surveyor_found = True
                                        break
                                    else:
                                        pass
                                                # logging.warning(f"Error in fetching the id: {surveyor.get('id', 'Unknown')}")
                                            
                            
                                if not surveyor_found:
                                    if page >= total_pages:
                                        print(f"Surveyor ID {surveyor_id} not found.")
                                        break
                                    page += 1          

                        else:
                            print("Total attribute not found in API response")
                    
                    else:
                        print(f"Failed to fetch data. Status code: {response.status_code}")
                        break
                         
                            
                except requests.exceptions.ConnectionError as errc:
                    print(f"Error Connecting: {errc}")
                    break
                        
                except requests.exceptions.Timeout as errt:
                    print(f"Timeout Error: {errt}")
                    break
                        
                except requests.exceptions.RequestException as err:
                    print(f"Something went wrong: {err}")
                    break
                        
                except Exception as e:
                    print(e,"error for this")
                    break
                    

        else:
            print("all pages done")
                

    db.close()
    return sqldata




def fetchdatacron(): #### fetching data herr
    emp_user_data_append()
    try:
        
        # projects fetches from api
        # listofprojects = projects_in_date() 
        # for prj in listofprojects:
        #     #  pass
        #     projects_id_db = Project.objects.values_list('capi_checklist_id',flat = True)
        #     if prj['choiceId'] not in projects_id_db:
        #         Project.objects.create(

        #         )
        #     fetchdata2(Project.objects.get(capi_checklist_id=prj['choiceId']).pk, '', capi_checklist_id) 

        # projects_id_db = Project.objects.filter(active=True).order_by(('-pk')).values_list('capi_checklist_id',flat = True)
        
        for proj in Project.objects.filter(active=True).order_by(('-pk')):
            capi_checklist_id = proj.capi_checklist_id
            
            print(f'fetching data for {capi_checklist_id}')
            print(datetime.now())

            fetchdata2(Project.objects.get(capi_checklist_id=capi_checklist_id).pk, '', capi_checklist_id)
            
            print(f'fetched data for ->>>>> {capi_checklist_id}')


        
    except Exception as e:
        print(e)
        print('%s %s before entering fetch %s' % (Exception, e, Project.objects.get(capi_checklist_id=capi_checklist_id).name))
        pass
    
    finally:
        sftp.close()
        print('closse ssh')
        ssh.close()

def fetchdata2(project, data, capi_checklist_id):
    """
    Fetches and processes survey data for a given project and checklist ID.

    Args:
        project (int): Project ID.
        capi_checklist_id (int): Checklist ID.
    """

    # surveyors = listofsurveyors(project)

    list_of_uids = listofuids(capi_checklist_id)
    print(list_of_uids)
    if not list_of_uids:
        logger.error(f"No UIDs found for capi_checklist_id {capi_checklist_id}. Exiting fetchdata2.")
        return
    
    logger.info(f"Fetched UIDs: {list_of_uids}")

    token = AccessToken.get_existing_token().token
        
    headers = {"Authorization":token,"accept":"application/json","locale":"en"}

    # maxaudios = 0
    responsesdict = {}
    vflag = 0
    # print(data)

    for survey_id, uids in list_of_uids.items():
        for uid in uids:
            print(uid,"uids????")
            url = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/submitted-choice-details/{uid}"

            for attempt in range(3):  # Retry up to 3 times
                print(attempt,">>>")
                try:
                    response = requests.get(url, headers=headers, timeout=10)

                    if response.status_code == 401: ###if error get in authentication
                        refresh_api_key()
                        fetchdata2(project, data, capi_checklist_id)

                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json().get('data', {})
                    logger.info(f"Fetched data for UID {uid}")
                    # Add logic to process and save the data to the database
                    break  # Exit retry loop on success
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Error fetching details for UID {uid} (attempt {attempt + 1}): {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                except KeyError as e:
                    logger.error(f"Key error while parsing response for UID {uid}: {e}")
                    break  # Exit retry loop on unrecoverable error
            else:
                logger.error(f"Failed to fetch details for UID {uid} after 3 attempts.")
            # print(data,"data here")

    # surveyour_url = "https://api.axismyindia.in/v1/admin/surveyors/qc-service/surveyor-list?page=1&size=10"
    # for dict_of_surveys in list_of_uids:
    #     for uid in list_of_uids[dict_of_surveys]:
    #         print(uid)
    #         url2 = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/submitted-choice-details/{uid}"

    #         r2 = requests.get(url2,headers=headers)
    #         # print(r2.json())
            
    #         data = r2.json()['data']
    #         # print(data)

# fetchdata2(12,90)
        

  

            if Project.objects.get(id=project).geocodes_available:
                vflag = 1
            else:
                vflag = 0

            if data['responseId'] in responsesdict.keys():
                pass
            elif SurveyResponse.objects.filter(uid=data['responseId']).count() > 0:
                deleted_flag = False

                if deleted_flag:
        
                    responsesdict[uid] = {
                                'surveyor': None,
                                'date': None,
                                'time': None,
                                'id1': data['responseId'],
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
                                'otpstatus': None,
                                'audiourls': None,
                                'audioanswers': None,
                                'actualaddress': None,
                                'tldetails': None,
                                'vflag': vflag,
                                'registration_details': None
                        }
                else:
                    continue

            else:
                responsesdict[uid] = {
                    'surveyor': None,
                    'date': None,
                    'time': None,
                    'id1': data['responseId'],
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
                    'otpstatus': None,
                    'audiourls': None,
                    'audioanswers': None,
                    'actualaddress': None,
                    'tldetails': None,
                    'vflag': vflag,
                    'registration_details': None
                }
                
                
            ## get survyor
            if responsesdict[uid]['surveyor'] == None:
                print(data['surveyorId'])
                surveyorname = getsurveyorname(data['surveyorId'])
                try:    
                    responsesdict[uid]['surveyor'] = '%s - (%s)' % (surveyorname[0][0], surveyorname[0][1])
                except:
                    responsesdict[uid]['surveyor'] =  surveyorname

                print(responsesdict[uid]['surveyor'],"surveyoridddddddddddd")             

            
            
            if responsesdict[uid]['village'] == None:            #### village
                        for value in data['answers']:
                            # print(value)
                            if (value['title'].strip()).lower() == 'village':
                                
                                print('village done>>>')
                                village = value['displayValue']
                                responsesdict[uid]['village'] = value['displayValue']
                                village, state, lat, lng = extractvillagegeocodes(village)
                                responsesdict[uid]['vflag'] = vflag  
                                break
                            else:
                                responsesdict[uid]['village'] = None

                            
            #             #     #### if villages present


                # Fetch Distance and Movement
            if responsesdict[uid]['village_distance'] == None or responsesdict[uid]['movement'] == None:
                    """code for village_distance need to be written movement code cant be get"""
                    pass
                    
                ## tl details

            if responsesdict[uid]['tldetails'] == None:
                            
                        for value in data['answers']:
                            if (value['title'].strip()).upper() == 'FR NAME':                         #### fr name
                                # print('fr name  >>>')
                                # print(value['value'],"valueeee")
                                responsesdict[uid]['tldetails'] = value['displayValue']
                                # print(responsesdict[uid]['tldetails'],"<><><>")
                                break
                            else:
                                responsesdict[uid]['tldetails'] = None


            if responsesdict[uid]['date'] == None:                   #### date

                    responsesdict = fetchdatetime(responsesdict, data)         
                
            answers_political = []


            ##added responsesdict

            if responsesdict[uid]['registration_details'] == None:
                registration_details_fiels = []
                # for value in data['registration_details']:
                if 'registrationDetails' in data:
                    print('ok')
                    if 'mobileNumber' in  data['registrationDetails']:
                        if data['registrationDetails']['mobileNumber'] == '':
                            registration_details_fiels.append([None,"MOBILE NUMBER"])
                        else:
                            print('adddddddddddddd')
                            registration_details_fiels.append([data['registrationDetails']['mobileNumber'],"MOBILE NUMBER"])
                    if 'dob' in  data['registrationDetails']:
                        if data['registrationDetails']['dob'] == '':
                            registration_details_fiels.append([None,"DOB"])
                        else:
                            registration_details_fiels.append([data['registrationDetails']['dob'],"DOB"])
                    if 'gender' in  data['registrationDetails']:
                        if data['registrationDetails']['gender'] == '':
                            registration_details_fiels.append([None,"GENDER"])
                        else:
                            registration_details_fiels.append([data['registrationDetails']['gender'],"GENDER"])
                    if 'area' in  data['registrationDetails']:
                        if data['registrationDetails']['area'] == '':
                            registration_details_fiels.append([None,"AREA"])
                        else:
                            registration_details_fiels.append([data['registrationDetails']['area'],"AREA"])
                    if 'occupation' in  data['registrationDetails']:
                        if data['registrationDetails']['occupation'] == '':
                            registration_details_fiels.append([None,"OCCUPATION"]) 
                        else:
                            registration_details_fiels.append([data['registrationDetails']['occupation'],"OCCUPATION"])                
                    responsesdict[uid]['registration_details'] =  registration_details_fiels
                else:
                    responsesdict[uid]['registration_details'] = registration_details_fiels                  
                      
            print(responsesdict,"responssssssssseeeeeeeesssssssssdicccct")    



                

            # print(responsesdict,"ressss")
                # Fetch audios
            if responsesdict[uid]['audiourls'] == None:
                    print("audiourls")
                    audiourls = audio_urls(data['responseId'])
                    
                    registration_audio_urls = registration_audio(data['responseId'])
                    # registration_audio = registration_audio(data['responseId'])

                    audiourls_with_frname = [[responsesdict[uid]['tldetails'],audiourls,"FR NAME"]]

                
                    if registration_audio_urls != None:
                        audiourls_with_frname.append(['Registration',registration_audio_urls,"USER"])
                    
                    print(audiourls,"aaaaa")
                    responsesdict[uid]['audiourls'] = audiourls_with_frname
                    try:
                    ## fetch audio answers 
                        for response in data['answers']:
                            # print(response,"responseses")
                            # print("file")
                            if "isImportant" in response.keys():
                                if response['isImportant'] == True:
                                    print('ansssweeeeee')
                                    print(response)

                                    if response['displayValue'] != None:

                                        try:
                                            data = response['displayValue']
                                            type_result = isinstance(data, dict)
                                        except:
                                            type_result = False

                                        if type_result:
                                            try:
                                                for key, value in data.items():

                                                    try:
                                                        answers_political.append([f"{key.encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape')} : {value.encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape')}", response["title"].encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape')])
                                                    except:
                                                            
                                                        answers_political.append([f"{key} : {value}" , response["title"]])
                                            except Exception as e:
                                                print(e,"error")
                                                answers_political = []

                                        # elif "," in response['displayValue']:### do here
                                        #     try:
                                        #         for value in response['displayValue'].split(","):
                                        #             try:
                                        #                 answers_political.append([value.encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape'),response["title"].encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape')])
                                        #             except:
                                        #                 answers_political.append([value, response["title"]])

                                        #     except Exception as e:
                                        #         print(e,"eeee")
                                            # print(answers_political,"polittical")

                                        else:
                                            
                                            try:
                                                answers_political.append([response["displayValue"].encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape'),response["title"].encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape')])
                                            except:
                                                answers_political.append([response["displayValue"], response["title"]])
                                            print(answers_political,"polittical")
                                    else:
                                        try:
                                            answers_political.append([response["displayValue"].encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape'),response["title"].encode('raw-unicode-escape').decode('utf-8').encode("utf-8").decode('unicode-escape')])
                                        except:
                                            answers_political.append([response["displayValue"], response["title"]])
                                            print(answers_political,"polittical")

                                else:
                                    pass
                            
                            else:
                                pass
                                # print("no audio answers")
                            # print("accesss")
                            # print(responsesdict[uid])
                            
                        audioanswers = answers_political
                    except Exception as e:
                        audioanswers = []
                    # print(audioanswers,"audioanserrr")

                    responsesdict[uid]['audioanswers'] = audioanswers


        for key in responsesdict.keys():
            print('Pre populate %s %s' % (key, Project.objects.get(pk=project).name))
                    
            populateSurveyResponse(key, responsesdict, data, project)

          



def fetchdatetime(responsesdict, d):
    ''' fetching date and time  ARGS: responsesdict dictionary where appned data
    d: data from api call'''
    

    starttime = None
    endtime = None
    actualaddress = None

    

        # Display Date
    # print(d['startTime'])
    date_object = datetime.strptime(d['startTime'], '%Y-%m-%d %H:%M:%S')

    responsesdict[d['responseId']]['date'] = date_object.strftime('%d-%b-%Y')

    # print(responsesdict[d['responseId']]['date'])

    
    starttime = d['startTime']
    actualaddress = extractlocation(d['lat'],d['lon'])
        
    endtime = d['endTime']

    if endtime is None or starttime is None:
        timedifference = '-'
    else:
        endtime_dt = datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
        starttime_dt = datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')

        timedifference = (endtime_dt - starttime_dt).seconds
    # print(timedifference)
    # responsesdict[d[3]]['date'] = devicedate

    if starttime != None:
        responsesdict[d['responseId']]['meta'] = {'datetime': 1}
        start_time = datetime.strptime(d['startTime'], '%Y-%m-%d %H:%M:%S')
        responsesdict[d['responseId']]['time'] = start_time.strftime('%H:%M:%S')
        # print(start_time.strftime('%H:%M:%S'))
    else:
        responsesdict[d['responseId']]['meta'] = {'datetime': 0}
        # responsesdict[d[3]]['time'] = starttime
        start_time = datetime.strptime(d['startTime'], '%Y-%m-%d %H:%M:%S')
        responsesdict[d['responseId']]['time'] = start_time.strftime('%H:%M:%S')
        # print(start_time.strftime('%H:%M:%S'))

        if responsesdict[d['responseId']]['date'] == None:
            responsesdict[d['responseId']]['date'] = start_time.strftime('%d-%b-%Y')
            # print(start_time.strftime('%d-%b-%Y'))

    responsesdict[d['responseId']]["startlat"] = float(d['lat'])
    responsesdict[d['responseId']]['startlong'] = float(d['lon'])
    responsesdict[d['responseId']]['timedifference'] = '%s seconds' % (timedifference)
    responsesdict[d['responseId']]['actualaddress'] = actualaddress

    # print(responsesdict)
    return responsesdict
                    
            

###for fetching address            
def extractlocation(lat,long):
    try:
            key = "AIzaSyBdsOVmHPsbuqF2GWC-fcCW_Nlw_0TJVeo"
            # key = "AIzaSyB_ZIG03KZ6Uj9o4ROuhIoK7NqR-SuuUJg"
            # key = "AIzaSyB-drA36Kmgr6fTzu0z8g28Sod5ZbwpJiY"
            # key = "AIzaSyDXvfMPhjz1LnaKVKoIuyfHjoMIhysfxjo"
            base = "https://maps.googleapis.com/maps/api/geocode/json?"
            # state = "Maharashtra"
            # address = village+', '+state
            params = "latlng={lat},{long}&key={key}".format(lat=lat,long=long,key=key)
            url = "{base}{params}".format(base=base, params=params)
            response = requests.get(url)
            geocodes = response.json()['results'][0]['formatted_address']
            debug_logger.debug("extralocation access ---->>>>")
            return geocodes
    except Exception as e:
        return None
###for fetching address    

    # print(responsesdict)
# pope()

def extractvillagegeocodes(village):
    # try:
    #     base = "https://apis.mapmyindia.com/advancedmaps/v1/ztgf2xai9pexed26o3kev3zb6cfs8bjk/geo_code?"
    #     state = Project.objects.get(id=project).state.name
    #     address = village+', '+state
    #     params = "addr={address}".format(
    #         address=address
    #     )
    #
    #     url = "{base}{params}".format(base=base, params=params)
    #     response = requests.get(url)
    #     geocodes = response.json()['results'][0]
    #
    #     lat = geocodes['lat']
    #     lng = geocodes['lng']
    #
    #     return village, state, lat, lng
    # except Exception as e:
    #     #print 'Key exhausted', e
    #     return village, None, None, None
        try:
            key = "AIzaSyBdsOVmHPsbuqF2GWC-fcCW_Nlw_0TJVeo"
            # key = "AIzaSyB_ZIG03KZ6Uj9o4ROuhIoK7NqR-SuuUJg"
            # key = "AIzaSyB-drA36Kmgr6fTzu0z8g28Sod5ZbwpJiY"
            # key = "AIzaSyDXvfMPhjz1LnaKVKoIuyfHjoMIhysfxjo"
            base = "https://maps.googleapis.com/maps/api/geocode/json?"
            state = "Maharashtra"
            address = village+', '+state
            params = "address={address}&sensor={sen}&key={key}".format(
                address=address,
                sen='false',
                key=key
            )
            url = "{base}{params}".format(base=base, params=params)
            response = requests.get(url)
            geocodes = response.json()['results'][0]['geometry']['location']
            lat = geocodes['lat']
            lng = geocodes['lng']

            debug_logger.debug("extravillagegeocodes access ---->>>>")

            return village, state, lat, lng
        except Exception as e:
            return village, state, None, None


def projects_in_date():                                 ###### list of projects of that particular date range
        
        token = AccessToken.get_existing_token().token

       
        headers = {"Authorization":token,"accept":"application/json","locale":"en"}

        url2 = "https://api.axismyindia.in/v1/admin/surveyors/qc-service/surveys?page=1&limit=10&startDate=2024-12-12&endDate=2024-12-27"

        try:
            response = requests.get(url2,headers=headers)

            if response.status_code == 401: ###if error get in authentication
                refresh_api_key()
                projects_in_date()
            # print(r2.json())

            Projects = response.json()['data']['list']
        
        except Exception as e:
            print(f"error in fetching project error : {e}")
        # print(Projects)
        return Projects

# print(projects_in_date())


# def listofsurveyors():                                   ### get dictionary of surveyorids with projects

#         projects_list = projects_in_date()
#         # print(projects_list)

#         token = AccessToken.get_existing_token().token
       
#         headers = {"Authorization":token,"accept":"application/json","locale":"en"}

#         dict_of_surveyors_with_surveyid = defaultdict(list)

#         for project in projects_list:

#             # print(project)
#             url2 = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-qc-dashboard?surveyId={project['choiceId']}&startDate=2024-01-12&endDate=2024-12-27"

#             r2 = requests.get(url2,headers=headers)
#             # print(r2.json())

#             choice_id = r2.json()['data']['choiceId']

#             surveyor = r2.json()['data']['surveyors'][0]['surveyorId']

#             dict_of_surveyors_with_surveyid[choice_id].append(surveyor)

#         return dict_of_surveyors_with_surveyid


# print(listofsurveyors())


# print(listofuids())

def audio_urls(uid):

    token = AccessToken.get_existing_token().token
    print("entterrrrrr in functionssssss")
    # token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyQ29kZSI6IkFNSSIsImlzUGFydG5lciI6dHJ1ZSwiaWF0IjoxNzM2NDIyODQ1LCJleHAiOjE3MzcwMjc2NDV9.lNN0fjMmbDvuq70p--_kkAtmZC-7g5wcs5Gen6mpBYU"
    headers = {
        "Authorization": token,
        "accept": "application/json",
        "locale": "en",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # result = listofuids()  # Assuming this returns a dictionary with UID values

    MEDIA_DIR = os.path.join(settings.BASE_DIR, 'media/audio/')
    os.makedirs(MEDIA_DIR, exist_ok=True)  # Ensure the directory exists
    audio_filename = os.path.join(MEDIA_DIR, f"{uid}.wav")

    # MEDIA_DIR = '/opt/tomcat/webapps/Audio/'
    # audio_filename = os.path.join(MEDIA_DIR, f"{uid}.wav")
    # remote_dir = os.path.dirname(audio_filename)
    # print(remote_dir)
                
    # Check if the file already exists
    if os.path.exists(audio_filename):
        print(f"Audio file for UID {uid} already exists: {audio_filename}")
        return f"{settings.MEDIA_URL}audio/{uid}.wav"


    # try: 
    #     sftp.stat(audio_filename)
    #     print(f"Audio file for UID {uid} already exists: {audio_filename}")
    #     return f"http://192.168.1.251:8080/Audio/{uid}.wav"
    
    # except FileNotFoundError:
    #     print("File does not exist on the server.")


    url2 = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-recording/{uid}?type=audio"
    response = requests.get(url2, headers=headers)
            
    if response.status_code == 200:
        print("audioofetching")
        try:
            response = requests.get(url2, headers=headers)
            
            if response.status_code == 401: ###if error get in authentication
                refresh_api_key()
                audio_urls(uid)

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            audio_url = response.text.strip()
            if audio_url.startswith("https://storage.googleapis.com"):
                print(f"Downloading audio file from {audio_url}")

                # Extract the filename from the URL using urlparse
                # parsed_url = urlparse(audio_url)
                # audio_filename = os.path.basename(parsed_url.path)  # Extract filename from path
                 # Define audio storage path
                

                # audio_filename = f"{uid}.wav"  # Remove any query string if present

                # Send a request to download the audio file from the Google Cloud Storage URL
                audio_response = requests.get(audio_url, stream=True)
                audio_response.raise_for_status()
                
                    # Save the audio file
                with open(audio_filename, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

                # with sftp.file(audio_filename, 'wb') as f:
                #     for chunk in audio_response.iter_content(chunk_size=1024):
                #             if chunk:
                #                 f.write(chunk)


                    print(f"Audio file {uid} downloaded successfully as {audio_filename}!")
                
                # print(f"Failed to download audio file for UID {uid} from the URL")
                return f"{settings.MEDIA_URL}audio/{uid}.wav"
                # return f"http://192.168.1.251:8080/Audio/{uid}.wav"
             
             
            else:
                print(f"Invalid URL for UID {uid}: {audio_url}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while processing UID {uid}: {e}")
            return None
    else:
        print(f"Failed to get response for UID {uid} (Status Code: {response.status_code})")
        print("Response Content:", response.text)
        return None




### added responsesdict

def registration_audio(uid):

    token = AccessToken.get_existing_token().token
    #token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyQ29kZSI6IkFNSSIsImlzUGFydG5lciI6dHJ1ZSwiaWF0IjoxNzQ2ODE5Mzc1fQ.y0G4AjBVasFII3ULLH4PFsqfBi7QDXGxThXTeFhT2F8"
    # token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoiUUMxNzM3OTY0NjI4MzAwSVQiLCJpc1BhcnRuZXIiOnRydWUsImlhdCI6MTczNzk2NDYyOH0.J7sukW_N8IBO7lRLbwFa11AjOp6mgmXLXfLCk7jQG28"
    print("entterrrrrr in functionssssss registration")
    #token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyQ29kZSI6IkFNSSIsImlzUGFydG5lciI6dHJ1ZSwiaWF0IjoxNzM2NDIyODQ1LCJleHAiOjE3MzcwMjc2NDV9.lNN0fjMmbDvuq70p--_kkAtmZC-7g5wcs5Gen6mpBYU"
    headers = {
        "Authorization": token,
        "accept": "application/json",
        "locale": "en",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # result = listofuids()  # Assuming this returns a dictionary with UID values

    MEDIA_DIR = os.path.join(settings.BASE_DIR, 'media/registration/')
    os.makedirs(MEDIA_DIR, exist_ok=True)  # Ensure the directory exists
    audio_filename = os.path.join(MEDIA_DIR, f"{uid}_registration.wav")

    # MEDIA_DIR = '/opt/tomcat/webapps/Audio/'
    # audio_filename = os.path.join(MEDIA_DIR, f"{uid}_registration.wav")
    # remote_dir = os.path.dirname(audio_filename)
    # print(remote_dir)
                
    # Check if the file already exists
    if os.path.exists(audio_filename):
        print(f"Audio file for UID {uid}_registration already exists: {audio_filename}")
        return f"{settings.MEDIA_URL}registration/{uid}_registration.wav"


    # try: 
    #     sftp.stat(audio_filename)
    #     print(f"Audio file for UID {uid}_registration already exists: {audio_filename}")
    #     return f"http://192.168.1.251:8080/Audio/{uid}_registration.wav"
    
    # except FileNotFoundError:
    #     print("File does not exist on the server.")


    url2 = f"https://api.axismyindia.in/v1/admin/surveyors/qc-service/survey-response-recording/{uid}?type=registration"
    response = requests.get(url2, headers=headers)
            
    if response.status_code == 200:
        print("audioofetching registraions")
        try:
            response = requests.get(url2, headers=headers)
            
            if response.status_code == 401: ###if error get in authentication
                refresh_api_key()
                registration_audio(uid)

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            audio_url = response.text.strip()
            if audio_url.startswith("https://storage.googleapis.com"):
                print(f"Downloading audio file from {audio_url} registraiton")

                # Extract the filename from the URL using urlparse
                # parsed_url = urlparse(audio_url)
                # audio_filename = os.path.basename(parsed_url.path)  # Extract filename from path
                 # Define audio storage path
                

                # audio_filename = f"{uid}.wav"  # Remove any query string if present

                # Send a request to download the audio file from the Google Cloud Storage URL
                audio_response = requests.get(audio_url, stream=True)
                audio_response.raise_for_status()
                
                    # Save the audio file
                with open(audio_filename, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

                # with sftp.file(audio_filename, 'wb') as f:
                #     for chunk in audio_response.iter_content(chunk_size=1024):
                #             if chunk:
                #                 f.write(chunk)


                    print(f"Audio file {uid}_registration downloaded successfully as {audio_filename}!")
                
                print(f"Failed to download audio file for UID {uid}_registration from the URL")
                return f"{settings.MEDIA_URL}registration/{uid}_registration.wav"
                # return f"http://192.168.1.251:8080/Audio/{uid}_registration.wav"
             
             
            else:
                print(f"Invalid URL for UID {uid}_registration: {audio_url}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while processing UID {uid}_registration: {e}")
            return None
    else:
        print(f"Failed to get response for UID {uid}_registration (Status Code: {response.status_code})")
        print("Response Content:", response.text)
        return None
# audio_urls()


# Call the function
# print(audio_urls())

### populatesurveyresponse code ####

def populateSurveyResponse(key, responsesdict, data, project):
    # Populate remarks
    responseparamdict = {}

    responseparamdict['id1'] = key
    responseparamdict['surveyor'] = responsesdict[key]['surveyor']



    if SurveyResponse.objects.filter(uid=key,project=Project.objects.get(id=project)).count() == 0:
        if responsesdict[key]['village_distance'] == None:
            responsesdict[key]['village_distance'] = 'GPS issue'
        if responsesdict[key]['movement'] == None:
            responsesdict[key]['movement'] = 'GPS issue'

        try:
            if responsesdict[key]['audiourls'] == []:
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='No Recordings'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'].split(' ')[0])
                    )
            elif responsesdict[key]['actualaddress'] != None:
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'].split(' ')[0])
                    )
            else:
                responsesdict[key]['actualaddress'] = 'GPS issue'
                SurveyResponse.objects.create(
                    uid=key,
                    project=Project.objects.get(id=project),
                    verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                    params=json.dumps(responsesdict[key]),
                    remarks=json.dumps(responseparamdict),
                    surveyor=Employee.objects.get(employee_id=responseparamdict['surveyor'].split(' ')[0])
                 )

            print('%s -> %s (populate)' % (key, Project.objects.get(pk=project).name))
        except Exception as e:
            try:
                # SurveyResponse.objects.create(
                #     uid=key,
                #     project=Project.objects.get(id=project),
                #     verification_status=VerificationStatus.objects.get(name='To Be Verified'),
                #     params=json.dumps(responsesdict[key]),
                #     remarks=json.dumps(responseparamdict)
                #     )

                print ('%s -> %s (ERROR GET WHILE POPULATING) -> %s' % (key, Project.objects.get(pk=project).name,e))
            except Exception as e:
                print(e, ' during populate')
                pass


    return data


import threading
####calling fetchdatacron####
def run_threaded(job_func):
   job_thread = threading.Thread(target=job_func)
   job_thread.start()




###loop for infinite

while True:

    if __name__ == '__main__':
        run_threaded(fetchdatacron)
        
    time.sleep(3600)
  