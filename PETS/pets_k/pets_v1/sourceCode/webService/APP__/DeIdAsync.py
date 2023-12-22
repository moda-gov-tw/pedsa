# -*- coding: utf-8 -*-
#!/usr/bin/python

"""
Created on 20210723  DeIdAsync.py
#塔台的輸入&檢查 概化 +K檢查 +匯出

@author: A70353
"""
import pandas as pd
import numpy as np
    
import requests

from config.connect_sql import ConnectSQL 
from config.loginInfo import getConfig

from log.logging_tester import _getLogger


import time
import sys
import os
import json
import io
import base64
import datetime as dt
import math 

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
        print('errTable: check_appstatus error-2. {0}, {1}'.format(str(e),str(Application_Name)))

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
        errMsg = 'errTable: updateToMysql fail'
        print(errMsg)

# update process status to mysql
def insertToMysql(conn, project_id, valueSampleData, sqltable):
#def updateToMysql_config(conn, project_id, qi_col, minKvalue, after_col_value, tableDisCount, gen_qi_settingvalue, tablekeycol):
    # print('########updateToMysql###########')
    # condisionSampleData = {
    #         'project_id': project_id
    #     }

    # print(valueSampleData)

    resultSampleData = conn.insertValue('DeIdService',
                                            sqltable,
                                            valueSampleData)
    print(resultSampleData)
    if resultSampleData['result'] == 1:
        print("update mysql: SUCCESS!")
            #conn.close()
        return None
    else:
        errMsg = 'errTable: insertToMysql fail'
        print(errMsg)


def select_cols(checkjson):
    #read json
    with io.open(checkjson, 'r',encoding="utf-8") as reader:
        jf = json.loads(reader.read())

    pro_col_cht = jf['pro_col_cht'] #column name
    col_cht = pro_col_cht.split(',')
    #dataitem_id = jf['dataitem'] #ID
    
    #datatype = jf['datatype'] #datatype
    target_col = jf['target_col'] 
    #isNull_ = jf['isNull'].split(',')
#     print(datatype)
    #get datatype
    #cols_type = datatype.split(',')
#     print(cols_type)
    #get the type of column is numeric 
    #float_col = []
    #for i in range(len(cols_type)):
    #    if cols_type[i] == 'number': #col: number
    #        float_col.append(i)
            
    return col_cht, target_col #dataitem_id, float_col, cols_type, isNull_

def check_type(df, id_col, numeric_col, col_cht, isNull_):
    #check column name
    df_cols = df.columns.tolist()
#     if len(list(set(df_cols).symmetric_difference(set(col_cht)))) != 0:
#         print('error column name')
#         return 'False', 'False'
    print('isNull_' ,isNull_)
    DF = df.copy()

    #選擇有N的欄位進行過濾
    null_indexes = [n for n,x in enumerate(isNull_) if x=='N']
    print("null_indexes: ", null_indexes)    
    df_cols_null = [df_cols[i] for i in null_indexes]
    # print("df_cols_null: ", df_cols_null)  
    df = df.dropna(subset=df_cols_null)
    # print("df_null: ",df.shape)
    # print("DF_null: ",DF.shape)
    drop_row_id_null = list(set(DF[id_col].values) - set(df[id_col].values))
    # print('drop_row_id_null', drop_row_id_null)
    # print("i_null: ",df.shape)
    df = df.replace(np.nan, math.pi)    
    # print(df.head(10))  

    #數字欄位的有字串可以被找到
    for i in numeric_col:
        index_ = df_cols[i]
        df[index_] = pd.to_numeric(df[index_], errors='coerce')
    new_df = df.dropna(axis = 0, how ='any') 

    if new_df.shape[0] != DF.shape[0]:
    #     id_col_idx = df.columns.tolist()[id_col]
        # print(df.head())
        # print(new_df.head())
        complete_flag = "False"       
        drop_row_id = list(set(DF[id_col].values) - set(new_df[id_col].values))
        drop_row = DF.loc[DF[id_col].isin(drop_row_id)].to_json(orient='records')
#         drop_row = df[id_col][drop_row_id].to_json(orient='records')
    else:
        complete_flag ="True"
        drop_row = "None"
        drop_row_id="None"

    new_df = new_df.replace(math.pi, np.nan)

    return complete_flag, drop_row, drop_row_id, new_df  

def list_clean(_list):
    json_encoded_list = json.dumps(_list)
    b64_encoded_list = base64.b64encode(json_encoded_list.encode("utf-8"))
    print("b64_encoded_list: ",b64_encoded_list)
    decoded_list = base64.b64decode(b64_encoded_list)
    my_list_again = json.loads(decoded_list)
    print("my_list_again: ",my_list_again)
    return b64_encoded_list.decode("utf-8")

#20201203
def main(args):

    global  _logger,_vlogger, check_conn     
    # debug log
    _logger  =_getLogger('error__DeIdAsync')
    # verify log
    _vlogger =_getLogger('verify__DeIdAsync')

    ################################
    #get ip config for openapi
    web_ip,web_port,flask_ip,flask_port = getConfig().getOpenAPI()
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
    sep_ = args['sep']
    columns_mac = args['columns_mac']
    dataHash = args['dataHash']
    onlyHash = args['onlyHash']
    # onlyGen = args['onlyGen']

    response = {}


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

    try: # update project status
        check_conn = ConnectSQL()
        updateToMysql(check_conn, pid, {'project_status':1000,'statusname':'檢查資料欄位'}, 'T_ProjectStatus')
        check_conn.close()
    except Exception as e:
        errMsg = 'datafilter update projectstatus: - %s:%s' %(type(e).__name__, e)
        _logger.debug('errTable: {0}'.format(str(errMsg)))

    #檢查資料欄位>filter nan>再save來給hash
    try:
        # get parameter from config file
        path = getConfig().getExportPath('local')
        configPath = os.path.join(path[:-12], 'dataConfig/') + configName
        path_ = "/home/hadoop/proj_/dataMac/input/" + hashTableName + ".csv"

        #重組分隔符號
        re_sep_ = ""
        # sep_ = "^|"
        # print(sep_)
        for i_sep_ in sep_:
        #   print(i)
          re_sep_=re_sep_+"\\"+str(i_sep_)

        df = pd.read_csv(path_,sep = re_sep_)#"\^\|")
        
        tableCount_before = df.shape[0]

        #step1:read json
        #col_cht, id_col, float_col, datatype, isNull_, target_col = select_cols(configPath)
        col_cht, target_col = select_cols(configPath)

        #step2:check df: complete_flag(True:完整), drop_row, drop_row_id, new_df
        #complete_flag, drop_row, drop_row_id, new_df = check_type(df, id_col, float_col, col_cht, isNull_)  
        '''
        # if complete_flag == "False", 過濾資料update data/sql table
        if complete_flag == "False":
            #以"^|"作為分隔符號寫檔
            myCsv = new_df.astype(str).apply(lambda x: sep_.join(x), axis=1)
            myCsv.rename(sep_.join(new_df.columns)).to_csv(path_, header=True,index=False)
            # myCsv = new_df.astype(str).apply(lambda x: '^|'.join(x), axis=1)
            # myCsv.rename('^|'.join(new_df.columns)).to_csv(path_, header=True,index=False)

            # with open("/home/hadoop/proj_/dataMac/input/" +hashTableName+"drop_row.txt", "w") as fp:
            #     json.dump(drop_row_id, fp)
            drop_row_base64 = list_clean(drop_row)
            #塔台過濾資料table更新到mysql    
            valueSampleData_filter = {
                'project_id': str(pid),
                'project_name': p_dsname,
                'pdf_data': drop_row_base64, #被過濾的資料內容(一整列含欄位名稱)用json
                'pdf_item': ','.join(drop_row_id), #被過濾的item
                'pdf_config': configName #那個時間點使用的config
                # 'createtime': str(dt.datetime.now())
                }
            print(valueSampleData_filter)
            try:
                check_conn = ConnectSQL()
                insertToMysql(check_conn, pid, valueSampleData_filter, 'T_ProjectDataFilter')
                check_conn.close()
            except Exception as e:
                _logger.debug('errTable: update T_ProjectDataFilter error. {0}'.format(str(e)))
        '''
        # with open("test.txt", "r") as fp:
        #     b = json.load(fp)
    except Exception as e:
        errMsg = 'DeIdAsync check error: - %s:%s' %(type(e).__name__, e)
        _logger.debug('errTable: {0}'.format(str(errMsg)))
       
    try: # datafilter update project status
        check_conn = ConnectSQL()
        updateToMysql(check_conn, pid, {'project_status':1,'statusname':'資料匯入'}, 'T_ProjectStatus')
        check_conn.close()
    except Exception as e:
        errMsg = 'datafilter update projectstatus2: - %s:%s' %(type(e).__name__, e)
        _logger.debug('errTable: {0}'.format(str(errMsg)))
    
    # FOR Mac API:  flask: aes_async(no hashkey)
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
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None)
        #response_g = requests.post("http://"+flask_ip+":"+flask_port+"/aes_async", json=Hash_para,timeout=None)
        #response_dic = response_g.json()
        #print("HASH JSON: ",response_dic)
        _vlogger.debug('AES_HashMac_flag: '+ str(1))
        response['HashMac']='1' #response_dic['state']
    except Exception as e:
        _logger.debug('errTable: AES_Hash_request error. {0}'.format(str(e)))

    # check hash status
    progress = 0
    while int(progress) != 100:
        try:
            time.sleep(15)
            progress, progress_state =  check_appstatus(pid, 'udfMacUID')
            if int(progress) == 100:
                break;
            if progress_state == 'err':
                errMsg = "hash fail: No file?"
                _logger.debug('errTable: {0}'.format(str(errMsg)))           
                break;
        except Exception as e:
            pass
    
    #0709 create proj > AEShash > import
    # /api/WebAPI/ImportData
    # Need parameter:pid
    # if  int(response['InsertProject_flag'])==1:
    try: #API:ImportData
        ImportData_para = { "p_dsname": p_dsname, "pid": pid }
        print('ImportData_para: ',ImportData_para)
        response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/ImportData", params=ImportData_para,timeout=None)
        response_dic = response_g.json()
        print("IMPORT DATA JSON: ",response_dic)
        response['ImportData_flag']=response_dic
        _vlogger.debug('ImportData_flag: '+ str(response_dic))
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
            minKvalue = dict_data['minKvalue'] #'3':需要補
            pro_col_cht_config = dict_data['pro_col_cht']  #important comparing
            after_col_value = dict_data['after_col_value'] #important
            #tableDisCount = new_df.shape[0] #dict_data['tableDisCount']
            gen_qi_settingvalue = dict_data['gen_qi_settingvalue']
            tablekeycol = dict_data['tablekeycol']
            # pro_tb_config = dict_data['pro_tb']
            
            valueSampleData = {
            'project_id': pid,
            'qi_col': qi_col,
            'minKvalue': minKvalue,
            'after_col_value': after_col_value,
            #'tableDisCount': tableDisCount,
            'gen_qi_settingvalue': gen_qi_settingvalue,
            'tablekeycol': tablekeycol
            }
            check_conn = ConnectSQL()

            sqlStr = "UPDATE `DeIdService`.`T_Project_SampleTable` SET tableCount_before = '{}'  where project_id like '{}';".format(tableCount_before,pid)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                print("SUCCESS:insert tableCount_before ")

            sqlStr = "UPDATE `DeIdService`.`T_Project_SampleTable` SET dataconfig = '{}'  where project_id like '{}';".format(configName,pid)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                print("SUCCESS:insert configName ")

            #202020620: check config.json pro_tb is mapping to the project right now.
            sqlStr = "SELECT pro_tb  FROM `DeIdService`.`T_Project_SampleTable` where project_id like '{}';".format(pid)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                pro_tb = resultCheck["fetchall"][0]['pro_tb']
                
            # temp_gen_qi = valueSampleData['gen_qi_settingvalue'].split('*')
            # temp_gen_qi[0] = pro_tb
            #valueSampleData['gen_qi_settingvalue'] = '*'.join(temp_gen_qi)
            valueSampleData['gen_qi_settingvalue'] = pro_tb+'*'+gen_qi_settingvalue
            selectqivalue = pro_tb+'*'+gen_qi_settingvalue
            # print('####################')
            # print('####################')
            # print(selectqivalue)

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
            print("check_conn, pid, project_status:5, T_ProjectStatus")
            response['check_flag']= int(progress)
            #return make_response(jsonify(response))    
        except Exception as e:
            errMsg = 'request_config_error: ' + str(e)
            _logger.debug('{0}'.format(str(errMsg)))
            sys.exit(0)
    
    ###20210723:原版概化+K檢查+匯出
    # /api/WebAPI/Generalizationasync
    try: #API:Generalizationasync
        Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue":selectqivalue,"k_value":minKvalue, "tablename":pro_tb}#, "pro_col_en":pro_col_en,"pro_col_cht":pro_col_cht}
        print('Gen_para: ',Gen_para)
        response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None)
        response_dic = response_g.json()
        print("Gen DATA JSON: ",response_dic)
        response['Gen__flag']=response_dic
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
        GetSingleTable_para = {"pid":pid, "pname": p_dsname, "tablename":finaltblName, "jobname":'job1'}
        print('GetSingleTable_para: '+str(GetSingleTable_para))
        response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/GetSingleTable", params=GetSingleTable_para,timeout=None)
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
        GetKChecking_para = {"pid":pid, "pname": p_dsname, "jobname":'job1'}
        print('GetKChecking_para: '+str(GetKChecking_para))
        response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/GetKChecking", params=GetKChecking_para,timeout=None)
        response_dic = response_g.json()
        print("GetKChecking DATA JSON: ",response_dic)
        response['GetKChecking__flag']=response_dic
    except Exception as e:
        errMsg = 'request_GetKChecking_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    # check getKchecking_one status
    progress = 0 
    status_start = time.time()
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
            # if time.time()-status_start > 120:
            #     errMsg = 'projstatus error: ' + "getKchecking_one fail?"         
            #     _logger.debug('{0}'.format(errMsg)) 
            #     break;

        except Exception as e:
            pass    

    #MLutility
    try:
        #get MLutility variable
        check_conn = ConnectSQL()
        sqlStr = "SELECT finaltblName  FROM `DeIdService`.`T_Project_SampleTable` where project_id like '{}';".format(pid)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            fname = resultCheck["fetchall"][0]['finaltblName']
        check_conn.close()
    except Exception as e:
        errMsg = 'fetch_finaltblName_fail: - %s:%s' %(type(e).__name__, e)
        _logger.debug('{0}'.format(errMsg))

    #/api/WebAPI/SendMLutility
    try: #API:SendMLutility
        SendMLutility_para = {"pid":pid, "pname": p_dsname, "fname":fname, "targernm":target_col}
        print('SendMLutility_para: '+str(SendMLutility_para))
        response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/SendMLutility", params=SendMLutility_para,timeout=None)
        response_dic = response_g.json()
        print("SendMLutility DATA JSON: ",response_dic)
        response['SendMLutility__flag']=response_dic
    except Exception as e:
        errMsg = 'request_SendMLutility_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    # check MLutility status
    progress = 0 
    status_start = time.time()
    while int(progress) != 100:
        try: 
            time.sleep(30)
            progress, progress_state  =  check_appstatus(pid, 'MLutility')
            if int(progress) == 100:
                break;
            if progress_state == 'Error':#int(progress) == 10:
                errMsg = 'projstatus error: ' + "MLutility fail? check hadoop log!"         
                _logger.debug('{0}'.format(errMsg)) 
                break;
        except Exception as e:
            pass

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
        errMsg = 'request_export_error: ' + str(e)
        _logger.debug('{0}'.format(errMsg))

    print("citc_final____Mission Complete")


    '''    
    # /api/WebAPI/Generalizationasync
    try: #API:Generalizationasync
        Gen_para = {"pid":pid, "pname": p_dsname, "selectqivalue": selectqivalue, "k_value":minKvalue, "tablename":pro_tb}#, "pro_col_en":pro_col_en,"pro_col_cht":pro_col_cht}
        print('Gen_para: ',Gen_para)
        # response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/Generalizationasync", params=Gen_para,timeout=None)
        #20201223: 塔台用GEN
        response_g = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/Generalization_InterAgent_Async", params=Gen_para,timeout=None)
        response_dic = response_g.json()
        print("Gen DATA JSON: ",response_dic)
        response['Gen__flag']=response_dic
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
    
    print("citc_final____Mission Complete")
    '''




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
    # parser.add_argument("-onlyGen", "--onlyGen", help='True,DEID只做到GEN')
    args = vars(parser.parse_args())
    print(args)
    print ("in __main__")
    main(args)
