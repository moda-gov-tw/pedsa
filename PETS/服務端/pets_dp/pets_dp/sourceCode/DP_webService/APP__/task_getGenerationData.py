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
from .API.mysql_create_celery import createTbl_T_CeleryStatus, list_clean

#from .log.logging_tester import _getLogger
from .log.logging_tester import _getLogger
redis_store = FlaskRedis(app)

###itri, for gen data(start)######################
@celery.task(bind=True)
def getGenerationData_longTask(self, _jsonBase64,nothing):

    """
    fileName: string
    tarCol: string
    genBool: string
    colNames: string list
    sampleBool: string ##20181128:Pei
    """
    global _logger, _vlogger, _errlogger

    _logger=_getLogger('verify_getGenerationData_longTask')
    _vlogger=_getLogger('verify_getGenerationData')
    _errlogger  =_getLogger('error__genData')

    if not re.match(r'^[A-Za-z0-9+/=]+$', _jsonBase64):
        _logger.debug("Invalid json format")
        return 'Fail'
    _vlogger.debug('input : '+_jsonBase64)

    _errlogger.debug("error_getGenerationData")
    #print 'train_feature_longTask'
    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if jsonfile is None:
        errMsg = 'get json error!'
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'}) 
        return 'Fail'

    ''' {'userID': '1', 'projID': '91', 'projName': 'single0725', 
    'fileName': 'single0725_single.csv', 
    'colNames': ['workclass_sys_test', 'income_sys_test'], 
    'select_colNames': ['workclass_sys_test', 'capital_gain_sys_test', 'capital_loss_sys_test', 'hours_per_week_sys_test', 'income_sys_test'],
    'keyName': ['']}
    '''


    try:
        userID = jsonfile['userID']
        projName = jsonfile['projName']#.encode('utf-8')
        fileName = jsonfile['fileName']#.encode('utf-8')
        colNames_ = jsonfile['colNames']#.encode('utf-8')
        select_colNames_ = jsonfile['select_colNames']
        keyName_ = jsonfile['keyName']#.encode('utf-8')
        projID = jsonfile['projID'] #projID from front-end

        if not re.match("^[a-zA-Z0-9_]+$", str(userID)):
            _logger.debug("Invalid userID format")
            return 'Fail'
 
        if not re.match("^[a-zA-Z0-9_ ]+$", projName):
            _logger.debug("Invalid projName format")
            return 'Fail'

        if not re.match("^[a-zA-Z0-9_ .]+$", fileName):
            _logger.debug("Invalid fileName format")
            return 'Fail'
        
        if not isinstance(colNames_, list):
            _logger.debug("Invalid colNames_ format")
            raise 'Fail'

        if not isinstance(select_colNames_, list):
            _logger.debug("Invalid colNames_ format")
            raise 'Fail'

        if not isinstance(keyName_, list):
            _logger.debug("Invalid keyName_ format")
            raise 'Fail'

        if not re.match("^[a-zA-Z0-9_]+$", str(projID)):
            _logger.debug("Invalid projID format")
            return 'Fail'
        
    except Exception as err:
        errMsg = 'json file first layer error! - %s:%s' %(type(err).__name__, err)
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'})
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
    if fileName == '':        
        errMsg = 'fileName varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'
    if colNames_ == '':        
        errMsg = 'colNames_ varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail'   
    if select_colNames_ == '':        
        errMsg = 'select_colNames_ varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return 'Fail' 

    print ("============INITIAL================")


    print ("============CONNECT================")

        
    # print cmdStr
    print('projID:',projID)
    print('userID:',userID)
    print('projName:',projName)
    print('fileName:',fileName)
    print('keyName_:',keyName_[0])
    print('col:',colNames_)
    print('select_colNames_:',select_colNames_)
    # print('path:',os.getcwd())

    cmd=["python","app/devp/syn_gen/train_feature.py","-userID",userID,"-projID",projID,"-projName",projName,"-fileName",fileName,"-keyName",keyName_[0],"-colName"]
    print(cmd)


    for col_idx in range(len(colNames_)):
        cmd.append(colNames_[col_idx])
    print(cmd)

    cmd.append("-select_colNames")

    for select_col_idx in range(len(select_colNames_)):
        cmd.append(select_colNames_[select_col_idx])
    print(cmd)


    sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #20200207: add return parameter'Flag_complete' 
    #for check whether process is complete default is 'False'
    #iF return 'True' meaning mission complete.
    outList, Flag_complete = getSparkAppId(self, sp, False, projID, userID) #original
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
        _errlogger.debug( errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'})
        return 'Fail'
    #create table if not exist
    try:
        result = createTbl_T_CeleryStatus(check_conn)
        if result['result'] == 1:
            _vlogger.debug('result 1')
        else:
            print('mysql fail')
    except Exception as e:
        errMsg = 'Mysql fail: - %s:%s' %(type(e).__name__, e)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-2'})
        return 'Fail'
    # update value to table
    if Flag_complete == 'True':
        #complete
        project_status=4
        statusname=u'感興趣欄位設定'
    elif Flag_complete == 'False':
        #mission fail
         project_status = 99 
         statusname=u'資料生成錯誤' 
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_projectstatus(self, check_conn,projID,project_status,statusname)
        updateToMysql_celerystatus(self, check_conn,userID, projID, projName, fileName, outList, err_list)
        _vlogger.debug('updateToMysql_status succeed.')
    except Exception as e:
        errMsg = 'errTable: updateToMysql_status fail. {0}'.format(str(e))
        _errlogger.debug(errMsg)
        return 'Fail'
    return outList
def updateToMysql_projectstatus(self, conn,projID,project_status,statusname):
    # update process status to mysql

    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID
        }

    valueSampleData = {
            'project_id': projID,
            'project_status': project_status,
            'statusname':statusname,
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
        errMsg ='insertSampleDataToMysql fail'
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"
    
def updateToMysql_celerystatus(self, conn,userID,projID, projName, table, return_result, errorlog):
    # update process status to mysql
    print('########updateToMysql_status###########')
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'step':'GAN',
            'file_name': table
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'step':'GAN',
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
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"
        
def getSparkAppId(self, subprocess, viewSparkProcess_,projID,userID):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')
    print('output')
    viewSparkProcess = viewSparkProcess_
    #viewSparkProcess = True
    meta_={}# python dict
    #fundTabName = 0
    Flag_complete = 'False'
    print("This is PID: ",subprocess.pid)
    self.update_state(state="PROGRESS", 
                      meta={'PID': subprocess.pid,'userID':userID,'projID': projID,'projStep':'GAN'})

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
        
        ##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_') 
            errReson_=line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            # print ('task id is '+self.request.id)
            _logger.debug('The errReson_ is ' + errReson_)
            # _logger.debug('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;
        ##20181217 verify__genData#######
        if "verify__genData" in  line:
            #fundTabName = 1
            kTable_index=line.find('verify__genData - DEBUG -') 
            kTable_=line[kTable_index:]
            # tmpStrList = kTable_.split("__")
            tmpStrList = kTable_.split("verify__genData - DEBUG -")
            #print(len(tmpStrList[1]))
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
            
        if "error__genData" in  line:
            #fundTabName = 1
            kTable_index=line.find('error__genData - DEBUG -') 
            kTable_=line[kTable_index:]

            # tmpStrList = kTable_.split("__")
            tmpStrList = kTable_.split("error__genData - DEBUG -")
            #print(len(tmpStrList[1]))
            # _errlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            # print "LOG in Generation"
            print('error__genData: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            #print('fundTabName___________________')
            #print(fundTabName)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errMsg'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
            #break

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
            print( "HERE citc____genSyncFile_")
            print('The JOBE is done: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            #print('fundTabName___________________')
            #print(fundTabName)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
            Flag_complete='True'
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
        self.update_state(state="SUCCESS", meta=meta_)
    ##20180103 add, citc add for error (end)###########
    
    if 0:
        output = subprocess.communicate()[0]
        exitCode = subprocess.returncode

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
    return outList, Flag_complete
    ########################33  


###itri, for deID (end)######################

