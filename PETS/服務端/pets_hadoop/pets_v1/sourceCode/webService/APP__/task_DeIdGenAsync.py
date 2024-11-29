#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import subprocess
import json
from marshmallow import pprint
from celery import  states

from module import JsonSchema as JsonSchema
from module.base64convert import *

from config.connect_sql import ConnectSQL
# from Mysql_.connect_sql import ConnectSQL 
# from API.mysql_create_celery import createTbl_T_CeleryStatus, list_clean
from config.loginInfo import getConfig
import requests
from log.logging_tester import _getLogger

redis_store = FlaskRedis(app)

def list_clean(err_list):
    json_encoded_list = json.dumps(err_list)
    b64_encoded_list = base64.b64encode(json_encoded_list.encode("utf-8"))
    print("b64_encoded_list: ",b64_encoded_list)
    decoded_list = base64.b64decode(b64_encoded_list)
    my_list_again = json.loads(decoded_list)
    print("my_list_again: ",my_list_again)
    return b64_encoded_list.decode("utf-8")

###2020/12/02 非同步自動化:[塔台用]，只到Gen ######################
@celery.task(bind=True)
def DeIdGenAsync_longTask(self, _jsonBase64,nothing):

    global _errlogger, _vlogger

    _vlogger=_getLogger('verify_DeIdGenAsync')
    _errlogger  =_getLogger('error__DeIdGenAsync')

    _vlogger.debug('input : '+_jsonBase64)

    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if jsonfile is None:
        errMsg = 'Jsonfile is None: DeIDFail- {}'.format(jsonfile)
        _errlogger.debug(errMsg)
        self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-2'}) 
        return 'DeIDFail'
    
    #get parameter
    try:
        pname = jsonfile['pname'].encode("utf-8")
        prodesc =  jsonfile['prodesc'].encode("utf-8")
        powner =  '1' #jsonfile['powner']
        p_dsname =  jsonfile['p_dsname'] #projName
        step = '1' #jsonfile['step']
        configName = jsonfile['configName']
        #for hash
        hashTableName = jsonfile['hashTableName']
        #hashkey = jsonfile['hashkey']
        sep = jsonfile['sep']
        columns_mac = jsonfile['columns_mac']
        dataHash = jsonfile['dataHash']
        onlyHash = "N"
        # onlyGen  = jsonfile['onlyGen']
    except Exception as err:
        errMsg =  'Json format error: DeIDFail- %s:%s' %(type(err).__name__, err)
        #_errlogger.debug('json file first layer error! - %s:%s' %(type(err).__name__, err))
        _errlogger.debug(errMsg)
        self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-2'})
        return 'DeIDFail'

    #check parameter null?
    if pname == '' or prodesc == '' or powner == '' or p_dsname == '' or hashTableName == '' or sep == '' or columns_mac == '' or dataHash == '' or configName == '':
        errMsg = 'Missing parameter: DeIDFail-' + str(' Null parameter')
        self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-1'})
        return 'DeIDFail'

    print('pname:{}, prodesc:{}, powner:{}, p_dsname:{}, hashTableName:{}, sep:{}, columns_mac:{}, dataHash:{}, configName:{}').format(pname, prodesc, powner, p_dsname, hashTableName, sep, columns_mac, dataHash, configName)

    #2020.07.10: create project API 
    ################################
    #get ip config for openapi
    web_ip,web_port,flask_ip,flask_port = getConfig().getOpenAPI()
    web_ip = str(web_ip)
    web_port = str(web_port)
    flask_ip = str(flask_ip)
    flask_port = str(flask_port)
    ################################
    response = {}
    try:
        # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc } 
                # InsertProject_para = { "p_dsname": p_dsname, "pname": pname, "powner": powner, "prodesc": prodesc }  #原版
        InsertProject_para = { "p_dsname": pname, "pname": p_dsname, "powner": powner, "prodesc": prodesc } 
        response_get = requests.get("http://"+web_ip+":"+web_port+"/api/WebAPI/InsertProject", params=InsertProject_para)
        print(response_get.url)
        response_dic = response_get.json()
        # _vlogger.debug('InsertProject_flag: '+ str(response_dic))
        # print("response_get: ",response_dic)
        response['InsertProject_flag']=response_dic
    except Exception as e:
        _errlogger.debug('Insert project error. {0}'.format(str(e)))
        errMsg = 'Insert project error. {0}'.format(str(e))
        self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-4'})
        return 'DeIDFail'
    #check create project
    try:
        if int(response['InsertProject_flag'])==1:
            _vlogger.debug('InsertProject_flag: '+ str(response_dic))
            # print("citc____Mission START")
            # pass
        elif int(response['InsertProject_flag'])==-5:
            error_insertproj = 'Duplicate project name' #'專案名稱重複'
            errMsg = 'Insert project error: - %s' %(error_insertproj)
            _errlogger.debug('{0}'.format(str(errMsg)))
            self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-4'})
            return 'DeIDFail'
            sys.exit(0)
        elif int(response['InsertProject_flag'])==-4:
            error_insertproj = 'Project status error' #'專案狀態錯誤'
            errMsg = 'Insert project error: - %s' %(error_insertproj)
            _errlogger.debug('{0}'.format(str(errMsg)))
            self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-4'})
            return 'DeIDFail'
            sys.exit(0)
        else:
            error_insertproj = 'Whether p_dsname is reused'#'系統寫入出現錯誤:檢查p_dsname是否重複使用'
            errMsg = 'Insert project error: - %s' %(error_insertproj)
            _errlogger.debug('{0}'.format(str(errMsg)))
            self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-4'})
            return 'DeIDFail'
            sys.exit(0)
    except Exception as e:
        _errlogger.debug('Insert project error. {0}'.format(str(e)))
        errMsg = 'Insert project error. {0}'.format(str(e))
        self.update_state(state="DeIDFail", meta={'errMsg':errMsg,'stateno':'-4'})
        return 'DeIDFail'
        sys.exit(0)

         
    # print cmdStr
    cmd=["python","app/devp/DeidGenAsync.py","-pname",pname,"-prodesc",prodesc,"-powner",powner,"-p_dsname",p_dsname,"-step",step,"-configName",configName,"-hashTableName",hashTableName,"-sep",sep,"-columns_mac",columns_mac,"-dataHash",dataHash,"-onlyHash",onlyHash]
    print(cmd)

    sp = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    '''
    while sp.poll() is None:
        print("AFTER SP")
        out, err = sp.communicate()
        if err:
            print('The process raised an error:', err.decode())
            outList = []
        else:
            outList = getSparkAppId(self, sp, False, projID,projName,userID)
    '''
    outList = getSparkAppId(self, sp, False, p_dsname)

    err = sp.stderr.readlines()
    err_list = []
    if err:
        flag_err = 0
        print("something wrong")
        for err_line in err:
            sys.stdout.write(err_line)
            err_list.append(err_line.decode())
            flag_err = 1
            sys.stdout.flush()
        errMsg = str(err_list)
        # self.update_state(state='FAIL', meta={'errMsg':errMsg,'stateno':'-1'})
        # return {'errMsg':errMsg,'stateno':'-1'}

    
    ####citc, add for ssh call py (end)#####################
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
    outTblName = outTblName[:-1]
    appID=appID[:-1]
    ts1 = time.time()
    print (ts1-ts0)
    print ("#######outList#######"    )
    err_list = list_clean(err_list)

    return outList

def getSparkAppId(self, subprocess, viewSparkProcess_,projName):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')
    print('output')

    viewSparkProcess = viewSparkProcess_
    meta_={}# python dict
    print("This is PID: ",subprocess.pid)
    # meta={'PID': subprocess.pid,'projStep':'DeId_async','projName':projName}
    self.update_state(state="PROGRESS", meta={'PID': subprocess.pid,'projStep':'DeId_async','projName':projName})

    while True:
        line= subprocess.stdout.readline().decode()#stdout_ 
        if line == ' ' and subprocess.poll() is not None:
            break
        sys.stdout.write(line)
        sys.stdout.flush()

        if line == '':
            break
        
        ##20181217 verify__genData#######
        if "verify_DeIdAsync" in  line:
            kTable_index=line.find('verify__DeIdAsync - DEBUG -') 
            kTable_=line[kTable_index:]
            tmpStrList = kTable_.split("verify__DeIdAsync - DEBUG -")
            _vlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            # if "PATH" in tmpStrList[1]:
                # meta_['synPath'] = kTable_.split("PATH:")[1]
            print('verify__: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            meta_['verify'] = kTable_
            outList.append(kTable_)
            
        if "error__DeIdAsync" in  line:
            kTable_index=line.find('error__DeIdAsync - DEBUG -') 
            kTable_=line[kTable_index:]
            tmpStrList = kTable_.split("error__DeIdAsync - DEBUG -")
            _errlogger.debug(tmpStrList[1])
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            print('error: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            meta_['errMsg'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)
            self.update_state( state="errTable", meta=meta_)
            # break
        # #kTable_
        # if "citc____Mission START" in  line:
        #     kTable_index=line.find('citc____Mission START') 
        #     kTable_=line[kTable_index:]
        #     tmpStrList = kTable_.split("____")
        #     kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
        #     print('The JOBE is STARTED: ' + tmpStrList[1])
        #     print ('task id is '+self.request.id)
        #     meta_['kTable'] = kTable_
        #     outList.append(kTable_)
        #     self.update_state( state="PROGRESS", meta=meta_)
        #     break
        #kTable_
        if "citc_final____Mission Complete" in  line:
            kTable_index=line.find('citc_final____Mission Complete') 
            kTable_=line[kTable_index:]
            tmpStrList = kTable_.split("____")
            kTable_ = tmpStrList[1][0:len(tmpStrList[1])-1]
            print('The JOBE is done: ' + tmpStrList[1])
            print ('task id is '+self.request.id)
            meta_['kTable'] = kTable_
            outList.append(kTable_)
            break

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
       
    return outList
    ########################33  


