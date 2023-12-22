# -*- coding: utf-8 -*-
#!/usr/bin/python

"""
Created on 20200708 DeIdAsync

@author: A70353
"""
import pandas as pd
import numpy as np
    
import requests

from config.connect_sql import ConnectSQL 
from config.loginInfo import getConfig

from log.logging_tester import _getLogger

from flask import render_template, request, jsonify,make_response
import time
import sys
import os
import json

def check_appstatus(proj_id, Application_Name):
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        print('errTable: connect sql error [check_appstatus]. {0}'.format(str(e)))
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
        print('errTable: check_appstatus error. {0}'.format(str(e)))

# update process status to mysql
def updateToMysql(conn, project_id, valueSampleData, sqltable):
#def updateToMysql_config(conn, project_id, qi_col, minKvalue, after_col_value, tableDisCount, gen_qi_settingvalue, tablekeycol):
    # print('########updateToMysql###########')
    condisionSampleData = {
            'project_id': str(project_id)
        }

    # print(valueSampleData)

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
        errMsg = 'errTable: updateToMysql_config fail'
        print(errMsg)

#citc, 20220308
def get_host_name():
    host_file = "/host_name"
    try:
        with open(host_file,'r') as fp:
            host_name= fp.read()
            host_name=host_name.strip()
            return host_name
    except Exception as e:
        return "gethostname err"+str(e)

def test_get_response(errMsg):
    response = dict()


    response['status'] = -100
    response['errMsg'] = errMsg
    #log_time.printLog(errMsg)
    return make_response(jsonify(response))

#0708
def main(args):

    global  _logger,_vlogger, check_conn     
    # debug log
    _logger  =_getLogger('error__DeIdAsync')
    # verify log
    _vlogger =_getLogger('verify__DeIdAsync')

    ################################
    #get ip config for openapi
    # web_ip,web_port,flask_ip,flask_port = getConfig().getOpenAPI_withoutHostName()
    # curren_host = get_host_name()
    # if "gethostname err" in curren_host:
    #     return test_get_response("get host name error"+curren_host)
    # web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
    curren_host = get_host_name()
    web_ip,web_port,flask_ip,flask_port,hsm_key, hsm_url = getConfig().getOpenAPI(curren_host)
    web_ip = str(web_ip)
    web_port = str(web_port)
    flask_ip = str(flask_ip)
    flask_port = str(flask_port)
    ################################

    pname = args['pname'].encode("utf-8")
    prodesc =  args['prodesc'].encode("utf-8")
    powner =  args['powner']
    p_dsname =  args['p_dsname'] #projName
    step = args['step']
    configName = args['configName']
    #for hash
    hashTableName = args['hashTableName']
    hashkey = args['hashkey']
    sep = args['sep']
    columns_mac = args['columns_mac']
    dataHash = args['dataHash']
    onlyHash = args['onlyHash']
    uId = args['memberid']
    uAccount = args['memberacc']
    response = {}

    '''
    #create project
    try:
        InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc ,'memberid': uId,'memberacc': uAccount} 
        response_get = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para, verify=False)
        print(response_get.url)
        response_dic = response_get.json()
        # _vlogger.debug('InsertProject_flag: '+ str(response_dic))
        print("response_get: ",response_dic)
        response['InsertProject_flag']=response_dic
    except Exception as e:
        _logger.debug('errTable: InsertProject_request error. {0}'.format(str(e)))

    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            _vlogger.debug('InsertProject_flag: '+ str(response_dic))
            print("citc____Mission START")
            # pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = '專案名稱重複'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            _logger.debug('errTable: {0}'.format(str(errMsg)))
            sys.exit(0)
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = '專案狀態錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            _logger.debug('errTable: {0}'.format(str(errMsg)))
            sys.exit(0)
        else:
            error_insertproj ='系統寫入出現錯誤'
            errMsg = 'InsertProject fail: - %s' %(error_insertproj)
            _logger.debug('errTable: {0}'.format(str(errMsg)))
            sys.exit(0)
    except Exception as e:
        _logger.debug('errTable: InsertProject error. {0}'.format(str(e)))
        sys.exit(0)
    '''

    # get the parameter:pid in mysql
    time.sleep(5)
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'connectToMysql get pid fail: - %s:%s' %(type(e).__name__, e)
        _logger.debug('errTable: {0}'.format(str(errMsg)))
    try: # fetch parameter: pid
        sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project` where project_name like '{}';".format(p_dsname)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            pid = resultCheck["fetchall"][0]['project_id']
            response['pid'] = str(pid)
        check_conn.close()
    except Exception as e:
        errMsg = 'fetch pid fail: - %s:%s' %(type(e).__name__, e)
        _logger.debug('errTable: {0}'.format(str(errMsg)))

    # FOR Mac API:  /api/WebAPI/hash
    try:
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash,
                "onlyHash": onlyHash
                }
        response_g = requests.post("https://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("HASH JSON: ",response_dic)
        _logger.debug('HashMac_flag: '+ str(1))
        response['HashMac']='1' #response_dic['state']
    except Exception as e:
        _logger.debug('errTable: Hash_request error. {0}'.format(str(e)))

    # check hash status
    progress = 0
    while int(progress) != 100:
        try:
            progress, progress_state =  check_appstatus(pid, 'udfMacUID')
            if int(progress) == 100:
                break;
            if progress_state == 'err':
                errMsg = "hash fail: No file?"
                _logger.debug('errTable: {0}'.format(str(errMsg)))           
                break;
        except Exception as e:
            pass
    
    #0709 create proj > hash > import
    # /api/WebAPI/ImportData
    # Need parameter:pid
    # if  int(response['InsertProject_flag'])==1:
    try: #API:ImportData
        ImportData_para = { "p_dsname": p_dsname, "pid": pid, 'memberid': uId,'memberacc': uAccount }
        print('ImportData_para: ',ImportData_para)
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/ImportData", params=ImportData_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("IMPORT DATA JSON: ",response_dic)
        response['ImportData_flag']=response_dic
        _logger.debug('ImportData_flag: '+ str(response_dic))
    except Exception as e:
        _logger.debug('errTable: ImportData error. {0}'.format(str(e)))

    # check importdat status
    progress = 0 
    while int(progress) != 100:
        print("check_appstatus(pid,import)")
        try: 
            time.sleep(15)
            progress, progress_state  =  check_appstatus(pid, 'import')
            if int(progress) == 100:
                break;
            if progress_state == 'err':
                errMsg = "import data fail"
                _logger.debug('errTable: {0}'.format(errMsg))           
                break;
        except Exception as e:
            pass   

    print("**********************")
    print("**********************")
    print("**********************")
    _logger.debug("**********************")

    #2020.07.10: if progress==100, import > config rule
    if int(progress)==100:
        try:
            # get parameter from config file
            # print("getConfig().getExportPath('local')")
            path = getConfig().getExportPath('local')
            configPath = os.path.join(path[:-12], 'dataConfig/') + configName
            with open(configPath, 'r') as read_file:
                dict_data = json.load(read_file)
            qi_col = dict_data['qi_col']
            _logger.debug('qi_col: {}'.format(qi_col))
            minKvalue = dict_data['minKvalue']
            _logger.debug('minKvalue: {}'.format(minKvalue))
            pro_col_cht_config = dict_data['pro_col_cht']  #important comparing
            after_col_value = dict_data['after_col_value'] #important
            # tableDisCount = dict_data['tableDisCount']
            gen_qi_settingvalue = dict_data['gen_qi_settingvalue']
            tablekeycol = dict_data['tablekeycol']
            pro_tb_config = dict_data['pro_tb']
            r_value = dict_data['r_value']
            t1 = dict_data['t1']
            t2 = dict_data['t2']
            
            valueSampleData = {
            'project_id': pid,
            'qi_col': qi_col,
            'minKvalue': minKvalue,
            'after_col_value': after_col_value,
            # 'tableDisCount': tableDisCount,
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
            _logger.debug('pro_col_cht_config_array: {}'.format(pro_col_cht_config_array))
            _logger.debug('pro_col_cht_array: {}'.format(pro_col_cht_array))
            _logger.debug('pro_col_en_array: {}'.format(pro_col_en_array))
            _logger.debug('after_col_value_array: {}'.format(after_col_value_array))
            _logger.debug('after_col_value_update: {}'.format(after_col_value_update))
            # #202020620: check config.json pro_tb is mapping to the project right now.
            # if pro_tb != pro_tb_config:
            #     updateToMysql(check_conn, pid, {'project_status':'98','statusname':'錯誤的config檔案'}, 'T_ProjectStatus')
            #     errMsg = 'request_error: ' + 'plz check the used config is mapping the project.'
            #     _logger.debug('errTable: {0}'.format(str(errMsg)))
            #     sys.exit(0)

            #check: len not same
            if len(pro_col_cht_config_array)!=len(pro_col_cht_array):
                updateToMysql(check_conn, pid, {'project_status':'98','statusname':'錯誤的config檔案:欄位數'}, 'T_ProjectStatus')
                errMsg = 'request_error: ' + '#. col is not equal to the #. in config'
                _logger.debug('errTable: {0}'.format(str(errMsg)))
                sys.exit(0)
            
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
                            updateToMysql(check_conn, pid, {'project_status':'98','statusname':'錯誤的config檔案:欄位名稱'}, 'T_ProjectStatus')
                            errMsg = 'request_error: ' + 'the column name of dataset is not same as config dataset'
                            _logger.debug('errTable: {0}'.format(str(errMsg)))
                            sys.exit(0)

            _logger.debug('after_col_value_update len : {}'.format(len(after_col_value_update)))
            _logger.debug('pro_col_cht_array len : {}'.format(len(pro_col_cht_array)))
            _logger.debug('pro_col_en_array len : {}'.format(len(pro_col_en_array)))

            no_cht_choose = []
            no_en_choose = []

            try:
                for k in range(len(after_col_value_update)):
                    _logger.debug('k   : {}'.format(k))
                    _logger.debug('after_col_value_update[k]  : {}'.format(after_col_value_update[k]))
                    if int(after_col_value_update[k])==0:
                        no_cht_choose.append(pro_col_cht_array[k])
                        no_en_choose.append(pro_col_en_array[k])
            except Exception as e:
                errMsg = 'request_config_error: ' + str(e)
                _logger.debug('request_after_col_value_update_error: {0}'.format(str(errMsg)))

            pro_col_cht_array = [x for x in pro_col_cht_array if (x not in no_cht_choose)]
            pro_col_en_array =  [x for x in pro_col_en_array if (x not in no_en_choose)]

            _logger.debug('pro_col_cht_array: {}'.format(pro_col_cht_array))
            _logger.debug('pro_col_en_array: {}'.format(pro_col_en_array))

            valueSampleData['after_col_value']=','.join(after_col_value_update)
            valueSampleData['after_col_cht']=','.join(pro_col_cht_array)
            valueSampleData['after_col_en']=','.join(pro_col_en_array)
            #Read config AND insert to mysql tbl for gen
            updateToMysql(check_conn, pid, valueSampleData, 'T_Project_SampleTable')
            #update rule status
            updateToMysql(check_conn, pid, {'project_status':'5'}, 'T_ProjectStatus')
            check_conn.close()
            print("check_conn, pid, project_status:5, T_ProjectStatus")
            response['check_flag']= int(progress)
            #return make_response(jsonify(response))    
        except Exception as e:
            errMsg = 'request_config_error: ' + str(e)
            _logger.debug('{0}'.format(str(errMsg)))
            sys.exit(0)
        
    # /api/WebAPI/Generalizationasync
    try: #API:Generalizationasync
        _logger.debug('gen_qi_settingvalue: {}'.format(gen_qi_settingvalue))
        settingvalue_split = gen_qi_settingvalue.split("*")
        if len(settingvalue_split) == 2:
            gen_qi_settingvalue = pro_tb + "*" + gen_qi_settingvalue.encode('utf8')
        else:
            gen_qi_settingvalue = gen_qi_settingvalue.encode('utf8')
        _logger.debug('gen_qi_settingvalue_utf8: {}'.format(gen_qi_settingvalue))
        Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue":gen_qi_settingvalue, "k_value":minKvalue, "tablename":pro_tb,'memberid': uId,'memberacc': uAccount}#, "pro_col_en":pro_col_en,"pro_col_cht":pro_col_cht}
        print('Gen_para: ',Gen_para)
        _logger.debug('Gen_para: {}'.format(Gen_para))
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("Gen DATA JSON: ",response_dic)
        response['Gen__flag']=response_dic
        _logger.debug('response: {}'.format(response))
    except Exception as e:
        errMsg = 'request_Gen_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    # check_status
    if str(response['Gen__flag']) != 'False':
        progress = 0 #check_appstatus(pid , 'import')
        while int(progress) != 100:
            try: 
                time.sleep(15)
                progress, progress_state  =  check_appstatus(pid, 'gen')
                if int(progress) == 100:
                    break;
                if progress_state == 'err':#int(progress) == 10:
                    errMsg = 'projstatus error: ' + "gen fail?"
                    _logger.debug('errTable: {0}'.format(str(errMsg)))           
                    break;
            except Exception as e:
                #progress = 0
                pass
    else:
        errMsg = 'GEN_check_error'
        _logger.debug('{0}'.format(errMsg))

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
        errMsg = 'fetch_finaltblName_fail: - %s:%s' %(type(e).__name__, e)
        _logger.debug('{0}'.format(errMsg))     

    try: #API:GetSingleTable
        GetSingleTable_para = {"pid":pid, "pname": p_dsname, "tablename":finaltblName, "jobname":'job1','memberid': uId,'memberacc': uAccount}
        print('GetSingleTable_para: '+str(GetSingleTable_para))
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/GetSingleTable", params=GetSingleTable_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("GetSingleTable DATA JSON: ",response_dic)
        response['GetSingle__flag']=response_dic
            #return make_response(jsonify(response))
    except Exception as e:
        errMsg = 'request_GetSingleTable_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    #kchecking-2
    #/api/WebAPI/GetKChecking
    try: #API:GetKChecking
        GetKChecking_para = {"pid":pid, "pname": p_dsname, "jobname":'job1','memberid': uId,'memberacc': uAccount}
        print('GetKChecking_para: '+str(GetKChecking_para))
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/GetKChecking", params=GetKChecking_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("GetKChecking DATA JSON: ",response_dic)
        response['GetKChecking__flag']=response_dic
    except Exception as e:
        errMsg = 'request_GetKChecking_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    # check getKchecking_one status
    progress = 0 
    while int(progress) != 100:
        try: 
            time.sleep(15)
            progress, progress_state  =  check_appstatus(pid, 'getKchecking_one')
            if int(progress) == 100:
                break;
            if progress_state == 'err':#int(progress) == 10:
                errMsg = 'projstatus error: ' + "getKchecking_one fail?"
                _logger.debug('{0}'.format(errMsg)) 
                break;
        except Exception as e:
            pass    

    try: 
        ExportData_para = {"pid":pid, "p_dsname": p_dsname,'memberid': uId,'memberacc': uAccount}
        print('ExportData_para: ',ExportData_para)
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/ExportData", params=ExportData_para,timeout=None, verify=False)
        response_dic = response_g.json()
        print("Export DATA JSON: ",response_dic)
        response['ExportData_flag']=response_dic
        response['gen_flag']='finish'
        #return make_response(jsonify(response))
    except Exception as e:
        errMsg = 'request_export_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    # #save df_drop.head() to sql
    # #data = df_drop.sample(n=5).to_json(orient='records')
    # data = df_drop.head(5).to_json(orient='records')
    # try:
    #     updateToMysql_sample(check_conn,userID,projID, projName, fileName, data)
    #     _vlogger.debug('sampleStr_succeed.')
    # except Exception as e:
    #     _logger.debug('errTable: Sample fail. {0}'.format(str(e)))
    #     return

    # #save df_drop.ob_columns to sql
    # try:
    #     #list: pro_col_en,pro_col_cht,ob_col
    #     #updateToMysql_colType(conn,projID, projName, fileName, pro_col_en,pro_col_cht,tableCount,ob_col)
    #     updateToMysql_colType(check_conn,userID,projID, projName, fileName, all_raw_col, all_col,tableCount,ob_col,join_drop_columns,pro_col_en_nunique)
    #     _vlogger.debug('insert column type succeed.')
    # except Exception as e:
    #     _logger.debug('errTable: insert column type fail. {0}'.format(str(e)))
    #     return
    # try:
    #         #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
    #     updateToMysql_status(check_conn,userID, projID, projName, fileName, 'finish', 100)
    #         #_vlogger.debug('updateToMysql_status succeed.')
    # except Exception as e:
    #     _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
    #     return None
    print("citc_final____Mission Complete")




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-pname", "--pname", help='專案名稱')
    parser.add_argument("-p_dsname", "--p_dsname", help='專案資料集名稱')
    parser.add_argument("-prodesc", "--prodesc", help='專案描述')
    parser.add_argument("-powner", "--powner", help='1: deidadmin')

    parser.add_argument("-step", "--step", help='default is 1')
    parser.add_argument("-configName", "--configName", help='欄位判定與概化條件要用的json')
    parser.add_argument("-hashTableName", "--hashTableName", help='在dataMac的裡的資料名稱')
    parser.add_argument("-hashkey", "--hashkey", help='需要的key')
    parser.add_argument("-sep", "--sep", help='資料集分隔符號')
    parser.add_argument("-columns_mac", "--columns_mac", help='hash需要的id column')
    parser.add_argument("-dataHash", "--dataHash", help='是否hash')
    parser.add_argument("-onlyHash", "--onlyHash", help='default is "N"')
    parser.add_argument("-memberid", "--memberid", help='memberid')
    parser.add_argument("-memberacc", "--memberacc", help='memberacc')
    args = vars(parser.parse_args())
    print(args)
    print ("in __main__")
    main(args)
