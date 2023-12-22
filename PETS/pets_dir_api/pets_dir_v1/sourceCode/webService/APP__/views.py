#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import os
import json
import requests #pip install requests
import base64
from app import app
from . import tasks,SparkJobManager

##20220829 add
# from . import task_removeProject_Data

# from . import task_export,task_import,task_getGenTbl,task_uid_enc,task_createProject, task_getReport, task_setJsonProfile
# from . import task_export,task_import,task_uid_enc,task_createProject, task_getReport, task_CheckProjStatus,task_DeIdAsyncMac,task_export_PETs,task_import_PETs
# from . import task_uid_enc,task_createProject, task_setJsonProfile,task_getGenTbl,task_getKchecking, task_DeIdAsyncAES,task_Join,task_multipleHash
# from . import task_DeIdGenAsync,task_udfAESUID, task_udfMacUID, task_GetConfigList, task_GetconfigData, task_UpdateConfigData, task_CheckProjStatus, task_DeIdAsync, task_HashMacAsync,task_getMLutility
# from . import task_exportData_InterAgent,task_getGenTbl_InterAgent,task_getReport_InterAgent
#20230328
# from . import task_udfMacUIDImport
from . import task_multipleHash
from flask_redis import FlaskRedis
from flask import render_template, request, jsonify,make_response
from celery import states
from module.JsonSchema import rmDataByProjNameSchema, jsonBase64Schema,loadJson,tableInfoSchema,getCheckTempleteSchema,jobIDSchema,getExporDataSchema
from module.base64convert import getJsonParser, encodeDic
from module.checkTemplete import getReplacePath, getUserRule
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs
import pandas as pd
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
# app.config["SWAGGER"] = {"title": "DEMO-SWAGGER-Deid", "uiversion": 3}
app.config["SWAGGER"] = {"uiversion": 3}

swagger_config = {
    "headers": [('Access-Control-Allow-Origin', '*')],        #('Access-Control-Allow-Origin', '*'),
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
# def add_2_numbers(num1, num2):
#     output = {"sum_of_numbers": 0}
#     sum_of_2_numbers = num1 + num2
#     output["sum_of_numbers"] = sum_of_2_numbers
#     return output

# @app.route("/add_2_numbers", methods=["POST"])
# @swag_from("swagger_yml/swagger_add.yml")
# def add_numbers():
#     input_json = request.get_json()
#     print('###############################################')
#     print(input_json)
#     try:
#         num1 = int(input_json["x1"])
#         num2 = int(input_json["x2"])
#         res = add_2_numbers(num1, num2)
#     except:
#         res = {"success": False, "message": "Unknown error"}

#     return json.dumps(res)
################################
#get ip config for openapi
#web_ip,web_port,flask_ip,flask_port,hsm_key = getConfig().getOpenAPI()
#web_ip = str(web_ip)
#web_port = str(web_port)
#flask_ip = str(flask_ip)
#flask_port = str(flask_port)
##20220301, citc------------------------d
#hsm_key = str(hsm_key)


################################
def check_appstatus(proj_id, Application_Name):

    #test_result = ""
    Progress=""
    Progress_State=""
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        #response = dict()
        #errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        #response['status'] = -1
        #response['errMsg'] = errMsg
        #log_time.printLog(errMsg)
        #Progress="99999"
        #Progress="199999"+str(e)
        #return Progress, Progress_State
        raise Exception("mysql conn err:"+str(e))

        #return make_response(jsonify(response))
    try: # fetch parameter: pid
        #sqlStr = "SELECT Progress  FROM `spark_status`.`appStatus` where proj_id like '{}';".format(proj_id,Application_Name)
        sqlStr = "SELECT Progress  FROM `spark_status`.`appStatus` where proj_id like '{}' AND Application_Name like '{}';".format(proj_id, Application_Name)
        Progress="18888"
        print("in check_appstatus: sqlStr="+sqlStr)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            Progress = resultCheck["fetchall"][0]['Progress']
        Progress="28888"+Progress
        sqlStr = "SELECT Progress_State  FROM `spark_status`.`appStatus` where proj_id like '{}' AND Application_Name like '{}';".format(proj_id, Application_Name)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        Progress="38888"
        if int(resultCheck['result'])==1:
            Progress_State = resultCheck["fetchall"][0]['Progress_State']
        Progress="48888"
        check_conn.close()
        print("in check_appstatus: Progress_State="+Progress_State)
        Progress = "100"
        return Progress, Progress_State

    except Exception as e:
        #response = dict()
        #errMsg = 'fetch progress fail: - %s:%s' %(type(e).__name__, e)
        #response['status'] = -1
        #response['errMsg'] = errMsg
        #return make_response(jsonify(response))
        #Progress=Progress+str(e)
        #Progress="3199999"
        #return Progress, Progress_State
        raise Exception("mysql select err:"+str(e))

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
    print(resultSampleData)
    if resultSampleData['result'] == 1:
        print("update mysql: SUCCESS!")
        #conn.close()
        return None
    else:
        response = dict()
        errMsg = 'updateToMysql_config fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -98
        response['errMsg'] = errMsg
        return make_response(jsonify(response))



###20201130:[同步]刪除專案:​/api​/WebAPI​/DeleteProject: project_id
#@app.route("/delProject_Sync", methods=["POST"])
#@swag_from("swagger_yml/DeleteProject.yml")
def DeleteProject_Sync():
    log_time = GetLogTime('DeleteProject_Sync')
    log_time.printLog("Start DeleteProject_Sync")
    ts0 = time.time()
    response = dict()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Json format error: ' + str(e) # 210219: curl sent "", without dict()
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -2
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    #get parameter
    try:
        p_dsname =  data_raw['p_dsname'] #projName:en
    except Exception as e:
        response = dict()
        errMsg = 'Missing parameter: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))    

    # get the parameter:pid in mysql
    time.sleep(5)
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'Sql fail: ConnectToMysql fail- %s:%s' %(type(e).__name__, e)
        response['status'] = -98
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try: # fetch parameter: pid
        sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project` where project_name like '{}';".format(p_dsname)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            pid = resultCheck["fetchall"][0]['project_id']
            response['pid'] = int(pid)
        check_conn.close()
    except Exception as e:
        errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
        errMsg = 'Sql fail: fetch data fail- %s:%s' %(type(e).__name__, e)
        response['status'] = -98
        log_time.printLog(errMsg)
        return make_response(jsonify(response))     
        # FOR Mac API:  /api/WebAPI/hash
    try:
        DeleteProject_para = {
                "project_id": int(pid)
                }
        print('DeleteProject_para: ', DeleteProject_para)            
        response_get = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/DeleteProject", params=DeleteProject_para)
        print(response_get.url)
        # response_dic = response_get.json()
        # print("response_get: ",response_dic)
        # response_dic = response_g.json()
        # print("DeleteProject JSON: ",response_dic)
        response['status']='1' #response_dic['state']
        #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'Unknown error: ' + str(e) #requests.get fail
        response['status'] = -99
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))   

    ts1 = time.time()
    response['dataraw']=data_raw
    response['Project Status'] = 'DeleteProject'
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))    

####20201201:[同步]重設專案:/api/WebAPI/CancelProjectStatus: project_id, pname, project_status:3
#@app.route("/cancelProjectStatus_Sync", methods=["POST"])
@swag_from("swagger_yml/CancelProject.yml")
def CancelProjectStatus_Sync():
    log_time = GetLogTime('CancelProject_Sync')
    log_time.printLog("Start CancelProject_Sync")
    ts0 = time.time()
    response = dict()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Json format error: ' + str(e) # 210219: curl sent "", without dict()
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -2
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    #get parameter
    try:
        p_dsname =  data_raw['projName'] #projName:en
    except Exception as e:
        response = dict()
        errMsg = 'Missing parameter: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))    

    # get the parameter:pid in mysql
    time.sleep(5)
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        response = dict()
        errMsg = 'Sql fail: ConnectToMysql fail- %s:%s' %(type(e).__name__, e)
        response['status'] = -98
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
        response = dict()
        errMsg = 'fetch data fail: project name or project id not found - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))     
    curren_host = get_host_name()
    if "gethostname err" in curren_host:
        return test_get_response("get host name error"+curren_host)
    #else:
        #return test_get_response("host name = "+curren_host)
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

    try:
        CancelProject_para = {
                "project_id": int(pid),
                "pname":p_dsname,
                "project_status":str(3)
                }
        print('CancelProject_para: ', CancelProject_para)            
        
        response_get = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/CancelProjectStatus", params=CancelProject_para,verify=False)
        response_dic = response_get.json()
        print("CancelProject JSON: ",response_dic)
        response['status']='1' #success
        # return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'Unknown error: ' + str(e) #requests.get fail
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))   

    ts1 = time.time()
    response['dataraw']=data_raw
    response['Project Status'] = 'CancelProject'
    response['status'] = 1
    response['errMsg'] = ''
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 

#0930 swagger: 呼叫非同步hash自動化的flask API: /HashMac_Async
#swagger: create project > hashmac 
#@app.route("/setHashMac_Async", methods=["POST"])
# @swag_from("swagger_yml/HashMac_Async.yml")
def HashMac_Async():
    log_time = GetLogTime('HashMac_Async')
    log_time.printLog("Start HashMac_Async")

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
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName

        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or hashkey == '' or sep_ == '' or columns_mac == '' or dataHash == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))              


    response = {}
    # CheckProjStatus:
    try:
        HashMacAsync_para = {
            "p_dsname": p_dsname, 
            "pname": pname, 
            "powner": powner, 
            "prodesc": prodesc, 
            "hashTableName":hashTableName, 
            "hashkey":hashkey,
            "sep":sep_, 
            "columns_mac":columns_mac, 
            "projName": p_dsname, 
            "dataHash": dataHash ,
            "onlyHash": onlyHash
            }
        print('HashMacAsync_para: ', HashMacAsync_para)            
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/HashMacAsync", json=HashMacAsync_para,timeout=None)
        response_dic = response_g.json()
        print("HashMacAsync JSON: ",response_dic)
        response['HashMacAsync']=response_dic #response_dic['state']
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
    
    ts1 = time.time()
    response['dataraw']=data_raw
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))






#swagger: CheckProjStatus
#@app.route("/checkStatus_Sync", methods=["POST"])
@swag_from("swagger_yml/CheckProjStatus.yml")
def AutoCheckProjStatus_Sync():
    log_time = GetLogTime('AutoCheckProjStatus_Sync')
    log_time.printLog("Start AutoCheckProjStatus_Sync")

    ts0 = time.time()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Json format error: ' + str(e) # 210219: curl sent "", without dict()
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -2
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        p_dsname = data_raw['projName']
        powner =  '1'#data_raw['powner']
    except Exception as e:
        response = dict()
        errMsg = 'Missing parameter: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if p_dsname == '' or powner == '':
        response = dict()
        errMsg = 'Missing parameter: ' + str('Null parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    response = {}
    # CheckProjStatus:
    ##20220308, citc------------------------d
    print("##20220301, citc------HSM KEY ------------------d")
    curren_host = get_host_name()
    if "gethostname err" in curren_host:
        return test_get_response("get host name error"+curren_host)
    #else:
        #return test_get_response("host name = "+curren_host)
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
    try:
        CheckProjStatus_para = {
                "userID":powner, 
                "projName": p_dsname
                }
        print('CheckProjStatus_para: ', CheckProjStatus_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/CheckProjStatus", json=CheckProjStatus_para,timeout=None,verify=False)
        response_dic = response_g.json()
        print("CheckProjStatus JSON: ",response_dic)
        response['CheckProjStatus']=response_dic #response_dic['state']

    except Exception as e:
        response = dict()
        errMsg = 'Unknown error: ' + str(e) #requests.get fail
        response['status'] = -99
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
    
    ts1 = time.time()
    response['dataraw']=data_raw
    try:
        response['status'] = response_dic['status']
    except:
        response['status'] = 1
    try:
        response['errMsg'] = response_dic['errMsg']
    except:
        response['errMsg'] = ''
        #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#swagger: check report
#@app.route("/getReport_Sync", methods=["POST"])
@swag_from("swagger_yml/AutoReport.yml")
def AutoGetReport_Sync():
    log_time = GetLogTime('AutoGetReport_Sync')
    log_time.printLog("Start AutoGetReport_Sync")
    
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
        projName =  data_raw['projName'] #projName
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if projName == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #response = {}
    curren_host = get_host_name()
    if "gethostname err" in curren_host:
        return test_get_response("get host name error"+curren_host)
    #else:
        #return test_get_response("host name = "+curren_host)
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

    try:
        report_para = {'projName':projName}
        print('report_para: ', report_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/getReport_async", json=report_para,timeout=None,verify=False)
        response_dic = response_g.json()
        print("report_JSON: ",response_dic)
        #response['getReport']=response_dic #response_dic['state']
        response = response_dic 
        #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    ts1 = time.time()
    #response['dataraw']=data_raw
    #response['STATE'] = state_
    if response['report']['mainInfo'] == []:
        response['status'] = -1
    else:
        response['status'] = 1
    if response['report']['mainInfo'] == []:
        response['errMsg'] = 'fetch data fail'  
    else:
        response['errMsg'] = ''
    response['time_async'] = str(ts1-ts0)
    return make_response(jsonify(response))

#swagger: create project > hashmac 
#@app.route("/AutoDeId_AESHash", methods=["POST"])
# @swag_from("swagger_yml/HashAES.yml")
def AutoHashAES_Sync():
    log_time = GetLogTime('AutoHashAES_Sync')
    log_time.printLog("Start AutoHashAES_Sync")
    
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
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}
    # response['InsertProject_flag'] = "2"# "for export"
    #/api/WebAPI/InsertProject
    #step=1:create project > hash > import
    try:
        # InsertProject_para = { "p_dsname": p_dsname, "pinput": pinput, "pname": pname, "poutput": poutput, "powner": powner, "prodesc": prodesc } 
        # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  #原版
        InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc } 
        response_get = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para)
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

    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        else:
            error_insertproj ='系統寫入出現錯誤:檢查p_dsname是否重複使用'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
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
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash 
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
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

    # check hash status  (try)
    # progress = check_appstatus(128 , 'udfMacUID')
    progress = 0 #check_appstatus(pid , 'udfMacUID')
    while int(progress) != 100:
        try:
            time.sleep(15)
            progress, progress_state =  check_appstatus(pid, 'udfMacUID')
            if int(progress) == 100:
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
      
    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#cit, 20220308
def get_host_name():
    host_file = "/host_name"
    try:
        with open(host_file,'r') as fp:
            host_name= fp.read()
            host_name=host_name.strip()
            return host_name
    except Exception as e:
        return "gethostname err"+str(e)




#####citc, 20220302
###2022/02/24 getHSMKey
def getAESHSMKey(hsm_keydata_, hsm_url):
    #step1 read /config/developer.ini
    # 自訂表頭
    #hsm_keydata='E7FA33BC0DCB39FE182FAF7CE960A2B0BA63AFEEDC76D8A92AED52938AA06ABA' #read developini
    hsm_keydata = hsm_keydata_
    my_headers = {'Connection': 'close'}
    hashkey =''

    ut_host =  "darhcdp01"
    uat_host =  "tarhcdp01"
    prod_host =  "parhcdp01"



    try:
    
       hsm_para = {
         "ssoid": "CRM-LX-CDP-02",
         "keyIV": "",
         "keyName": "CRM-LX-CDP-02_KEK",
         "decryptMode": 4,
         "dataFormat": "hex",
         "data": hsm_keydata,
         "responseFormat": "hex"
        }

       print('Hash_para: ', hsm_para)
       response_g = requests.get("https://"+hsm_url,headers=my_headers, json=hsm_para,timeout=None)
       response_dic = response_g.json()
       print("hsm result JSON: ",response_dic)

       hashkey = response_dic['data']
    
    except Exception as e:
       print('hsm exception: ',str(e))

    return hashkey



#@app.route("/MacHashGroupImport_Sync", methods=["POST"])
@swag_from("swagger_yml/setHashMacGImport.yml")
def MacHashGroupImport_Sync():
    log_time = GetLogTime('MacHashGroupImport_Sync')
    log_time.printLog("Start MacHashGroupImport_Sync")
    
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
    
    # try: #connection SQL
    #     check_conn = ConnectSQL()
    # except Exception as e:
    #     errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))

    # if data_raw['hashkey'] == '':
    #     try: # fetch parameter: pid
    #         group_name =  data_raw['group_name']
    #         sqlStr = "SELECT  group_hashkey FROM `DeIdService`.`T_Group` where group_name like '{}';".format(group_name)
    #         resultCheck = check_conn.doSqlCommand(sqlStr)
    #         if int(resultCheck['result'])==1:
    #             hashkey = resultCheck["fetchall"][0]['group_hashkey']
    #         check_conn.close()
    #     except Exception as e:
    #         errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
    #         response['status'] = -1
    #         response['errMsg'] = errMsg
    #         log_time.printLog(errMsg)
    #         return make_response(jsonify(response))
    # else:
    #     hashkey = data_raw['hashkey']


    #get parameter
    try:
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']
        group_name =  data_raw['group_name']
        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = "Y" #data_raw['dataHash']
        onlyHash = "Y"
        userId = data_raw['userId']
        userAccount = data_raw['userAccount']
        # account = data_raw['member_account']
        # m_id = data_raw['member_id']


    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}


    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)


    pid = 999

    try:
        # if int(step) == 1:
            # InsertProject_para = { "p_dsname": p_dsname, "pinput": pinput, "pname": pname, "poutput": poutput, "powner": powner, "prodesc": prodesc } 
            # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  # 原版
        InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc ,'memberid': userId,'memberacc': userAccount} 
        print("InsertProject_para: ",InsertProject_para)

        response_get = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para, verify=False)
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

    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        else:
            error_insertproj ='系統寫入出現錯誤:檢查p_dsname是否重複使用'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
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
    



    
    try:
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash,
                "group_name":group_name,
                "userId":userId,
                "userAccount":userAccount
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/macgroupimport_async", json=Hash_para,timeout=None, verify=False)
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

    progress = 0 #check_appstatus(pid , 'udfMacUID')
    while int(progress) != 100:
        try:
            time.sleep(15)
            progress, progress_state =  check_appstatus(pid, 'udfMacUID')
            if int(progress) == 100:
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

    try: #API:ImportData
        ImportData_para = { "p_dsname": p_dsname, "pid": pid ,'memberid': userId,'memberacc': userAccount}
        print('ImportData_para: ',ImportData_para)
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/ImportData", params=ImportData_para,timeout=None, verify=False)
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


    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

#@app.route("/MacHashGroup_Async", methods=["POST"])
@swag_from("swagger_yml/setHashMacG.yml")
def MacHashGroup_Async():
    log_time = GetLogTime('MacHashG_Async')
    log_time.printLog("Start MacHashG_Async")
    
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
    
    # try: #connection SQL
    #     check_conn = ConnectSQL()
    # except Exception as e:
    #     errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))

    # if data_raw['hashkey'] == '':
    #     try: # fetch parameter: pid
    #         group_name =  data_raw['group_name']
    #         sqlStr = "SELECT  group_hashkey FROM `DeIdService`.`T_Group` where group_name like '{}';".format(group_name)
    #         resultCheck = check_conn.doSqlCommand(sqlStr)
    #         if int(resultCheck['result'])==1:
    #             hashkey = resultCheck["fetchall"][0]['group_hashkey']
    #         check_conn.close()
    #     except Exception as e:
    #         errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
    #         response['status'] = -1
    #         response['errMsg'] = errMsg
    #         log_time.printLog(errMsg)
    #         return make_response(jsonify(response))
    # else:
    #     hashkey = data_raw['hashkey']


    #get parameter
    try:
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']
        group_name =  data_raw['group_name']
        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = "Y" #data_raw['dataHash']
        onlyHash = "Y"
        userId = data_raw['userId']
        userAccount = data_raw['userAccount']
        # account = data_raw['member_account']
        # m_id = data_raw['member_id']


    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}


    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)


    pid = 999

    # try:
    #     # if int(step) == 1:
    #         # InsertProject_para = { "p_dsname": p_dsname, "pinput": pinput, "pname": pname, "poutput": poutput, "powner": powner, "prodesc": prodesc } 
    #         # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  # 原版
    #     InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc ,'memberid': userId,'memberacc': userAccount} 
    #     print("InsertProject_para: ",InsertProject_para)

    #     response_get = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para, verify=False)
    #     print(response_get.url)
    #     response_dic = response_get.json()
    #     print("response_get: ",response_dic)
    #     response['InsertProject_flag']=response_dic
    #         #print(response['InsertProject_flag'])
    #         #return make_response(jsonify(response))
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))

    # #check create project
    # try:
    #     if int(response['InsertProject_flag'])==1:
    #         pass
    #     elif int(response['InsertProject_flag'])==-5:
    #         error_insertproj = '專案名稱重複'
    #         errMsg = 'InsertProject fail: - %s' %(error_insertproj)
    #         response['errMsg'] = errMsg
    #         log_time.printLog(errMsg)
    #         response['status'] = response['InsertProject_flag']
    #         return make_response(jsonify(response))
    #     elif int(response['InsertProject_flag'])==-4:
    #         error_insertproj = '專案狀態錯誤'
    #         errMsg = 'InsertProject fail: - %s' %(error_insertproj)
    #         response['errMsg'] = errMsg
    #         log_time.printLog(errMsg)
    #         response['status'] = response['InsertProject_flag']
    #         return make_response(jsonify(response))
    #     else:
    #         error_insertproj ='系統寫入出現錯誤:檢查p_dsname是否重複使用'
    #         errMsg = 'InsertProject fail: - %s' %(error_insertproj)
    #         response['errMsg'] = errMsg
    #         log_time.printLog(errMsg)
    #         response['status'] = response['InsertProject_flag']
    #         return make_response(jsonify(response))
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))

    # # get the parameter:pid in mysql
    # time.sleep(5)
    # try: #connection SQL
    #     check_conn = ConnectSQL()
    # except Exception as e:
    #     errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))
    # try: # fetch parameter: pid
    #     sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project` where project_name like '{}';".format(p_dsname)
    #     resultCheck = check_conn.doSqlCommand(sqlStr)
    #     if int(resultCheck['result'])==1:
    #         pid = resultCheck["fetchall"][0]['project_id']
    #         response['pid'] = str(pid)
    #     check_conn.close()
    # except Exception as e:
    #     errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))
    




    try:
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash,
                "group_name":group_name,
                "userId":userId,
                "userAccount":userAccount
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/macgroup_async", json=Hash_para,timeout=None, verify=False)
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

    # progress = 0 #check_appstatus(pid , 'udfMacUID')
    # while int(progress) != 100:
    #     try:
    #         time.sleep(15)
    #         progress, progress_state =  check_appstatus(pid, 'udfMacUID')
    #         if int(progress) == 100:
    #             # progress = 100
    #             break;
    #         if progress_state == 'err':#int(progress) == 10:
    #             response = dict()
    #             errMsg = 'projstatus error: ' + "hash fail: No file?"
    #             response['status'] = -1
    #             response['errMsg'] = errMsg
    #             log_time.printLog(errMsg)
    #             return make_response(jsonify(response))            
    #             break;
    #     except Exception as e:
    #         #progress = 0
    #         pass

    # try: #API:ImportData
    #     ImportData_para = { "p_dsname": p_dsname, "pid": pid ,'memberid': userId,'memberacc': userAccount}
    #     print('ImportData_para: ',ImportData_para)
    #     response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/ImportData", params=ImportData_para,timeout=None, verify=False)
    #     response_dic = response_g.json()
    #     print("IMPORT DATA JSON: ",response_dic)
    #     response['ImportData_flag']=response_dic
    #     #return make_response(jsonify(response))
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))


    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

#@app.route("/AESDecryptGroup_Async", methods=["POST"])
@swag_from("swagger_yml/AESDecryptG_Async.yml")
def AESDecryptGroup_Async():
    log_time = GetLogTime('AESDecryptGroup_Async')
    log_time.printLog("Start AESDecryptGroup_Async")
    
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
    #return test_get_response("errMsg 1")
    #get parameter
    try:
        # pname = data_raw['pname'].encode("utf-8")
        # prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        group_name =  data_raw['group_name']
        #citc, 20220117
        hashkey = data_raw['hashkey']
        userId = data_raw['userId']
        userAccount = data_raw['userAccount']
        #return test_get_response("errMsg 2")
       #############################################################
        ##20220308, citc------------------------d
        print("##20220301, citc------HSM KEY ------------------d")
        curren_host = get_host_name()
        if curren_host == "":
            return test_get_response("get host name error")
        #else:
            #return test_get_response("host name = "+curren_host)    
        
        web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
        hsm_key = str(hsm_key)
        print("##20220301, citc------hsm_key = {}".format(hsm_key))
        if "HSM" in hashkey:
            print("----(AESDecrypt_Sync)--------citc HSM get key here -----------")
            hashkey = hsm_key
        ##20220302################################
        #hsm_key = getAESHSMKey(hsm_key,hsm_url)
        ################################

        

        hsm_key = str(hsm_key)

        ##20220302################################
        #hsm_key = getAESHSMKey(hsm_key,hsm_url)
        ################################

        
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -12
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -13
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -14
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}

    pid = 999 

    # FOR Mac API:  flask_port+"/aes_async"
    try:
        #citc, 20220117
        dataHash = "yes"
        onlyHash = "yes"
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash,
                "group_name":group_name,
                "userId":userId,
                "userAccount":userAccount 
                }
        print('Hash_para: ', Hash_para)    


        #citc, 20220117, ssl certificate 
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context        
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aesgroup_async", json=Hash_para,timeout=None, verify=False)
        #response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
        

        response_dic = response_g.json()
        print("HASH JSON: ",response_dic)
        response['HashMac']='1' #response_dic['state']
        #return make_response(jsonify(response))
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     response['status'] = -15
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))



    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#@app.route("/AESHashGroup_Async", methods=["POST"])
@swag_from("swagger_yml/AESHashG_Async.yml")
def AESHashGroup_Async():
    log_time = GetLogTime('AESHashGroup_Async')
    log_time.printLog("Start AESHashGroup_Async")
    
    ts0 = time.time()

    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -11
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    #get parameter
    try:
        # pname = data_raw['pname'].encode("utf-8")
        # prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']
        group_name =  data_raw['group_name']
        #for hash
        hashTableName = data_raw['hashTableName']

        #citc, 20220117
        hashkey = data_raw['hashkey']

        userId = data_raw['userId']
        userAccount = data_raw['userAccount']
        #############################################################
        ##20220308, citc------------------------d
        print("##20220301, citc------HSM KEY ------------------d")
        curren_host = get_host_name()
        if "gethostname err" in curren_host:
            return test_get_response("get host name error"+curren_host)
        #else:
            #return test_get_response("host name = "+curren_host)


        web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

        # hsm_key = str(hsm_key)

        # ##20220302################################
        # #hsm_key = getAESHSMKey(hsm_key,hsm_url)
        # ################################


        # print("##20220301, citc------hsm_key = {}".format(hsm_key))
        # if "HSM" in hashkey:
        #     print("----(AESHash_Sync)--------citc HSM get key here -----------")
        #     hashkey = hsm_key
        #############################################################

        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -12
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if powner == '' or p_dsname == '' or hashTableName == '' or columns_mac == '' or sep_ == '' or dataHash == '': # or hashkey == '' or columns_mac == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -13
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}

    pid = 999 

    # FOR Mac API:  flask_port+"/aes_async"
    progress_ = "1t1"
    try:

        #20220117 add
        onlyHash = "No" #for enc
        dataHash = "yes"

        Hash_para = {"tablename":hashTableName, 
                #citc, 20220117
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash,
                "group_name":group_name,
                "userId":userId,
                "userAccount":userAccount
                }
        print('Hash_para: ', Hash_para)   

        #citc, 20220117, ssl certificate 
        #import ssl
        #ssl._create_default_https_context = ssl._create_unverified_context  
        #cert_pem = "/app/app/devp/cert.pem"
        #key_pem = "/app/app/devp/key.pem"
        #ca_pem = "/app/app/devp/ca.pem"

        #return test_get_response("before requests.post")

        #response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None, cert=(cert_pem,key_pem), verify=ca_pem)
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aesgroup_async", json=Hash_para,timeout=None, verify=False)
        #return test_get_response("after requests.post")
 

        response_dic = response_g.json()
        #########citc###################
        print("HASH JSON_citc: ",response_dic)
        #################################
        response['HashMac']='1' #response_dic['state']
        #return make_response(jsonify(response))

    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -14
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try:
        response = dict()
        ts1 = time.time()
        # response['citc']="2"
        # response['citc2_progress_']=progress_
        response['dataraw']=data_raw
        #20220802 add
        response['result']=response_dic
        response['status'] = 1
        response['errMsg'] = ''
        #response['STATE'] = state_
        response['time_async'] =str(ts1-ts0)
        return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -15
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))    


#20231027
@app.route('/m_hash_async', methods=['POST'])
def m_hash_async():
    log_time = GetLogTime("m_hash_async")
    log_time.printLog("Start m_hash_async")

    ########################################
    jarFileName='/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    app_ID=99999

    try:
        input_ = request.get_json()
        log_time.printLog(input_)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))


    tblName = input_["tablename"]
    key = input_["key"]
    sep_ = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]
    onlyHash = input_["onlyHash"]
    AES_key = input_["AES_key"]
    AES_columns_mac = input_["AES_columns_mac"]

    try:
        task = task_multipleHash.multiplehash_longTask.apply_async((tblName,key,sep_,columns_mac,projName,projID,dataHash,onlyHash,AES_key,AES_columns_mac))

        response = dict()
        response['projStep'] = 'data_mac'

        if True:
            state_ = "test"
            while state_ != 'PROGRESS':
                mac_longTask_task = task_multipleHash.multiplehash_longTask.AsyncResult(task.id)
                state_ = mac_longTask_task.state
                response['state'] = state_
                response['celeyId'] = mac_longTask_task.id
                #print state_
                if state_ == 'PROGRESS':
                    response['status'] = '1'
                    response['spark_jobID'] =task.info.get('jobID')
                    break
                if state_ == states.SUCCESS:
                    break
                if state_ == states.FAILURE:
                    response['err'] ='celery job fail'
                    break
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
 
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)

    return make_response(jsonify(response))

#20231027
@app.route("/direct_enc_async", methods=["POST"])
@swag_from("swagger_yml/MultipleHash.yml")
def direct_enc_async():
    log_time = GetLogTime('direct_enc_async')
    log_time.printLog("Start direct_enc_async")
    
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
        # pname = data_raw['pname'].encode("utf-8")
        # prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        # p_dsname =  data_raw['projName'] #projName
        p_dsname = 'enc_output'
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hash_table_name']
        hashkey = data_raw['enc_key']
        sep_ = data_raw['sep']
        columns_mac = data_raw['mac_col']#dataHash是yes or Y 的話，一定要有值
        dataHash = "Y" #data_raw['dataHash']
        onlyHash = "Y"
        AES_hashkey = data_raw['enc_key']
        AES_columns_mac = data_raw['aes_col']#dataHash是yes or Y 的話，一定要有值
        # account = data_raw['member_account']
        # m_id = data_raw['member_id']

        if columns_mac == None or columns_mac is None:
            columns_mac = ''

        if AES_columns_mac == None or AES_columns_mac is None:
            AES_columns_mac = ''




    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if sep_ == '' or AES_hashkey == '' or hashTableName == '' or hashkey == '' :
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '' and AES_columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}


    #curren_host = get_host_name()
    #web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
    web_ip,web_port,flask_ip,flask_port = getConfig().getOpenAPI_withoutHostName()


    pid = 999
    try:
        Multiple_Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash,
                "AES_key": AES_hashkey,
                "AES_columns_mac":AES_columns_mac 
                }
        print('Multiple_Hash_para: ', Multiple_Hash_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/m_hash_async", json=Multiple_Hash_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("Multiple_Hash_para JSON: ",response_dic)
        response['HashMac']='1' #response_dic['state']
        #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

#@app.route("/MacHash_Async", methods=["POST"])
@swag_from("swagger_yml/setHashMac.yml")
def MacHash_Async():
    log_time = GetLogTime('MacHash_Async')
    log_time.printLog("Start MacHash_Async")
    
    ts0 = time.time()

    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg0
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    #get parameter
    try:
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = "Y" #data_raw['dataHash']
        onlyHash = "Y"
        # account = data_raw['member_account']
        # m_id = data_raw['member_id']


    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or hashkey == '' or sep_ == '' or columns_mac == '' or dataHash == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}


    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)


    pid = 999
    try:
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash 
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None, verify=False)
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

    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

    ### 2022/01/10
#citc, 20220117, to https, and transproting key
### swagger: AES hashmac 
#@app.route("/AESHash_Async", methods=["POST"])
@swag_from("swagger_yml/AESHash_Async.yml")
def AESHash_Async():
    log_time = GetLogTime('AESHash_Async')
    log_time.printLog("Start AESHash_Async")
    
    ts0 = time.time()

    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -11
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    #get parameter
    try:
        # pname = data_raw['pname'].encode("utf-8")
        # prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']

        #citc, 20220117
        hashkey = data_raw['hashkey']

        #############################################################
        ##20220308, citc------------------------d
        print("##20220301, citc------HSM KEY ------------------d")
        curren_host = get_host_name()
        if "gethostname err" in curren_host:
            return test_get_response("get host name error"+curren_host)
        #else:
            #return test_get_response("host name = "+curren_host)


        web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

        hsm_key = str(hsm_key)

        ##20220302################################
        #hsm_key = getAESHSMKey(hsm_key,hsm_url)
        ################################


        print("##20220301, citc------hsm_key = {}".format(hsm_key))
        if "HSM" in hashkey:
            print("----(AESHash_Sync)--------citc HSM get key here -----------")
            hashkey = hsm_key
        #############################################################

        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -12
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -13
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}

    pid = 999 

    # FOR Mac API:  flask_port+"/aes_async"
    progress_ = "1t1"
    try:

        #20220117 add
        onlyHash = "No" #for enc
        dataHash = "yes"

        Hash_para = {"tablename":hashTableName, 
                #citc, 20220117
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash
                }
        print('Hash_para: ', Hash_para)   

        #citc, 20220117, ssl certificate 
        #import ssl
        #ssl._create_default_https_context = ssl._create_unverified_context  
        #cert_pem = "/app/app/devp/cert.pem"
        #key_pem = "/app/app/devp/key.pem"
        #ca_pem = "/app/app/devp/ca.pem"

        #return test_get_response("before requests.post")

        #response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None, cert=(cert_pem,key_pem), verify=ca_pem)
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None, verify=False)
        #return test_get_response("after requests.post")
 

        response_dic = response_g.json()
        #########citc###################
        print("HASH JSON_citc: ",response_dic)
        #################################
        response['HashMac']='1' #response_dic['state']
        #return make_response(jsonify(response))
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))

    # ts1 = time.time()
    # response['dataraw']=data_raw
    # #response['STATE'] = state_
    # response['status'] = 1
    # response['errMsg'] = ''
    # response['time_async'] =str(ts1-ts0)
    # return make_response(jsonify(response))
    
    # citc. nask for test not exec the following problem
    # except Exception as e:
    #    response = dict()
    #    errMsg = 'request_error: ' + str(e)
    #    response['status'] = -1
    #    response['errMsg'] = errMsg
    #    log_time.printLog(errMsg)
    #    return make_response(jsonify(response))
    

        # print("---------------citc      befor   check_appstatus----------------")
        # # check hash status  (try)
        # # progress = check_appstatus(128 , 'udfMacUID')
        # progress = 0 #check_appstatus(pid , 'udfMacUID')
        # print("---- progress type---{}",format(type(progress)))

        # polling=0
        
        # progress_state = "2t2"
        #while int(progress) != 100:
        # while True:
        #     try:
                #print("---- progress type 0---{}".format(type(progress_)))
                #progress_ = "t0"
                # time.sleep(5)
                #progress, progress_state =  check_appstatus(pid, 'udfMacUID')
                #progress_, progress_state =  check_appstatus(pid, 'udfAESUID_new') #pid=999 (fixed in udfAESUID_new.py)
                # progress, progress_state =  check_appstatus(pid, 'AES_Enc') #pid=999 (fixed in udfAESUID_new.py) AES_ENC is NAME in udfAESUID_new.py
                #print("---- progress type 1---{}".format(type(progress_)))
                #progress_ = progress_+"t01"
                # if progress > 20:
                #     # progress = 100
                #     break;
                # if polling > 3:
                #     progress_ = progress_+"t01_3"
                #     break;
                #print("---- progress type 2---{}".format(type(progress_)))
                #progress_ = progress_+"t2"
                # if progress_state == 'err':#int(progress) == 10:
                #     response = dict()
                #     errMsg = 'projstatus error: ' + "hash fail: No file? or hash column name error"
                #     response['status'] = -18
                #     response['errMsg'] = errMsg
                #     log_time.printLog(errMsg)
                #     return make_response(jsonify(response))            
                #     break;
                #print("---- progress type 3---{}".format(type(progress_)))
                #progress_ = progress_+"t3"
                # polling = polling+1 
                
             
                #return make_response(jsonify(response))       
            # except Exception as e:


            #     response = dict()
            #     errMsg = 'request_error: ' + str(e)
            #     response['status'] = -19
            #     response['errMsg'] = errMsg
            #     #response['citc2_err_']=progress_
            #     log_time.printLog(errMsg)
            #     return make_response(jsonify(response))
                #progress = 0
                #break
    
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -14
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try:
        response = dict()
        ts1 = time.time()
        # response['citc']="2"
        # response['citc2_progress_']=progress_
        response['dataraw']=data_raw
        #20220802 add
        response['result']=response_dic
        response['status'] = 1
        response['errMsg'] = ''
        #response['STATE'] = state_
        response['time_async'] =str(ts1-ts0)
        return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -15
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))    


def test_get_response(errMsg):
    response = dict()
    
    
    response['status'] = -100
    response['errMsg'] = errMsg
    #log_time.printLog(errMsg)
    return make_response(jsonify(response))

############20220302#######################
### 2022/01/14
#20220117, to https, and back transporting key
### swagger: AES hashmac 
#@app.route("/AESDecrypt_Async", methods=["POST"])
@swag_from("swagger_yml/AESDecrypt_Async.yml")
def AESDecrypt_Async():
    log_time = GetLogTime('AESDecrypt_Async')
    log_time.printLog("Start AESDecrypt_Async")
    
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
    #return test_get_response("errMsg 1")
    #get parameter
    try:
        # pname = data_raw['pname'].encode("utf-8")
        # prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['projName'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        
        #citc, 20220117
        hashkey = data_raw['hashkey']
        #return test_get_response("errMsg 2")
       #############################################################
        ##20220308, citc------------------------d
        print("##20220301, citc------HSM KEY ------------------d")
        curren_host = get_host_name()
        if curren_host == "":
            return test_get_response("get host name error")
        #else:
            #return test_get_response("host name = "+curren_host)    
        
        web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
        hsm_key = str(hsm_key)
        print("##20220301, citc------hsm_key = {}".format(hsm_key))
        if "HSM" in hashkey:
            print("----(AESDecrypt_Sync)--------citc HSM get key here -----------")
            hashkey = hsm_key
        ##20220302################################
        #hsm_key = getAESHSMKey(hsm_key,hsm_url)
        ################################

        

        hsm_key = str(hsm_key)

        ##20220302################################
        #hsm_key = getAESHSMKey(hsm_key,hsm_url)
        ################################

        
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -12
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -13
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -14
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}

    pid = 999 

    # FOR Mac API:  flask_port+"/aes_async"
    try:
        #citc, 20220117
        dataHash = "yes"
        onlyHash = "yes"
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash 
                }
        print('Hash_para: ', Hash_para)    


        #citc, 20220117, ssl certificate 
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context        
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None, verify=False)
        #response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
        

        response_dic = response_g.json()
        print("HASH JSON: ",response_dic)
        response['HashMac']='1' #response_dic['state']
        #return make_response(jsonify(response))
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     response['status'] = -15
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))



    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

    # # check hash status  (try)
    # # progress = check_appstatus(128 , 'udfMacUID')
    # progress = 0 #check_appstatus(pid , 'udfMacUID')

    # #while int(progress) != 100:
    # polling = 0
    # while True:
    #     try:
    #         time.sleep(15)
    #         #progress, progress_state =  check_appstatus(pid, 'udfMacUID')
    #         #progress, progress_state =  check_appstatus(pid, 'udfAESUID_new') #pid=999 (fixed in udfAESUID_new.py)
    #         progress, progress_state =  check_appstatus(pid, 'AES_Enc') #pid=999 (fixed in udfAESUID_new.py) AES_ENC is NAME in udfAESUID_new.py
    #         if int(progress) == 100:
    #             # progress = 100
    #             break;
    #         if polling > 3:
    #             break;
    #         if progress_state == 'err':#int(progress) == 10:
    #             response = dict()
    #             errMsg = 'projstatus error: ' + "hash fail: No file?"
    #             response['status'] = -18
    #             response['errMsg'] = errMsg
    #             log_time.printLog(errMsg)
    #             return make_response(jsonify(response))            
    #             break;
    #         polling = polling+1
    #     except Exception as e:

    #         response = dict()
    #         errMsg = 'request_error: ' + str(e)
    #         response['status'] = -19
    #         response['errMsg'] = errMsg
    #         #response['citc2_err_']=progress_
    #         log_time.printLog(errMsg)
    #         return make_response(jsonify(response))
    #         #progress = 0
    #         #pass
      
    # ts1 = time.time()
    # response['dataraw']=data_raw
    # #20220802 add
    # response['result']=response_dic
    # #response['STATE'] = state_
    # response['time_async'] =str(ts1-ts0)
    # return make_response(jsonify(response))


#20201204:Tony setJP_async
#20210727: Pei minKvalue
#@app.route('/setJP_Async', methods=['POST'])
def setJP_Async():
    print("Start setJP_Async")
    log_time = GetLogTime("setJP_Async")
    log_time.printLog("Start setJP_Async")

    ########################################
    # jarFileName='/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    # app_ID=99999

    try:
        input_ = request.get_json()
        log_time.printLog(input_)
        # response = dict()
        # response['Msg'] = input_
        # return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error1: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    print (input_)
 

    try:
        input_values = list(input_.values())
        for v in input_values:
            if v != "":
                print (v)
            else:
                error
    except Exception as e:
        response = dict()
        errMsg = 'request_error2: ' + 'Dictionary value can not null'
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
        # break
    
    try:
        if len(input_.get("pro_col_cht").split(',')) == len(input_.get("datatype").split(',')): #len(input_.get("isNull").split(',')) !=
            input_ = input_
        else:
            error
    except Exception as e:
        response = dict()
        errMsg = 'request_error3: ' + "Dictionary values'length are not the same. Please check again (pro_col_cht,isNull,datatype)"
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
        # break

    qi_col = input_["qi_col"]
    after_col_value = input_["after_col_value"]
    gen_qi_settingvalue = input_["gen_qi_settingvalue"]
    pro_col_cht = input_["pro_col_cht"]
    tablekeycol = input_["tablekeycol"]
    dataitem  = input_["dataitem"]
    datatype = input_["datatype"]
    isNull = input_["isNull"]
    csv_name = input_["csv_name"]
    minKvalue = input_["minKvalue"]
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
    task = task_setJsonProfile.setJP_longTask.apply_async((qi_col, after_col_value, gen_qi_settingvalue, pro_col_cht, tablekeycol,dataitem, datatype, isNull, csv_name, minKvalue))

    response = dict()
    #response['state'] = state
    # response['sparkAppID'] = ''
    # response['celeryID'] = ''
    # response['status'] = ''
    # response['errMsg'] = ''
    response['projStep'] = 'setJsonProfile'
    # response['dbName'] = ''
    # response['tblName'] = ''

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            jp_longTask_task = task_setJsonProfile.setJP_longTask.AsyncResult(task.id)
            state_ = jp_longTask_task.state
            response['status'] = '1'
            response['celeyId'] = jp_longTask_task.id
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


    
#@app.route("/setJsonProfile_Async", methods=["POST"])
@swag_from("swagger_yml/JsonProfile.yml")
def JsonProfile_Async():
    log_time = GetLogTime('JsonProfile_Async')
    log_time.printLog("Start JsonProfile_Async")
    ts0 = time.time()
    response = dict()
    try:
        input_ = request.get_json()
        log_time.printLog(input_)
        # response = dict()
        # response['Msg'] = input_
        # return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_errorA: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    print (input_)
    # log_time.printLog(input_)
    # schema = jsonBase64Schema()
    # data = loadJson(input_, schema)
    # log_time.printLog(data)
    # print (data)



    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

    qi_col = input_["qi_col"]
    after_col_value = input_["after_col_value"]
    gen_qi_settingvalue = input_["gen_qi_settingvalue"]
    pro_col_cht = input_["pro_col_cht"]
    tablekeycol = input_["tablekeycol"]
    dataitem  = input_["dataitem"]
    datatype = input_["datatype"]
    isNull = input_["isNull"]
    csv_name = input_["csv_name"]
    minKvalue = input_["minKvalue"]

    try:
        setJP_para = {
            "qi_col": qi_col,
            "after_col_value": after_col_value,
            "gen_qi_settingvalue": gen_qi_settingvalue,
            "pro_col_cht": pro_col_cht,
            "tablekeycol": tablekeycol,
            "dataitem": dataitem,
            "datatype": datatype,
            "isNull": isNull,
            "csv_name": csv_name,
            "minKvalue": minKvalue
            }
        print('setJP_para: ', setJP_para)           
        # response_g = requests.post("http://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None)
        response_setJP = requests.post("https://"+flask_ip+":"+flask_port+"/setJP_Async", json=setJP_para,timeout=None,verify=False)
        response_dic = response_setJP.json()
        print("setJP_Async JSON: ",response_dic)
        response['setJP_Async']=response_dic
 
    except Exception as e:
        response = dict()
        errMsg = 'request_errorB: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)

    ts1 = time.time()
    # response['dataraw']=data_raw
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 


#0708 swagger: OpenAPI 呼叫非同步Deid自動化的flask API: /AutoDeId_Async
#@app.route("/setAutoDeId_Async", methods=["POST"])
@swag_from("swagger_yml/Deid_Async.yml")
def setAutoDeId_Async():
    log_time = GetLogTime('AutoDeIdAES_Async')
    log_time.printLog("Start AutoDeIdAES_Async")
    ts0 = time.time()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -11
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        pname = data_raw['pname'].encode('utf-8')
        prodesc =  data_raw['prodesc'].encode('utf-8')
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        step = '1' #data_raw['step']
        configName = data_raw['configName']
        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']

        uId = data_raw['userId']
        uAccount = data_raw['userAccount']

        print("##20220301, citc------HSM KEY ------------------d")
        '''
        icl, not use
        curren_host = get_host_name()
        if "gethostname err" in curren_host:
            return test_get_response("get host name error"+curren_host)
        '''    

        # print("##20220301, citc------hsm_key = {}".format(hsm_key))
        # if "HSM" in hashkey:
        #     print("----(AESHash_Sync)--------citc HSM get key here -----------")
        #     hashkey = hsm_key
        #############################################################

        sep = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "N"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -12
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    #check parameter null?
    if pname != p_dsname:
        response = dict()
        errMsg = 'The pname parameter and the p_dsname parameter must be the same' 
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))        

    if powner == '' or p_dsname == '' or hashTableName == '' or sep == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -13
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y":
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
    response = {}

    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)


    hashkey = hsm_key
    pid = 999
    # FOR Mac API:  flask_port+"/aes_async"
    progress_ = "1t1"
    try:
        onlyHash = "No"
        dataHash = "yes"

        hashkey = hsm_key
        # try:
        #     Hash_para = {"tablename":hashTableName, 
        #             "key":hashkey,
        #             "sep":sep, 
        #             "columns_mac":columns_mac, 
        #             "projName": p_dsname, 
        #             "projID": str(pid), 
        #             "dataHash": dataHash,
        #             "onlyHash": onlyHash
        #             }
        #     response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None, verify=False)
        #     response_dic = response_g.json()
        #     print("HASH JSON: ",response_dic)
        #     log_time.printLog('HashMac_flag: '+ str(1))
        #     response['HashMac']='1' #response_dic['state']
        # except Exception as e:
        #     log_time.printLog('errTable: Hash_request error. {0}'.format(str(e)))

        # # check hash status
        # progress = 0
        # while int(progress) != 100:
        #     try:
        #         progress, progress_state =  check_appstatus(pid, 'AES_Enc')
        #         if int(progress) == 100:

        #             break;
        #         if progress_state == 'err':
        #             errMsg = "hash fail: No file?"
        #             log_time.printLog('errTable: {0}'.format(str(errMsg)))           
        #             break;
        #     except Exception as e:
        #         pass


        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        AutoDeIdAsync_para = {
            "p_dsname": p_dsname,
            "pname": pname,
            "powner": powner,
            "prodesc": prodesc,
            "hashTableName":hashTableName,
            "hashkey":hashkey,
            "sep":sep,
            "columns_mac":columns_mac,
            "projName": p_dsname,
            "dataHash": dataHash ,
            "configName":configName,
            "onlyHash": onlyHash,
            'memberid': uId,
            'memberacc': uAccount
        }
        print('AutoDeIdAsync_para: ', AutoDeIdAsync_para)
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/DeIdAsyncAES", json=AutoDeIdAsync_para,timeout=None, verify=False)


        # response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
        #
        # InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc }
        # response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para, verify=False)
        # gen_qi_settingvalue = "5,4,5,0,0,4,4,4,0,0*5,???,3,0,0,???,???,???,0,0"
        # minKvalue = 5
        # pro_tb = "mac_adult_id"
        # Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue":gen_qi_settingvalue,"k_value":minKvalue, "tablename":pro_tb}
        # print('Gen_para: ',Gen_para)
        # response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None, verify=False)


        # response_dic = response_g.json()
        # #########citc###################
        # print("HASH JSON_citc: ",response_dic)
        # #################################
        # response['HashMac']='1' #response_dic['state']

        # print("---------------citc      befor   check_appstatus----------------")
        # progress = 0
        # print("---- progress type---{}",format(type(progress)))
        # polling=0
        # progress_state = "2t2"
        # while True:
        #     try:
        #         time.sleep(5)
        #         #progress_, progress_state =  check_appstatus(pid, 'udfAESUID_new')
        #         progress, progress_state =  check_appstatus(pid, 'AES_Enc') #pid=999 (fixed in udfAESUID_new.py) AES_ENC is NAME in udfAESUID_new.py
        #         if progress_ == "100":
        #             break;
        #         if polling > 3:
        #             progress_ = progress_+"t01_3"
        #             break;
        #         if progress_state == 'err':
        #             response = dict()
        #             errMsg = 'projstatus error: ' + "hash fail: No file?"
        #             response['status'] = -18
        #             response['errMsg'] = errMsg
        #             log_time.printLog(errMsg)
        #             return make_response(jsonify(response))
        #             break;
        #         polling = polling+1

        #     except Exception as e:
        #         response = dict()
        #         errMsg = 'request_error: ' + str(e)
        #         response['status'] = -19
        #         response['errMsg'] = errMsg
        #         log_time.printLog(errMsg)
        #         return make_response(jsonify(response))

    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -14
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try:
        response = dict()
        ts1 = time.time()
        # response['citc']="2"
        # response['citc2_progress_']=progress_
        response['dataraw']=data_raw
        response['status'] = 1
        response['errMsg'] = ''
        #response['STATE'] = state_
        response['time_async'] =str(ts1-ts0)
        return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -15
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))



#0708 swagger: OpenAPI 呼叫非同步Deid自動化的flask API: /AutoDeId_Async
#@app.route("/setAutoDeIdMac_Async", methods=["POST"])
@swag_from("swagger_yml/DeidMac_Async.yml")
def setAutoDeIdMac_Async():
    log_time = GetLogTime('AutoDeIdMac_Async')
    log_time.printLog("Start AutoDeIdMac_Async")
    ts0 = time.time()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -11
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        pname = data_raw['pname'].encode('utf-8')
        prodesc =  data_raw['prodesc'].encode('utf-8')
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        step = '1' #data_raw['step']
        configName = data_raw['configName']
        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']

        uId = data_raw['userId']
        uAccount = data_raw['userAccount']

        print("##20220301, citc------HSM KEY ------------------d")
        '''
        icl, not use
        curren_host = get_host_name()
        if "gethostname err" in curren_host:
            return test_get_response("get host name error"+curren_host)
        '''    

        # print("##20220301, citc------hsm_key = {}".format(hsm_key))
        # if "HSM" in hashkey:
        #     print("----(AESHash_Sync)--------citc HSM get key here -----------")
        #     hashkey = hsm_key
        #############################################################

        sep = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "N"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -12
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    #check parameter null?
    if pname != p_dsname:
        response = dict()
        errMsg = 'The pname parameter and the p_dsname parameter must be the same' 
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))        


    if powner == '' or p_dsname == '' or hashTableName == '' or sep == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -13
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y":
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
    response = {}

    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)


    # hashkey = hsm_key
    pid = 999
    # FOR Mac API:  flask_port+"/aes_async"
    progress_ = "1t1"
    try:
        onlyHash = "No"
        dataHash = "yes"

        # hashkey = hsm_key

        # try:
        #     Hash_para = {"tablename":hashTableName, 
        #             "key":hashkey,
        #             "sep":sep, 
        #             "columns_mac":columns_mac, 
        #             "projName": p_dsname, 
        #             "projID": str(pid), 
        #             "dataHash": dataHash,
        #             "onlyHash": onlyHash
        #             }
        #     response_g = requests.post("https://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None, verify=False)
        #     response_dic = response_g.json()
        #     print("HASH JSON: ",response_dic)
        #     log_time.printLog('HashMac_flag: '+ str(1))
        #     response['HashMac']='1' #response_dic['state']
        # except Exception as e:
        #     log_time.printLog('errTable: Hash_request error. {0}'.format(str(e)))

        # # check hash status
        # progress = 0
        # while int(progress) != 100:
        #     try:
        #         progress, progress_state =  check_appstatus(pid, 'AES_Enc')
        #         if int(progress) == 100:

        #             break;
        #         if progress_state == 'err':
        #             errMsg = "hash fail: No file?"
        #             log_time.printLog('errTable: {0}'.format(str(errMsg)))           
        #             break;
        #     except Exception as e:
        #         pass


        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        AutoDeIdAsync_para = {
            "p_dsname": p_dsname,
            "pname": pname,
            "powner": powner,
            "prodesc": prodesc,
            "hashTableName":hashTableName,
            "hashkey":hashkey,
            "sep":sep,
            "columns_mac":columns_mac,
            "projName": p_dsname,
            "dataHash": dataHash ,
            "configName":configName,
            "onlyHash": onlyHash,
            'memberid': uId,
            'memberacc': uAccount
        }
        print('AutoDeIdAsync_para: ', AutoDeIdAsync_para)
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/DeIdAsyncMac", json=AutoDeIdAsync_para,timeout=None, verify=False)


        # response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
        #
        # InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc }
        # response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para, verify=False)
        # gen_qi_settingvalue = "5,4,5,0,0,4,4,4,0,0*5,???,3,0,0,???,???,???,0,0"
        # minKvalue = 5
        # pro_tb = "mac_adult_id"
        # Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue":gen_qi_settingvalue,"k_value":minKvalue, "tablename":pro_tb}
        # print('Gen_para: ',Gen_para)
        # response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None, verify=False)


        # response_dic = response_g.json()
        # #########citc###################
        # print("HASH JSON_citc: ",response_dic)
        # #################################
        # response['HashMac']='1' #response_dic['state']

        # print("---------------citc      befor   check_appstatus----------------")
        # progress = 0
        # print("---- progress type---{}",format(type(progress)))
        # polling=0
        # progress_state = "2t2"
        # while True:
        #     try:
        #         time.sleep(5)
        #         #progress_, progress_state =  check_appstatus(pid, 'udfAESUID_new')
        #         progress, progress_state =  check_appstatus(pid, 'AES_Enc') #pid=999 (fixed in udfAESUID_new.py) AES_ENC is NAME in udfAESUID_new.py
        #         if progress_ == "100":
        #             break;
        #         if polling > 3:
        #             progress_ = progress_+"t01_3"
        #             break;
        #         if progress_state == 'err':
        #             response = dict()
        #             errMsg = 'projstatus error: ' + "hash fail: No file?"
        #             response['status'] = -18
        #             response['errMsg'] = errMsg
        #             log_time.printLog(errMsg)
        #             return make_response(jsonify(response))
        #             break;
        #         polling = polling+1

        #     except Exception as e:
        #         response = dict()
        #         errMsg = 'request_error: ' + str(e)
        #         response['status'] = -19
        #         response['errMsg'] = errMsg
        #         log_time.printLog(errMsg)
        #         return make_response(jsonify(response))

    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -14
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try:
        response = dict()
        ts1 = time.time()
        # response['citc']="2"
        # response['citc2_progress_']=progress_
        response['dataraw']=data_raw
        response['status'] = 1
        response['errMsg'] = ''
        #response['STATE'] = state_
        response['time_async'] =str(ts1-ts0)
        return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -15
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))



    #0708 swagger: OpenAPI 呼叫非同步Deid自動化的flask API: /AutoDeId_Async
#@app.route("/setAutoDeIdAES_Async", methods=["POST"])
#@swag_from("swagger_yml/DeidAES_Async.yml")
def setAutoDeIdaes_Async():
    log_time = GetLogTime('AutoDeId_Async')
    log_time.printLog("Start AutoDeId_Async")

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
        pname = data_raw['pname'].encode('utf-8')
        prodesc =  data_raw['prodesc'].encode('utf-8')
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        step = '1' #data_raw['step']
        configName = data_raw['configName']
        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep = data_raw['sep']
        columns_mac = data_raw['columns_mac'] #dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "N"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or  p_dsname == '' or hashTableName == '' or hashkey == '' or sep == '' or dataHash == '' or configName == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))                


    response = {}
    # CheckProjStatus:
    try:
        AutoDeIdAsync_para = {
            "p_dsname": p_dsname, 
            "pname": pname, 
            "powner": powner, 
            "prodesc": prodesc, 
            "hashTableName":hashTableName, 
            "hashkey":hashkey,
            "sep":sep, 
            "columns_mac":columns_mac, 
            "projName": p_dsname, 
            "dataHash": dataHash ,
            "configName":configName,
            "onlyHash": onlyHash
            }
        print('AutoDeIdAsync_para: ', AutoDeIdAsync_para)            
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/DeIdAsyncAES", json=AutoDeIdAsync_para,timeout=None)
        response_dic = response_g.json()
        print("AutoDeIdAsync JSON: ",response_dic)
        response['AutoDeIdAsync']=response_dic #response_dic['state']
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
    
    ts1 = time.time()
    response['dataraw']=data_raw
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))



#swagger: create project > hashmac 
#@app.route("/setAutoDeIdAESHash_Async", methods=["POST"])
#@swag_from("swagger_yml/HashAES_Async.yml")
def setAutoHashAES_Async():
    log_time = GetLogTime('AutoHashAES_Sync')
    log_time.printLog("Start AutoHashAES_Sync")
    
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
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        # hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or sep_ == '' or columns_mac == '' or dataHash == '': # or hashkey == ''
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}
    # response['InsertProject_flag'] = "2"# "for export"
    #/api/WebAPI/InsertProject
    #step=1:create project > hash > import
    try:
        # InsertProject_para = { "p_dsname": p_dsname, "pinput": pinput, "pname": pname, "poutput": poutput, "powner": powner, "prodesc": prodesc } 
        # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  #原版
        InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc } 
        response_get = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para)
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

    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        else:
            error_insertproj ='系統寫入出現錯誤:檢查p_dsname是否重複使用'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
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
                # "key":hashkey,
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash 
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
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

    # check hash status  (try)
    # progress = check_appstatus(128 , 'udfMacUID')
    # progress = 0 #check_appstatus(pid , 'udfMacUID')
    # while int(progress) != 100:
    #     try:
    #         time.sleep(15)
    #         progress, progress_state =  check_appstatus(pid, 'udfMacUID')
    #         if int(progress) == 100:
    #             # progress = 100
    #             break;
    #         if progress_state == 'err':#int(progress) == 10:
    #             response = dict()
    #             errMsg = 'projstatus error: ' + "hash fail: No file?"
    #             response['status'] = -1
    #             response['errMsg'] = errMsg
    #             log_time.printLog(errMsg)
    #             return make_response(jsonify(response))            
    #             break;
    #     except Exception as e:
    #         #progress = 0
    #         pass
    step = "2"
    # /api/WebAPI/ExportData
    # Need parameter:pid
    # step=2: export
    if int(step)==2:
        try: 
            ExportData_para = { "p_dsname": p_dsname, "pid": pid }
            print('ExportData_para: ',ExportData_para)

            response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/ExportData", params=ExportData_para,timeout=None)

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
    
      
    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#swagger: create project > hashmac 
#@app.route("/setAutoDeIdMacHash_Async", methods=["POST"])
#@swag_from("swagger_yml/HashMac.yml")
def setAutoDeId_Hash():
    log_time = GetLogTime('AutoHashMac_Sync')
    log_time.printLog("Start AutoHashMac_Sync")
    
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
        pname = data_raw['pname'].encode("utf-8")
        prodesc =  data_raw['prodesc'].encode("utf-8")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        #step = data_raw['step']
        #configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "Y"
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or hashkey == '' or sep_ == '' or columns_mac == '' or dataHash == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
            response = dict()
            errMsg = 'request_error: ' + str('Empty parameter')
            errMsg = errMsg + ' ; request: {}'.format(request)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))  
    response = {}
    # response['InsertProject_flag'] = "2"# "for export"
    #/api/WebAPI/InsertProject
    #step=1:create project > hash > import
    try:
        # InsertProject_para = { "p_dsname": p_dsname, "pinput": pinput, "pname": pname, "poutput": poutput, "powner": powner, "prodesc": prodesc } 
        # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  #原版
        InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc } 
        response_get = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para)
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

    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        else:
            error_insertproj ='系統寫入出現錯誤:檢查p_dsname是否重複使用'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
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
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash":onlyHash 
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None)
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
    # progress = 0 #check_appstatus(pid , 'udfMacUID')
    # while int(progress) != 100:
    #     try:
    #         time.sleep(15)
    #         progress, progress_state =  check_appstatus(pid, 'udfMacUID')
    #         if int(progress) == 100:
    #             # progress = 100
    #             break;
    #         if progress_state == 'err':#int(progress) == 10:
    #             response = dict()
    #             errMsg = 'projstatus error: ' + "hash fail: No file?"
    #             response['status'] = -1
    #             response['errMsg'] = errMsg
    #             log_time.printLog(errMsg)
    #             return make_response(jsonify(response))            
    #             break;
    #     except Exception as e:
    #         #progress = 0
    #         pass
      
    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

#swagger
#@app.route("/AutoDeId_Sync", methods=["POST"])
# @swag_from("swagger_yml/Auto_Deid.yml")
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
    
    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

    #get parameter
    try:
        pname = data_raw['pname'].encode("utf-8")#.decode("latin1")
        prodesc =  data_raw['prodesc'].encode("utf-8")#.decode("latin1")
        #pinput =  data_raw['pinput']
        #poutput =  data_raw['poutput']
        powner =  '1' #data_raw['powner']
        p_dsname =  data_raw['p_dsname'] #projName
        step = '1' #data_raw['step']
        configName = data_raw['configName']

        #for hash
        hashTableName = data_raw['hashTableName']
        hashkey = data_raw['hashkey']
        sep_ = data_raw['sep']
        columns_mac = data_raw['columns_mac']#dataHash是yes or Y 的話，一定要有值
        dataHash = data_raw['dataHash']
        onlyHash = "N"
        uId = data_raw['userId']
        uAccount = data_raw['userAccount']

    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or hashkey == '' or sep_ == '' or columns_mac == '' or dataHash == '' or configName == '':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    if dataHash =="Y" or dataHash =="yes" or dataHash =="y": 
        if columns_mac == '':
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
            # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  # 原版
            InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc ,'memberid': uId,'memberacc': uAccount} 
            print("InsertProject_para: ",InsertProject_para)

            response_get = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para, verify=False)
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

    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
        else:
            error_insertproj ='系統寫入出現錯誤:檢查p_dsname是否重複使用'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            response['status'] = response['InsertProject_flag']
            return make_response(jsonify(response))
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
                "sep":sep_, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash ,
                "onlyHash": onlyHash
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None, verify=False)
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
    while int(progress) != 100:
        try:
            time.sleep(15)
            progress, progress_state =  check_appstatus(pid, 'udfMacUID')
            if int(progress) == 100:
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
            ImportData_para = { "p_dsname": p_dsname, "pid": pid ,'memberid': uId,'memberacc': uAccount}
            print('ImportData_para: ',ImportData_para)
            response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/ImportData", params=ImportData_para,timeout=None, verify=False)
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
            temp_gen_qi = valueSampleData['gen_qi_settingvalue'].split('*')
            temp_gen_qi[0] = pro_tb
            valueSampleData['gen_qi_settingvalue'] = '*'.join(temp_gen_qi)
            
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
            # if pro_tb != pro_tb_config:
            #     response = dict()
            #     errMsg = 'request_error: ' + 'plz check the used config is mapping the project.'
            #     response['status'] = -1
            #     response['errMsg'] = errMsg
            #     log_time.printLog(errMsg)
            #     return make_response(jsonify(response))

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
        Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue":gen_qi_settingvalue,"k_value":minKvalue, "tablename":pro_tb,'memberid': uId,'memberacc': uAccount}#, "pro_col_en":pro_col_en,"pro_col_cht":pro_col_cht}
        log_time.printLog('Gen_para: '+str(Gen_para))
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None, verify=False)
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

    #kchecking-1
    try:
        #get k-checking variable
        check_conn = ConnectSQL()
        sqlStr = "SELECT finaltblName  FROM `DeIdService`.`T_Project_SampleTable` where project_id like '{}';".format(pid)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            finaltblName = resultCheck["fetchall"][0]['finaltblName']
        check_conn.close()
    except Exception as e:
        errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))       

    try: #API:GetSingleTable
        GetSingleTable_para = {"pid":pid, "pname": p_dsname, "tablename":finaltblName, "jobname":'job1','memberid': uId,'memberacc': uAccount}
        log_time.printLog('GetSingleTable_para: '+str(GetSingleTable_para))
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/GetSingleTable", params=GetSingleTable_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("GetSingleTable DATA JSON: ",response_dic)
        response['GetSingle__flag']=response_dic
            #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #kchecking-2
    #/api/WebAPI/GetKChecking
    try: #API:GetKChecking
        GetKChecking_para = {"pid":pid, "pname": p_dsname, "jobname":'job1','memberid': uId,'memberacc': uAccount}
        log_time.printLog('GetKChecking_para: '+str(GetKChecking_para))
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/GetKChecking", params=GetKChecking_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("GetKChecking DATA JSON: ",response_dic)
        response['GetKChecking__flag']=response_dic
            #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    # check_status
    progress = 0 
    while int(progress) != 100:
        try: 
            time.sleep(15)
            progress, progress_state  =  check_appstatus(pid, 'getKchecking_one')
            if int(progress) == 100:
                break;
            if progress_state == 'err':#int(progress) == 10:
                response = dict()
                errMsg = 'projstatus error: ' + "getKchecking_one fail?"
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))            
                break;
        except Exception as e:
            #progress = 0
            pass

    step = "2"
    # /api/WebAPI/ExportData
    # Need parameter:pid
    # step=2: export
    if int(step)==2:
        try: 
            ExportData_para = { "p_dsname": p_dsname, "pid": pid ,'memberid': uId,'memberacc': uAccount}
            print('ExportData_para: ',ExportData_para)

            response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/ExportData", params=ExportData_para,timeout=None, verify=False)

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
    
    
    ts1 = time.time()
    response['dataraw']=data_raw
    #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

# #swagger: export data 2020Dec-Jade
#@app.route('/export_Async', methods=['POST'])
#@swag_from("swagger_yml/exportData.yml")
def export_Async():
    log_time = GetLogTime('exportData')
    log_time.printLog("Start exportData")

    ts0 = time.time()

     #response = dict()

     #response['celeryID'] = ''#str
     #response['status'] = ''#str (1: succeed, -1: fail )
     #response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
     #response['projStep'] = 'export'#str (select, gen, join, distinct,single k checking,export,import)
     #response['dbName'] = ''#str
     #response['tblName'] = ''#str

     # get parameter from swagger
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

    try:
        projName = data_raw['projName']
         #configName = data_raw['configName']
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    if projName=='':
        response = dict()
        errMsg = 'request_error: ' + str('Empty parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        response = dict()
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    try: # fetch parameter: pid
        response = dict()
        sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project` where project_name like '{}';".format(projName)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            pid = resultCheck["fetchall"][0]['project_id']
            response['pid'] = str(pid)
        check_conn.close()
    except Exception as e:
        response = dict()
        errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
        
    #############################################################
    ##20220308, citc------------------------d
    print("##20220301, citc------HSM KEY ------------------d")
    curren_host = get_host_name()
    if "gethostname err" in curren_host:
        return test_get_response("get host name error"+curren_host)
    #else:
        #return test_get_response("host name = "+curren_host)


    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

     #response = dict()
    try:
        report_para = {'pid':str(pid), 'projName':projName}
        print('report_para: ', report_para)
        response_g = requests.post("https//"+flask_ip+":"+flask_port+"/exportData_InterAgent", json=report_para,timeout=None,verify=False)
        response_dic = response_g.json()
        print("report_JSON: ",response_dic)
         #response['getReport']=response_dic #response_dic['state']
        response = response_dic
         #return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    ts1 = time.time()
     #response['dataraw']=data_raw
    response['status'] = 1 
    response['projStep'] = 'export'
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

# #######END SWAGGER ##################

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



###########icl, add rm_T_Project_DataByProjName 20220623#################################
#curl -H 'Content-Type: application/json' -X POST "http://140.96.81.155:5915/rm_T_Project_DataByTimeB64" -d '{"jsonBase64": "eyJkYXRlVGltZSI6ICIyMDIxLTAzLTE1In0="}'
###DEBUG:##################################
#docker service logs CITCWebservice_web -f#
###########################################
     #jsonDic_ = {"proj_name": "t1_porj"}, base64 string: eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9
    #curl: curl -H 'Content-Type: application/json' -X POST "http://140.96.81.155:5915/rm_T_Project_DataByProjNameB64" 
    # -d '{"jsonBase64": "eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9"}'
@app.route('/rm_T_Project_DataByProjNameB64', methods=['POST'])
def rm_T_Project_DataByProjNameB64():

    log_time = GetLogTime('rm_T_Project_DataByProjNameB64')
    log_time.printLog("Start rm_T_Project_DataByProjNameB64")
    try:   
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)

        #r_icl = {"err": "rm_T_Project_DataByTimeB64 -2"}
        #return make_response(jsonify(r_icl))
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

        #citc, add to JsonSchema.py 
    #20220614, add
    if 0:
        icl_dict = {"err11": "str(e)"}
        return make_response(jsonify(icl_dict))
    try:
        
        schema = rmDataByProjNameSchema()
    except Exception as e:
        icl_dict = {"err11": str(e)}
        return make_response(jsonify(icl_dict))
    
        
    #schema = jsonBase64Schema()#rmDataSchema()
    try:
        data = loadJson(jsonData, schema)
    except Exception as e:
        icl_dict = {"err12": str(e)}
        return make_response(jsonify(icl_dict))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % jsonData
        log_time.printLog(err_msg)
        return err_msg, 405
    print data

    if 0:
        icl_dict = {"dateTime1": data}
        return make_response(jsonify(icl_dict))
    #print 'enter getSparkJobStatus_4'
    
    #jsonDic_ = {"proj_name": "t1_porj"}, base64 string: eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9
    #curl: curl -H 'Content-Type: application/json' -X POST "http://140.96.81.155:5915/rm_T_Project_DataByProjNameB64" 
    # -d '{"jsonBase64": "eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9"}'
    try:
        proj_name = data["projName"]
        print (proj_name)
        if 0:
            icl_dict = {"dateTime": dateTime}
            return make_response(jsonify(icl_dict))
        response = SparkJobManager.rm_T_Project_DataByTime("0-0-0___"+proj_name)
        #print 'enter getSparkJobStatus_5'
        base64_return = encodeDic(response)
        log_time.printLog("Return base64: {0}".format(base64_return))
        log_time.printLog(response)
    except Exception as e:
        log_time.printLog(data)
        base64_return = data
        if 1:
            icl_dict = {"err1": str(e)}
            return make_response(jsonify(icl_dict))
    
    #{"err": "global name 'mete' is not defined"}
    return make_response(jsonify({'jsonBase64': base64_return}))
###########icl, end 20220623, remove data by proj_name


#####citc, 20191126 add##############getSparkNodeDiskStatus
#curl -H 'Content-Type: application/json' -X POST "http://IP address:5088/getSparkNodeDiskStatus"
#{  "jsonBase64": "eyJkaXJOYW1lIjogIi8iLCAidXNlZFBlcmNlbiI6ICIyMiUifQ=="}
#eyJkaXJOYW1lIjogIi8iLCAidXNlZFBlcmNlbiI6ICIyMiUifQ==: {"dirName": "/", "usedPercen": "22%"}
@app.route('/getSparkNodeDiskStatus', methods=['POST'])
def getSparkNodeDiskStatus():
    log_time = GetLogTime('getSparkNodeDiskStatus')
    log_time.printLog("Start getSparkNodeDiskStatus")
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


# ExportFile
#@app.route("/ExportData_Async", methods=["POST"])
@swag_from("swagger_yml/exportData_Async.yml")
def ExportData_Async():
    log_time = GetLogTime('ExportData_Async')
    log_time.printLog("Start ExportData_Async")

    ts0 = time.time()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Json format error: ' + str(e) # 210219: curl sent "", without dict()
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -2
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        p_dsname = data_raw['projName']
        uId = data_raw['userId']
        uAccount = data_raw['userAccount']
        powner =  '1'#data_raw['powner']
    except Exception as e:
        response = dict()
        errMsg = 'Missing parameter: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if p_dsname == '' or powner == '':
        response = dict()
        errMsg = 'Missing parameter: ' + str('Null parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    response = {}
    # CheckProjStatus:
    ##20220308, citc------------------------d
    print("##20220301, citc------HSM KEY ------------------d")
    curren_host = get_host_name()
    if "gethostname err" in curren_host:
        return test_get_response("get host name error"+curren_host)
    #else:
        #return test_get_response("host name = "+curren_host)
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
    try:
        ExportData_para = {'projName': p_dsname,'userId': uId,'userAccount': uAccount}
        print('ExportData_para: ', ExportData_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/ExportFile", json=ExportData_para,timeout=None,verify=False)
        response_dic = response_g.json()
        print("ExportFile JSON: ",response_dic)
        response['ExportFile']=response_dic #response_dic['state']

    except Exception as e:
        response = dict()
        errMsg = 'Unknown error: ' + str(e) #requests.get fail
        response['status'] = -99
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
    
    ts1 = time.time()
    response['dataraw']=data_raw
    # if response['ExportFile']['status'] == -1:
    #     response['status'] = -1
    # else:
    #     response['status'] = 1

    # if response['ExportFile']['errMsg'] != '':
    #     response['errMsg'] = response['ExportFile']['errMsg']
    # else:
    #     response['errMsg'] = ''
    #     #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#@app.route("/ExportData_Async_PETs", methods=["POST"])
@swag_from("swagger_yml/exportData_Async_PETs.yml")
def ExportData_Async_PETs():
    log_time = GetLogTime('ExportData_Async')
    log_time.printLog("Start ExportData_Async")

    ts0 = time.time()
    try:
        data_raw = request.get_json() # get parameter from swagger curl
        print(data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Json format error: ' + str(e) # 210219: curl sent "", without dict()
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -2
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        p_dsname = data_raw['projName']
        uId = data_raw['userId']
        uAccount = data_raw['userAccount']
        powner =  '1'#data_raw['powner']
    except Exception as e:
        response = dict()
        errMsg = 'Missing parameter: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #check parameter null?
    if p_dsname == '' or powner == '':
        response = dict()
        errMsg = 'Missing parameter: ' + str('Null parameter')
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
    
    response = {}
    # CheckProjStatus:
    ##20220308, citc------------------------d
    print("##20220301, citc------HSM KEY ------------------d")
    curren_host = get_host_name()
    if "gethostname err" in curren_host:
        return test_get_response("get host name error"+curren_host)
    #else:
        #return test_get_response("host name = "+curren_host)
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
    try:
        ExportData_para = {'projName': p_dsname,'userId': uId,'userAccount': uAccount}
        print('ExportData_para: ', ExportData_para)            
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/ExportFile_PETs", json=ExportData_para,timeout=None,verify=False)
        response_dic = response_g.json()
        print("ExportFile JSON: ",response_dic)
        response['ExportFile_PETs']=response_dic #response_dic['state']

    except Exception as e:
        response = dict()
        errMsg = 'Unknown error: ' + str(e) #requests.get fail
        response['status'] = -99
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
    
    ts1 = time.time()
    response['dataraw']=data_raw
    # if response['ExportFile_PETs']['status'] == -1:
    #     response['status'] = -1
    # else:
    #     response['status'] = 1

    # if response['ExportFile_PETs']['errMsg'] != '':
    #     response['errMsg'] = response['ExportFile']['errMsg']
    # else:
    #     response['errMsg'] = ''
    #     #response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))




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

    # schema = getExporDataSchema()
    # data = loadJson(data_raw, schema)
    # if data is None:
    #     err_msg = "<p>Json file error '%s'</p>" % data_raw
    #     log_time.printLog(err_msg)
    #     return err_msg, 405

    # jsonBase64 =  data["jsonBase64"]
    # log_time.printLog("data_raw: {0}".format(data_raw)) 
    print("##2023, data_raw------------------d")

    print(data_raw)
    # jsonBase64 = encodeDic(data_raw)
    # data_raw = {'projName': p_dsname,'userId': uId,'userAccount': uAccount}
    # {"projID":"27", "projStep":"export","projName":"test_tpe0117","userAccount":"deidadmin","userId":"1","mainInfo": {"tbl_1":{"pro_tb":"mac_test7_s","finaltblName":"g_mac_test7_s_k_job1","location":"local"}}}
    # {u'jsonBase64': u'eyJwcm9qSUQiOiIyNyIsICJwcm9qU3RlcCI6ImV4cG9ydCIsInByb2pOYW1lIjoidGVzdF90cGUwMTE3IiwidXNlckFjY291bnQiOiJkZWlkYWRtaW4iLCJ1c2VySWQiOiIxIiwibWFpbkluZm8iOiB7InRibF8xIjp7InByb190YiI6Im1hY190ZXN0N19zIiwiZmluYWx0YmxOYW1lIjoiZ19tYWNfdGVzdDdfc19rX2pvYjEiLCJsb2NhdGlvbiI6ImxvY2FsIn19fQ=='}
    
    try:
        p_dsname = data_raw['projName']
        userAccount = data_raw['userAccount']
        userId = data_raw['userId']



        try: #connection SQL
            check_conn = ConnectSQL()
        except Exception as e:
            errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
        try: # fetch parameter: pid
            sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project_SampleTable` where pro_db like '{}';".format(p_dsname)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pid = resultCheck["fetchall"][0]['project_id']
                projID = str(pid)
            check_conn.close()
        except Exception as e:
            errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

        try: #connection SQL
            check_conn = ConnectSQL()
        except Exception as e:
            errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
        try: # fetch parameter: pid
            sqlStr = "SELECT  pro_tb FROM `DeIdService`.`T_Project_SampleTable` where pro_db like '{}';".format(p_dsname)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pro_tb = resultCheck["fetchall"][0]['pro_tb']
                proTB = str(pro_tb)
            check_conn.close()
        except Exception as e:
            errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

            
        try: #connection SQL
            check_conn = ConnectSQL()
        except Exception as e:
            errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
        try: # fetch parameter: pid
            sqlStr = "SELECT  finaltblName FROM `DeIdService`.`T_Project_SampleTable` where pro_db like '{}';".format(p_dsname)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                finaltblName = resultCheck["fetchall"][0]['finaltblName']
                FTBName = str(finaltblName)
            check_conn.close()
        except Exception as e:
            errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

        all_data = dict() 
        all_data['projID'] = projID #"27" # projID
        all_data['projStep'] = 'export'
        all_data['projName'] = p_dsname
        all_data['userAccount'] = userAccount
        all_data['userId'] = userId
        all_data['mainInfo'] = dict()
        all_data['mainInfo']['tbl_1'] = dict()
        all_data['mainInfo']['tbl_1']['pro_tb'] = proTB #'mac_test7_s'#  # proTB
        all_data['mainInfo']['tbl_1']['finaltblName'] = FTBName #'g_mac_test7_s_k_job1'  #FTBName # 
        all_data['mainInfo']['tbl_1']['location'] = 'local'

        # encoded_dict = str(all_data).encode('utf-8')
        # base64_dict_all_data = base64.b64encode(encoded_dict)
        base64_dict_all_data = encodeDic(all_data)


        jsonBase64_a = dict()
        jsonBase64_a['jsonBase64'] = base64_dict_all_data

        # encoded_dict = str(jsonBase64_a).encode('utf-8')
        # base64_dict_jsonBase64_a = base64.b64encode(encoded_dict)
        # jsonBase64 = base64_dict_jsonBase64_a
        jsonBase64 = encodeDic(jsonBase64_a)

        # data_raw['projID'] = projID
        # data_raw['projStep'] = 'export'
        # data_raw['proTB'] = FTBName
        # data_raw['FTBName'] = FTBName

        # jsonBase64 = encodeDic(data_raw)
        
    except:
        # data_raw = request.get_json()
        # schema = getExporDataSchema()
        # data = loadJson(data_raw, schema)
        # if data is None:
        #     err_msg = "<p>Json file error '%s'</p>" % data_raw
        #     log_time.printLog(err_msg)
        #     return err_msg, 405
        # jsonBase64 =  data["jsonBase64"]
        jsonBase64 = encodeDic(data_raw)

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
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify(response))  

    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))



# update:20180625
@app.route('/ExportFile_PETs', methods=['POST'])
def ExportFile_PETs():
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

    # schema = getExporDataSchema()
    # data = loadJson(data_raw, schema)
    # if data is None:
    #     err_msg = "<p>Json file error '%s'</p>" % data_raw
    #     log_time.printLog(err_msg)
    #     return err_msg, 405

    # jsonBase64 =  data["jsonBase64"]
    # log_time.printLog("data_raw: {0}".format(data_raw)) 
    print("##2023, data_raw------------------d")

    print(data_raw)
    # jsonBase64 = encodeDic(data_raw)
    # data_raw = {'projName': p_dsname,'userId': uId,'userAccount': uAccount}
    # {"projID":"27", "projStep":"export","projName":"test_tpe0117","userAccount":"deidadmin","userId":"1","mainInfo": {"tbl_1":{"pro_tb":"mac_test7_s","finaltblName":"g_mac_test7_s_k_job1","location":"local"}}}
    # {u'jsonBase64': u'eyJwcm9qSUQiOiIyNyIsICJwcm9qU3RlcCI6ImV4cG9ydCIsInByb2pOYW1lIjoidGVzdF90cGUwMTE3IiwidXNlckFjY291bnQiOiJkZWlkYWRtaW4iLCJ1c2VySWQiOiIxIiwibWFpbkluZm8iOiB7InRibF8xIjp7InByb190YiI6Im1hY190ZXN0N19zIiwiZmluYWx0YmxOYW1lIjoiZ19tYWNfdGVzdDdfc19rX2pvYjEiLCJsb2NhdGlvbiI6ImxvY2FsIn19fQ=='}
    
    try:
        p_dsname = data_raw['projName']
        userAccount = data_raw['userAccount']
        userId = data_raw['userId']



        try: #connection SQL
            check_conn = ConnectSQL()
        except Exception as e:
            errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
        try: # fetch parameter: pid
            sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project_SampleTable` where pro_db like '{}';".format(p_dsname)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pid = resultCheck["fetchall"][0]['project_id']
                projID = str(pid)
            check_conn.close()
        except Exception as e:
            errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

        try: #connection SQL
            check_conn = ConnectSQL()
        except Exception as e:
            errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
        try: # fetch parameter: pid
            sqlStr = "SELECT  pro_tb FROM `DeIdService`.`T_Project_SampleTable` where pro_db like '{}';".format(p_dsname)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pro_tb = resultCheck["fetchall"][0]['pro_tb']
                proTB = str(pro_tb)
            check_conn.close()
        except Exception as e:
            errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

            
        try: #connection SQL
            check_conn = ConnectSQL()
        except Exception as e:
            errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))
        try: # fetch parameter: pid
            sqlStr = "SELECT  finaltblName FROM `DeIdService`.`T_Project_SampleTable` where pro_db like '{}';".format(p_dsname)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                finaltblName = resultCheck["fetchall"][0]['finaltblName']
                FTBName = str(finaltblName)
            check_conn.close()
        except Exception as e:
            errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
            response['status'] = -1
            response['errMsg'] = errMsg
            log_time.printLog(errMsg)
            return make_response(jsonify(response))

        all_data = dict() 
        all_data['projID'] = projID #"27" # projID
        all_data['projStep'] = 'export'
        all_data['projName'] = p_dsname
        all_data['userAccount'] = userAccount
        all_data['userId'] = userId
        all_data['mainInfo'] = dict()
        all_data['mainInfo']['tbl_1'] = dict()
        all_data['mainInfo']['tbl_1']['pro_tb'] = proTB #'mac_test7_s'#  # proTB
        all_data['mainInfo']['tbl_1']['finaltblName'] = FTBName #'g_mac_test7_s_k_job1'  #FTBName # 
        all_data['mainInfo']['tbl_1']['location'] = 'local'

        # encoded_dict = str(all_data).encode('utf-8')
        # base64_dict_all_data = base64.b64encode(encoded_dict)
        base64_dict_all_data = encodeDic(all_data)


        jsonBase64_a = dict()
        jsonBase64_a['jsonBase64'] = base64_dict_all_data

        # encoded_dict = str(jsonBase64_a).encode('utf-8')
        # base64_dict_jsonBase64_a = base64.b64encode(encoded_dict)
        # jsonBase64 = base64_dict_jsonBase64_a
        jsonBase64 = encodeDic(jsonBase64_a)

        # data_raw['projID'] = projID
        # data_raw['projStep'] = 'export'
        # data_raw['proTB'] = FTBName
        # data_raw['FTBName'] = FTBName

        # jsonBase64 = encodeDic(data_raw)
        
    except:
        # data_raw = request.get_json()
        # schema = getExporDataSchema()
        # data = loadJson(data_raw, schema)
        # if data is None:
        #     err_msg = "<p>Json file error '%s'</p>" % data_raw
        #     log_time.printLog(err_msg)
        #     return err_msg, 405
        # jsonBase64 =  data["jsonBase64"]
        jsonBase64 = encodeDic(data_raw)

    task = task_export_PETs.export_longTask_PETs.apply_async((jsonBase64, 1))

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            export_longTask_task = task_export_PETs.export_longTask_PETs.AsyncResult(task.id)
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
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify(response))  

    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify({'jsonBase64': base64_return}))


#update:20180622
@app.route('/getServerFolderDataMac', methods=['POST'])
def getServerFolderDataMac():
    log_time = GetLogTime('getServerFolderDataMac')
    log_time.printLog("Start getServerFolderDataMac")

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
        serverPath = getConfig().getImportMacPath(type_)
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

###@@ICL, add, 20220929 start @@@@@@@@@@@@@@@@###############
#sync, see above#curl: curl -H 'Content-Type: application/json' -X POST "http://140.96.81.155:5915/rm_T_Project_DataByProjNameB64"
#async #curl: curl -H 'Content-Type: application/json' -X POST "http://140.96.81.155:5915/RemoveProjByName" 
    # -d '{"jsonBase64": "eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9"}'
    #eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9 = {"proj_name": "t1_porj"}

###add async rm project by name#############################
#@app.route('/RemoveProjByName_async', methods=['POST'])
@swag_from("swagger_yml/RemoveProjByName_async.yml")
def RemoveProjByName_async():
    log_time = GetLogTime('RemoveProjByName')
    log_time.printLog("Start RemoveProjByName")

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

    #schema = jsonBase64Schema()
    #data = loadJson(data_raw, schema)
    #if data is None:
    #    err_msg = "<p>Json file error '%s'</p>" % data_raw
    #    log_time.printLog(err_msg)
    #    return err_msg, 405

    #jsonBase64 =  data["jsonBase64"]
    #log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    #log_time.printLog(json.loads(base64.b64decode(jsonBase64)))
    #{"proj_name": "t1_porj"} = jsonBase64

    #21. 20220623 {"proj_name": "t1_porj"}
    #class rmDataByProjNameSchema(Schema):
    #     proj_name = fields.Str()
    schema = rmDataByProjNameSchema()
    data = loadJson(data_raw, schema)
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % data_raw
        log_time.printLog(err_msg)
        return err_msg, 405
    log_time.printLog("----1-in RemoveProjByName_async, data: {0}".format(data))
    projName =  data["projName"]
    log_time.printLog("-----Get projName from UI: {0}".format(projName))
    
    base64_return = encodeDic(data)
    log_time.printLog("-----Get jsonBase64 from base64.b64encode: {0}".format(base64_return))
    #{"proj_name": "t1_porj"} = jsonBase64

    task = task_removeProject_Data.removeprojectdata_longTask.apply_async((base64_return, 1))

    response = dict()
    response['sparkAppID'] = ''#str
    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'removeProject_Data'#str (select, gen, join, distinct,single k checking,export,import)
    response['dbName'] = ''#str
    #response['tblNames'] = ''#str


    if True:
        state_ = "test"
        #while state_ != 'PROGRESS':
        while True:
            #####2018014, citc trace#####################################################
            log_time.printLog("----2-in RemoveProjByName_async, state_: {0}".format(state_))                                #task_removeProject_Data.py
            ICL_removeprojectdata_longTask = task_removeProject_Data.removeprojectdata_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = ICL_removeprojectdata_longTask.state
            #response['state'] = state_
            response['celeryID'] = ICL_removeprojectdata_longTask.id
            if state_ == 'ICL_START':
                ####task.info = (meta from task_XXXX.py)
                if task.info.get('sparkAppID') is None:
                    #response['err'] ='spark job fail'
                    response['errMsg'] ='spark context fail'
                    response['status'] = '-1'
                    log_time.printLog(response['errMsg'])
                    break

                response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
                response['dbName'] = task.info.get('dbName').strip('\n')
                #response['tblNames'] = task.info.get('tblNames').strip('\n')
                response['status'] = '1'
                break #ICL, 20220901 for async

            #####20180615, citc add#####################################################
            if state_ == 'FAIL_CELERY':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break

 
            #####2018014, citc add (end)#################################################
            #if state_ == states.SUCCESS:
            #    break
            if state_ == 'ICL_END':
                if task.info.get('dropHiveTblResult') is None:
                    #response['err'] ='spark job fail'
                    response['errMsg'] ='dropHiveTblResult fail'
                    response['status'] = '-1'
                    log_time.printLog(response['errMsg'])
                    break

                try:
                    #response['rmPorjectName'] = task.info.get('rmPorjectName').strip('\n')
                    response['dropHiveTblResult'] = task.info.get('dropHiveTblResult').strip('\n')
                    response['rmHdfsDir_output_Result'] = task.info.get('rmHdfsDir_output_Result').strip('\n')
                    response['rmHdfsDir_input_Result'] = task.info.get('rmHdfsDir_input_Result').strip('\n')
                    response['rmLocalHostDir_dataMac_output_Result'] = task.info.get('rmLocalHostDir_dataMac_output_Result').strip('\n')
                    response['rmLocalHostDir_output_Result'] = task.info.get('rmLocalHostDir_output_Result').strip('\n')
                    response['rmLocalHostDir_input_Result'] = task.info.get('rmLocalHostDir_input_Result').strip('\n')
                    response['deleteMariaDataByProjectId_Result'] = task.info.get('deleteMariaDataByProjectId_Result').strip('\n')
                    
                    response['status'] = '1'

                except Exception as e:
                    response = dict()
                    errMsg = 'get task_removeProject_Data ret error: ' + str(e)
                    #errMsg = errMsg + ' ; request: {}'.format(request)
                    response['status'] = -1
                    response['errMsg'] = errMsg
                    log_time.printLog(errMsg)
                    return make_response(jsonify(response))    
                break



            if state_ == "ICL_FAILURE":
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
            #####20221229###1##############
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
            #####20221229###1 end##############

    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    base64_return = encodeDic(response)
    log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    return make_response(jsonify(response))
    #return make_response(jsonify({'jsonBase64':base64_return}))
###@@ICL, add, 20220929 end @@@@@@@@@@@@@@@@###############












#join 20230922

@app.route('/join_Async', methods=['POST'])
def join_Async():
    print("Start join_Async")
    log_time = GetLogTime("join_Async")
    log_time.printLog("Start join_Async")

    ########################################
    # jarFileName='/app/sqljdbc4-2.0.jar'
    #########################################

    ts0 = time.time()
    # app_ID=99999

    try:
        input_ = request.get_json()
        # log_time.printLog(input_)
        # response = dict()
        # response['Msg'] = input_
        # return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_error1: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))
  
    try:
        jsonBase64 = input_["jsonbase64"]
    except Exception as e:
        print(e)

    task = task_Join.Join.apply_async((jsonBase64, 1))
 
    response = dict()
    #response['state'] = state
    # response['sparkAppID'] = ''
    # response['celeryID'] = ''
    # response['status'] = ''
    # response['errMsg'] = ''
    response['projStep'] = 'JoinFile'
    # response['dbName'] = ''
    # response['tblName'] = ''

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            j_longTask_task = task_Join.Join.AsyncResult(task.id)
            state_ = j_longTask_task.state
            response['status'] = '1'
            response['celeyId'] = j_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                if task.info.get('jobID') is None:
                    response['err'] ='spark job fail'
                    break
                response['status'] = '1'
                response['spark_jobID'] =task.info.get('jobID')
                break
            if state_ == states.SUCCESS:
                break
            if state_ == states.FAILURE:
                response['err'] ='celery job fail'
                break
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)
    return make_response(jsonify(response))








#@app.route('/JoinFile', methods=['POST'])
@swag_from("swagger_yml/Join.yml")
def JoinFile():
    log_time = GetLogTime('JsonProfile_Async')
    log_time.printLog("Start JsonProfile_Async")
    ts0 = time.time()
    response = dict()
    try:
        input_ = request.get_json()
        log_time.printLog(input_)
        # response = dict()
        # response['Msg'] = input_
        # return make_response(jsonify(response))
    except Exception as e:
        response = dict()
        errMsg = 'request_errorA: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    print (input_)

    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)

 

    try:
        join_para = input_
        print('join_para: ', join_para)           
        # response_g = requests.post("http://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None)
        response_J = requests.post("https://"+flask_ip+":"+flask_port+"/join_Async", json=join_para,timeout=None,verify=False)
        response_dic = response_J.json()
        print("join_Async JSON: ",response_dic)
        response['join_Async']=response_dic
 
    except Exception as e:
        response = dict()
        errMsg = 'request_errorB: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)

    ts1 = time.time()
    response['dataraw']=join_para
    #response['STATE'] = state_
    response['status'] = 1
    response['errMsg'] = ''
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 








    #join_Async


    #log_time = GetLogTime('Join')
    #log_time.printLog("Start JoinFile")
    
    
    # ts0 = time.time()
    # try:
    #     data_raw = request.get_json()
    # except Exception as e:
    #     response = dict()
    #     errMsg = 'request_error: ' + str(e)
    #     errMsg = errMsg + ' ; request: {}'.format(request)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     #log_time.printLog(errMsg)
    #     return make_response(jsonify(response))
    
    # return {'accept data raw:':data_raw}
    '''
    jsonBase64 =  data_raw["jsonBase64"]
    log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
    log_time.printLog(json.loads(base64.b64decode(jsonBase64)))

    task = task_Join.Join.apply_async((jsonBase64, 1))

    response = dict()
    response['sparkAppID'] = ''#str
    response['celeryID'] = ''#str
    response['status'] = ''#str (1: succeed, -1: fail )
    response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'join'#str (select, gen, join, distinct,single k checking,export,import)
    response['dbName'] = ''#str
    response['tblNames'] = ''#str


    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            Join_longTask_task = task_Join.Join.AsyncResult(task.id)
            #########################################################################
            state_ = Join_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = Join_longTask_task.id
            if state_ == 'PROGRESS':
                if task.info.get('sparkAppID') is None:
                    #response['err'] ='spark job fail'
                    response['errMsg'] ='spark context fail'
                    response['status'] = '-1'
                    log_time.printLog(response['errMsg'])
                    break

                response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
                # response['dbName'] = task.info.get('dbName').strip('\n')
                # response['tblNames'] = task.info.get('tblNames').strip('\n')
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
    '''



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


@app.route('/ImportFile_PETs', methods=['POST'])
def ImportFile_PETs():
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

    task = task_import_PETs.import_longTask_PETs.apply_async((jsonBase64, 1))

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
            import_longTask_task = task_import_PETs.import_longTask_PETs.AsyncResult(task.id)
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


#update:20201221
@app.route('/Generalization_InterAgent_async', methods=['POST'])
def Generalization_InterAgent_async():
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

    task = task_getGenTbl_InterAgent.generalization_longTask.apply_async((jsonBase64, 1))

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
            generalization_longTask_task = task_getGenTbl_InterAgent.generalization_longTask.AsyncResult(task.id)
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
        log_time.printLog("--sparkTest = {}".format(sparkTest))
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
    log_time.printLog("(kchecking_async) Get jsonBase64 from UI: {0}".format(base64_))
    log_time.printLog("---json.loads(base64.b64decode(base64_)={}".format(json.loads(base64.b64decode(base64_))))

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
                    # break
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


    # try: #connection SQL
    #     check_conn = ConnectSQL()
    # except Exception as e:
    #     errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
    #     response['status'] = -1
    #     response['errMsg'] = errMsg
    #     log_time.printLog(errMsg)
    #     return make_response(jsonify(response))

    # try:
    #     group_name =  input_['group_name']
    #     if input_['key'] == '':
    #         try: # fetch parameter: pid
    #             group_name =  input_['group_name']
    #             sqlStr = "SELECT  group_hashkey FROM `DeIdService`.`T_Group` where group_name like '{}';".format(group_name)
    #             resultCheck = check_conn.doSqlCommand(sqlStr)
    #             if int(resultCheck['result'])==1:
    #                 key = resultCheck["fetchall"][0]['group_hashkey']
    #             check_conn.close()
    #         except Exception as e:
    #             errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
    #             response['status'] = -1
    #             response['errMsg'] = errMsg
    #             log_time.printLog(errMsg)
    #             return make_response(jsonify(response))
    #     else:
    #         key = "BASRsdfs456465"
    # except:
    #     key = "BASRsdfs456465"
    #     pass


    tblName = input_["tablename"]
    key = input_["key"]
    sep_ = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]
    onlyHash = input_["onlyHash"]

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
    try:
        task = task_udfMacUID.mac_longTask.apply_async((tblName,key,sep_,columns_mac,projName,projID,dataHash,onlyHash))

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
                    # if task.info.get('jobID') is None:
                    #     response['err'] ='spark job fail'
                    #     break
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
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))


    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)

    return make_response(jsonify(response))


#20200617
@app.route('/macgroup_async', methods=['POST'])
def macgroup_async():
    log_time = GetLogTime("macgroup_async")
    log_time.printLog("Start macgroup_async")

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


    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        group_name =  input_['group_name']
        if input_['key'] == '':
            try: # fetch parameter: pid
                group_name =  input_['group_name']
                sqlStr = "SELECT  group_hashkey FROM `DeIdService`.`T_Group` where group_name like '{}';".format(group_name)
                resultCheck = check_conn.doSqlCommand(sqlStr)
                if int(resultCheck['result'])==1:
                    key = resultCheck["fetchall"][0]['group_hashkey']
                check_conn.close()
            except Exception as e:
                errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))
        else:
            key = input_["key"]
    except Exception as e:
        response = dict()
        errMsg = 'request_error no group name: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    tblName = input_["tablename"]
    # key = input_["key"]
    sep_ = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]
    onlyHash = input_["onlyHash"]
    userId = input_["userId"] 
    userAccount = input_["userAccount"] 
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
    try:
        task = task_udfMacUID.mac_longTask.apply_async((tblName,key,sep_,columns_mac,projName,projID,dataHash,onlyHash,userId,userAccount))

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
                    # if task.info.get('jobID') is None:
                    #     response['err'] ='spark job fail'
                    #     break
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
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))


    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['status'] = 1
    response['errMsg'] = ""
    log_time.printLog(response)

    return make_response(jsonify(response))


@app.route('/macgroupimport_async', methods=['POST'])
def macgroupimport_async():
    log_time = GetLogTime("macgroupimport_async")
    log_time.printLog("Start macgroupimport_async")

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


    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        group_name =  input_['group_name']
        if input_['key'] == '':
            try: # fetch parameter: pid
                group_name =  input_['group_name']
                sqlStr = "SELECT  group_hashkey FROM `DeIdService`.`T_Group` where group_name like '{}';".format(group_name)
                resultCheck = check_conn.doSqlCommand(sqlStr)
                if int(resultCheck['result'])==1:
                    key = resultCheck["fetchall"][0]['group_hashkey']
                check_conn.close()
            except Exception as e:
                errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))
        else:
            key = input_["key"]
    except Exception as e:
        response = dict()
        errMsg = 'request_error no group name: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    tblName = input_["tablename"]
    # key = input_["key"]
    sep_ = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]
    onlyHash = input_["onlyHash"]
    userId = input_["userId"] 
    userAccount = input_["userAccount"] 
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
    try:
        task = task_udfMacUIDImport.mac_longTask.apply_async((tblName,key,sep_,columns_mac,projName,projID,dataHash,onlyHash,userId,userAccount))

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
                mac_longTask_task = task_udfMacUIDImport.mac_longTask.AsyncResult(task.id)
                state_ = mac_longTask_task.state
                response['state'] = state_
                response['celeyId'] = mac_longTask_task.id
                #print state_
                if state_ == 'PROGRESS':
                    # if task.info.get('jobID') is None:
                    #     response['err'] ='spark job fail'
                    #     break
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

            # curren_host = get_host_name()
            # web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
            # web_ip,web_port,flask_ip,flask_port = getConfig().getOpenAPI_withoutHostName()

            # try: #API:ImportData
            #     ImportData_para = { "p_dsname": projName, "pid": projID ,'memberid': userId,'memberacc': userAccount}
            #     print('ImportData_para: ',ImportData_para)
            #     response_g = requests.get("https://"+flask_ip+":"+flask_port+"/ImportFile", params=ImportData_para,timeout=None, verify=False)
            #     response_dic = response_g.json()
            #     print("IMPORT DATA JSON: ",response_dic)
            #     response['ImportData_flag']=response_dic
            #     #return make_response(jsonify(response))
            # except Exception as e:
            #     response = dict()
            #     errMsg = 'request_error: ' + str(e)
            #     response['status'] = -1
            #     response['errMsg'] = errMsg
            #     log_time.printLog(errMsg)
            #     return make_response(jsonify(response))

        # try:
        #     # data_raw = request.get_json()
        #     data_raw = { "p_dsname": projName, "pid": projID ,'memberid': userId,'memberacc': userAccount}
        # except Exception as e:
        #     response = dict()
        #     errMsg = 'request_error: ' + str(e)
        #     errMsg = errMsg + ' ; request: {}'.format(request)
        #     response['status'] = -1
        #     response['errMsg'] = errMsg
        #     log_time.printLog(errMsg)
        #     return make_response(jsonify(response))

        # schema = jsonBase64Schema()
        # data = loadJson(data_raw, schema)
        # if data is None:
        #     err_msg = "<p>Json file error '%s'</p>" % data_raw
        #     log_time.printLog(err_msg)
        #     return err_msg, 405

        # jsonBase64 =  data["jsonBase64"]
        # log_time.printLog("Get jsonBase64 from UI: {0}".format(jsonBase64))
        # log_time.printLog(json.loads(base64.b64decode(jsonBase64)))

        # task = task_import.import_longTask.apply_async((jsonBase64, 1))



    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))


    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['status'] = 1
    response['errMsg'] = ""
    log_time.printLog(response)

    return make_response(jsonify(response))



#20201221
@app.route('/aesgroup_async', methods=['POST'])
def aesgroup_async():
    log_time = GetLogTime("aesgroup_async")
    log_time.printLog("Start aesgroup_async")

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


    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    try:
        group_name =  input_['group_name']
        if input_['key'] == '':
            try: # fetch parameter: pid
                group_name =  input_['group_name']
                sqlStr = "SELECT  group_aeskey FROM `DeIdService`.`T_Group` where group_name like '{}';".format(group_name)
                resultCheck = check_conn.doSqlCommand(sqlStr)
                if int(resultCheck['result'])==1:
                    key = resultCheck["fetchall"][0]['group_aeskey']
                check_conn.close()
            except Exception as e:
                errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
                response['status'] = -1
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                return make_response(jsonify(response))
        else:
            key = input_["key"]
    except Exception as e:
        response = dict()
        errMsg = 'request_error no group name: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

 


    tblName = input_["tablename"]
    #citc, 20220117
    # key = input_["key"]
    sep_ = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]
    onlyHash = input_["onlyHash"]
    userId = input_["userId"] 
    userAccount = input_["userAccount"] 
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

    #2022, citc add
    try:
        task = task_udfAESUID.aes_longTask.apply_async((tblName,key,sep_,columns_mac,projName,projID,dataHash,onlyHash,userId,userAccount))
        #task = task_udfAESUID.aes_longTask.apply_async((tblName,sep_,columns_mac,projName,projID,dataHash,onlyHash))

        response = dict()
        #response['state'] = state
        # response['sparkAppID'] = ''
        # response['celeryID'] = ''
        # response['status'] = ''
        # response['errMsg'] = ''
        response['projStep'] = 'data_aes'
        # response['dbName'] = ''
        # response['tblName'] = ''



        if True:
            state_ = "test"
            while True:
                mac_longTask_task = task_udfAESUID.aes_longTask.AsyncResult(task.id)
                state_ = mac_longTask_task.state
                response['state'] = state_
                response['celeyId'] = mac_longTask_task.id
                #print state_
                progress, progress_state =  check_appstatus(projID, 'AES_Enc') #pid=999 (fixed in udfAESUID_new.py) AES_ENC is NAME in udfAESUID_new.py
                #print("---- progress type 1---{}".format(type(progress_)))
                #progress_ = progress_+"t01"
                if progress >= 20:
                    # progress = 100
                    if state_ == 'PROGRESS':
                        # if task.info.get('jobID') is None:
                        #     response['err'] ='spark job fail'
                        #     break
                        #if task.info.get('kTable') is None:
                        #    response['err'] ='spark job fail'
                            # break
                        # response['status'] = '1'
                        # response['spark_jobID'] =task.info.get('jobID')
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
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['status'] = 1
    response['errMsg'] = ""
    log_time.printLog(response)
    return make_response(jsonify(response))


#20201221
@app.route('/aes_async', methods=['POST'])
def aes_async():
    log_time = GetLogTime("aes_async")
    log_time.printLog("Start aes_async")

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
    #citc, 20220117
    key = input_["key"]
    sep_ = input_["sep"]
    columns_mac = input_["columns_mac"]
    projName = input_["projName"]
    projID = input_["projID"]
    dataHash = input_["dataHash"]
    onlyHash = input_["onlyHash"]

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

    #2022, citc add
    try:
        task = task_udfAESUID.aes_longTask.apply_async((tblName,key,sep_,columns_mac,projName,projID,dataHash,onlyHash))
        #task = task_udfAESUID.aes_longTask.apply_async((tblName,sep_,columns_mac,projName,projID,dataHash,onlyHash))

        response = dict()
        #response['state'] = state
        # response['sparkAppID'] = ''
        # response['celeryID'] = ''
        # response['status'] = ''
        # response['errMsg'] = ''
        response['projStep'] = 'data_aes'
        # response['dbName'] = ''
        # response['tblName'] = ''



        if True:
            state_ = "test"
            while True:
                mac_longTask_task = task_udfAESUID.aes_longTask.AsyncResult(task.id)
                state_ = mac_longTask_task.state
                response['state'] = state_
                response['celeyId'] = mac_longTask_task.id
                #print state_
                progress, progress_state =  check_appstatus(projID, 'AES_Enc') #pid=999 (fixed in udfAESUID_new.py) AES_ENC is NAME in udfAESUID_new.py
                #print("---- progress type 1---{}".format(type(progress_)))
                #progress_ = progress_+"t01"
                if progress >= 20:
                    # progress = 100
                    if state_ == 'PROGRESS':
                        # if task.info.get('jobID') is None:
                        #     response['err'] ='spark job fail'
                        #     break
                        #if task.info.get('kTable') is None:
                        #    response['err'] ='spark job fail'
                            # break
                        # response['status'] = '1'
                        # response['spark_jobID'] =task.info.get('jobID')
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
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        log_time.printLog(errMsg)
        return make_response(jsonify(response))

    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    log_time.printLog(response)
    return make_response(jsonify(response))



    # if True:
    #     state_ = "PROGRESS"
    #     #while state_ == 'PROGRESS':
    #     while True:
    #         mac_longTask_task = task_udfAESUID.aes_longTask.AsyncResult(task.id)
    #         state_ = mac_longTask_task.state
    #         response['state'] = state_
    #         response['celeyId'] = mac_longTask_task.id
    #         #print state_
    #         if state_ == 'ICL_START':
    #             if task.info.get('jobID') is None:
    #                 response['err'] ='spark job fail'
    #                 break
    #             #if task.info.get('kTable') is None:
    #             #    response['err'] ='spark job fail'
    #                 # break
    #             response['status'] = '1'
    #             response['spark_jobID'] =task.info.get('jobID')
    #             #response['out_path'] =task.info.get('out_path')
    #             state_ = 'PROGRESS'
    #             #print task.info
    #             #print(kcheck_longTask_task.backend)
    #             #self.update_state(state=states.PENDING)
    #             #break
    #         #if state_ == states.SUCCESS:
    #         if state_ == 'ICL_END':

    #             response['out_path'] =task.info.get('out_path')
    #             response['status'] = '1'
    #             break
    #         #if state_ == states.FAILURE:
    #         #    response['err'] ='celery job fail'
    #         #    break
    #         if state_ == 'FAIL_CELERY':
    #             response['err'] ='celery job fail'
    #             #meta_['errTable'] = errReson_ #in task_udfAESUID.py

    #             response['status'] = '-3'
    #             response['errMsg'] = task.info.get('errTable')
    #             if "not_fileExist" in response['errMsg']:
    #                 response['status'] = '-1'

    #             if "err_udfEncCols" in response['errMsg']:
    #                 response['status'] = '-2'    

                
    #             break            
    # #print(task.get(on_message=on_raw_message, propagate=False))
    # #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    # ts1 = time.time()
    # response['time_async'] =str(ts1-ts0)
    # log_time.printLog(response)
    # return make_response(jsonify(response))


#20200702 GetConfigList: list dataConfig/ config json
@app.route('/GetConfigList', methods=['POST'])
def GetConfigList():
    log_time = GetLogTime('GetConfigList')
    log_time.printLog("Start GetConfigList")

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

    task = task_GetConfigList.GetConfigList_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'GetConfigList'#str (select, gen, join, distinct,single k checking,export,import)
    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            GetConfigList_longTask_task = task_GetConfigList.GetConfigList_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = GetConfigList_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = GetConfigList_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['projStep'] = task.info.get('projStep')
                response['userID'] = task.info.get('userID')
                response['projName'] = task.info.get('projName')
                response['ConfigList'] = task.info.get('ConfigList')
                response['status'] = '1'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('Msg')
                response['errMsg'] = Msg
                log_time.printLog(Msg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  

#20200702 GetconfigData: user選了config.json>回傳config json to bruce
@app.route('/GetconfigData', methods=['POST'])
def GetconfigData():
    log_time = GetLogTime('GetconfigData')
    log_time.printLog("Start GetconfigData")

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

    task = task_GetconfigData.GetconfigData_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'GetconfigData'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            GetConfigList_longTask_task = task_GetConfigList.GetConfigList_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = GetConfigList_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = GetConfigList_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['projStep'] = task.info.get('projStep')
                response['userID'] = task.info.get('userID')
                response['projName'] = task.info.get('projName')
                response['configName'] = task.info.get('configName')
                response['configData'] = task.info.get('configData')
                response['status'] = '1'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('Msg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  

#20200702 UpdateConfigData: 使用者更新config > bruce回傳更新json>複寫原本的config file
@app.route('/UpdateConfigData', methods=['POST'])
def UpdateConfigData():
    log_time = GetLogTime('UpdateConfigData')
    log_time.printLog("Start UpdateConfigData")

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

    task = task_UpdateConfigData.UpdateConfigData_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'UpdateConfigData'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            UpdateConfigData_longTask_task = task_UpdateConfigData.UpdateConfigData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = UpdateConfigData_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = UpdateConfigData_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['projStep'] = task.info.get('projStep')
                response['userID'] = task.info.get('userID')
                response['projName'] = task.info.get('projName')
                response['configName'] = task.info.get('configName')
                response['status'] = '1'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('Msg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  

#20200703 task_CheckProjStatus: 使用者追蹤project狀態
@app.route('/CheckProjStatus', methods=['POST'])
def CheckProjStatus():
    log_time = GetLogTime('CheckProjStatus')
    log_time.printLog("Start CheckProjStatus")

    ts0 = time.time()
    try:
        parameter_fromweb = request.get_json() # get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
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

    task = task_CheckProjStatus.CheckProjStatus_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'CheckProjStatus'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            CheckProjStatus_longTask_task = task_CheckProjStatus.CheckProjStatus_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = CheckProjStatus_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = CheckProjStatus_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                flag= task.info.get('flag')
                if flag == "T":
                    response['Progress'] = task.info.get('Progress')
                    response['Progress_State'] = task.info.get('Progress_State')
                response['projStep'] = task.info.get('projStep')
                response['userID'] = task.info.get('userID')
                response['projName'] = task.info.get('projName')
                response['Project Status'] = task.info.get('Status')
                response['Data_filtered'] = task.info.get('Data_filtered') #20201223
                response['status'] = '1'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('Msg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  


#20200225
@app.route('/getReport_async', methods=['POST'])
def getReport_async():
    print("Start getReport_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    projName = data_raw['projName']
    print("Get project name: {}".format(projName))

    task = task_getReport.getReport_longTask.apply_async((projName,1))

    response = {}#python dict

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            getReport_longTask_task = task_getReport.getReport_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = getReport_longTask_task.state
            print (state_)
            if state_ == 'PROGRESS':
                response['report'] = task.info
                print(response)
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
    response['report'] = task.info
    print(response)
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#20200708 task_DeIdAsync: 測試Deid自動化[非同步]
@app.route('/DeIdAsync', methods=['POST'])
def DeIdAsync():
    log_time = GetLogTime('DeIdAsync')
    log_time.printLog("Start DeIdAsync")

    ts0 = time.time()
    try:
        parameter_fromweb = request.get_json() # get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
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

    task = task_DeIdAsync.DeIdAsync_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'DeIdAsync'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            DeIdAsync_longTask_task = task_DeIdAsync.DeIdAsync_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = DeIdAsync_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = DeIdAsync_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                flag= task.info.get('flag')
                # response['projStep'] = task.info.get('projStep')
                response['PID'] = task.info.get('PID')
                response['projName'] = task.info.get('projName')
                response['Project Status'] = task.info.get('projStep')
                response['status'] = '1'
                break
            #####errTable####################################################
            if state_ == 'errTable':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-2'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  

#20200708 task_DeIdAsync: 測試Deid自動化[非同步]
@app.route('/DeIdAsyncAES', methods=['POST'])
def DeIdAsyncAES():
    log_time = GetLogTime('DeIdAsync')
    log_time.printLog("Start DeIdAsync")

    ts0 = time.time()
    try:
        parameter_fromweb = request.get_json() # get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
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

    task = task_DeIdAsyncAES.DeIdAsync_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'DeIdAsyncAES'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            DeIdAsync_longTask_task = task_DeIdAsyncAES.DeIdAsync_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = DeIdAsync_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = DeIdAsync_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                flag= task.info.get('flag')
                # response['projStep'] = task.info.get('projStep')
                response['PID'] = task.info.get('PID')
                response['projName'] = task.info.get('projName')
                response['Project Status'] = task.info.get('projStep')
                response['status'] = '1'
                break
            #####errTable####################################################
            if state_ == 'errTable':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-2'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  

#20200708 task_DeIdAsync: 測試Deid自動化[非同步]
@app.route('/DeIdAsyncMac', methods=['POST'])
def DeIdAsyncMac():
    log_time = GetLogTime('DeIdAsyncMac')
    log_time.printLog("Start DeIdAsyncMac")

    ts0 = time.time()
    try:
        parameter_fromweb = request.get_json() # get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
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

    task = task_DeIdAsyncMac.DeIdAsync_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'DeIdAsyncAES'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            DeIdAsync_longTask_task = task_DeIdAsyncMac.DeIdAsync_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = DeIdAsync_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = DeIdAsync_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                flag= task.info.get('flag')
                # response['projStep'] = task.info.get('projStep')
                response['PID'] = task.info.get('PID')
                response['projName'] = task.info.get('projName')
                response['Project Status'] = task.info.get('projStep')
                response['status'] = '1'
                break
            #####errTable####################################################
            if state_ == 'errTable':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-2'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  


#20200930 swagger: 呼叫非同步hash自動化的flask API: /HashMac_Async
#swagger: create project > hashmac 
#task_HashMacAsync: 測試hashmac自動化[非同步]
@app.route('/HashMacAsync', methods=['POST'])
def HashMacAsync():
    log_time = GetLogTime('HashMacAsync')
    log_time.printLog("Start HashMacAsync")

    ts0 = time.time()
    try:
        parameter_fromweb = request.get_json() # get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
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

    task = task_HashMacAsync.HashMacAsync_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'HashMacAsync'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            HashMacAsync_longTask_task = task_HashMacAsync.HashMacAsync_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = HashMacAsync_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = HashMacAsync_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                flag= task.info.get('flag')
                # response['projStep'] = task.info.get('projStep')
                response['PID'] = task.info.get('PID')
                response['projName'] = task.info.get('projName')
                response['Project Status'] = task.info.get('projStep')
                response['status'] = '1'
                break
            #####errTable####################################################
            if state_ == 'errTable':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-2'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('errMsg')   
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-1'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'celery job fail'
                response['status'] = '-1'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    return make_response(jsonify(response))  

# 20201201 [塔台用]呼叫[非同步]Deid自動化(僅做到Gen)
# 建專案>讀取config檔自動檢查格式>hash>Gen
# task_DeIdGenAsync: 測試Deid自動化[非同步]
@app.route('/DeIdGenAsync', methods=['POST'])
def DeIdGenAsync():
    log_time = GetLogTime('DeIdGenAsync')
    log_time.printLog("Start DeIdGenAsync")

    ts0 = time.time()
    try:
        parameter_fromweb = request.get_json() # get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
    except Exception as e:
        response = dict()
        errMsg = 'Json format error: ' + str(e) # 210219: curl sent "", without dict()
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -2
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

    task = task_DeIdGenAsync.DeIdGenAsync_longTask.apply_async((jsonBase64, 1))

    response = dict()
    response['projStep'] = 'DeIdGenAsync'#str (select, gen, join, distinct,single k checking,export,import)

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            DeIdGenAsync_longTask_task = task_DeIdGenAsync.DeIdGenAsync_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = DeIdGenAsync_longTask_task.state
            #response['state'] = state_
            response['celeryID'] = DeIdGenAsync_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                flag= task.info.get('flag')
                # response['projStep'] = task.info.get('projStep')
                response['PID'] = task.info.get('PID')
                response['projName'] = task.info.get('projName')
                response['Project Status'] = task.info.get('projStep')
                response['status'] = '1'
                break
            #####errTable####################################################
            if state_ == 'errTable':
                errMsg = task.info.get('errMsg')
                response['errMsg'] =  'Unknown error: '+errMsg
                log_time.printLog(errMsg)
                response['status'] = '-99'
                break
            #####FAIL####################################################
            if state_ == 'FAIL':
                errMsg = task.info.get('errMsg')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = '-99'
                break
            #####DEID FAIL STATUS####################################################
            if state_ == 'DeIDFail':
                errMsg = task.info.get('errMsg')
                stateno = task.info.get('stateno')
                response['errMsg'] = errMsg
                log_time.printLog(errMsg)
                response['status'] = stateno#'-99'
                break
            #####SUCCESS#################################################
            # if state_ == states.SUCCESS:
            #     break
            if state_ == states.FAILURE:
                response['errMsg'] = 'Celery job fail'
                response['status'] = '-97'
                break
    ts1 = time.time()
    response['time_async'] = str(ts1-ts0)
    # base64_return = encodeDic(response)
    # log_time.printLog("Return base64: {0}".format(base64_return))
    # log_time.printLog(response)
    # return make_response(jsonify({'jsonBase64':base64_return}))
    return make_response(jsonify(response))  

    #to do list: 
    #flask.py,celery.py,views.py >> import task_DeIdGenAsync
    #task_DeIdGenAsync>>建專案>讀取config檔自動檢查格式，存檔過濾>hash>Gen
# InterAgent export data with AES 2020DEC-Jade
@app.route('/exportData_InterAgent', methods=['POST'])
def exportData_InterAgent():
    log_time = GetLogTime('exportData_InterAgent')
    log_time.printLog("Start exportData_InterAgent")

    ts0 = time.time()

    response = dict()

    #response['celeryID'] = ''#str
    #response['status'] = ''#str (1: succeed, -1: fail )
    #response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
    response['projStep'] = 'export'#str (select, gen, join, distinct,single k checking,export,import)
    #response['dbName'] = ''#str
    #response['tblName'] = ''#str

    try:
        parameter_fromweb = request.get_json()# get parameter from swagger curl
        print(parameter_fromweb)
        data_jsonBase64__ = base64.b64encode(json.dumps(parameter_fromweb).encode('utf-8')) # b64encode curl parameter for task_xxx
        data_raw = {'jsonBase64':data_jsonBase64__} # recombine json for task_xxx
        print('#################')
        print(data_raw)
        print('#################')
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

    task = task_exportData_InterAgent.exportData_InterAgent_longTask.apply_async((jsonBase64, 1))

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####2018014, citc trace#####################################################
            exportData_longTask_task = task_exportData_InterAgent.exportData_InterAgent_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = exportData_longTask_task.state
            #print(state_)
            #response['state'] = state_
            #response['celeryID'] = exportData_longTask_task.id
            if state_ == 'PROGRESS':
                response['dbName'] = task.info.get('dbName').strip('\n')
                response['tblName'] = task.info.get('tblName').strip('\n')
                #response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
                response['outputPath'] = task.info.get('outputPath').strip('\n')
                #response['status'] = '1'
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
    #response['time_async'] = str(ts1-ts0)
    #base64_return = encodeDic(response)
    #log_time.printLog("Return base64: {0}".format(base64_return))
    log_time.printLog(response)
    print(response)
    return make_response(jsonify(response))
