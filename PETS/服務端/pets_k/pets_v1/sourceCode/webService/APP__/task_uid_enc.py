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
import paramiko

#citc, 20181022 add for SSH login into local hadoop cluster
from mylib.loginInfo import getLoginLoacalHadoop
from log.logging_tester import _getLogger
from module.JsonSchema import jsonBase64Schema
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs



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
        print('uidEnc_longTask')
        ts0 = time.time()

        # Set log.
        global _logger, _vlogger
        _logger = _getLogger('udfEncUID')
        _vlogger = _getLogger('verify__' + 'udfEncUID')

        ####################
        dbName =  _dbName
        tblName = _tblName
        #colNames = fields.List(fields.Str())
        colNames_= _colNames
        #jarFileName = '/app/*.jar'
        #jarFileName='sqljdbc4-2.0.jar,udfEncrypt_3.jar,myLogging_1.jar'
        jarFileName = getConfig().getJarFiles('udfEncrypt_4.jar,myLogging_1.jar')


        #####citc, 20181015 add for ssh call py###########################
        ##a. ssh login##########


        #citc, 20181022 add for SSH login into local hadoop cluster
        ip, port_, user_, pwd = getLoginLoacalHadoop('app/devp/login_localHadoop.txt')
        print("=========ip===================")
        print(ip)
        print(port_)


        print("============================")


        '''
        port =2232
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.connect("140.96.81.162",port,"root", "citcw200@")
        ssh.connect(ip,int(port_),user_, pwd)
        '''


        cmdStr='spark-submit'+' '+'--jars '+jarFileName+' proj_/longTaskDir_gau/udfEncUID.py'+' '+dbName+' '+tblName
        #itri_crime itri_drugs  2 caseno closereason'



        lenStr = str(len(colNames_))
        cmdStr = cmdStr+' '+lenStr

        for col in colNames_:
            cmdStr = cmdStr+' '+col

        print(cmdStr)


        ##b. ssh remote call python script##########
        #stdin, stdout, stderr = ssh.exec_command(cmdStr)

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

        '''
        projName = 'uid_enc'
        # make .sh file
        tmpFileName = projName + '_getServerFolder_tmp.sh'
        sh_file = """
        source /etc/profile
        {}
        """.format(cmdStr)
        c_mksh = 'echo "{}" > {}'.format(sh_file,tmpFileName)
        ssh_for_sh = ssh_hdfs()
        ssh_for_sh.callCommand_noOutput(c_mksh)
        ssh_for_sh.close()


        # bash .sh file
        c_bashsh = 'bash {}'.format(tmpFileName)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(c_bashsh)


        # rm .sh file
        c_rmsh = 'rm {}'.format(tmpFileName)
        ssh_for_rm = ssh_hdfs()
        ssh_for_rm.callCommand_noOutput(c_rmsh)
        ssh_for_sh.close()
        '''







        if 0:

            lines = stdout.readlines()
            #print liness
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
        #print outTblName
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
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    #viewSparkProcess = True
    meta_={}# python dict
    fundTabName = 0
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
            fundTabName = 1
            kTable_index=line.find('udfEncTable_')
            kTable_=line[kTable_index:]
            print('The udfEncTable_ is ' + kTable_)
            print ('task id is '+self.request.id)
            print('fundTabName___________________')
            print(fundTabName)
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
            print('fundTabName___________________')
            print(fundTabName)
            outList.append(app_ID)
            if fundTabName == 1:
                print('break___________________0')
                if not viewSparkProcess:
                    print('break___________________')
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

