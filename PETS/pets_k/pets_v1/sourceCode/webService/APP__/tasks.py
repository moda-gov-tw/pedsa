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

import numpy as np
import pandas as pd

import paramiko


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
            print len(unique_values), len(df)
            if len(unique_values) < len(df):
                info['unique_values'] = unique_values
            else:
                info['unique_values'] = True

        result.append(info)

    return result
#itri, 20171115 add (end)######################

###itri, for deID (start)######################
@celery.task(bind=True)
def kcheck_longTask(self, _dbName, _tblName, _colNames,_jarFileName):
    """
    dbName: string
    tblName: string
    colNames: string list
    """
    with app.app_context():
        print 'kcheck_longTask'
        ts0 = time.time()
        ####################
        dbName =  _dbName
        tblName = _tblName    
        #colNames = fields.List(fields.Str())
        colNames_= _colNames
        jarFileName = _jarFileName
        #print colNames_
        ####################
        ##a. ssh login##########
        port =20022
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("140.96.178.106",port,"gau", "Ncku12345")
        
        cmdStr='spark-submit longTaskDir/kchecking.py'+' '+dbName+' '+tblName
        #itri_crime itri_drugs  2 caseno closereason'
        
        lenStr = str(len(colNames_))
        cmdStr = cmdStr+' '+lenStr
        
        for col in colNames_:
            cmdStr = cmdStr+' '+col
             
        print cmdStr
        ##b. ssh remote call python script##########
        stdin, stdout, stderr = ssh.exec_command(cmdStr)
        if 0:
            
            lines = stdout.readlines()
            #print lines
            #print stderr.readlines()
            ssh.close()
            
            for line in lines:
                print line
            
            outList = getSparkAppId_( lines)
            print outList
        else:
            ##c. get spark ID, table name##########
            outList = getSparkAppId(self, stdout, False)
            print outList
            
        
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
        ##d. close ssh section##########
        ssh.close()
        return outList
        
##2018/03/30, citc recover###############################
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
        if "kTable_" in  line:
            kTable_index=line.find('kTable_') 
            kTable_=line[kTable_index:]
            print('The kTable_ is ' + kTable_)
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
            #print ('task id is '+self.request.id)
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
            #print ('task id is '+self.request.id)
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

    print '#####meta_######'
    print "meta len ="+str(len(meta_))
    print meta_
    print '#####meta_ (end)######'
    

    return outList
    ########################33  


###itri, for deID (end)######################

