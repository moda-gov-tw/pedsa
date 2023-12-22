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

from .Mysql_.connect_sql import ConnectSQL 
from .API.mysql_create_celery import createDB_SynService,createTbl_T_CeleryStatus, list_clean

#from .log.logging_tester import _getLogger
from .log.logging_tester import _getLogger
redis_store = FlaskRedis(app)

###itri, for gen data(start)######################
@celery.task(bind=True)
# def train_feature_longTask(self, _fileName, _tarCol, _genBool, _colNames,_sampleBool): #1212:pei
# def getGenerationData_longTask(self, _fileName, _genBool, _colNames,_sampleBool): #1224:pei
#def getGenerationData_longTask(self, _projName, _fileName, _colNames, _keyName):
def killProcess_longTask(self, _jsonBase64,nothing):

    """
    projID: int
    projStep: string
    projName: string
    """
    global _logger, _vlogger, _errlogger
    _logger=_getLogger('verify_killProcess_longTask')
    _vlogger=_getLogger('verify_killProcess')
    _errlogger  =_getLogger('error__killProcess')

    _vlogger.debug('input : '+_jsonBase64)
    #_errlogger.debug("killProcess_error")
    #print 'train_feature_longTask'
    ts0 = time.time()

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
        PID = jsonfile['PID']
    except Exception as err:
        errMsg = 'json error! - %s:%s' %(type(err).__name__, err)
        #_logger.debug('json file first layer error! - %s:%s' %(type(err).__name__, err))
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
        #return  None
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
    if PID == '':
        errMsg = 'PID varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
         
    # print cmdStr
    print('userID: ',userID)
    print('projID:',projID)
    print('projName:',projName)
    print('PID: ',PID)


    cmd=["python","app/devp/API/killProcess.py","-PID",PID]
    print(cmd)

    #sp = subprocess.Popen(["python","train_feature.py","-projName","ProAdult","-fileName","data/adult_raw.csv","-colName","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class","-keyName","workclass"],stdout=subprocess.PIPE)
    #sp = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    outList = getSparkAppId(self, sp, False, projID, projName, userID)

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
    ####citc, add for ssh call py (end)#####################
    #print outList
    #print "1=========="
    # if len(outList) < 2:
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

    #print ("#######outTblName#######"    )
    #print (outTblName)
    #print len(outTblName)
    outTblName = outTblName[:-1]
    appID=appID[:-1]
    ts1 = time.time()
    print (ts1-ts0)
    print ("#######outList#######"    )
    err_list = list_clean(err_list)

    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
    except Exception as e:
        errMsg = 'connectToMysql fail: - %s:%s' %(type(e).__name__, e)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
        return 'Fail'

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


    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(self, check_conn, userID, projID, projName, '', outList, err_list)
        _vlogger.debug('updateToMysql_status succeed.')
    except Exception as e:
        errMsg = 'updateToMysql_status fail. {0}'.format(str(e))
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'}) 
        return 'Fail'
    return outList

def updateToMysql_status(self, conn,userID,projID, projName, table, return_result, errorlog):
    # update process status to mysql

    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'step':'killProcess',
            'file_name': table
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'step':'killProcess',
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
    meta_={}# python dict
    #fundTabName = 0
    print("This is PID: ",subprocess.pid)
    #self.update_state(state="PROGRESS", 
    #                  meta={'PID': subprocess.pid,'userID':userID,'projID': projID,'projStep':'create folder','projName':projName})
    meta_={'PID': subprocess.pid,'userID':userID,'projID': projID,'projStep':'kill process','projName':projName}

    while True:
        line= subprocess.stdout.readline().decode()#stdout_ 
        #print("CELERY:",line)
        if line == ' ' and sparkCommand.poll() is not None:
            break
        sys.stdout.write(line)
        sys.stdout.flush()

    #for line in lines:
        # line = stdout_.readline()
        # line = stdout_
        # print('in while')
        if line == '':
            break
        # print line
        #sys.stdout.write(line)
        #sys.stdout.flush()
        
        ##20181217 verify__genData#######
        if "verify__genData" in  line:
            #fundTabName = 1
            kTable_index=line.find('verify__genData - DEBUG -') 
            kTable_=line[kTable_index:]
            # tmpStrList = kTable_.split("__")
            tmpStrList = kTable_.split("verify__genData - DEBUG -")
            #print(len(tmpStrList[1]))
            _vlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            if "PATH" in tmpStrList[1]:
                meta_['synPath'] = kTable_.split("PATH:")[1]
            # print "LOG in Generation"
            print('verify__: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            #print('fundTabName___________________')
            #print(fundTabName)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['verify'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
            
        if "error__killProcess" in  line:
            #fundTabName = 1
            kTable_index=line.find('error__killProcess - DEBUG -') 
            kTable_=line[kTable_index:]

            # tmpStrList = kTable_.split("__")
            tmpStrList = kTable_.split("error__killProcess - DEBUG -")
            #print(len(tmpStrList[1]))
            _errlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            # print "LOG in Generation"
            print('error__killProcess: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            #print('fundTabName___________________')
            #print(fundTabName)
            meta_['Msg'] = kTable_
            meta_['stateno']='-2'
            self.update_state(self.request.id, state="FAIL", meta=meta_)

            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
            break

        #kTable_
        if "citc____Mission Complete" in  line:
        # if "citc" in  line:

            #fundTabName = 1
            kTable_index=line.find('citc____Mission Complete') 
            # kTable_index=line.find('citc') 

            kTable_=line[kTable_index:]

            tmpStrList = kTable_.split("____")
            #print(len(tmpStrList[1]))

            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            print( "HERE citc____Mission Complete")
            print('The JOBE is done: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            #print('fundTabName___________________')
            #print(fundTabName)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            #meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            #self.update_state( state="PROGRESS", meta= meta_)
            outList.append(kTable_)
            break


        #if line == line[-1]:
        #    print("the last")
        #    break
             

    print ('#####meta_######')
    print (len(meta_))
    print (meta_)
    
    ##20180103 add, citc add for error#############
    if 'errTable' in (meta_.keys()):
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
    print ('#####outList___######')
    #print len(outList)
    print (outList)
    return outList
    ########################33  


###itri, for deID (end)######################

