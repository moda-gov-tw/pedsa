#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import pymysql
import ast
import time
from app import app, celery
from flask_redis import FlaskRedis
from log.logging_tester import _getLogger
from config.loginInfo import getLoginMysql
import module.JsonSchema as JsonSchema
from module.base64convert import *
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig
from config.connect_sql import ConnectSQL

 
redis_store = FlaskRedis(app)



def createCustomizedRule( self, dbName_, tblName_, origColName_,listDict_, colName_ ):
    try:
        path_db = '/app/app/devp/udfRule/{}'.format(dbName_)
        if os.path.exists(path_db) == False:
            os.mkdir(path_db)
        path_tbl = '/app/app/devp/udfRule/{}/{}'.format(dbName_,tblName_)
        if os.path.exists(path_tbl) == False:
            os.mkdir(path_tbl)
    except Exception as e:
        errMsg = 'mkdir error:'+str(e)
        return errMsg
    try:    
        file = open(path_tbl+'/{}_rule.txt'.format(origColName_),'w')
        file.write(
"""[setting]
# if autoGen is True, for those value which is not defined below [rule] will replace by autoGenValue
autoGen = {} 
autoGenValue = {}
level = {}

[information]
""".format('False', 'others', 0)) 
        dict_ = listDict_
        L = len(dict_) #dic = pd.to_dict('record')
        for i in range(0,L):
            file.write('{} = {};{};*\n'.format('rule_%d' %(i+1), dict_[i]['count'], dict_[i][colName_])) 
        file.close()
        return 'Succeed'
    except Exception as e:
        errMsg = 'write2local_error:'+str(e)
        #_logger.debug(errMsg)
        #self.update_state(state="FAIL_CELERY", meta={'errMsg':errMsg})
        return errMsg

@celery.task(bind=True)
def getDistinctData_longTask(self, _jsonBase64,_jarFileName):
    # Set log.
    global _logger, _vlogger
    _logger = _getLogger('celery__getDistinctData')
    _vlogger = _getLogger('verify__getDistinctData')
    _vlogger.debug('input : '+_jsonBase64)
    
    with app.app_context():
        _vlogger.debug('getDistinctData_longTask')
        ts0 = time.time()
        ####################
        # get json
        jsonfile = getJsonParser(_jsonBase64)
        if jsonfile is None:
            _logger.debug('get json error!')
            return None
    
        # get schemaName, jobName and projName
        try:
            projStep = jsonfile['projStep'].encode('utf-8')
            jobName = jsonfile['jobName'].encode('utf-8')
            projName = jsonfile['projName'].encode('utf-8')
            projID = int(jsonfile['projID'].encode('utf-8'))
        except Exception as err:
            _logger.debug('json file first layer error! - %s:%s' %(type(err).__name__, err))
            return None
                      
        # get schema
        try:
            if projStep == 'distinct':
                schema = JsonSchema.tableInfoSchema()
            else:
                _logger.debug('get schema error!')
                return None
        except Exception as err:
            _logger.debug('get schema error! - %s:%s' %(type(err).__name__, err))
            return None

        # check json mainInfo schema and load
        try:
            mainInfo = jsonfile['mainInfo']
            mainInfo_dic = JsonSchema.loadJson(mainInfo, schema)
            _vlogger.debug(mainInfo_dic)
            mainInfoB64 = encodeDic(mainInfo_dic)
            #mainInfo_ = "%s%s%s" %('"',str(mainInfo_dic),'"')
        except Exception as err:
            _logger.debug('mainInfo schema error! - %s:%s' %(type(err).__name__, err))
            return None

        global reqFunc
        reqFunc = mainInfo['reqFunc']
        origCol = mainInfo['origColNames']
        _vlogger.debug('origCol : {}'.format(origCol))
        #jsonBase64 = _jsonBase64
        jarFileName = _jarFileName
        #print colNames_
        ####################
        ##a. ssh login##########

        sparkCode = getConfig().getSparkCode('getDistinctData.py')
        cmdStr = '''
        spark-submit {} {} {} {}'''.format(sparkCode, mainInfoB64, projName, jobName)
        _vlogger.debug(cmdStr)
        _logger.debug(cmdStr)

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)


        if 0:
            
            lines = stdout.readlines()
            #print lines
            #print stderr.readlines()

            for line in lines:
                print(line)
            
            meta = getSparkAppId_(lines)
            print("***********************")
            _vlogger.debug(meta)
        else:
            ##c. get spark ID, table name##########
            meta = getSparkAppId(self, stdout, False)
            print("##########################")
            _vlogger.debug(meta)
            
        
        #self.update_state(self.request.id, state="PROGRESS", meta={'progress': 90})
        #time.sleep(1)
  
        if len(meta) < 2:
            #appID=app_ID
            appID = "9999"
            outTblName = "errTable"
        else:
            appID = meta['sparkAppID']
            outTblName = meta['outTblNames']
        colList = ast.literal_eval(meta['cols'][0])
        _vlogger.debug(meta)
        _vlogger.debug(meta['distinctDic'])
        for i in range(0,len(colList)):
            distinctData_ = str(meta['distinctDic'][i].encode("utf-8").strip())
            _vlogger.debug(distinctData_)
            _vlogger.debug(type(distinctData_))
            col_ = str(colList[i])
            origCol_ = str(origCol[i])
            _vlogger.debug(col_)
            #disDF = pd.DataFrame(distinctData_)
            #_vlogger.debug(disDF)

            try:
                #connect to mysql
                connection = ConnectSQL()
            except Exception as e:
                _logger.debug('connectToMysql error! - %s:%s' %(type(e).__name__, e))

            #colValue = {}
            #colValue['project_id'] = str(projID)
            #colValue['pro_db'] = str(meta['dbName'].encode("utf-8").strip())
            #colValue['pro_tb'] = str(meta['tblName'].encode("utf-8").strip())
            #colValue['pro_col'] = col_
            #colValue['pro_discol_count'] = distinctData_            
            #_vlogger.debug(colValue)
            db = str(meta['dbName'].encode("utf-8").strip())
            tbl = str(meta['tblName'].encode("utf-8").strip())
            insertSQL = """
            INSERT INTO DeIdService.T_Pro_DistinctTB(project_id, pro_db, pro_tb, pro_col, pro_discol_count, createtime)
            VALUES ({}, "{}", "{}", "{}", "{}", now())""".format(projID, db, tbl, origCol_, distinctData_)
            #print('insertSQL: ',insertSQL) 
            try:
                MySQLresult = connection.doSqlCommand(insertSQL)
                #MySQLresult = connection.insertValue("DeIdService","T_Pro_DistinctTB",colValue)
                #_vlogger.debug('insert MySQL result : '+str(MySQLresult))
                _vlogger.debug("============================")
                distinctData_ = ast.literal_eval(distinctData_)
                _vlogger.debug(distinctData_)
                _vlogger.debug(type(distinctData_))
                customizedRule = createCustomizedRule( self, db, tbl, origCol_, distinctData_, col_)
                _vlogger.debug('Customized Rule output result : '+customizedRule)        
            except Exception as e:
                _logger.debug('insertToMysql error! - %s:%s' %(type(e).__name__, e))
        #if reqFunc == 0 and MySQLresult == 'Succeed':
            #self.update_state( state="PROGRESS", meta=meta)
        #ts1 = time.time()
        #print(ts1-ts0)
        ##d. close ssh section##########
        #ssh.close()
        return meta
    
def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID=9999
    outList=[]
    outTblList = []
    colList = []
    disDicList = []
    disNumList = []
    print('in getSparkAppId')
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    meta_ = {}# python dict
    while True:
        line = stdout_.readline()
        if line == '':
            break
        #print(line)
        #sys.stdout.write(line)
        #sys.stdout.flush()
        
        ##20180103 add, citc add for error###########
        if "errTable_" in line:
            kTable_index = line.find('errTable_') 
            errReson_ = line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;
        ##20180103 add, citc add for error (end)#######

        if "jobName_" in line:
            jobName_index=line.find('jobName_') 
            jobName_=line[(jobName_index+8):]
            #print('The job name is ' + jobName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['jobName'] = jobName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(jobName_)
        
        if "dbName_" in line:
            dbName_index=line.find('dbName_') 
            dbName_=line[(dbName_index+7):]
            #print('The DB name is ' + dbName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['dbName'] = dbName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(dbName_)
        
        if "tblName_" in line:
            tblName_index=line.find('tblName_') 
            tblName_=line[(tblName_index+8):]
            #print('table name is ' + tblName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            #tblList.append(tblName_)
            meta_['tblName'] = tblName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(tblName_)

        if "registTblName_" in line:
            tblName_index=line.find('registTblName_') 
            tblName_=line[(tblName_index+14):]
            #print('RegistTblName table name is ' + tblName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            outTblList.append(tblName_)
            meta_['outTblNames'] = outTblList
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(tblName_)

        if "cols_" in line:
            cols_index=line.find('cols_') 
            cols_=line[(cols_index+5):]
            #print('The columns are ' + cols_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            colList.append(cols_)
            meta_['cols'] = colList
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(colList)

        if "spark__" in line:
            error_index=line.find('spark__')
            error_=line[error_index:]
            print('The error is ' + error_)
            print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errMsg'] = error_
            meta_['taskID'] = self.request.id
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(error_)

        if "distinctNum_" in line:
            disNum_index=line.find('distinctNum_') 
            disNum_=line[(disNum_index+12):]
            #print('table name is ' + tblName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            disNumList.append(disNum_)
            meta_['distinctNum'] = disNumList
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(disNumList)

        
        if "distinctDic_" in line:
            disDic_index=line.find('distinctDic_')
            disDic_=line[(disDic_index+12):]
            #print('table name is ' + tblName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            disDicList.append(disDic_)
            meta_['distinctDic'] = list(disDicList)
            outList.append(disDicList)       

             
        if "sc.applicationId:" in line:
            app_ID_index=line.find('application_') 
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            #print('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            if reqFunc == 1:
                self.update_state(state="PROGRESS", meta=meta_)
                outList.append(app_ID)
                if not viewSparkProcess:
                    break

    _vlogger.debug('#####meta_######')
    _vlogger.debug(len(meta_))
    _vlogger.debug(meta_)
    
    ##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
        self.update_state(state="FAIL", meta=meta_)
    else:
        self.update_state(state="PROGRESS", meta=meta_)
    ##20180103 add, citc add for error (end)###########


    """
    if 0:
        output = sparkCommand.communicate()[0]
        exitCode = sparkCommand.returncode

        if (exitCode == 0):
            #return output
            pass
        else:
            print(exitCode)
            print(output)
    """

            
            #raise subprocess.ProcessException(command, exitCode, output)
    print(len(outList))
    print(outList)
    return meta_#outList
########################33   
##(end, 2018/03/30)###################

#2018/03/26, citc         
def getSparkAppId_( lines):
    app_ID=9999
    outList=[]
    print('in getSparkAppId_')
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    meta_={}# python dict
    #while True:
    for line in lines:

        
        ##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_') 
            errReson_=line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;
        ##20180103 add, citc add for error (end)#######
        
        #kTable_
        if "kTable_" in  line:
            kTable_index=line.find('kTable_') 
            kTable_=line[kTable_index:]
            print('The kTable_ is ' + kTable_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)

        if "spark__" in  line:
            error_index=line.find('spark_')
            error_=line[error_index:]
            print('The error is ' + error_)
            print('task id is '+ self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errMsg'] = error_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(error_)
             
        #if "local-" in  line: application_
        if "application_" in  line: 
            app_ID_index=line.find('application_') 
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            print('The app ID is ' + app_ID)
            meta_['sparkJobID'] = app_ID
            #self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)

    print('#####meta_######')
    print("meta len ="+str(len(meta_)))
    print(meta_)
    print('#####meta_ (end)######')
    
    return meta_#outList
