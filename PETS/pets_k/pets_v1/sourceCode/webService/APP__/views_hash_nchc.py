#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import os
import json
import requests #pip install requests
import base64
from app import app
from . import tasks,SparkJobManager,task_getDistinctData,task_getJoinData,task_getKchecking, task_getMLutility,task_getRiskAnalysis


from . import task_export,task_import,task_getGenTbl,task_uid_enc,task_createProject
from . import task_udfMacUID
from flask_redis import FlaskRedis
from flask import render_template, request, jsonify,make_response
from celery import states
from module.JsonSchema import jsonBase64Schema,loadJson,tableInfoSchema,getCheckTempleteSchema,jobIDSchema
from module.base64convert import getJsonParser, encodeDic
from module.checkTemplete import getReplacePath, getUserRule
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs

##swagger###
# pip --no-cache-dir install flasgger
from flasgger import Swagger
from flasgger.utils import swag_from
from flasgger import LazyString, LazyJSONEncoder
##################################
from config.connect_sql import ConnectSQL 
#################################
redis_store = FlaskRedis(app)

#START for swagger setting
app.config["SWAGGER"] = {"title": "Swagger-UI-Deid", "uiversion": 2}
swagger_config = {
    "headers": [],        #('Access-Control-Allow-Origin', '*'),
        #('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        #("Access-Control-Allow-Headers","Content-Type, api_key, Authorization"),
        #('Access-Control-Allow-Credentials', "true"),],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            #"rule_filter": lambda rule: True,  # all in
            #"model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/swagger/",
}

#template = dict(    swaggerUiPrefix=LazyString(lambda: request.environ.get("HTTP_X_SCRIPT_NAME", "")))

        
app.json_encoder = LazyJSONEncoder
swagger = Swagger(app, config=swagger_config)#, template=template)
### END for swagger setting


def splitSymbol(list_):
    return [i.split('\n',1)[0] for i in list_]


class GetLogTime:
    def __init__(self, name):
        self.name = name
        self.now = time.strftime("%Y/%m/%d %H:%M:%S")
    def printLog(self, msg):
        print('{0} - {1} - {2}'.format(self.now, self.name, msg))

@app.route('/')
def index():
    return "HELLO FLASK!"
    #return render_template('index.html')

########################
#testing swagger API
def add_2_numbers(num1, num2):
    output = {"sum_of_numbers": 0}
    sum_of_2_numbers = num1 + num2
    output["sum_of_numbers"] = sum_of_2_numbers
    return output

@app.route("/add_2_numbers", methods=["POST"])
@swag_from("swagger_yml/swagger_add.yml")
def add_numbers():
    input_json = request.get_json()
    print('###############################################')
    print(input_json)
    try:
        num1 = int(input_json["x1"])
        num2 = int(input_json["x2"])
        res = add_2_numbers(num1, num2)
    except:
        res = {"success": False, "message": "Unknown error"}

    return json.dumps(res)
################################
def check_appstatus(proj_id, Application_Name):
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        response = dict()
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        #log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try: # fetch parameter: pid
        #sqlStr = "SELECT Progress  FROM `spark_status`.`appStatus` where proj_id like '{}';".format(proj_id,Application_Name)
        sqlStr = "SELECT Progress  FROM `spark_status`.`appStatus` where proj_id like '{}' AND Application_Name like '{}';".format(proj_id, Application_Name)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            Progress = resultCheck["fetchall"][0]['Progress']

        sqlStr = "SELECT Progress_State  FROM `spark_status`.`appStatus` where proj_id like '{}' AND Application_Name like '{}';".format(proj_id, Application_Name)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            Progress_State = resultCheck["fetchall"][0]['Progress_State']

        check_conn.close()
        return Progress, Progress_State

    except Exception as e:
        response = dict()
        errMsg = 'fetch progress fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

# update process status to mysql
def updateToMysql(conn, project_id, valueSampleData, sqltable):
#def updateToMysql_config(conn, project_id, qi_col, minKvalue, after_col_value, tableDisCount, gen_qi_settingvalue, tablekeycol):
    print('########updateToMysql###########')
    condisionSampleData = {
            'project_id': project_id
        }

    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('DeIdService',
                                            sqltable,
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        print("update mysql: SUCCESS!")
        #conn.close()
        return None
    else:
        response = dict()
        errMsg = 'updateToMysql_config fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


#swagger
@app.route("/AutoDeId_Sync", methods=["POST"])
@swag_from("swagger_yml/hash.yml")
def AutoDeId_Sync():
    log_time = GetLogTime('AutoDeId_Sync')
    log_time.printLog("Start AutoDeId_Sync")
    
    ts0 = time.time()

    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    #get parameter
    try:
        pname = data_raw['pname']
        prodesc =  data_raw['prodesc']
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        step = data_raw['step']
        configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep = data_raw['sep']
        columns_mac = data_raw['columns_mac']
        dataHash = data_raw['dataHash']

    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or hashkey == '' or sep == '' or columns_mac == '' or dataHash == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    response = {}
    response['InsertProject_flag'] = "2"# "for export"
    #/api/WebAPI/InsertProject
    #step=1:create project > hash > import
    try:
        if int(step) == 1:
            # InsertProject_para = { "p_dsname": p_dsname, "pinput": pinput, "pname": pname, "poutput": poutput, "powner": powner, "prodesc": prodesc } 
            InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc } 
            response_get = requests.get("http://deidweb_compose:11000/api/WebAPI/InsertProject", params=InsertProject_para)
            print(response_get.url)
            response_dic = response_get.json()
            print("response_get: ",response_dic)
            response['InsertProject_flag']=response_dic
            #print(response['InsertProject_flag'])
            #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    # get the parameter:pid in mysql
    time.sleep(5)
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try: # fetch parameter: pid
        sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project` where project_name like '{}';".format(p_dsname)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            pid = resultCheck["fetchall"][0]['project_id']
            response['pid'] = str(pid)
        check_conn.close()
    except Exception as e:
        errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    # FOR Mac API:  /api/WebAPI/hash
    try:
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash 
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("http://deidweb_compose:5099/mac_async", json=Hash_para,timeout=None)
        response_dic = response_g.json()
        print("HASH JSON: ",response_dic)
        response['HashMac']='1' #response_dic['state']
        #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    # check hash status
    # progress = check_appstatus(128 , 'udfMacUID')
    progress = 0 #check_appstatus(pid , 'udfMacUID')
    while int(progress) != 40:
        try:
            time.sleep(15)
            progress, progress_state =  check_appstatus(pid, 'udfMacUID')
            if int(progress) == 40:
                # progress = 100
                break;
            if progress_state == 'err':#int(progress) == 10:
                response = dict()
                errMsg = 'projstatus error: ' + "hash fail: No file?"
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))            
                break;
        except Exception as e:
            #progress = 0
            pass
 
    # /api/WebAPI/ImportData
    # Need parameter:pid
    if  int(response['InsertProject_flag'])==1:
        try: #API:ImportData
            ImportData_para = { "p_dsname": p_dsname, "pid": pid }
            print('ImportData_para: ',ImportData_para)
            response_g = requests.get("http://deidweb_compose:11000/api/WebAPI/ImportData", params=ImportData_para,timeout=None)
            response_dic = response_g.json()
            print("IMPORT DATA JSON: ",response_dic)
            response['ImportData_flag']=response_dic
            #return make_response(jsonify(response))
        except Exception as e:
            response = dict()
            errMsg = 'request_error: ' + str(e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

    # check_status
    progress = 0 #check_appstatus(pid , 'import')
    while int(progress) != 100:
        try: 
            time.sleep(15)
            progress, progress_state  =  check_appstatus(pid, 'import')
            if int(progress) == 100:
                break;
            if progress_state == 'err':#int(progress) == 10:
                response = dict()
                errMsg = 'projstatus error: ' + "import fail?"
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))            
                break;
        except Exception as e:
            #progress = 0
            pass

    #if progress==100, import > config rule
    if int(progress)==100:
        #Read config AND insert to mysql tbl for gen
        try:
            # get parameter from config file
            path = getConfig().getExportPath('local')
            configPath = os.path.join(path[:-12], 'dataConfig/') + configName
            with open(configPath, 'r') as read_file:
                dict_data = json.load(read_file)
            qi_col = dict_data['qi_col'] 
            minKvalue = dict_data['minKvalue']
            pro_col_cht_config = dict_data['pro_col_cht']  #important comparing
            after_col_value = dict_data['after_col_value'] #important
            tableDisCount = dict_data['tableDisCount']
            gen_qi_settingvalue = dict_data['gen_qi_settingvalue']
            tablekeycol = dict_data['tablekeycol']
            pro_tb_config = dict_data['pro_tb']
            
            valueSampleData = {
            'project_id': pid,
            'qi_col': qi_col,
            'minKvalue': minKvalue,
            'after_col_value': after_col_value,
            'tableDisCount': tableDisCount,
            'gen_qi_settingvalue': gen_qi_settingvalue,
            'tablekeycol': tablekeycol
            }
            check_conn = ConnectSQL()

            #202020620: check config.json pro_tb is mapping to the project right now.
            sqlStr = "SELECT pro_tb  FROM `DeIdService`.`T_Project_SampleTable` where project_id like '{}';".format(pid)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pro_tb = resultCheck["fetchall"][0]['pro_tb']

            #check whether after_col_value is mapping the correct column 
            sqlStr = "SELECT pro_col_cht  FROM `DeIdService`.`T_Project_SampleTable` where project_id like '{}';".format(pid)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pro_col_cht = resultCheck["fetchall"][0]['pro_col_cht']

            #check whether after_col_value is mapping the correct column 
            sqlStr = "SELECT pro_col_en  FROM `DeIdService`.`T_Project_SampleTable` where project_id like '{}';".format(pid)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pro_col_en = resultCheck["fetchall"][0]['pro_col_en']

            pro_col_cht_config_array = pro_col_cht_config.split(',') #from config
            pro_col_cht_array = pro_col_cht.split(',')
            pro_col_en_array = pro_col_en.split(',')
            after_col_value_array = after_col_value.split(',') #from config
            after_col_value_update = after_col_value_array[:] 
            

            #202020620: check config.json pro_tb is mapping to the project right now.
            if pro_tb != pro_tb_config:
                response = dict()
                errMsg = 'request_error: ' + 'plz check the used config is mapping the project.'
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))

            #check: len not same
            if len(pro_col_cht_config_array)!=len(pro_col_cht_array):
                response = dict()
                errMsg = 'request_error: ' + '#. col is not equal to the #. in config'
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))
            
            #NEED_TO_DO also check different column name?           
            for i in range(len(pro_col_cht_config_array)):
                check_count = 0
                for j in range(len(pro_col_cht_array)):
                    if pro_col_cht_config_array[i] == pro_col_cht_array[j]:
                        after_col_value_update[j] = after_col_value_array[i]
                        break;
                    elif pro_col_cht_config_array[i] != pro_col_cht_array[j]:
                        check_count = check_count + 1
                    
                        if check_count == int(len(pro_col_cht_array)):
                            response = dict()
                            errMsg = 'request_error: ' + 'the column name of dataset is not same as config dataset'
                            response['status'] = -1
                            response['errMsg'] = errMsg
                            log_time.printLog(errMsg)
                            return make_response(jsonify(response))


            for k in range(len(after_col_value_update)):
                if int(after_col_value_update[k])==0:
                    pro_col_cht_array.remove(pro_col_cht_array[k])
                    pro_col_en_array.remove(pro_col_en_array[k])

            valueSampleData['after_col_value']=','.join(after_col_value_update)
            valueSampleData['after_col_cht']=','.join(pro_col_cht_array)
            valueSampleData['after_col_en']=','.join(pro_col_en_array)
            #Read config AND insert to mysql tbl for gen
            updateToMysql(check_conn, pid, valueSampleData, 'T_Project_SampleTable')
            #update rule status
            updateToMysql(check_conn, pid, {'project_status':'5'}, 'T_ProjectStatus')
            check_conn.close()
            response['check_flag']= int(progress)
            #return make_response(jsonify(response))    
        except Exception as e:
            response = dict()
            errMsg = 'request_error: ' + str(e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

    # /api/WebAPI/Generalizationasync
    try: #API:Generalizationasync
        Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue":gen_qi_settingvalue,"k_value":minKvalue, "tablename":pro_tb}#, "pro_col_en":pro_col_en,"pro_col_cht":pro_col_cht}
        log_time.printLog('Gen_para: '+str(Gen_para))
        response_g = requests.get("http://deidweb_compose:11000/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None)
        response_dic = response_g.json()
        print("Gen DATA JSON: ",response_dic)
        response['Gen__flag']=response_dic
            #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    # check_status
    progress = 0 #check_appstatus(pid , 'import')
    while int(progress) != 100:
        try: 
            time.sleep(15)
            progress, progress_state  =  check_appstatus(pid, 'gen')
            if int(progress) == 100:
                break;
            if progress_state == 'err':#int(progress) == 10:
                response = dict()
                errMsg = 'projstatus error: ' + "gen fail?"
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))            
                break;
        except Exception as e:
            #progress = 0
            pass


    # /api/WebAPI/ExportData
    # Need parameter:pid
    # step=2: export
    if int(step)==2:
        try: 
            ExportData_para = { "p_dsname": p_dsname, "pid": pid }
            print('ExportData_para: ',ExportData_para)

            response_g = requests.get("http://deidweb_compose:11000/api/WebAPI/ExportData", params=ExportData_para,timeout=None)

            response_dic = response_g.json()
            print("Export DATA JSON: ",response_dic)
            response['ExportData_flag']=response_dic
            response['gen_flag']='finish'
            #return make_response(jsonify(response))
        except Exception as e:
            response = dict()
            errMsg = 'request_error: ' + str(e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
    else: 
        if int(response['InsertProject_flag'])==1:
            pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
        else:
            error_insertproj ='系統寫入出現錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
        response['status'] = response['InsertProject_flag']
        return make_response(jsonify(response))
    
    
    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))
        
#######END SWAGGER ##################

###original code (start)##############
@app.route('/hello_world_')
def hello_world():
    redis_store.set('hello-world-msg', 'Hello from Flask-Redis-Celery')
    view_count = redis_store.incr('hello-world-view-count')

    msg = redis_store.get('hello-world-msg').decode("utf-8")

    return msg + '.<br /><br />This page has been seen ' + str(view_count) + ' times.'


@app.route('/save_counter')
def counter_save():
    tasks.counter_save.delay()

    return 'Sent an async request to Celery, to order Redis to SAVE data to disk.'


@app.route('/reset_counter')
def counter_reset():
    tasks.counter_reset.delay()

    return 'Sent an async request to Celery, to order Redis to RESET data to disk.'
###original code (end)##############
#uidEnc_longTask(self, _dbName, _tblName, _colNames):

##########20200102 add (start)####################
#####citc, 20191126 add##############getSparkNodeDiskStatus
#curl -H 'Content-Type: application/json' -X POST "http://IP address:5088/getSparkNodeDiskStatus"
#{  "jsonBase64": "eyJkaXJOYW1lIjogIi8iLCAidXNlZFBlcmNlbiI6ICIyMiUifQ=="}
#eyJkaXJOYW1lIjogIi8iLCAidXNlZFBlcmNlbiI6ICIyMiUifQ==: {"dirName": "/", "usedPercen": "22%"}
@app.route('/getSparkNodeDiskStatus', methods=['POST'])
def getSparkNodeDiskStatus():
    log_time = GetLogTime('getSparkNodeDiskStatus')
    log_time.printLog("Start getSparkNodeDiskStatus")
    '''
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405
    jsonBase64 = data["jsonBase64"]

    jsonData = getJsonParser(jsonBase64)
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(jsonData)

    print 'enter getSparkJobStatus_2'
    schema = jobIDSchema()
    print 'enter getSparkJobStatus_3'
    data = loadJson(jsonData, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % jsonData
        log_time.printLog(err_msg)
        return err_msg, 405
    print data
    print 'enter getSparkJobStatus_4'
    jobID = data["applicationID"]
    print("in getSparkNodeStatusB64")
    print (jobID)
    '''
    response = SparkJobManager.getSparkNodeDiskStatus()
    print 'enter getSparkNodeDiskStatus_5'
    print(response)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))

#####citc, 20191125 add##############
@app.route('/getSparkNodeStatusB64', methods=['POST'])
def getSparkNodeStatusB64():
    log_time = GetLogTime('getSparkNodeStatusB64')
    log_time.printLog("Start getSparkNodeStatusB64")
    '''
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405
    jsonBase64 = data["jsonBase64"]

    jsonData = getJsonParser(jsonBase64)
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(jsonData)

    print 'enter getSparkJobStatus_2'
    schema = jobIDSchema()
    print 'enter getSparkJobStatus_3'
    data = loadJson(jsonData, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % jsonData
        log_time.printLog(err_msg)
        return err_msg, 405
    print data
    print 'enter getSparkJobStatus_4'
    jobID = data["applicationID"]
    print("in getSparkNodeStatusB64")
    print (jobID)
    '''
    response = SparkJobManager.getSparkNodeStatus()
    print 'enter getSparkNodeStatusB64_5'
    print(response)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))

##########20200102 add (end)####################




#####citc, 20180705 add##############
@app.route('/killSparkJobB64', methods=['POST'])
def killSparkJobB64():
    log_time = GetLogTime('killSparkJobB64')
    log_time.printLog("Start killSparkJobB64")
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405
    jsonBase64 = data["jsonBase64"]

    jsonData = getJsonParser(jsonBase64)
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(jsonData)

    #print 'enter getSparkJobStatus_2'
    schema = jobIDSchema()
    #print 'enter getSparkJobStatus_3'
    data = loadJson(jsonData, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % jsonData
        log_time.printLog(err_msg)
        return err_msg, 405
    #print data
    #print 'enter getSparkJobStatus_4'
    jobID = data["applicationID"]
    #print jobID
    response = SparkJobManager.killSparkJob(jobID)
    #print 'enter getSparkJobStatus_5'

    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))


#####citc, 20180705 add##############
@app.route('/getSparkJobStatusB64', methods=['POST'])
def getSparkJobStatusB64():
    log_time = GetLogTime('getSparkJobStatusB64')
    log_time.printLog("Start getSparkJobStatusB64")
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405
    jsonBase64 = data["jsonBase64"]

    jsonData = getJsonParser(jsonBase64)
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(jsonData)

    #print 'enter getSparkJobStatus_2'
    schema = jobIDSchema()
    #print 'enter getSparkJobStatus_3'
    data = loadJson(jsonData, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % jsonData
        log_time.printLog(err_msg)
        return err_msg, 405
    #print data
    #print 'enter getSparkJobStatus_4'
    jobID = data["applicationID"]
    #print jobID
    response = SparkJobManager.getSparkJobStatus(jobID)
    #print 'enter getSparkJobStatus_5'
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))


# update:20180625
@app.route('/createProject', methods=['POST'])
def createProject():
    log_time = GetLogTime('createProject')
    log_time.printLog("Start createProject")

    ts0 = time.time()

    response = dict()

    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'createProject'#str
    response['dbName'] = ''#str
    response['tblName'] = ''#str

    # decode base64
    try:
        data_raw = request.get_json()
    except Exception as e:
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405

    jsonBase64 =  data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64)))

    task = task_createProject.createProject_longTask.apply_async((jsonBase64,1))

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            createProject_longTask_task = task_createProject.createProject_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = createProject_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = createProject_longTask_task.id
            if state_ == 'PROGRESS':
                response['dbName'] = task.info.get('dbName').strip('\n')
                #response['tblName'] = task.info.get('tblName').strip('\n')
                response['status'] = '1'
                break

            #####20180615, citc add#####################################################
            if state_ == 'FAIL_CELERY':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break

            #####2018014, citc add#####################################################
            if state_ == 'FAIL_SPARK':
                #print 'fail_____'
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['errMsg'] ='Celery job fail'
                response['status'] = '-1'
                break

    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))

# update:20180625
@app.route('/ExportFile', methods=['POST'])
def ExportFile():
    log_time = GetLogTime('ExportFile')
    log_time.printLog("Start ExportFile")

    ts0 = time.time()

    response = dict()

    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'export'#str (select, gen, join, distinct,single k checking,export,import)
    response['dbName'] = ''#str
    response['tblName'] = ''#str

    # decode base64
    try:
        data_raw = request.get_json()
    except Exception as e:
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405

    jsonBase64 =  data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64)))

    task = task_export.export_longTask.apply_async((jsonBase64, 1))

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            export_longTask_task = task_export.export_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = export_longTask_task.state
            #print(state_)
            #response['state'] = state_
            response['celeryID'] = export_longTask_task.id
            if state_ == 'PROGRESS':
                response['dbName'] = task.info.get('dbName').strip('\n')
                response['tblName'] = task.info.get('tblName').strip('\n')
                response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
                response['status'] = '1'
                break

            #####20180615, citc add#####################################################
            if state_ == 'FAIL_CELERY':
                errMsg = task.info.get('errMsg')
                log_time.printLog(errMsg)
                response['errMsg'] = errMsg
                response['status'] = '-1'
                break

            #####2018014, citc add#####################################################
            if state_ == 'FAIL_SPARK':
                #print 'fail_____'
                errMsg = task.info.get('errTable')
                log_time.printLog(errMsg)
                response['errMsg'] = errMsg
                response['status'] = '-1'
                break
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['errMsg'] ='Celery job fail'
                response['status'] = '-1'
                break

    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))


#update:20180622
@app.route('/getServerFolder', methods=['POST'])
def getServerFolder():
    log_time = GetLogTime('getServerFolder')
    log_time.printLog("Start getServerFolder")

    #return json
    response = dict()
    response['status'] = 1

    # get information
    try:
        data_raw = request.get_json()
        schema = jsonBase64Schema()
        data = loadJson(data_raw, schema)
        if data is None:
            err_msg = "<p>Json file error '%s'</p>" % data_raw
            log_time.printLog(err_msg)
            return err_msg, 405
        jsonBase64 =  data["jsonBase64"]

        jsonAll = getJsonParser(jsonBase64) # projID, projStep, projName
        log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
        log_time.printLog(jsonAll)

        if isinstance(jsonAll, str):
            errMsg = 'getJsonParer_error: ' + str(jsonAll)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            base64_return = encodeDic(response)
            return make_response(jsonify({'jsonBase64': base64_return}))

        projID = jsonAll['projID']
        projStep = jsonAll['projStep']
        projName = jsonAll['projName']
    except Exception as e:
        errMsg = 'getJsonParer_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        base64_return = encodeDic(response)
        return make_response(jsonify({'jsonBase64':base64_return}))

    # check projStep
    if projStep != 'getServerFolder':
        errMsg = 'celery_import_error_projStep_is_not_import'
        response['status'] = -1
        response['errMsg'] = "Mysql_connect_error_" + errMsg
        log_time.printLog(response['errMsg'])
        base64_return = encodeDic(response)
        return make_response(jsonify({'jsonBase64':base64_return}))

    # connect to mysql
    try:
        #combine commands
        #serverPath = "/user/itribd/import"
        #serverPath = "hdfs://Aquila-nn2.citc.local/user/gau/import"

        type_ = 'local'
        serverPath = getConfig().getImportPath(type_)
        filePath = os.path.join(serverPath, projName, '*/*')
        if type_ == 'hdfs':
            cmdStr = 'hadoop fs -stat "%n" ' + filePath
        else:
            cmdStr = 'stat --format "%n" ' + filePath
        #print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        #print(cmdStr)
        #print(filePath)

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=False)


    except Exception as e:
        errMsg = 'ssh_connect_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        base64_return = encodeDic(response)
        return make_response(jsonify({'jsonBase64':base64_return}))

    # collect server folder
    try:
        folders = []
        for line in stdout.readlines():
            log_time.printLog(line)
            folders.append(line.strip('\n'))
            #folders.append(line[:-1])
        response['folders'] = ';'.join(folders)


    except Exception as e:
        errMsg = 'collect_server_folder_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = "Mysql_connect_error_" + errMsg
        log_time.printLog(response['errMsg'])
        base64_return = encodeDic(response)
        return make_response(jsonify({'jsonBase64':base64_return}))

    if len(response['folders']) == 0:
        response['status'] = -1
        response['errMsg'] = "Cannot find any files in this project"
        log_time.printLog(response['errMsg'])
        base64_return = encodeDic(response)
        return make_response(jsonify({'jsonBase64':base64_return}))

    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))
    #return make_response(jsonify(response))


#update 20180615
@app.route('/ImportFile', methods=['POST'])
def ImportFile():
    log_time = GetLogTime('ImportFile')
    log_time.printLog("Start ImportFile")

    ts0 = time.time()
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405

    jsonBase64 =  data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64)))

    task = task_import.import_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['sparkAppID'] = ''#str
    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'import'#str (select, gen, join, distinct,single k checking,export,import)
    response['dbName'] = ''#str
    response['tblNames'] = ''#str


    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            import_longTask_task = task_import.import_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = import_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = import_longTask_task.id
            if state_ == 'PROGRESS':
                if task.info.get('sparkAppID') is None:
                    #response['err'] ='spark job fail'
                    response['errMsg'] ='spark context fail'
                    response['status'] = '-1'
                    log_time.printLog(response['errMsg'])
                    break

                response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
                response['dbName'] = task.info.get('dbName').strip('\n')
                response['tblNames'] = task.info.get('tblNames').strip('\n')
                response['status'] = '1'
                break

            #####20180615, citc add#####################################################
            if state_ == 'FAIL_CELERY':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break

            #####2018014, citc add#####################################################
            if state_ == 'SparkError':
                response['errMsg'] = task.info.get('errTable')
                response['sparkAppID'] = task.info.get('sparkAppID')
                log_time.printLog(response['errMsg'])
                response['status'] = '-1'
                break
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break

            if state_ == states.FAILURE:
                #print 'fail_____'
                try:
                    errMsg = task.info.get('errMsg')
                    response['errMsg'] = errMsg
                    log_time.printLog(errMsg)
                    response['status'] = '-1'
                    break
                except Exception as e:
                    response['errMsg'] = str(e)
                    response['status'] = '-1'
                    break

    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))


#update:20180614
@app.route('/checkTemplete', methods=['POST'])
def checkTemplete():
    log_time = GetLogTime('checkTemplete')
    log_time.printLog("Start checkTemplete")

    #return json
    response = dict()
    response['status'] = 1
    response['errMsg'] = None
    try:
        data_raw = request.get_json()
    except Exception as e:
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405
    jsonBase64 =  data["jsonBase64"]

    jsonAll = getJsonParser(jsonBase64)
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(jsonAll)

    # check mainInfo
    schema = getCheckTempleteSchema()
    data = loadJson(jsonAll['mainInfo'],schema) # return None if error
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % jsonAll['mainInfo']
        log_time.printLog(err_msg)
        return err_msg, 405

    userRulePath = data['userRule']

    #check if file exist
    if (os.path.isfile(userRulePath)) == False:
        response['status'] = -1
        response['errMsg'] = 'celery_gen_error_file_not_found: '+userRulePath
        log_time.printLog(response['errMsg'])
        return make_response(jsonify(response))

    # get user rule
    try:
        autoGen, autoGenValue, level, userRule = getUserRule(userRulePath)
    except Exception as e:
        response['status'] = -1
        response['errMsg'] = 'getUserRule error: ' + str(e)
        log_time.printLog(response['errMsg'])
        return make_response(jsonify(response))

    if autoGen == 0:
        response['status'] = -1
        response['errMsg'] = 'celery_gen_error_getSqlString_getGenUdf: '+ autoGenValue
        log_time.printLog(response['errMsg'])
        return make_response(jsonify(response))


    # get replace path
    try:
        replacePath = getReplacePath(userRule, 0)
    except Exception as e:
        response['status'] = -1
        response['errMsg'] = 'getReplacePath error: ' + str(e)
        log_time.printLog(response['errMsg'])
        return make_response(jsonify(response))


    if replacePath[:18] == 'checkTemplete_error':
        response['status'] = -1
        response['errMsg'] = 'gen_error_getSqlString_getGenUdf_' + replacePath
        log_time.printLog(response['errMsg'])
    else:
        response['userRule'] = replacePath

    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))

#update:20180614
@app.route('/Generalization_async', methods=['POST'])
def Generalization_async():
    log_time = GetLogTime('Generalization_async')
    log_time.printLog("Start Generalization_async")

    ts0 = time.time()
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405

    jsonBase64 = data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64)))

    task = task_getGenTbl.generalization_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['sparkAppID'] = ''#str
    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'gen'#str (select, gen, join, distinct,single k checking,export,import)
    response['dbName'] = ''#str
    response['tblName'] = ''#str

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            generalization_longTask_task = task_getGenTbl.generalization_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = generalization_longTask_task.state
            #print state_
            #response['state'] = state_
            response['celeryID'] = generalization_longTask_task.id
            #print(state_)
            if state_ == 'PROGRESS':
                if task.info.get('sparkAppID') is None:
                    #response['err'] ='spark job fail'
                    response['errMsg'] ='spark context fail'
                    response['status'] = '-1'
                    break

                response['sparkAppID'] =task.info.get('sparkAppID').strip('\n')
                response['dbName'] = task.info.get('dbName').strip('\n')
                response['tblName'] = task.info.get('tblName').strip('\n')
                response['status'] = '1'
                log_time.printLog(response)
                break

            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break

            if state_ == 'FAIL_CELERY':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break

            if state_ == 'FAIL_SPARK':
                #print 'fail_____'
                errMsg = task.info.get('errTable')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break

            if state_ == states.FAILURE:
                #print 'fail_____'
                try:
                    errMsg = task.info.get('errMsg')
                    response['errMsg'] = errMsg
                    log_time.printLog(errMsg)
                    break
                except Exception as e:
                    response['errMsg'] ='Celery job fail: {0}'.format(str(e))
                    break

    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))


@app.route('/getDistinctData_async', methods=['POST'])
def getDistinctData_async():
    log_time = GetLogTime('getDistinctData_async')
    log_time.printLog("Start getDistinctData_async")

    ########################################
    jarFileName = '/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    try:
        input_ = request.get_json()
        log_time.printLog(input_)
        log_time.printLog('***request : '+str(request))
        log_time.printLog(request.form.to_dict('records'))
        log_time.printLog(request.args.to_dict('records'))


    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        log_time.printLog(errMsg)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(input_, schema)

    if data is None:
        err_msg = "<p>Json file error</p>"
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64__)))

    task = task_getDistinctData.getDistinctData_longTask.apply_async((jsonBase64__, jarFileName))

    response = dict()
    response['jobID'] = ''
    response['sparkAppID'] = ''
    response['celeryID'] = ''
    response['status'] = ''
    response['errMsg'] = ''
    response['projStep'] = 'distinct'
    response['dbName'] = ''
    response['tblName'] = ''

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            dis_longTask_task = task_getDistinctData.getDistinctData_longTask.AsyncResult(task.id)
            #print dis_longTask_task
            state_ = dis_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = dis_longTask_task.id
            #print(state_)
            if state_ == 'PROGRESS':
                if task.info.get('sparkAppID') is None:
                    response['errMsg'] ='spark job fail'
                    response['status'] = '-1'
                    break

                response['sparkAppID'] = task.info.get('sparkAppID').strip()
                response['jobID'] = task.info.get('jobName').strip()
                response['status'] = '1'
                response['dbName'] = task.info.get('dbName').strip()
                response['tblName'] = task.info.get('tblName').strip()
                response['outTblName'] = splitSymbol(task.info.get('outTblNames'))
                #response['cols'] = task.info.get('cols').strip()
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                response['errMsg'] ='celery job fail'
                break
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))



@app.route('/getJoinData_async', methods=['POST'])
def getJoinData_async():
    log_time = GetLogTime('getJoinData_async')
    log_time.printLog("Start getJoinData_async")

    ########################################
    jarFileName='/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    app_ID = 99999

    try:
        input_ = request.get_json()
        #print input_
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(input_, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % app_ID
        log_time.printLog(err_msg)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64__)))

    task = task_getJoinData.getJoinData_longTask.apply_async((jsonBase64__, jarFileName))

    response = dict()
    response['jobID'] = ''
    response['sparkAppID'] = ''
    response['celeryID'] = ''
    response['status'] = ''
    response['errMsg'] = ''
    response['projStep'] = 'join'
    response['dbName'] = ''
    response['tblName'] = ''

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            join_longTask_task = task_getJoinData.getJoinData_longTask.AsyncResult(task.id)
            state_ = join_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = join_longTask_task.id
            #print(state_)
            if state_ == 'PROGRESS':
                if task.info.get('sparkAppID') is None:
                    response['errMsg'] ='spark job fail'
                    response['status'] = '-1'
                    break

                response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
                response['jobID'] = task.info.get('jobName').strip('\n')
                response['status'] = '1'
                response['dbName'] = splitSymbol(task.info.get('dbName'))
                response['tblName'] = splitSymbol(task.info.get('tblName'))
                response['outTblName'] = task.info.get('outTblName').strip('\n')
                log_time.printLog(response)
                #response['cols'] = splitSymbol(task.info.get('cols'))
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                response['errMsg'] ='celery job fail'
                break
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64':base64_return}))



@app.route('/kchecking_async', methods=['POST'])
def kchecking_async():
    log_time = GetLogTime('kchecking_async')
    log_time.printLog("Start kchecking_async")

    ts0 = time.time()
    app_ID=99999
    try:
        sparkTest = request.get_json()
        log_time.printLog(sparkTest)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(sparkTest, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % app_ID
        return err_msg, 405

    base64_ = data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(base64_))
    log_time.printLog(json.loads(base64.b64decode(base64_)))

    task = task_getKchecking.kchecking_longTask.apply_async((base64_,1))
    #############################################################################

    response = dict()
    #response['state'] = state
    ##########################################
    # Add 20180615############################

    response['sparkAppID'] = ''
    response['celeryID'] = ''
    response['status'] = ''
    response['errMsg'] = ''
    response['projStep'] = 'kchecking'
    response['dbName'] = ''
    response['tblName'] = ''

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            kchecking_longTask_task = task_getKchecking.kchecking_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = kchecking_longTask_task.state
#            print state_
            response['state'] = state_
            response['celeryID'] = kchecking_longTask_task.id
#            print state_
            if state_ == 'PROGRESS':
                if task.info.get('sparkAppID') is None:
                    response['errMsg'] ='spark context fail'
                    response['status'] = '-1'
                    break

                response['sparkAppID'] = task.info.get('sparkAppID')[:-1]
                response['tblName'] = task.info.get('tblName')[:-1]
                response['dbName'] = task.info.get('dbName')[:-1]
                response['status'] = '1'
                response['finaltblName'] = task.info.get('finaltblName')[:-1]

                break

            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                response['err'] ='spark job fail'
                break
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break

    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))

@app.route('/uidEnc_async', methods=['POST'])
def uidEnc_async():
    log_time = GetLogTime('uidEnc_async')
    log_time.printLog("Start uidEnc_async")

    ts0 = time.time()
    app_ID=99999
    sparkTest = request.get_json()
    log_time.printLog(sparkTest)
    schema = tableInfoSchema()

    data = loadJson(sparkTest, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % app_ID
        return err_msg, 405

    dbName =  data["dbName"]
    tblName = data["tableName"]
    colNames_=data["colNames"]
    #####2018014, citc trace#####################################################
    task = task_uid_enc.uidEnc_longTask.apply_async((dbName, tblName, colNames_))
    #############################################################################

    response = dict()

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            kcheck_longTask_task = task_uid_enc.uidEnc_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = kcheck_longTask_task.state
            #print state_
            #response['state'] = state_
            response['celeyId'] = kcheck_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                if task.info.get('jobID') is None:
                    response['err'] ='spark job fail'
                    break
                if task.info.get('kTable') is None:
                    response['err'] ='spark job fail'
                    break
                response['spark_jobID'] =task.info.get('jobID')
                response['kTable'] =task.info.get('kTable')
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break

            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                err = task.info.get('err')
                response['err'] = err
                #response['err'] ='spark job fail'
                break
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break

    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)
    return make_response(jsonify(response))



@app.route('/kcheck_async', methods=['POST'])
def kcheck_async():
    log_time = GetLogTime("kcheck_async")
    log_time.printLog("Start kcheck_async")

    ########################################
    jarFileName='/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    app_ID=99999
    sparkTest = request.get_json()
    log_time.printLog(sparkTest)
    schema = tableInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(sparkTest, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % app_ID
        return err_msg, 405

    dbName =  data["dbName"]
    tblName = data["tableName"]
    colNames_=data["colNames"]
    task = tasks.kcheck_longTask.apply_async((dbName, tblName, colNames_, jarFileName))

    response = dict()
    #response['state'] = state

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            kcheck_longTask_task = tasks.kcheck_longTask.AsyncResult(task.id)
            state_ = kcheck_longTask_task.state
            #response['state'] = state_
            response['celeyId'] = kcheck_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                if task.info.get('jobID') is None:
                    response['err'] ='spark job fail'
                    break
                #if task.info.get('kTable') is None:
                #    response['err'] ='spark job fail'
                    break
                response['spark_jobID'] =task.info.get('jobID')
                #response['kTable'] =task.info.get('kTable')
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                response['err'] ='celery job fail'
                break
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)
    return make_response(jsonify(response))


def on_raw_message(body):
    print(body)


@app.route('/park_task/<task_id>', methods=['GET'])
def check_task_status(task_id):
    log_time = GetLogTime("check_task_status")
    log_time.printLog("Start check_task_status")

    task = tasks.kcheck_longTask.AsyncResult(task_id)
    state = task.state
    response = dict()
    response['state'] = state

    if state == "PROGRESS":
        if task.info.get('mainInfo') is not None:
            response['mainInfo'] = task.info.get('mainInfo')

    elif state == states.SUCCESS:
        log_time.printLog("check_task_status___SUCCESS")
        response['result'] = task.get()
    elif state == states.FAILURE:
        try:
            response['error'] = task.info.get('error')
        except Exception as e:
            response['error'] = 'Unknown error occurred'

    log_time.printLog(response.get('state'))
    log_time.printLog(response)
    return make_response(jsonify(response))

@app.route('/MLutility_async', methods=['POST'])
def MLutility_async():
    print("Start MLutility_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        #print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405
    #result = schema.load(data_raw)
    #pprint(result.data)
    #print (type(data))
    # pprint(data)
    #print data["dbName"]
    #print data["tableName"]

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    ############citc add, 20181122###
    #1projName = data["projName"]
    #2fileName =  data["fileName"]
    #3keyName_ = data["keyName"]
    # tarCol = data["tarCol"] #1212:pei   
    # genBool = data["genBool"]   
    #4colNames_=data["colNames"]    
    #5print (colNames_)
    ###1128:pei
    # sampleBool = data["sampleBool"] 
    #################################

    #####20181121, citc trace#####################################################
    # task = task_train_feature.train_feature_longTask.apply_async((fileName, tarCol, genBool, colNames_, sampleBool))
    # task = task_getMLutility.getMLutility_longTask.apply_async((fileName, genBool, colNames_, sampleBool)) #1212:pei
    #task = task_getMLutility.getMLutility_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_getMLutility.getMLutility_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            MLutility_longTask_task = task_getMLutility.getMLutility_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = MLutility_longTask_task.state
            print (state_)
            #response['state'] = state_
            #response['celeryId'] = MLutility_longTask_task.id
            if state_ == 'PROGRESS':
                # if task.info.get('jobID') is None:
                #     response['err'] ='spark job fail'
                #     break
                
                #if task.info.get('verify') is None:
                #    response['err'] ='verify job fail'
                #    break   


                #if task.info.get('kTable') is None:
                #    response['err'] ='spark job fail'
                #    break    

                #response['PID'] = task.info.get('PID')
                response['celeryId'] = task.info.get('celeryId')
                response['projName'] = task.info.get('projName')
                #response['targetCols'] = task.info.get('targetCols')
                response['projStep'] = 'MLutility'
                response['userID'] = task.info.get('userID')
                response['projID'] = task.info.get('projID')
                response['sparkAppID'] = task.info.get('sparkAppID')
                response['status'] = task.info.get('status')
                response['errMsg'] = task.info.get('errMsg')
                print(response)
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                response['err'] ='spark job fail'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break;    
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    #print 'state_ is'
    #print state_ (SUCCESS)
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))



@app.route('/getRisk_async', methods=['POST'])
def getRisk_async():
    print("Start getRiskAnalysis_async")
    
    log_time = GetLogTime('getRisk_async')

    log_time.printLog("Start getRiskAnalysis_async")
    log_time.printLog("Start getRisk_async")

    ts0 = time.time()

    #下面紀錄JSON擷取方法
    #-------------------------------------------------------
    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    schema = jsonBase64Schema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405

    jsonBase64 =  data["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64)))
    #-------------------------------------------------------
    #20200208更新回傳前端頁面資訊
    jsonfile = json.loads(base64.b64decode(jsonBase64))
    projStep = jsonfile['projStep']
    dbName = jsonfile['projName']
    #maininfo = jsonfile['mainInfo']
    #maininfoDIC = maininfo[0]
    #dbName = maininfoDIC['dbname']




    #下面這段執行task
    #=====================================================
    task = task_getRiskAnalysis.getRiskAnalysis_longTask.apply_async((jsonBase64,1)) #1224:pei
    #=====================================================
    
    response = dict()
    
    #20200208更新回傳前端頁面資訊
    #20200416, citc modified, for multi tables 
    response['sparkAppID'] = ''#str
    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = projStep#str 
    response['dbName'] = dbName#str
    
    log_time.printLog("response = {0}".format(response))

    #下面這段執行RiskAnalysis_longTask_task
    #-------------------------------------------------------


    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20200208, citc trace#####################################################
            RiskAnalysis_longTask_task = task_getRiskAnalysis.getRiskAnalysis_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = RiskAnalysis_longTask_task.state
            #print (state_)
            #log_time.printLog("------------state_ = {0}".format(state_))
            #response['state'] = state_
            response['celeryID'] = RiskAnalysis_longTask_task.id

            #####20200208, citc trace#####################################################
            if state_ == 'PROGRESS':
                log_time.printLog("=======in PROGRESS=========response = {0}".format(response))
                #if task.info.get('sparkAppID') is None:
                #    response['errMsg'] ='spark job fail'
                #    response['status'] = '-1'
                #    break

                response['sparkAppID'] = task.info.get('sparkAppID').strip()
                response['status'] = '1'

                #response['cols'] = task.info.get('cols').strip()
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                log_time.printLog("response = {0}".format(response))
                break
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                response['errMsg'] ='celery job fail'
                break
          

            #####20180615, citc add#####################################################
            if state_ == 'FAIL_CELERY':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break

            #####2018014, citc add#####################################################
            if state_ == 'SparkError':
                response['errMsg'] = task.info.get('errTable')
                response['sparkAppID'] = task.info.get('sparkAppID')
                log_time.printLog(response['errMsg'])
                response['status'] = '-1'
                break
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                break

            if state_ == states.FAILURE:
                #print 'fail_____'
                try:
                    errMsg = task.info.get('errMsg')
                    response['errMsg'] = errMsg
                    log_time.printLog(errMsg)
                    response['status'] = '-1'
                    break
                except Exception as e:
                    response['errMsg'] = str(e)
                    response['status'] = '-1'
                    break
    #-------------------------------------------------------

    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify(response))
   

#20200617
@app.route('/mac_async', methods=['POST'])
def mac_async():
    log_time = GetLogTime("mac_async")
    log_time.printLog("Start mac_async")

    ########################################
    jarFileName='/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    app_ID=99999

    try:
        input_ = request.get_json()
        log_time.printLog(input_)
        # response = dict()
        # response['Msg'] = input_
        # return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    # print (input_)
    # log_time.printLog(input_)
    # schema = jsonBase64Schema()
    # data = loadJson(input_, schema)
    # log_time.printLog(data)
    # print (data)


    tblName = input_["tablename"]
    key = input_["key"]
    sep = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]

    # sparkTest = request.get_json()
    # log_time.printLog(sparkTest)
    # schema = tableInfoSchema()
    # #dbName = fields.Str()
    # #tableName = fields.Str()
    # data = loadJson(sparkTest, schema)
    # if data is None:
    #     err_msg = "<p>Json file error '%s'</p>" % app_ID
    #     return err_msg, 405

    # dbName =  data["dbName"]
    # tblName = data["tableName"]
    # colNames_=data["colNames"]
    task = task_udfMacUID.mac_longTask.apply_async((tblName,key,sep,columns_mac,projName,projID,dataHash))

    response = dict()
    #response['state'] = state
    # response['sparkAppID'] = ''
    # response['celeryID'] = ''
    # response['status'] = ''
    # response['errMsg'] = ''
    response['projStep'] = 'data_mac'
    # response['dbName'] = ''
    # response['tblName'] = ''

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            mac_longTask_task = task_udfMacUID.mac_longTask.AsyncResult(task.id)
            state_ = mac_longTask_task.state
            response['state'] = state_
            response['celeyId'] = mac_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                if task.info.get('jobID') is None:
                    response['err'] ='spark job fail'
                    break
                #if task.info.get('kTable') is None:
                #    response['err'] ='spark job fail'
                    # break
                response['status'] = '1'
                response['spark_jobID'] =task.info.get('jobID')
                #response['kTable'] =task.info.get('kTable')
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                response['err'] ='celery job fail'
                break
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)
    return make_response(jsonify(response))




