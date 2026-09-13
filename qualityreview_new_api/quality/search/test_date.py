import json
from datetime import datetime
import pytz
# import mysql.connector
from dateutil import parser
 
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="axis@123",
#   database="quality"
# )
 
 
# mycursor = mydb.cursor()
 
# mycursor.execute("SELECT uid,params FROM quality.search_surveyresponse")
 
# myresult = mycursor.fetchall()
# print(myresult)
 
# for x in myresult:
 
 
# Your JSON data
# json_data = f'''
# {x[1]}
# '''
 
# # Load JSON data
# data = json.loads(json_data)
 
# Parse date string
date_string = "2024-09-14 04:21:20.83+00"
date_object = parser.isoparse(date_string)
 
# Convert to Asia/Kolkata timezone
kolkata_tz = pytz.timezone('Asia/Kolkata')
date_object_kolkata = date_object.astimezone(kolkata_tz)
 
# Format time as desired
time_string = date_object_kolkata.strftime('%H:%M:%S')
 
# Format date as desired
date_string_kolkata = date_object_kolkata.strftime('%d-%b-%Y')
 
# Update JSON data with time and date strings
print(time_string)
print(date_string_kolkata)

 
# Convert JSON data back to string

 
    # sql = "UPDATE quality.search_surveyresponse SET params = %s WHERE uid = %s"
    
    # val = (updated_json_data, x[0])
 
    # mycursor.execute(sql, val)
 
    # mydb.commit()