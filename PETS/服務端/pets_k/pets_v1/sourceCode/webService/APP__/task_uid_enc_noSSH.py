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
#from pyspark import SparkConf, SparkContext, StorageLevel
#from py4j.protocol import Py4JJavaError
#from pyspark.sql import SQLContext
#from pyspark.sql.functions import col
import logging
import subprocess
import json
from marshmallow import pprint
#from JsonSchema import jsonResponse, jsonResponseSchema, UserSchema, tableInfoSchema, loadJson
#from celery__ import celery_class
from celery import  states
#from celery import Celery
#from kchecking import  main__
from log.logging_tester import _getLogger
import shlex



redis_store = FlaskRedis(app)


###itri, for deID (start)######################
@celery.task(bind=True)
def uidEnc_longTask(self, _dbName, _tblName, _colNames):
    """
    dbName: string
    tblName: string
    colNames: string list
    """
    with app.app_context():
        print 'uidEnc_longTask'
        ts0 = time.time()

        # Set log.
        global _logger, _vlogger
        _logger = _getLogger('uidEnc')
        _vlogger = _getLogger('verify__' + 'uidEnc')



        ####################
        dbName =  _dbName
        tblName = _tblName    
        #colNames = fields.List(fields.Str())
        colNames_= _colNames
        #jarFileName = '/app/*.jar'
        #jarFileName='sqljdbc4-2.0.jar,udfEncrypt_3.jar,myLogging_1.jar'
        jarFileName='udfEncrypt_3.jar,myLogging_1.jar'
        
        #jarFileName='/app/sqljdbc4-2.0.jar'
        #target_jars = build_dir + '/' + '*.jar'
        #cmd = ['$SPARK_HOME/bin/spark-submit', '--jars', target_jars, '--f', script_file, '-exec spark'] + sys.argv[2:]
        #print colNames_
        ####################
        sparkSubmit=os.path.join(os.environ.get("SPARK_HOME"),"bin","spark-submit")
        #submitSparkList=[sparkSubmit,'--jars',jarFileName,'--driver-class-path',jarFileName,'kchecking.py',dbName,tblName]
        dbName = shlex.quote(dbName)
        tblName = shlex.quote(tblName)
        submitSparkList=[sparkSubmit,'--jars',jarFileName,'udfEncUID.py',shlex.quote(dbName),shlex.quote(tblName)]
        colNames_ = shlex.quote(colNames_)
        submitSparkList.append(str(len(colNames_)))
        for col in colNames_:
            col = shlex.quote(col)
            submitSparkList.append(col)

        submitSparkList = shlex.quote(submitSparkList)
        sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        outList = getSparkAppId(self, sparkCommand, False)
        sparkCommand.communicate()[0]
        
        #self.update_state(self.request.id, state="PROGRESS", meta={'progress': 90})
        #time.sleep(1)
  
        if len(outList) < 2:
            #appID=app_ID
            appID="9999"
            outTblName="errTable"
        else:
            appID=outList[1]
            outTblName=outList[0]
        print outTblName
        print len(outTblName)
        outTblName = outTblName[:-1]
        appID=appID[:-1]
    
    
        ts1 = time.time()
        print ts1-ts0
        return outList
        
def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID=9999
    outList=[]
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
        print line
        #sys.stdout.write(line)
        #sys.stdout.flush()
        
        ##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_') 
            errReson_=line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            print ('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;
        ##20180103 add, citc add for error (end)#######
        
        #kTable_
        if "udfEncTable_" in  line:
            kTable_index=line.find('udfEncTable_') 
            kTable_=line[kTable_index:]
            print('The udfEncTable_ is ' + kTable_)
            print ('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
             
        if "application_" in  line:
            app_ID_index=line.find('application_') 
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            print('The app ID is ' + app_ID)
            meta_['jobID'] = app_ID
            #self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)
            if not viewSparkProcess:
                break
    print '#####meta_######'
    print len(meta_)
    print meta_
    
    ##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
        print 'err fail'
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
            print exitCode
            print output
            
    #raise subprocess.ProcessException(command, exitCode, output)
    #print len(outList)
    return outList
    ########################33  


###itri, for deID (end)######################

