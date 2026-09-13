import json
import mysql.connector
import paramiko
db = mysql.connector.connect(
    host="localhost",
    database='quality',
    user='root',
    password='axis@123'
)

cursor = db.cursor()
# sql = cursor.execute('SELECT params FROM quality.search_surveyresponse where uid = 35081;')
# result = cursor.fetchall()
# print(result[0][0])
# string_val = json.dumps(result[0][0])

# value_in = f'/media/audio/35081.wav'

# if value_in in string_val:
#     print('yes')
#     string_val = string_val.replace(f'/media/audio/35081.wav',f"http://192.168.1.251:8080/Audio/35081.wav")
#     sql2 = f'UPDATE quality.search_surveyresponse SET params = {string_val} where uid = 35081'
#     cursor.execute(sql2) 
#     db.commit() 
# else:
#     print('no')
#     pass

# print(string_val)

host = "192.168.1.251"
username = "root"
password = "axis@123"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

sftp = ssh.open_sftp()
val = []
audio_filename = '/opt/tomcat/webapps/Audio/'

registration_audio_filename = '/opt/tomcat/webapps/Registration Audio/'

# select_audio_mode = int(input('Enter 1 if you want to dump registration audios else Enter 2: '))

# if select_audio_mode == 1:
#     files = sftp.listdir(registration_audio_filename)
    

# else:
#     files = sftp.listdir(audio_filename)
    

files = sftp.listdir(audio_filename)

sorted_files = sorted(files, key=lambda x: int(x.replace('_registration.wav', '') if 'registration' in x else x.replace('.wav', '')), reverse=True)
# print(sorted_files[2768])

# for i, value in enumerate(sorted_files):
#     if "registration" in value:
#         print(i)


with open('urls.txt', 'a') as f:
    for i in sorted_files[:451]:
        
        # pass
        f.write(i+",")
        if i.endswith('.wav'):
            if "_registration" in i:
                new_i = i.split('_')[0]
            else:
                new_i = i.split('.')[0]
            # print(new_i)
            val.append(new_i)
            sql = cursor.execute(f"SELECT params FROM quality.search_surveyresponse where uid = {new_i};")
            result = cursor.fetchall()
            print(result[0][0])
            if result:
                string_val = json.dumps(result[0][0])
                
                value_in = f'/media/audio/{new_i}.wav'

                if value_in in string_val:
                    print('yes')
                    string_val = string_val.replace(f'/media/audio/{new_i}.wav',f"http://192.168.1.251:8080/Audio/{new_i}.wav")
                    sql2 = f'UPDATE quality.search_surveyresponse SET params = {string_val} where uid = {new_i}'
                    cursor.execute(sql2) 
                    db.commit() 
                else:
                    print('no')
                   

db.close()
