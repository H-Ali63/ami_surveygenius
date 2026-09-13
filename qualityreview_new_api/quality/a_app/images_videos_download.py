import logging
import os
import mysql.connector #type: ignore
import xlsxwriter #type: ignore
import re
import json
import pandas as pd #type: ignore
import csv
import io
from django.http import HttpResponse #type: ignore
import requests #type: ignore
import cv2 #type: ignore
import numpy as np #type: ignore
from django.shortcuts import render, redirect #type: ignore
from django.views.generic import TemplateView #type: ignore
from django.utils.decorators import method_decorator #type: ignore
from quality.access_control import require_employee_ids #type: ignore

logger = logging.getLogger(__name__)


def _get_axismyindia_connection():
    """Return a mysql.connector connection to the AXISMYINDIA DB using env vars."""
    return mysql.connector.connect(
        host=os.environ.get('AXISMYINDIA_DB_HOST', '127.0.0.1'),
        user=os.environ.get('AXISMYINDIA_DB_USER', 'root'),
        passwd=os.environ.get('AXISMYINDIA_DB_PASSWORD', ''),
        database=os.environ.get('AXISMYINDIA_DB_NAME', 'AXISMYINDIA'),
    )


def _get_surveygenius_connection():
    """Return a mysql.connector connection to the SurveyGenius DB using env vars."""
    return mysql.connector.connect(
        host=os.environ.get('SURVEYGENIUS_DB_HOST', '127.0.0.1'),
        user=os.environ.get('SURVEYGENIUS_DB_USER', 'root'),
        passwd=os.environ.get('SURVEYGENIUS_DB_PASSWORD', ''),
        database=os.environ.get('SURVEYGENIUS_DB_NAME', 'surveygeniusdb'),
        port=int(os.environ.get('SURVEYGENIUS_DB_PORT', 9000)),
    )


@method_decorator(require_employee_ids("107424"), name='dispatch')
class Images_Export_Data(TemplateView):
    
    def get(self, request):
        data = {
            'htmlfilename': 'a_app_templates/images_videos.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            }
        
        print('123456',request.GET.keys())

        if 'fordate' and 'todate' in request.GET.keys():
            print(request.GET['fordate'])
            print(request.GET['todate'])



            db = _get_axismyindia_connection()

            try:
                cursor = db.cursor()
                
                sql = f'''SELECT id1  FROM `SAVE_SURVEY` WHERE `CHECKPOINT_ID` = '157512' AND `DATETIME` BETWEEN '{request.GET['fordate']} 00:00:00'  AND '{request.GET['todate']} 23:59:59' ORDER BY `SID`  DESC'''
                # sql = '''SELECT VALUE, AUDIO_URL, OTHER, CHECKPOINT_ID FROM SAVE_SURVEY WHERE AUDIO_URL IS NOT NULL AND id1 LIKE %s''' % (id1)
                cursor.execute(sql)
                id1_data = cursor.fetchall()
                print(id1_data)
            except:
                print('some eroor')
                id1_data = ''
            finally:
                db.close()

            if id1_data:
                list_of_id1=[]
                for i in range(len(id1_data)):
                    list_of_id1.append(id1_data[i][0])
                list_of_id1=tuple(list_of_id1)

            if list_of_id1:
                return self.export_data_images_videos(request,list_of_id1)
                
            ### work resume here

        return render(request, 'index.html', data)
    

    def post(self, request):
        data = {
            'htmlfilename': 'a_app_templates/images_videos.html',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'employee_pic': request.user.user_employee.get_profile_pic(),
            'userrole': request.user.user_employee.designation.name,
            'department': request.user.user_employee.designation.department.name,
            }
        
        
        
        return render(request, 'index.html', data)
    




    def export_data_images_videos(self,request,list_of_id1):
            database = _get_surveygenius_connection()

            mydb = database.cursor()

            if database.is_connected:
                print("connected")

            #### P/L FUNCTION
            def get_image_dimensions(image_url):

                try:
                    
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status()  # Raise an exception for bad status codes

                
                    image_data = np.frombuffer(response.raw.read(), dtype=np.uint8)
                    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                
                    if img is None:
                        #print(f"Error: Could not load image from URL: {image_url}")
                        return None

                    
                    height, width, channels = img.shape
                    if height > width:
                        return 'portrait'
                    if height < width:
                        return 'landscape'
                    else:
                        return 'square'


                except requests.exceptions.RequestException as e:
                    #print(f"Error: Could not download image from URL: {image_url}. Error: {e}")
                    return None
                except Exception as e:
                    #print(f"Error: An unexpected error occurred: {e}")
                    return None

            def exporttocsvfromdump(id=1441,list_of_id1=list_of_id1):
                    
                    fname_query = "SELECT * FROM `mainapp_project` WHERE `mainapp_project`.`id` = %s"

                    mydb.execute(fname_query,(id,))

                    fname_query = mydb.fetchall()
                    print(fname_query)

                    fname = fname_query[0][1]

                    output = f'{fname}.xlsx'
                    #output = StringIO()

                    # output = io.BytesIO()
                    output = io.BytesIO()
                    workbook = xlsxwriter.Workbook(output)
                    worksheet = workbook.add_worksheet('output')

                    # response = HttpResponse(content_type='text/csv')
                    # response['Content-Disposition'] = 'attachment; filename="qcanalystreport_%s.csv"' % (date.today() - timedelta(days=dayreq))
                    # writer = csv.writer(response)
                    # if output == 'IMAGES/VIDEOS SURVEY.xlsx':
                    #     output = "IMAGES.xlsx"
                    #     workbook = xlsxwriter.Workbook(f"X:/{output}")
                    #     worksheet = workbook.add_worksheet(output)

                    # else:
                    #     workbook = xlsxwriter.Workbook(f"X:/{output}")
                    #     worksheet = workbook.add_worksheet(output)

                    # if output == 'IMAGES/VIDEOS SURVEY.xlsx':
                    #     output = "IMAGES.xlsx"
                    #     workbook = xlsxwriter.Workbook(f"X:/IT/Saurabh/CRIS/{output}")
                    #     worksheet = workbook.add_worksheet(output)

                    # else:
                    #     workbook = xlsxwriter.Workbook(f"X:/IT/Saurabh/CRIS/{output}")
                    #     worksheet = workbook.add_worksheet(output)

                    row = 0
                    # id_placeholders = ','.join(['%s'] * len(list_of_id1))
                    # print(id_placeholders)
                    # data = AllDataDump.objects.filter(project=projectobj).order_by(('-pk'))
                    data = "SELECT `mainapp_alldatadump`.`id`, `mainapp_alldatadump`.`project_id`, `mainapp_alldatadump`.`checkpoints`, `mainapp_alldatadump`.`checkpoints_raw`, `mainapp_alldatadump`.`uidi`, `mainapp_alldatadump`.`uid`, `mainapp_alldatadump`.`rawdata`, `mainapp_alldatadump`.`rawdata_raw`, `mainapp_alldatadump`.`image_data` FROM `mainapp_alldatadump` WHERE `mainapp_alldatadump`.`project_id` = 1441 and `mainapp_alldatadump`.`uid` IN ({}) ORDER BY `mainapp_alldatadump`.`id` DESC LIMIT 1500".format(",".join(["%s"] * len(list_of_id1)))

                    print(type(list_of_id1))
                    mydb.execute(data,list_of_id1)

                    data = mydb.fetchall()
                    print(data,">>>>>>")
                    
                    # Headers
                    cp = data[0]  #only one accessing
                    #print(cp)
                    # print("cp",type(cp))
                    listdr =  json.loads(cp[2])    #only accessing headers
                    listdr = removejunkcolumns(listdr,id)
                    # print(listdr)
                    print("listdr",type(listdr))

                    col = 0

                    worksheet.write(row, col, "UID")
                    col+=1
                    worksheet.write(row, col, "Datetime")
                    col+=1

                    # nccs headers
                    nccs1 = "SELECT * FROM `mainapp_project` WHERE `mainapp_project`.`id` = %s"

                    mydb.execute(nccs1,(id,))

                    nccs1 = mydb.fetchall()

                    if nccs1[0][9] == 1:
                        durables_cols, durables_count, education_col = getnccsheaders(id, listdr) #project id
                        worksheet.write(row, col, "NCCS")
                        col+=1
                        worksheet.write(row, col, "Number of durables owned - calculated")
                        col+=1
                    else:
                        durables_cols, education_col, durables_count = None, None, None
                    # end of nccs headers

                    # Write headers
                    for q in listdr:
                        # print("q",type(q))
                        worksheet.write(row, col, q)
                        col += 1
                    
                    worksheet.write(row,col,"L/P")
                    col += 1
                    row += 1

                    # Split data into chunks
                    # for dr in data.iterator():
                    # Raw data
                    for i in range(0, len(data)):
                        dr = data[i]

                        # print("dr",type(dr))
                        
                        listdr =  json.loads(dr[6])
                        # #print() listdr[-9]
                        listdr = removejunkcolumns(listdr,id)

                        # print("listdr",type(listdr))
                        col = 0

                        skip = False

                        try:
                            if '-' in str(listdr[-9]):
                                print("listdr[-10]",type(listdr[-10]))
                                worksheet.write(row, col, listdr[-10])
                                col+=1
                                worksheet.write(row, col, listdr[-9])
                                col+=1
                            else:
                                worksheet.write(row, col, listdr[-9])
                                col+=1
                                worksheet.write(row, col, listdr[-8])
                                col+=1
                        except Exception as e:
                            continue

                        # nccs headers

                        nccs = "SELECT * FROM `mainapp_project` WHERE `mainapp_project`.`id` = %s"

                        mydb.execute(nccs,(id,))

                        nccs = mydb.fetchall()

                        if nccs[0][9] == 1:
                            nccs_result, durables_count_calculated = getnccsresults(listdr, durables_cols, education_col, durables_count)
                            #print(nccs_result, durables_count_calculated)
                            worksheet.write(row, col, nccs_result)
                            col+=1
                            worksheet.write(row, col, durables_count_calculated)
                            col+=1
                        # end of nccs headers
                        print(listdr,">>>>>>")
                        for dc in listdr:
                            if col == 0:
                                if dc == '-':
                                    row -= 1
                                    dr.delete()
                                    break
                            try:
                                # print("dc",type(dc))
                                worksheet.write(row, col, dc)
                                # worksheet.write(row, col, dc.encode('utf-8'))
                            except Exception as e:
                            
                                worksheet.write(row, col, dc)

                            col += 1
                        if str(listdr[2]).startswith('1-PICTURE') and listdr[3]!="": 
                            print(get_image_dimensions(listdr[3]))
                                
                            worksheet.write(row,28,get_image_dimensions(listdr[3]))
                        else:
                            print('else')
                            worksheet.write(row,28,"")
                        row += 1

                    workbook.close()

                
                    print(fname)
                    output.seek(0)
                    print(output.read)
                    
                    # response = output.read()
                    
                    output.seek(0)
                    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename="{fname}.xlsx"'

                    import gc
                    gc.collect()
                    database.close()
                    return response




            def removejunkcolumns(data,id):
                    
                    project = "SELECT * from `mainapp_project` WHERE `mainapp_project`.`id` = %s"

                    mydb.execute(project,(id,))

                    project = mydb.fetchall()
                    
                    finaldata = data

                    merge = "SELECT `mainapp_mergecolumns`.`id`, `mainapp_mergecolumns`.`project_id`, `mainapp_mergecolumns`.`startcol`, `mainapp_mergecolumns`.`endcol` FROM `mainapp_mergecolumns` WHERE `mainapp_mergecolumns`.`project_id` = %s"

                    mydb.execute(merge,(id,))

                    merge = mydb.fetchall()

                    print(merge)        #list of tuple   [(1964, 1167, 7, 16), (1965, 1167, 26, 27), (1966, 1167, 29, 432)]

                    print(type(merge))  #list

                    print(len(merge))

                    if len(merge) > 0:
                        mergeobj = merge
                        validcoldata = '-'

                        start_cols = []
                        all_cols = []
                        outputs = []

                        for mergeo in mergeobj:

                            print("mergeo",mergeo)   #tuple  (1964, 1167, 7, 16)
                            print(type(mergeo))

                            start_cols.append(int(mergeo[2]))
                            for i in range(int(mergeo[2]), int(mergeo[3]) + 1):
                                all_cols.append(int(i))

                            for op in data[int(mergeo[2]):(int(mergeo[3]) + 1)]:
                                if str(op) != '-':
                                    validcoldata = str(op)
                                    # if validcoldata != '-':
                                    #     validcoldata = '%s/%s' % (validcoldata, str(op))
                                else:
                                    pass

                            outputs.append(validcoldata)
                            validcoldata = '-'

                        finaldata = []

                        for i, d in enumerate(data):
                            if i in start_cols:
                                finaldata.append(outputs[start_cols.index(i)])
                            elif i in all_cols:
                                pass
                            else:
                                finaldata.append(d)

                    finaldata2 = []


                    similarcolumn = "SELECT `mainapp_similarcolumns`.`id`, `mainapp_similarcolumns`.`project_id`, `mainapp_similarcolumns`.`cols` FROM `mainapp_similarcolumns` WHERE `mainapp_similarcolumns`.`project_id` = %s"

                    mydb.execute(similarcolumn,(id,))

                    similarcolumn = mydb.fetchall()

                    similarcolumn = [i for i in similarcolumn]

                    if len(similarcolumn) > 0:
                        similarcolumnobj = similarcolumn[0]

                        tempcols = []
                        colnos = []

                        for col in json.loads(similarcolumnobj.cols):
                            temp = '-'

                            for subcol in col:
                                try:
                                    temp = finaldata[subcol] if finaldata[subcol] != '-' else temp
                                    colnos.append(int(subcol))
                                except Exception as e:
                                    continue

                            tempcols.append(temp)

                        for i, d in enumerate(finaldata):
                            if i not in colnos:
                                tempcols.append(d)

                        finaldata = tempcols

                    return finaldata



            durables_list = [
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  1-Electricity Connection",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  2-Ceiling Fan",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  3-LPG Stove",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  4-Two Wheeler",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  5-Colour TV",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  6-Refrigerator",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  7-Washing Machine",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  8-Personal Computer/ Laptop",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  9-Car/Jeep/Van",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  10-Air Conditioner",
                "Do you have a (READ OUT THE ITEMS ONE BY ONE) in your home (which is in working condition)?  11-Agricultural Land"
            ]



            def getnccsheaders(projectid, listdr):
                durables_cols = []
                durables_count = 0

                for i, dr in enumerate(listdr):

                    print(type(dr))

                    if 'Durables owned' in dr and 'Count' not in dr:
                        durables_cols.append(i)

                    if re.search(str("Do you have a", dr)) is not None:
                        durables_cols.append(i)

                    # if 'Can you please tell me your highest level of education?' in dr.strip():
                    if 'Can you please tell me your highest level of education?[CWE]' in dr.strip():
                        education_col = i

                    if 'Count of durables owned' in dr.strip():
                        durables_count = i

                return durables_cols, durables_count, education_col


            def getnccsresults(listdr, durables_cols, education_col, durables_count):
                # validkeys = [
                #     'Illiterate',
                #     'Literate but no formal schooling',
                #     'School – Up to 4th standard',
                #     '5th-9th standard',
                #     'SSC/HSC (10th-12th)',
                #     'Some college (incl. dip) but not graduate',
                #     'Graduate –General (B.A./B.Sc./B.Com.)',
                #     'Graduate –Professional (B.E./M.B.B.S./B.Tech)',
                #     'Post-Graduate-General (M.A./M.Sc./M.Com/M.Phil/Phd)',
                #     'Post-Graduate-Professional(M.E./M.Tech/MBA/etc)'
                # ]
                #
                # nccsgrid = {
                #     'Illiterate' : {
                #             0:'E3',
                #             1:'E2',
                #             2:'E1',
                #             3:'D2',
                #             4:'D1',
                #             5:'C2',
                #             6:'C1',
                #             7:'C1',
                #             8:'B1',
                #             9:'B1',
                #             10:'B1',
                #             11:'B1'
                #     },
                #     'Literate but no formal schooling' : {
                #             0:'E2',
                #             1:'E1',
                #             2:'E1',
                #             3:'D2',
                #             4:'C2',
                #             5:'C1',
                #             6:'B2',
                #             7:'B1',
                #             8:'A3',
                #             9:'A3',
                #             10:'A3',
                #             11:'A3'
                #     },
                #     'School – Up to 4th standard' : {
                #             0:'E2',
                #             1:'E1',
                #             2:'E1',
                #             3:'D2',
                #             4:'C2',
                #             5:'C1',
                #             6:'B2',
                #             7:'B1',
                #             8:'A3',
                #             9:'A3',
                #             10:'A3',
                #             11:'A3'
                #     },
                #     '5th-9th standard' : {
                #             0:'E2',
                #             1:'E1',
                #             2:'D2',
                #             3:'D1',
                #             4:'C2',
                #             5:'C1',
                #             6:'B2',
                #             7:'B1',
                #             8:'A3',
                #             9:'A3',
                #             10:'A3',
                #             11:'A3'
                #     },
                #     'SSC/HSC (10th-12th)' : {
                #             0:'E2',
                #             1:'E1',
                #             2:'D2',
                #             3:'D1',
                #             4:'C1',
                #             5:'B2',
                #             6:'B1',
                #             7:'A3',
                #             8:'A3',
                #             9:'A2',
                #             10:'A2',
                #             11:'A2'
                #     },
                #     'Some college (incl. dip) but not graduate' : {
                #             0:'E2',
                #             1:'D2',
                #             2:'D1',
                #             3:'C2',
                #             4:'C1',
                #             5:'B1',
                #             6:'A3',
                #             7:'A3',
                #             8:'A2',
                #             9:'A2',
                #             10:'A2',
                #             11:'A2'
                #     },
                #     'Graduate –General (B.A./B.Sc./B.Com.)' : {
                #             0:'E1',
                #             1:'D2',
                #             2:'D1',
                #             3:'C2',
                #             4:'B2',
                #             5:'B1',
                #             6:'A3',
                #             7:'A2',
                #             8:'A2',
                #             9:'A1',
                #             10:'A1',
                #             11:'A1'
                #     },
                #     'Graduate –Professional (B.E./M.B.B.S./B.Tech)' : {
                #             0:'D2',
                #             1:'D2',
                #             2:'D1',
                #             3:'C2',
                #             4:'B2',
                #             5:'B1',
                #             6:'A3',
                #             7:'A2',
                #             8:'A2',
                #             9:'A1',
                #             10:'A1',
                #             11:'A1'
                #     },
                #     'Post-Graduate-General (M.A./M.Sc./M.Com/M.Phil/Phd)' : {
                #             0:'E1',
                #             1:'D2',
                #             2:'D1',
                #             3:'C2',
                #             4:'B2',
                #             5:'B1',
                #             6:'A3',
                #             7:'A2',
                #             8:'A2',
                #             9:'A1',
                #             10:'A1',
                #             11:'A1'
                #     },
                #     'Post-Graduate-Professional(M.E./M.Tech/MBA/etc)' : {
                #             0:'D2',
                #             1:'D2',
                #             2:'D1',
                #             3:'C2',
                #             4:'B2',
                #             5:'B1',
                #             6:'A3',
                #             7:'A2',
                #             8:'A2',
                #             9:'A1',
                #             10:'A1',
                #             11:'A1'
                #     }
                # }

                nccsgrid = {
                    '1-Illiterate' : {
                            0:'E3',
                            1:'E2',
                            2:'E1',
                            3:'D2',
                            4:'D1',
                            5:'C2',
                            6:'C1',
                            7:'C1',
                            8:'B1',
                            9:'B1',
                            10:'B1',
                            11:'B1'
                    },
                    '2-Literate/ but no formal schooling / School up to 4 years' : {
                            0:'E2',
                            1:'E1',
                            2:'E1',
                            3:'D2',
                            4:'C2',
                            5:'C1',
                            6:'B2',
                            7:'B1',
                            8:'A3',
                            9:'A3',
                            10:'A3',
                            11:'A3'
                    },
                    '3-School 5-9 years' : {
                            0:'E2',
                            1:'E1',
                            2:'E1',
                            3:'D2',
                            4:'C2',
                            5:'C1',
                            6:'B2',
                            7:'B1',
                            8:'A3',
                            9:'A3',
                            10:'A3',
                            11:'A3'
                    },
                    '5th-9th standard' : {
                            0:'E2',
                            1:'E1',
                            2:'D2',
                            3:'D1',
                            4:'C2',
                            5:'C1',
                            6:'B2',
                            7:'B1',
                            8:'A3',
                            9:'A3',
                            10:'A3',
                            11:'A3'
                    },
                    '4-SSC/HSC' : {
                            0:'E2',
                            1:'E1',
                            2:'D2',
                            3:'D1',
                            4:'C1',
                            5:'B2',
                            6:'B1',
                            7:'A3',
                            8:'A3',
                            9:'A2',
                            10:'A2',
                            11:'A2'
                    },
                    '5-Some college (including Diploma) but not graduate' : {
                            0:'E2',
                            1:'D2',
                            2:'D1',
                            3:'C2',
                            4:'C1',
                            5:'B1',
                            6:'A3',
                            7:'A3',
                            8:'A2',
                            9:'A2',
                            10:'A2',
                            11:'A2'
                    },
                    '6-Graduate/ Post Graduate: General' : {
                            0:'E1',
                            1:'D2',
                            2:'D1',
                            3:'C2',
                            4:'B2',
                            5:'B1',
                            6:'A3',
                            7:'A2',
                            8:'A2',
                            9:'A1',
                            10:'A1',
                            11:'A1'
                    },
                    '7-Graduate/ Post Graduate: Professional' : {
                            0:'D2',
                            1:'D2',
                            2:'D1',
                            3:'C2',
                            4:'B2',
                            5:'B1',
                            6:'A3',
                            7:'A2',
                            8:'A2',
                            9:'A1',
                            10:'A1',
                            11:'A1'
                    },
                    'Post-Graduate-General (M.A./M.Sc./M.Com/M.Phil/Phd)' : {
                            0:'E1',
                            1:'D2',
                            2:'D1',
                            3:'C2',
                            4:'B2',
                            5:'B1',
                            6:'A3',
                            7:'A2',
                            8:'A2',
                            9:'A1',
                            10:'A1',
                            11:'A1'
                    },
                    'Post-Graduate-Professional(M.E./M.Tech/MBA/etc)' : {
                            0:'D2',
                            1:'D2',
                            2:'D1',
                            3:'C2',
                            4:'B2',
                            5:'B1',
                            6:'A3',
                            7:'A2',
                            8:'A2',
                            9:'A1',
                            10:'A1',
                            11:'A1'
                    }
                }

                durables_count_calculated = 0
                for i, dr in enumerate(listdr):
                    if str(dr) == 'Y' and i in durables_cols:
                        durables_count_calculated += 1

                try:
                    nccs_result = nccsgrid[listdr[int(education_col)]][int(durables_count_calculated)]
                except Exception as e:
                    return None, durables_count_calculated

                return nccs_result, durables_count_calculated
            # try:
            return exporttocsvfromdump(id=1441,list_of_id1=list_of_id1)
            
            # except Exception as e:
                # print(f"Error: {e}")
            # return HttpResponse('An error occurred', status=500)
            # finally:
                #
            # return HttpResponse('done')
