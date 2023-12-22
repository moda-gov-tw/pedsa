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
# def train_feature_longTask(self, _fileName, _tarCol, _genBool, _colNames,_sampleBool): #1212:pei
# def getMLutility_longTask(self, _fileName, _genBool, _colNames,_sampleBool): #1224:pei
#def getMLutility_longTask(self, _projName, _fileName, _colNames, _keyName):
def getMLutility_longTask(self, _jsonBase64,nothing):

    """
    projName: string
    rawDataName: string
    targetCols: list of string
    """
    global _logger, _vlogger

    _logger=_getLogger('error__MLutility_longTask')
    _vlogger=_getLogger('verify__MLutility_longTask')

    _vlogger.debug('input : '+_jsonBase64)

    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if jsonfile is None:
        errMsg = 'jsonfile is None: {}'.format(jsonfile)
        _logger.debug('get json error!')
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    try:
        projName = jsonfile['projName']#.encode('utf-8')
        rawDataName = jsonfile['rawDataName']#.encode('utf-8')
        targetCols = jsonfile['targetCols']#.encode('utf-8')
        projID = jsonfile['projID']
        userID = jsonfile['userID']
        synDataDir = os.path.join('/app', 'app', 'devp', 'folderForSynthetic', projName, 'synProcess', 'synthetic/')
        rawDataDir = os.path.join('/app', 'app', 'devp', 'folderForSynthetic', projName, 'inputRawdata', 'df_drop.csv')
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

    _vlogger.debug('projName:{}'.format(projName))
    _vlogger.debug('rawDataName:{}'.format(rawDataName))
    _vlogger.debug('targetCols:{}'.format(str(targetCols)))
    _vlogger.debug('synDataDir:{}'.format(synDataDir))
    _vlogger.debug('rawDataDir:{}'.format(rawDataDir))
    
    #check target column number
    #print(rawDataDir)
    #print(type(targetCols))
    raw_df = pd.read_csv(rawDataDir)
    checkedTargetCols_ = checkCategoryNumber(self,raw_df,targetCols)
    print(checkedTargetCols_)

    cmd='python /app/app/devp/API/MLutility.py {} {} {} {} {} {} \"{}\"'.format(userID, projID, projName, rawDataName, rawDataDir, synDataDir, str(checkedTargetCols_))
    _vlogger.debug(cmd)

    sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    
    result_, utilityResult_, stepList_ = getSparkAppId(self, sp, False, projName, projID, userID)
    
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
    _vlogger.debug("--------utilityResult_--------")
    _vlogger.debug(utilityResult_)
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
        updateToMysql_CeleryStatus(self, check_conn,userID, projID, projName, rawDataName, stepList_, err_list)
        check_conn.close()
        _vlogger.debug('updateToMysql_CeleryStatus succeed.')
    except Exception as e:
        errMsg = 'updateToMysql_CeleryStatus fail. {0}'.format(str(e))
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return 'Fail'
    
    #insert ML result into mariaDB
    L = len(utilityResult_['target_col'])
    for i in range(0,L):
        target_col = str(utilityResult_['target_col'][i])
        select_csv = str(utilityResult_['select_csv'][i])
        for j in range(0,3):
            model = str(utilityResult_['model'][i*3+j])
            MLresult_b64 = list_clean(utilityResult_['MLresult'][i*3+j])
            print(type(MLresult_b64))
            #print(getJsonParser(MLresult_b64))
            try:
                check_conn = ConnectSQL()
                updateToMysql_utilityResult(self, check_conn, projID, target_col, select_csv, model, MLresult_b64)
                #_vlogger.debug('updateToMysql_utilityResult succeed.')
                check_conn.close()
            except Exception as e:
                errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
                _logger.debug(errMsg)
                self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
                return 'Fail'
            #insertSQL = """
    #INSERT INTO SynService.T_utilityResult (project_id, target_col, select_csv, model, MLresult, createtime, updatetime)
    #VALUES("{}", "{}", "{}", "{}", "{}", now(), now())
    #ON DUPLICATE KEY UPDATE target_col=VALUES(target_col), select_csv=VALUES(select_csv), model=VALUES(model), MLresult=VALUES(MLresult), updatetime=VALUES(updatetime)
    #""".format(projID, target_col, select_csv, model, MLresult)
            #MySQLresult = check_conn.doSqlCommand(insertSQL)
            _vlogger.debug('------------------------------')
            #_vlogger.debug(insertSQL)
            #_vlogger.debug(MySQLresult)
    try:
        check_conn = ConnectSQL()
        if stepList_[-1] == 'Mission Complete':
            updateToMysql_ProjectStatus(self, check_conn, projID, 6, u'查看報表')
        else:
            updateToMysql_ProjectStatus(self, check_conn, projID, 98, u'可用性分析錯誤')
        check_conn.close()
        _vlogger.debug('updateToMysql_ProjectStatus succeed.')
    except Exception as e:
        errMsg = 'updateToMysql_ProjectStatus fail. {0}'.format(str(e))
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return 'Fail'

    return result_

def updateToMysql_CeleryStatus(self, conn,userID,projID, projName, table, return_result, errorlog):
    # update process status to mysql

    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'step':'MLutility',
            'file_name': table
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'step':'MLutility',
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
        _vlogger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        errMsg ='insertCeleryStatusToMysql fail: ' + msg
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"

def updateToMysql_utilityResult(self, conn, projID, targetCol, selectCSV, model, MLresult):
    # update process status to mysql

    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'target_col': targetCol,
            'select_csv': selectCSV,
            'model': model
        }

    valueSampleData = {
            'project_id': projID,
            'target_col': targetCol,
            'select_csv': selectCSV,
            'model': model,
            'MLresult': MLresult#','.join(errorlog)
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                            'T_utilityResult',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        errMsg ='insertUtilityResultToMysql fail: ' + msg
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
        _vlogger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        errMsg ='updateToMysql_ProjectStatus fail: ' + msg
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"   
        
def getSparkAppId(self, subprocess, viewSparkProcess_, projName, projID, userID):
    app_ID=9999
    stepList=[]
    print('in getSparkAppId')
    # line = stdout_.readlines()
    # line = stdout_
    # print (line)
    # print('output2')
    # for li in line:
    #     print (li)
    ######################
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    #viewSparkProcess = True
    meta_= {}# python dict
    target_col = []
    select_csv = []
    model = []
    MLresult = []
    #fundTabName = 0
    print("This is PID: {}".format(subprocess.pid))
    #self.update_state(state="PROGRESS", meta={'PID': subprocess.pid})
    meta_['PID'] = subprocess.pid
    meta_['celeryId'] = self.request.id
    meta_['projName'] = projName
    meta_['projID'] = projID
    meta_['userID'] = userID
    meta_['projStep'] = 'MLutility'
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
            print ('task id is '+ self.request.id)
            _logger.debug('The errReson_ is ' + errReson_)
            _logger.debug('task id is '+ self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            stepList.append(errReson_)
            break;

        ##20190903 #######
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

        if "target - " in  line:
            #fundTabName = 1
            target_col_index=line.find('target - ') 
            target_col_=line[(target_col_index+9):].strip('\n')           
            #meta_['target'] = bestTargetCol_
            target_col.append(target_col_)
            stepList.append(target_col_)
            print(target_col)

        if "best syn. data - " in  line:
            #fundTabName = 1
            bestSynData_index=line.find('best syn. data - ') 
            bestSynData_=line[(bestSynData_index+17):].strip('\n')
            #meta_['bestSynData'] = bestSynData_
            select_csv.append(bestSynData_)
            print(select_csv)

        if "model - " in  line:
            #fundTabName = 1
            model_index=line.find('model - ') 
            model_=line[(model_index+8):].strip('\n')           
            #meta_['model'] = model_
            model.append(model_)
            stepList.append(model_)
            print(model)
            
        if "MLresult - " in  line:
            #fundTabName = 1
            MLresult_index=line.find('MLresult - ') 
            MLresult_=line[(MLresult_index+11):].strip('\n')           
            #meta_['MLresult'] = MLresult_
            MLresult.append(MLresult_)
            print(MLresult)
            
        if "error__MLutility" in  line:
            #fundTabName = 1
            error_index=line.find('error__MLutility - DEBUG - ') 
            errMsg_=line[(error_index+27):]           
            meta_['celeryId'] = self.request.id
            meta_['errMsg'] = errMsg_
            stepList.append(errMsg_)
            print(meta_)
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            #break

        #kTable_
        if "------MLutility Finished------" in  line:
            meta_['celeryId'] = self.request.id
            print('------MLutility Finished------')
            stepList.append('Mission Complete')
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
    
    utilityResult = {}
    utilityResult['target_col'] = target_col   
    utilityResult['select_csv'] = select_csv
    utilityResult['model'] = model
    utilityResult['MLresult'] = MLresult
    #raise subprocess.ProcessException(command, exitCode, output)
    #print ('#####outList___######')
    #print len(outList)
    #print (outList)
    return meta_, utilityResult, stepList
    ########################33  


###itri, for deID (end)######################

