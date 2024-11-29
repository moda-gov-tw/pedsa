# -*- coding: UTF-8 -*-
from celery import Celery
from app import app
from app import celery
from flask_redis import FlaskRedis


import csv
import random
import sqlite3
from flask import Flask
from flask import g, render_template, request, jsonify,url_for,make_response
import datetime as dt
import time

import sys
import re
import os

from .Mysql_.connect_sql import ConnectSQL 
from .API.mysql_create_celery import createTbl_T_CeleryStatus, list_clean
####20181024, citc add for log
# from funniest import HiveLibs
# from funniest.logging_tester import _getLogger

import subprocess
import json
from marshmallow import pprint
#from JsonSchema import jsonResponse, jsonResponseSchema, UserSchema, tableInfoSchema, loadJson
#from celery__ import celery_class
from celery import  states

from .module import JsonSchema as JsonSchema
from .module.base64convert import *

from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
#from .log.logging_tester import _getLogger
from .log.logging_tester import _getLogger
redis_store = FlaskRedis(app)

def checkCategoryNumber(self,df,targets):
    for col in targets:
        if len(np.unique(df[col])) == 1:
            targets.remove(col)
    return targets

###itri, for gen data(start)######################
@celery.task(bind=True)
def exportData_longTask(self, _jsonBase64,nothing):

    """
    projName: string
    rawDataName: string
    targetCols: list of string
    """
    global _logger, _vlogger

    _logger=_getLogger('error__exportData_longTask')
    _vlogger=_getLogger('verify__exportData_longTask')

    if not re.match(r'^[A-Za-z0-9+/=]+$', _jsonBase64):
        _logger.debug("Invalid json format")
        return 'Fail'
    _vlogger.debug('input : '+_jsonBase64)

    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if jsonfile is None:
        _logger.debug('get json error!')
        errMsg = 'jsonfile is None: {}'.format(jsonfile)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    try:
        projName = jsonfile['projName']#.encode('utf-8')
        dataName = jsonfile['dataName']#.encode('utf-8')
        projID = jsonfile['projID']
        userID = jsonfile['userID']

        if not re.match("^[a-zA-Z0-9_]+$", userID):
            print("Invalid userID format")    
            return 'Fail'
        if not re.match("^[a-zA-Z0-9_]+$", projID):
            print("Invalid projID format")
            return 'Fail'
        if not re.match("^[a-zA-Z0-9_ ]+$", projName):
            print("Invalid projName format")  
            return 'Fail'
        if isinstance(dataName, list):
            for dataName_item in dataName:
                if not re.match("^[a-zA-Z0-9_ .]+$", dataName_item):
                    print("Invalid dataName format")   
                    return 'Fail'  
                
    except Exception as err:
        _logger.debug('json file first layer error! - %s:%s' %(type(err).__name__, err))
        errMsg = 'json error! - %s:%s' %(type(err).__name__, err)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    if userID == '':
        errMsg = 'userID varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    if projID == '':
        errMsg = 'projID varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    if projName == '':
        errMsg = 'projName varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    if dataName == '':
        errMsg = 'dataName varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'

    _vlogger.debug('projName:{}'.format(projName))
    _vlogger.debug('dataName:{}'.format(str(dataName)))
    

    #cmd = ["python","app/devp/API/exportData.py","-projName",projName,"-dataName",str(dataName)]i
    cmd = "python /app/app/devp/API/exportData.py {} {} {} \"{}\"".format(userID,projID,projName,str(dataName))
    _vlogger.debug(cmd)

    try:
        sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    except Exception as err:
        _logger.debug('Popen error! - %s:%s' %(type(err).__name__, err))

    result_, stepList_ = getSparkAppId(self, sp, False, projName, projID, userID)

    err = sp.stderr.readlines()
    err_list = []
    if err:
        flag_err = 0
        print("something wrong")
        for err_line in err:
            #sys.stdout.write(err_line)
            
            sys.stdout.write(err_line)
                #sys.stdout.flush()
            err_list.append(err_line.decode())
            flag_err = 1
            sys.stdout.flush()

    if len(result_) < 2: #1217:pei
        #appID=app_ID
        appID="9999"
        outTblName="errTable"
    else:
        PID = result_['PID']
        #taskID = result_['taskID']
        #bestSynData = result_['bestSynData']
        #bestTargetCol = result_['targetCol']
        #print(bestSynData)
        print(PID)

    _vlogger.debug("--------result_--------")
    _vlogger.debug(result_)
    _vlogger.debug("--------stepList_--------")
    _vlogger.debug(stepList_)

    ts1 = time.time()
    print (ts1-ts0)

    err_list = list_clean(err_list)
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
    
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(self, check_conn,userID, projID, projName, dataName, stepList_, err_list)
        if stepList_[-1] == 'Mission Complete':
            updateToMysql_ProjectStatus(self, check_conn, projID, 8, u'資料匯出完成')
        else:
            updateToMysql_ProjectStatus(self, check_conn, projID, 97, u'資料匯出失敗')       
        _vlogger.debug('updateToMysql_status succeed.')
        check_conn.close()
    except Exception as e:
        errMsg = 'updateToMysql_status fail. {0}'.format(str(e))
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return 'Fail'

    return result_

def updateToMysql_status(self, conn,userID,projID, projName, table, return_result, errorlog):
    # update process status to mysql

    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'step':'exportData',
            'file_name': ','.join(table)
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': ','.join(table),
            'step':'exportData',
            'isRead':0,
            'return_result':','.join(return_result),
            'log':errorlog #','.join(errorlog)
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                            'T_CeleryStatus',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug("Update mysql succeed.")
        return None
    else:
        errMsg ='insertSampleDataToMysql fail'
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"

def updateToMysql_ProjectStatus(self, conn, projID, projStatus, statusName):
    # update process status to mysql

    print('########updateToMysql_ProjectStatus###########')
    condisionSampleData = {
            'project_id': projID
        }

    valueSampleData = {
            'project_id': projID,
            'project_status': projStatus,
            'statusname': statusName,
            'updatetime':str(dt.datetime.now())
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                            'T_ProjectStatus',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug("Update mysql succeed.")
        return None
    else:
        errMsg ='updateToMysql_ProjectStatus fail' 
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"

def getSparkAppId(self, subprocess, viewSparkProcess_, projName, projID, userID):
    app_ID=9999
    stepList=[]
    print('in getSparkAppId')
    viewSparkProcess = viewSparkProcess_
    #viewSparkProcess = True
    meta_= {}# python dict
    #fundTabName = 0
    print("This is PID: {}".format(subprocess.pid))
    #self.update_state(state="PROGRESS", meta={'PID': subprocess.pid})
    meta_['PID'] = subprocess.pid
    meta_['celeryId'] = self.request.id
    meta_['projName'] = projName
    meta_['projID'] = projID
    meta_['userID'] = userID
    meta_['projStep'] = 'Export data'
    self.update_state(state="PROGRESS", meta=meta_)

    while True:
        line= subprocess.stdout.readline().decode()#stdout_ 
        #print("CELERY:",line)
        if line == ' ' and sparkCommand.poll() is not None:
            break
        sys.stdout.write(line)
        sys.stdout.flush()

        if line == '':
            break
        
        ##20180103 add, citc add for error###########
        if "errTable_" in line :
            kTable_index = line.find('errTable_') 
            errReson_ = line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            # print ('task id is '+ self.request.id)
            _logger.debug('The errReson_ is ' + errReson_)
            # _logger.debug('task id is '+ self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;

        ##20190903 #######
        """
        if "rawDir : " in  line:
            #fundTabName = 1
            rawDir_index=line.find('rawDir : ') 
            rawDir_=line[(rawDir_index+9):].strip('\n')
            meta_['rawDir'] = rawDir_
            print(meta_)

        if "targetCols : " in  line:
            #fundTabName = 1
            targetCols_index=line.find('targetCols : ') 
            targetCols_=line[(targetCols_index+13):].strip('\n')
            meta_['targetCols'] = targetCols_
            self.update_state(state="PROGRESS", meta=meta_)
            print(meta_)

        if "best syn. data : " in  line:
            #fundTabName = 1
            bestSynData_index=line.find('best syn. data : ') 
            bestSynData_=line[(bestSynData_index+17):].strip('\n')
            meta_['bestSynData'] = bestSynData_
            print(meta_)

        """
        if "Connect SQL" in  line:          
            stepList.append('Connect SQL')

        if "Check path" in  line:          
            stepList.append('Check path')

        if "Copy data" in  line:          
            stepList.append('Copy data')

        if "error__exportData" in  line:
            #fundTabName = 1
            error_index=line.find('error__exportData - DEBUG - ') 
            errMsg_=line[(error_index+28):]           
            meta_['celeryId'] = self.request.id
            meta_['errMsg'] = errMsg_
            print(meta_)
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            #break
        
        #kTable_
        if "------export data complete------" in  line:
            meta_['celeryId'] = self.request.id
            print('------export data complete------')
            stepList.append('Mission Complete')
            #self.update_state(state="PROGRESS", meta=meta_)
            print(meta_)
            #break


        #if line == line[-1]:
        #    print("the last")
        #    break
             

    #print ('#####meta_######')
    #print (len(meta_))
    #print (meta_)
    
    ##20180103 add, citc add for error#############
    if 'errMsg' in (meta_.keys()):
        print ('err fail')
        self.update_state(state="FAIL", meta=meta_)
    else:
        self.update_state(state="PROGRESS", meta=meta_)
    ##20180103 add, citc add for error (end)###########
    
    if 0:
        output = sparkCommand.communicate()[0]
        exitCode = sparkCommand.returncode

        if (exitCode == 0):
            #return output
            pass
        else:
            print (exitCode)
            print (output)
            
    #raise subprocess.ProcessException(command, exitCode, output)
    #print ('#####outList___######')
    #print len(outList)
    #print (outList)
    return meta_, stepList
    ########################33  


###itri, for deID (end)######################

