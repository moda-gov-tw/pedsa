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


#0708
def main(args):

    global  _logger,_vlogger, check_conn     
    # debug log
    _logger  =_getLogger('error__HashMacAsync')
    # verify log
    _vlogger =_getLogger('verify__HashMacAsync')

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

    #for hash
    hashTableName = args['hashTableName']
    hashkey = args['hashkey']
    sep = args['sep']
    columns_mac = args['columns_mac']
    dataHash = args['dataHash']
    onlyHash = args['onlyHash']

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

    # FOR Mac API:  /api/WebAPI/hash
    try:
        Hash_para = {"tablename":hashTableName, 
                "key":hashkey,
                "sep":sep, 
                "columns_mac":columns_mac, 
                "projName": p_dsname, 
                "projID": str(pid), 
                "dataHash": dataHash ,
                "onlyHash": onlyHash
                }
        print('Hash_para: ', Hash_para)            
        response_g = requests.post("http://"+flask_ip+":"+flask_port+"/mac_async", json=Hash_para,timeout=None)
        response_dic = response_g.json()
        print("HASH JSON: ",response_dic)
        _vlogger.debug('HashMac_flag: '+ str(1))
        response['HashMac']='1' #response_dic['state']
    except Exception as e:
        _logger.debug('errTable: Hash_request error. {0}'.format(str(e)))

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
                _logger.debug('projstatus error: {0}'.format(str(errMsg)))           
                break;
        except Exception as e:
            pass
    
    
    print("citc_final____Mission Complete")




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-pname", "--pname", help='專案名稱')
    parser.add_argument("-p_dsname", "--p_dsname", help='專案資料集名稱')
    parser.add_argument("-prodesc", "--prodesc", help='專案描述')
    parser.add_argument("-powner", "--powner", help='1: deidadmin')

    parser.add_argument("-hashTableName", "--hashTableName", help='在dataMac的裡的資料名稱')
    parser.add_argument("-hashkey", "--hashkey", help='需要的key')
    parser.add_argument("-sep", "--sep", help='資料集分隔符號')
    parser.add_argument("-columns_mac", "--columns_mac", help='hash需要的id column')
    parser.add_argument("-dataHash", "--dataHash", help='是否hash')
    parser.add_argument("-onlyHash", "--onlyHash", help='default is "Y"')
    args = vars(parser.parse_args())
    print(args)
    print ("in __main__")
    main(args)
