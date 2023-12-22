# -*- coding: UTF-8 -*-
from celery import Celery, states
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

import subprocess
import json
from marshmallow import pprint

from celery import  states

from .module import JsonSchema as JsonSchema
from .module.base64convert import *

from .Mysql_.connect_sql import ConnectSQL 
from .API.mysql_create_celery import createDB_SynService,createTbl_T_CeleryStatus, list_clean

from .log.logging_tester import _getLogger
redis_store = FlaskRedis(app)

###itri, for deleteProject(start)######################
@celery.task(bind=True)
# remove project folder to record the synthetic data generation process
# under the folderForSynthetic/
def deleteProject_longTask(self, _jsonBase64,nothing):

    #regist logger in log/logging_setting.yaml
    global _logger, _vlogger, _errlogger
    _logger=_getLogger('verify_deleteProject_longTask')
    _vlogger=_getLogger('verify_deleteProject')
    _errlogger  =_getLogger('error__deleteProject')

    _vlogger.debug('input : '+_jsonBase64)

    ts0 = time.time()

    #check json format
    #if error, update state and error msg to view.py
    jsonfile = getJsonParser(_jsonBase64)
    if jsonfile is None:
        errMsg = 'jsonfile is None: {}'.format(jsonfile)
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'}) 
        return 'Fail'
    try:
        userID = jsonfile['userID']
        projID = jsonfile['projID'] #projID from front-end
        projName = jsonfile['projName']#.encode('utf-8')
    except Exception as err:
        errMsg = 'json error! - %s:%s' %(type(err).__name__, err)
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'

    #check, whether variable is empty?
    #if error, update state and error msg to view.py
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
         
    # print cmdStr
    print('userID: ',userID)
    print('projID:',projID)
    print('projName:',projName)

    #Combination command: python API.py
    cmd=["python","app/devp/API/deleteProject.py","-projName",projName]
    print(cmd)

    #use popen to execute python API.py
    sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    #filter log and return_result to view.py
    outList = getSparkAppId(self, sp, False, projID,projName,userID)

    #error log in popen 
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

    if len(outList) < 2: #1217:pei
        #appID=app_ID
        appID="9999"
        outTblName="errTable"
    elif flag_err == 1: 
        print(err_list)
        appID=outList[1]
        outTblName=outList[0]
    else:
        appID=outList[1]
        outTblName=outList[0]

    outTblName = outTblName[:-1]
    appID=appID[:-1]
    ts1 = time.time()
    print (ts1-ts0)
    print ("#######outList#######"    )
    err_list = list_clean(err_list)

    # ConnectSQL
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
        return 'Fail'
    # create Table in SQL
    try :
        stepDict = {
            '0': createDB_SynService(check_conn),
            '1': createTbl_T_CeleryStatus(check_conn)
        }
        for i in range(len(stepDict)):
            print(i)
            try:
                result = stepDict[str(i)]
                if result['result'] == 1:
                    _vlogger.debug(result['msg'])
                else:
                    errMsg = result['msg']
                    print('mysql fail:' + result['msg'])
                    self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
                    #return False
            except:
                pass
    except Exception as e:
        errMsg = 'mysql fail: - %s:%s' %(type(e).__name__, e)
        _logger.debug(errMsg )
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
        return 'Fail'

    # update status in Table T_CeleryStatus
    try:
        updateToMysql_status(self, check_conn, userID, projID, projName, '', outList, err_list)
        _vlogger.debug('updateToMysql_status succeed.')
    except Exception as e:
        errMsg = 'updateToMysql_status fail. {0}'.format(str(e))
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
        return 'Fail'
    return outList

#function: filter log and return_result to view.py
def updateToMysql_status(self, conn,userID,projID, projName, table, return_result, errorlog):
    # update process status to mysql
    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'step':'Delete Project',
            'file_name': table
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'step':'Delete Project',
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
        errMsg = 'insertSampleDataToMysql fail: ' + msg
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
        return  'Fail'  

def getSparkAppId(self, subprocess, viewSparkProcess_,projID,projName,userID):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')
    print('output')
    
    viewSparkProcess = viewSparkProcess_
    #viewSparkProcess = True
    meta_={}# python dict
    #fundTabName = 0
    print("This is PID: ",subprocess.pid)
    #self.update_state(state="PROGRESS", 
    #                  meta={'PID': subprocess.pid,'userID':userID,'projID': projID,'projStep':'create folder','projName':projName})
    meta_={'PID': subprocess.pid,'userID':userID,'projID': projID,'projStep':'Delete Project','projName':projName}

    while True:
        line= subprocess.stdout.readline().decode()#stdout_ 
        if line == ' ' and sparkCommand.poll() is not None:
            break
        sys.stdout.write(line)
        sys.stdout.flush()

        if line == '':
            break

        
        ##filter log in logger:verify__deleteProject#######
        if "verify__deleteProject" in  line:
            kTable_index=line.find('verify__deleteProject - DEBUG -') 
            kTable_=line[kTable_index:]
            tmpStrList = kTable_.split("verify__deleteProject - DEBUG -")
            _vlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            if "PATH" in tmpStrList[1]:
                meta_['synPath'] = kTable_.split("PATH:")[1]
            print('verify__: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            meta_['verify'] = kTable_
            outList.append(kTable_)

        ##filter error log in logger:error__deleteProject#######     
        if "error__deleteProject" in  line:
            kTable_index=line.find('error__deleteProject - DEBUG -') 
            kTable_=line[kTable_index:]
            tmpStrList = kTable_.split("error__deleteProject - DEBUG -")
            _errlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            print('error__deleteProject: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            meta_['Msg'] = kTable_
            outList.append(kTable_)

        #check whether the python process finish
        if "citc____Mission Complete" in  line:
            kTable_index=line.find('citc____Mission Complete') 
            kTable_=line[kTable_index:]
            tmpStrList = kTable_.split("____")

            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            print( "HERE citc____Mission Complete")
            print('The JOBE is done: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            outList.append(kTable_)
            break


    print ('#####meta_######')
    print (len(meta_))
    print (meta_)
    
    ##update state to view.py#############
    if 'errTable' in (meta_.keys()):
        print ('err fail')
        self.update_state(state="FAIL", meta=meta_)
    else:
        self.update_state(state="PROGRESS", meta=meta_)
    ##???###########
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
    print ('#####outList___######')
    print (outList)
    return outList


###itri, for deleteProject (end)######################

