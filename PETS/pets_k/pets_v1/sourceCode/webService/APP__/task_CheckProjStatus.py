#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import re
import base64
import os
from app import app
from app import celery
from flask_redis import FlaskRedis
from celery import states
from log.logging_tester import _getLogger
from module.base64convert import getJsonParser
from module.JsonSchema import getImportSchema,loadJson
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig
from config.connect_sql import ConnectSQL
import sys
from os import listdir
import json
redis_store = FlaskRedis(app)


def check_project_status(proj_id):
    print("check_project_status: pid:'{}' \n".format(proj_id))
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        checkProject_Flag = 'False'
        status = '-1'
        errMsg = 'check_project_status connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        return checkProject_Flag, status, errMsg
    try: # fetch parameter: project_status, statusname
        sqlStr = "SELECT project_status  FROM `DeIdService`.`T_ProjectStatus` where project_id like '{}';".format(proj_id)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            project_status = resultCheck["fetchall"][0]['project_status']
        sqlStr = "SELECT statusname  FROM `DeIdService`.`T_ProjectStatus` where project_id like '{}';".format(proj_id)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            statusname = resultCheck["fetchall"][0]['statusname']
        check_conn.close()
        checkProject_Flag = 'True'
        return checkProject_Flag, project_status, statusname
    except Exception as e:
        checkProject_Flag = 'False'
        status = '-1'
        errMsg = 'check_project_status fetch progress fail: - %s:%s' %(type(e).__name__, e)
        return checkProject_Flag, status, errMsg

def check_status(proj_id, Application_Name):
    print("check_status: pid:'{}', Application_Name:'{}' \n".format(proj_id, Application_Name))
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        checkStatusFlag = 'AppName_False'
        status = '-1'
        errMsg = 'check_status connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        return checkStatusFlag, errMsg, status
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
        checkStatusFlag = 'True'
        return checkStatusFlag, Progress, Progress_State

    except Exception as e:
        checkStatusFlag = 'AppName_False'
        status = '-1'
        errMsg = 'check_status fetch progress fail: - %s:%s' %(type(e).__name__, e)
        return checkStatusFlag, errMsg, status

def status_to_ApplicationName(num):
    numbers = {
        2 : "import",
        6 : "gen",
        7 : "getKchecking_one",
        9 : "Risk",
        12 : "MLutility",
        14 : "export",
        40 : "udfMacUID"
    }
    return numbers.get(num, None)

def checkAppName(proj_id, project_status):
    print("checkAppName: pid:'{}', project_status:'{}' \n".format(proj_id, project_status))
    if int(project_status) in (2, 6, 7, 9, 12, 14, 40):
        print('status_to_ApplicationName')
        checkAppName_Flag = "True"
        Application_Name = status_to_ApplicationName(int(project_status))
        try: 
            checkStatusFlag, Progress, Progress_State = check_status(proj_id, Application_Name)
            if checkStatusFlag == 'True':
                return checkStatusFlag, Progress, Progress_State
            elif checkStatusFlag == 'AppName_False':
                return checkStatusFlag, Progress, Progress_State
        except Exception as e:
            checkAppName_Flag = 'AppName_False'
            status = '-1'
            errMsg = 'check_status fail: - %s:%s' %(type(e).__name__, e)
            return checkAppName_Flag, errMsg, status
    else:
        checkAppName_Flag = "False" 
        Progress = 'None'
        Progress_State = 'None'
        return checkAppName_Flag, Progress, Progress_State


###itri, for gen data(start)######################
@celery.task(bind=True)
#使用者check project status、appstatus 
def CheckProjStatus_longTask(self, _jsonBase64,nothing):

    """
    base64_: string ( projName: string, userID: int)
    nothing: 1
    """
    global _vlogger, _errlogger

    _vlogger=_getLogger('verify_CheckProjStatus')
    _errlogger  =_getLogger('error__CheckProjStatus')

    _vlogger.debug('input : '+_jsonBase64)


    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if isinstance(jsonfile,str):
            errMsg = 'decode_base64_error: %s',jsonfile
            _errlogger.debug(errMsg)
            self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'})
            return {'Msg':errMsg,'stateno':'-1'}
    try:
        userID = jsonfile['userID']
        projName = jsonfile['projName']#.encode('utf-8')
    except Exception as err:
        errMsg = 'json error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    if userID == '':
        errMsg = 'userID varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}
    if projName == '':
        errMsg = 'projName varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    # print cmdStr
    print('userID: ',userID)
    print('projName:',projName)

    #step1: GET pid
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}
    try: # fetch parameter: pid
        sqlStr = "SELECT  project_id FROM `DeIdService`.`T_Project` where project_name like '{}';".format(projName)
        resultCheck = check_conn.doSqlCommand(sqlStr)
        if int(resultCheck['result'])==1:
            pid = resultCheck["fetchall"][0]['project_id']
        check_conn.close()
    except Exception as e:
        errMsg = 'fetch data fail: - %s:%s' %(type(e).__name__, e)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    #step1: GET project_status from T_ProjectStatus
    try:
        checkProject_Flag, project_status, statusName = check_project_status(pid)
        if checkProject_Flag == "False":
            errMsg = statusName
            _errlogger.debug(errMsg)
            self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
            return {'Msg':errMsg,'stateno':'-1'}
    except Exception as err:
        errMsg = 'Get project_status error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    #step2: GET app_status from appStatus
    try:
        checkAppName_Flag, Progress, Progress_State = checkAppName(pid, project_status)
        #如果是2, 6, 7, 9, 12, 14, 40 -> check_status ->Progress百分比, Progress_State狀態
        if checkAppName_Flag == "True": 
            meta_={'flag':"T" ,'projStep':'CheckProjStatus','project_id':pid ,'userID':userID,'projName':projName, 'Status':statusName, 'Progress':Progress, 'Progress_State':Progress_State}
        elif checkAppName_Flag == "False":
            meta_={'flag':"F" ,'projStep':'CheckProjStatus','project_id':pid ,'userID':userID,'projName':projName, 'Status':statusName}
        elif checkAppName_Flag =='AppName_False':
            meta_ = self.update_state(state="FAIL", meta={'Msg':Progress,'stateno':'-1'})
            return {'Msg':Progress,'stateno':'-1'}
        print (meta_)
        self.update_state(state="PROGRESS", meta=meta_)
        return meta_ 
    except Exception as err:
        errMsg = 'checkAppName error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    
