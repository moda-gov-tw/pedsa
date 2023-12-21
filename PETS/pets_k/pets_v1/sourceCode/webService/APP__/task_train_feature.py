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
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
import logging

import subprocess
import json
from marshmallow import pprint
#from JsonSchema import jsonResponse, jsonResponseSchema, UserSchema, tableInfoSchema, loadJson
#from celery__ import celery_class
from celery import  states
#from celery import Celery
#from kchecking import  main__
import paramiko

#citc, 20181022 add for SSH login into local hadoop cluster
from mylib.loginInfo import getLoginLoacalHadoop


_logger=_getLogger('train_feature_longTask')
redis_store = FlaskRedis(app)

###itri, for gen data(start)######################
@celery.task(bind=True)
def train_feature_longTask(self, _fileName, _tarCol, _genBool, _colNames):
    """
    fileName: string
    tarCol: string
    genBool: string
    colNames: string list
    """

    
        #print 'train_feature_longTask'
    ts0 = time.time()
        ####################
    fileName =  _fileName
    tarCol = _tarCol
    genBool = _genBool     
    #colNames = fields.List(fields.Str())
    colNames_= _colNames
    #jarFileName = '/app/*.jar'
    #jarFileName='udfEncrypt_3.jar,myLogging_1.jar'
    #jarFileName='proj_/longTaskDir_gau/myLogging_1.jar'

    #####citc, 20181015 add for ssh call py###########################
    ##a. ssh login##########
    
    
    #citc, 20181022 add for SSH login into local hadoop cluster
    ip, port_, user_, pwd = getLoginLoacalHadoop('app/devp/login_AI.txt')
    print "=========ip==================="
    print ip
    print port_  
    print "============================"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect("140.96.81.162",port,"root", "citcw200@")

    try:
        ssh.connect(ip,int(port_),user_, pwd)

    except paramiko.SSHException as e: 
        _logger.debug(str(e))
        _logger.debug(ip)
        _logger.debug(port_)
        _logger.debug(user_)
        return

    #####20181121, citc############################################################################################
    ##python train_feature.py -d adult/adult.csv ##################################################################
    ###-col workclass education education_num marital_status occupation relationship race sex native_country class# 
    ####-tar_col class -gen True###################################################################################                                                
    ###############################################################################################################
    cmdStr='python'+' '+' /workspace/train_feature.py -d'+' '+fileName+' ' +'-col '
    
    #lenStr = str(len(colNames_))
    cmdStr = cmdStr+' '
    
    for col in colNames_:
        cmdStr = cmdStr+' '+col

    cmdStr = cmdStr+' '+'-tar_col'+' '+ tarCol+' '+'-gen '+ genBool  
         
    print cmdStr
    ##b. ssh remote call python script##########
    stdin, stdout, stderr = ssh.exec_command(cmdStr)

    #print(stderr)
    #print(stdout)
    if 0:
        
        lines = stdout.readlines()
        print lines
        print stderr.readlines()
        ssh.close()
        
        for line in lines:
            print line
        
        #outList = getSparkAppId( lines)
        outList = getSparkAppId(self, stdout, True)
        print outList
    else:
        ##c. get spark ID, table name##########
        print stderr.readlines()
        outList = getSparkAppId(self, stdout, True) #####20181029, debug
        #print outList

    ####citc, add for ssh call py (end)#####################
    #print outList
    #print "1=========="
    if len(outList) < 2:
        #appID=app_ID
        appID="9999"
        outTblName="errTable"
    else:
        appID=outList[1]
        outTblName=outList[0]
    print "#######outTblName#######"    
    print outTblName
    #print len(outTblName)
    outTblName = outTblName[:-1]
    appID=appID[:-1]
    #print "2=========="
    #print appID
    ts1 = time.time()
    print ts1-ts0
    return outList
        
def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')

    line = stdout_.readlines()
    print (line)
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    #viewSparkProcess = True
    meta_={}# python dict
    #fundTabName = 0
    while True:
        line = stdout_.readline()
        print('in while')
        print line
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
            _logger.debug('The errReson_ is ' + errReson_)
            _logger.debug('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;
        ##20180103 add, citc add for error (end)#######
        
        #kTable_
        if "citc____genSyncFile_" in  line:
            #fundTabName = 1
            kTable_index=line.find('citc____genSyncFile_') 
            kTable_=line[kTable_index:]

            tmpStrList = kTable_.split("____")
            #print(len(tmpStrList[1]))

            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]

            print('The udfEncTable_ is ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            #print('fundTabName___________________')
            #print(fundTabName)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
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
    print '#####outList___######'
    #print len(outList)
    print outList
    return outList
    ########################33  


###itri, for deID (end)######################

