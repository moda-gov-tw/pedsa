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

####20181024, citc add for log
# from funniest import HiveLibs
# from funniest.logging_tester import _getLogger

import subprocess
import base64
import json
from marshmallow import pprint
#from JsonSchema import jsonResponse, jsonResponseSchema, UserSchema, tableInfoSchema, loadJson
#from celery__ import celery_class
from celery import  states

from .module import JsonSchema as JsonSchema
from .module.base64convert import *
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs
from config.connect_sql import ConnectSQL
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from log.logging_tester import _getLogger
redis_store = FlaskRedis(app)

def checkCategoryNumber(self,df,targets):
    for col in targets:
        if len(np.unique(df[col])) == 1:
            targets.remove(col)
    return targets



def list_clean(err_list):
    json_encoded_list = json.dumps(err_list)
    b64_encoded_list = base64.b64encode(json_encoded_list.encode("utf-8"))
    print("b64_encoded_list: ",b64_encoded_list)
    decoded_list = base64.b64decode(b64_encoded_list)
    my_list_again = json.loads(decoded_list)
    print("my_list_again: ",my_list_again)
    return b64_encoded_list.decode("utf-8")


###itri, for gen data(start)######################
@celery.task(bind=True)
def getMLutility_longTask(self, _jsonBase64,nothing):

    """
    projName: string
    rawDataName: string
    targetCols: list of string
    """
    global _logger, _vlogger, _errlogger

    _logger=_getLogger('error__MLutility_longTask')
    _vlogger=_getLogger('verify__MLutility_longTask')

    _vlogger.debug('input : '+_jsonBase64)

    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if jsonfile is None:
        _logger.debug('get json error!')
        return None
    try:
        projName = jsonfile['projName']#.encode('utf-8')
        rawTbl = jsonfile['rawTbl']#.encode('utf-8')
        deIdTbl = jsonfile['deIdTbl']
        targetCols = str(jsonfile['targetCols']).encode('utf-8')
        projID = jsonfile['projID']
        userID = jsonfile['userID']
    except Exception as err:
        _logger.debug('json file first layer error! - %s:%s' %(type(err).__name__, err))
        return None

    _vlogger.debug('input json decode : {}'.format(jsonfile))
    _vlogger.debug('projName:{}'.format(projName))
    _vlogger.debug('rawTbl:{}'.format(rawTbl))
    _vlogger.debug('deIdTbl:{}'.format(deIdTbl))
    _vlogger.debug('targetCols:{}'.format(targetCols))
    print('++++++++++++++++++++++++++++++++++')
    
    #check target column number
    #print(rawDataDir)
    #print(type(targetCols))
    #raw_df = pd.read_csv(rawDataDir)
    #checkedTargetCols_ = checkCategoryNumber(self,raw_df,targetCols)
    #print(checkedTargetCols_)

    #cmd='python /app/app/devp/ml_utility/MLutility.py {} {} \"{}\"'.format(rawDataDir, synDataDir, str(checkedTargetCols_))
    #_vlogger.debug(cmd)
    #sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    
    sparkCode = getConfig().getSparkCode('MLutility.py')
    cmdStr = '''
    spark-submit {} {} {} {} {} {}'''.format(sparkCode, projID, projName, rawTbl, deIdTbl, '\"'+str(targetCols)+'\"')
    _vlogger.debug(cmdStr)
    ssh_for_bash = ssh_hdfs()
    stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
    #result_ = getSparkAppId(self, sp, False, projName, projID, userID)
    if 0:
          
        lines = stdout.readlines()
        #print lines
        #print stderr.readlines()
        ssh.close()
            
        for line in lines:
            print(line)
           
        meta = getSparkAppId_( lines)
        print(meta)
    else:
        ##c. get spark ID, table name##########
        meta, utilityResult = getSparkAppId(self, stdout, False, projName, projID, userID)
        print(meta)

    if len(meta) < 2: #1217:pei
        #appID=app_ID
        appID="9999"
        outTblName="errTable"
    else:
        appID = meta['sparkAppID']
        #taskID = result_['taskID']
        #bestSynData = result_['bestSynData']
        #bestTargetCol = result_['targetCol']
        #print(bestSynData)
        print(appID)

    _vlogger.debug("--------result--------")
    _vlogger.debug(meta)
    _vlogger.debug("--------utilityResult--------")
    _vlogger.debug(utilityResult)
    
    try:
        _logger.debug('start connectToMysql to check project_name in mysql: {}'.format(projName))
        check_conn = ConnectSQL()
    except Exception as e:
        meta['errMsg'] = str(e)
        _logger.debug('connectToMysql fail: ' + meta['errMsg'])
        self.update_state(state="FAIL_CELERY", meta=meta)
        return None
    
    #insert ML result into mariaDB
    L = len(utilityResult['target_col'])
    #print('1111111111111111111111')
    #print(len(utilityResult['model']))
    for i in range(0,L):
        target_col = str(utilityResult['target_col'][i])
        deIdTbl_ = str(utilityResult['deIdTbl'][i])
        for j in range(0,2):
            try:
                model = str(utilityResult['model'][i*2+j])
                MLresult_b64 = list_clean(utilityResult['MLresult'][i*2+j])
            except Exception as e:
                errMsg = 'get MLutility Result fail. {0}'.format(str(e))
                _logger.debug(errMsg)
                self.update_state(state="FAIL", meta={'errMsg':errMsg,'stateno':'-2'})
                return 'Fail'
            try:
                check_conn = ConnectSQL()
                updateToMysql_utilityResult(self, check_conn, projID, projName, deIdTbl_, target_col, model, MLresult_b64)
                #_vlogger.debug('updateToMysql_utilityResult succeed.')
                check_conn.close()
            except Exception as e:
                errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
                _logger.debug(errMsg)
                self.update_state(state="FAIL", meta={'errMsg':errMsg,'stateno':'-2'})
                return 'Fail'
            _vlogger.debug('------------------------------')
            #_vlogger.debug(insertSQL)
            #_vlogger.debug(MySQLresult)
    
    check_conn = ConnectSQL()
    updateToMysql_ProjectStatus(self, check_conn, projID, 11, u'查看報表')
    check_conn.close()
    _vlogger.debug('----- updateToMysql_ProjectStatus -----')
    ts1 = time.time()
    print (ts1-ts0)
    return meta

def updateToMysql_utilityResult(self, conn, projID, projName, deIdTbl, targetCol, model, MLresult):
    # update process status to mysql

    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'dbName': projName,
            'deIdTbl': deIdTbl,
            'target_col': targetCol, 
            'model': model
        }

    valueSampleData = {
            'project_id': projID,
            'dbName': projName,
            'deIdTbl': deIdTbl,
            'target_col': targetCol,            
            'model': model,
            'MLresult': MLresult#','.join(errorlog)
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('DeIdService',
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
        self.update_state(state="FAIL", meta={'errMsg':errMsg,'stateno':'-2'})
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

    resultSampleData = conn.updateValueMysql('DeIdService',
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

        
def getSparkAppId(self, stdout_, viewSparkProcess_, projName, projID, userID):
    app_ID=9999
    outList=[]
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
    model = []
    MLresult = []
    deIdTbl__ = []
    #fundTabName = 0
    #print("This is PID: {}".format(subprocess.pid))
    #self.update_state(state="PROGRESS", meta={'PID': subprocess.pid})
    #meta_['PID'] = subprocess.pid
    meta_['celeryId'] = self.request.id
    meta_['projName'] = projName
    meta_['projID'] = projID
    meta_['userID'] = userID


    while True:
        line = stdout_.readline()
        if line == '':
            break
        print(line)
        
        ##20180103 add, citc add for error###########
        if "errTable_" in line :
            kTable_index = line.find('errTable_') 
            errReson_ = line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            print ('task id is '+ self.request.id)
            _logger.debug('The errReson_ is ' + errReson_)
            _logger.debug('task id is '+ self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errMsg'] = errReson_
            meta_['status'] = -1
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;

        ##20190903 #######
        if "rawTbl : " in  line:
            #fundTabName = 1
            rawDir_index=line.find('rawTbl : ') 
            rawDir_=line[(rawDir_index+9):].strip('\n')
            meta_['rawDir'] = rawDir_
            print(meta_)

        if "targetCols : " in  line:
            #fundTabName = 1
            targetCols_index=line.find('targetCols : ') 
            targetCols_=line[(targetCols_index+13):].strip('\n')
            meta_['targetCols'] = targetCols_
            #self.update_state(state="PROGRESS", meta=meta_)
            print(meta_)

        if "droped columns - " in  line:
            #fundTabName = 1
            drop_col_index=line.find('droped columns - ')
            drop_col_=line[(drop_col_index+17):].strip('\n')
            #meta_['target'] = bestTargetCol_
            meta_['dropCols'] = drop_col_
            print("droped cols : {}".format(drop_col_))

        if "deIdTbl - " in  line:
            #fundTabName = 1
            deIdTbl_index=line.find('deIdTbl - ') 
            deIdTbl_=line[(deIdTbl_index+10):].strip('\n')
            meta_['deIdTbl'] = deIdTbl_
            deIdTbl__.append(deIdTbl_)
            print(meta_)

        if "target - " in  line:
            #fundTabName = 1
            target_col_index=line.find('target - ') 
            target_col_=line[(target_col_index+9):].strip('\n')           
            #meta_['target'] = bestTargetCol_
            target_col.append(target_col_)
            print(target_col)

        if "model - " in  line:
            #fundTabName = 1
            model_index=line.find('model - ') 
            model_=line[(model_index+8):].strip('\n')           
            #meta_['model'] = model_
            model.append(model_)
            print(model)

        if "MLresult - " in  line:
            #fundTabName = 1
            MLresult_index=line.find('MLresult - ') 
            MLresult_=line[(MLresult_index+11):].strip('\n')           
            #meta_['MLresult'] = MLresult_
            MLresult.append(MLresult_)
            print(MLresult)
        
        if "sc.applicationId:" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:].strip('\n')
            #this gives the app_ID
            #print('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            meta_['status'] = 1
            meta_['errMsg'] = ""
            self.update_state(state="PROGRESS", meta=meta_)
            outList.append(app_ID)
                        
        if "error__MLutility" in  line:
            #fundTabName = 1
            error_index=line.find('error__MLutility - DEBUG - ') 
            errMsg_=line[(error_index+27):]           
            meta_['celeryId'] = self.request.id
            meta_['status'] = -1
            meta_['errMsg'] = errMsg_
            print(meta_)
            check_conn = ConnectSQL()
            updateToMysql_ProjectStatus(self, check_conn, projID, 95, u'可用性分析錯誤')
            check_conn.close()
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            #break

        #kTable_
        if "------MLutility Finished------" in  line:
            meta_['celeryId'] = self.request.id
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
    utilityResult['deIdTbl'] = deIdTbl__   
    utilityResult['model'] = model
    utilityResult['MLresult'] = MLresult        
    #raise subprocess.ProcessException(command, exitCode, output)
    #print ('#####outList___######')
    #print len(outList)
    #print (outList)
    return meta_, utilityResult
    ########################33  


###itri, for deID (end)######################

