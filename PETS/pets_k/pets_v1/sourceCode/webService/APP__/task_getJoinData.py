#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import app, celery
from flask_redis import FlaskRedis
import time
from log.logging_tester import _getLogger
import numpy as np
import pandas as pd
import paramiko
import module.JsonSchema as JsonSchema
from module.base64convert import *
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs


redis_store = FlaskRedis(app)

#####original code (start)##############
@celery.task()
def counter_save():
    result = redis_store.save()
    return "Redis output: " + str(result)

@celery.task()
def counter_reset():
    result_reset = redis_store.set('hello-world-view-count', 0)
    result_save = redis_store.save()
    return "Redis output: " + str(result_reset)
###original code (end)##############

#itri, 20171115 add######################
@celery.task(bind=True)
def read_csv_task(self, path):
    self.update_state( state="PROGRESS", meta={'progress': self.request.id})
    #self.update_state(state=states.PENDING)
    #self.update_state( state="PROGRESS", meta={'progress': 10})
    #self.update_state( state="PROGRESS", meta={'progress': self.request.id})
    df = pd.read_csv(path)
    result = compute_properties(df)
    #self.update_state( state="PROGRESS", meta={'progress': 99})
    return result

def compute_properties(df):
    properties = {}

    properties['num_rows'] = len(df)
    properties['num_columns'] = len(df.columns)

    properties['column_data'] = get_column_data(df)

    return properties

def get_column_data(df):
    result = []

    for c in df:
        info = {}
        col = df[c]

        info['name'] = c
        info['num_null'] = col.isnull().sum()

        if col.dtypes == 'int64':
            info['mean'] = np.mean(col)
            info['median'] = np.median(col)
            info['stddev'] = np.std(col)
            info['min'] = col.min()
            info['max'] = col.max()
        else:
            unique_values = col.unique().tolist()
            print(len(unique_values), len(df))
            if len(unique_values) < len(df):
                info['unique_values'] = unique_values
            else:
                info['unique_values'] = True

        result.append(info)

    return result


@celery.task(bind=True)
def getJoinData_longTask(self, _jsonBase64,_jarFileName):
    # Set log.
    global _logger, _vlogger
    _logger = _getLogger('celery__getJoinData')
    _vlogger = _getLogger('verify__getJoinData')
    _vlogger.debug('input : '+_jsonBase64)

    with app.app_context():
        _vlogger.debug('getJoinData_longTask')
        ts0 = time.time()
        ####################
        # get json
        jsonfile = getJsonParser(_jsonBase64)
        if jsonfile is None:
            _logger.debug('DEBUG-get json error!')
            return None    
    
        # json file first layer : get schemaName and jobName
        try:
            projStep = jsonfile['projStep'].encode('utf-8')
            jobName = jsonfile['jobName'].encode('utf-8')
            projName = jsonfile['projName'].encode('utf-8')
            global kchecking
            kchecking = int(jsonfile['kchecking'])
        except Exception as err:
            _logger.debug('json file first layer error! - %s:%s' %(type(err).__name__, err))
            return None
    
        # get schema
        try:
            if projStep == 'join':
                schema = JsonSchema.joinInfoSchema()
            else:
                _logger.debug('projStep error!')
                return None
        except Exception as err:
            _logger.debug('get schema error! - %s:%s' %(type(err).__name__, err))
            return None
    
        # check json mainInfo schema and load
        try:
            mainInfo = jsonfile['mainInfo']
            mainInfo_dic = JsonSchema.loadJson(mainInfo, schema)
            mainInfoB64 = encodeDic(mainInfo_dic)
            #mainInfo_ = "%s%s%s" %('"',str(mainInfo_dic),'"')
        except Exception as err:
            _logger.debug('mainInfo schema error! - %s:%s' %(type(err).__name__, err))
            return None


        ####################
        ##a. ssh login##########
        sparkCode = getConfig().getSparkCode('getJoinData.py')
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
            ssh.close()
            
            for line in lines:
                print(line)
            
            meta = getSparkAppId_( lines)
            print(meta)
        else:
            ##c. get spark ID, table name##########
            meta = getSparkAppId(self, stdout, False)
            print(meta)
            
        
        #self.update_state(self.request.id, state="PROGRESS", meta={'progress': 90})
        #time.sleep(1)
  
        if len(meta) < 2:
            #appID=app_ID
            appID="9999"
            outTblName="errTable"
        else:
            appID = meta['sparkAppID']
            outTblName = meta['tblName']
        print(outTblName)
        print(len(outTblName))
        outTblName = outTblName[:-1]
        appID = appID[:-1]
        print('###### join output check ######')
        print(meta['dbName'][0][:-1])
        print(meta['outTblName'])
        
        ts1 = time.time()
        print(ts1-ts0)
        ##d. close ssh section##########
        
        if kchecking == 0:
            return meta
########################### kchecking task ###################################
        else:
            from task_getKchecking import kchecking4join_longTask
            k_ = kchecking4join_longTask(self, _jsonBase64, meta['dbName'][0].strip(), meta['outTblName'])
            self.update_state(state="FINISH", meta=k_)
            print(k_)
            return k_

def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID=9999
    outList=[]
    dbList = []
    tblList = []
    colList = []
    
    print('in getSparkAppId')
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    meta_={}# python dict
    while True:
        line = stdout_.readline()
        if line == '':
            break
        print(line)
        #sys.stdout.write(line)
        #sys.stdout.flush()
        
        ##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_') 
            errReson_=line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            print('task id is '+self.request.id)
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break
        ##20180103 add, citc add for error (end)#######

        if "jobName_" in  line:
            jobName_index=line.find('jobName_') 
            jobName_=line[(jobName_index+8):]
            #print('The job name is ' + jobName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['jobName'] = jobName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(jobName_)
        
        if "dbName_" in  line:
            dbName_index=line.find('dbName_') 
            dbName_=line[(dbName_index+7):]
            #print('The DB name is ' + dbName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            dbList.append(dbName_) 
            meta_['dbName'] = dbList
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(dbName_)
        
        if "tblName_" in  line:
            tblName_index=line.find('tblName_') 
            tblName_=line[(tblName_index+8):]
            #print('table name is ' + tblName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            tblList.append(tblName_)
            meta_['tblName'] = tblList
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(tblName_)

        if "registTblName_" in  line:
            tblName_index=line.find('registTblName_') 
            tblName_=line[(tblName_index+14):]
            #print('RegistTblName table name is ' + tblName_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['outTblName'] = tblName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(tblName_)

        if "cols_" in  line:
            cols_index=line.find('cols_') 
            cols_=line[(cols_index+5):]
            #print('The columns are ' + cols_)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            colList.append(cols_)
            meta_['cols'] = colList
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(cols_)

        if "spark__" in  line:
            error_index=line.find('spark__')
            error_=line[error_index:]
            print('The error is ' + error_)
            print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errMsg'] = error_
            meta_['taskID'] = self.request.id
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(error_)
            break

        if "sc.applicationId:" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            #print('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            if kchecking == 0:
                self.update_state(state="PROGRESS", meta=meta_)
            outList.append(app_ID)
            if not viewSparkProcess:
                break
    print('#####meta_######')
    print(len(meta_))
    print(meta_)
    
    ##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
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
            print(exitCode)
            print(output)
            
            #raise subprocess.ProcessException(command, exitCode, output)
    #print(len(outList))
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
             
        #if "local-" in  line: application_
        if "application_" in  line: 
            app_ID_index=line.find('application_') 
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            print('The app ID is ' + app_ID)
            meta_['jobID'] = app_ID
            #self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)

    print('#####meta_######')
    print("meta len ="+str(len(meta_)))
    print(meta_)
    print('#####meta_ (end)######')
    

    return meta_#outList



