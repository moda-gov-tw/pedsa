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

import os

####20181024, citc add for log
# from funniest import HiveLibs
# from funniest.logging_tester import _getLogger

import subprocess
import base64
import json
from marshmallow import pprint
#from JsonSchema import jsonResponse, jsonResponseSchema, UserSchema, tableInfoSchema, loadJson
#from celery__ import celery_class
from celery import  states

from .module import JsonSchema as JsonSchema
from .module.base64convert import *
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs
from config.connect_sql import ConnectSQL
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
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


###itri, for gen data(start)######################
@celery.task(bind=True)
def getReport_longTask(self, projName_, nothing):

    global _logger, _vlogger

    _logger=_getLogger('error__getReport_longTask')
    _vlogger=_getLogger('verify__getReport_longTask')

    _vlogger.debug('input : '+projName_)

    ts0 = time.time()

    try:
        _vlogger.debug('start connectToMysql to check project_name in mysql: {}'.format(projName_))
        check_conn = ConnectSQL()
    except Exception as e:
        #meta['errMsg'] = str(e)
        _logger.debug('connectToMysql fail: '+str(e))# + meta['errMsg'])
        #self.update_state(state="FAIL_CELERY", meta=meta)
        return None

    str_ = 'select project_id, pro_db, pro_tb, tableCount, tableCount, tableCountFinal, tableDisCountFinal, minKvalue, supRate, supCount, tablekeycol, qi_col, gen_qi_settingvalue, warning_col, after_col_en, after_col_cht  from DeIdService.T_Project_SampleTable where pro_db=\'{}\';'.format(str(projName_))
    info_ = check_conn.doSqlCommand(str_)['fetchall']
    #print(info_[0][u'gen_qi_settingvalue'].split('*')[2].split(',')[7].encode('utf-8','replace'))
    #print(type(info_[0][u'gen_qi_settingvalue'].split('*')[2].split(',').encode('utf-8','replace')))
    check_conn.close()
    
    report = {'projID':'', 'projName':'', 'mainInfo':[]}
    for tblInfo in info_:
        report['projID'] = tblInfo['project_id']
        report['projName'] = tblInfo['pro_db']
        tbl_ = {}
        tbl_['BasicInfo'] = getBasicInfo(tblInfo)
        tbl_['GenSetting'] = getGenSetting(tblInfo)
        tbl_['WarningCols'] = getWarningCols(tblInfo)
        report['mainInfo'].append(tbl_)

 
    #check_conn = ConnectSQL()
    #updateToMysql_ProjectStatus(self, check_conn, projID, 11, u'查看報表')
    #check_conn.close()
    #_vlogger.debug('----- updateToMysql_ProjectStatus -----')
    ts1 = time.time()
    print (ts1-ts0)
    return report


def updateToMysql_ProjectStatus(self, conn, projID, projStatus, statusName):
    # update process status to mysql

    print('########updateToMysql_ProjectStatus###########')
    condisionSampleData = {
            'project_id': projID
        }

    valueSampleData = {
            'project_id': projID,
            'project_status': projStatus,
            'statusname': statusName,
            'updatetime':str(dt.datetime.now())
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('DeIdService',
                                            'T_ProjectStatus',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        errMsg ='updateToMysql_ProjectStatus fail: ' + msg
        _logger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail"   

def getBasicInfo(tblInfo_):
    BasicInfo = {}
    BasicInfo['tblName'] = tblInfo_['pro_tb']
    BasicInfo['supRecords'] = tblInfo_['supCount']
    BasicInfo['KTblRecords'] = tblInfo_['tableCountFinal']
    BasicInfo['minimumK'] = tblInfo_['minKvalue']
    BasicInfo['KtblDistinctID'] = tblInfo_['tableDisCountFinal']
    BasicInfo['origTblRecords'] = tblInfo_['tableCount']
    BasicInfo['supRate'] = tblInfo_['supRate']
    return BasicInfo

def getWarningCols(tblInfo_):
    WarningCols = {}
    colNames = tblInfo_['warning_col'].split('*')[0].split(',')
    counts = tblInfo_['warning_col'].split('*')[1].split(',')
    for i in range(0,len(colNames)):
        WarningCols[colNames[i]] = counts[i]
    return WarningCols

def getGenSetting(tblInfo_):
    GenSetting = {}
    keys = tblInfo_['tablekeycol'].split(',')
    gen = tblInfo_['gen_qi_settingvalue'].split('*')
    qiCol =  tblInfo_['qi_col'].split(',')
    processMethod = gen[1].split(',')
    process = gen[2].split(',')
    for key in keys : 
        GenSetting[key] = {'Attribute':'直接識別','process':'hash'}
    for i in range(0,len(qiCol)):
        colName = qiCol[i][:-2]
        attri = qiCol[i][-1]
        if attri=='1':
            GenSetting[colName] = {'Attribute':'間接識別','process':getProcess(processMethod[i], process[i].encode('utf-8','replace'))}
        if attri=='2':
            GenSetting[colName] = {'Attribute':'敏感欄位','process':getProcess(processMethod[i], process[i].encode('utf-8','replace'))}
    return GenSetting

def getProcess(processMethod_, process_):
    if processMethod_ == '0':
        method = '不處理'
    elif processMethod_ == '1':
        method = '地址 - '+str(process_)
    elif processMethod_ == '2':
        method = '日期 - '+str(process_)
    elif processMethod_ == '3':
        method = '字串擷取 - '+str(process_)
    elif processMethod_ == '4':
        method = '數字大區間 - '+str(process_)
    elif processMethod_ == '5':
        method = '數字小區間 - '+str(process_)
    elif processMethod_ == '6':
        p_ = process_.split('#')
        method = '數字區間含上下界 - '
        method = method +'下界:'+str(p_[0])
        method = method +' / 數字區間:'+str(p_[1])
        method = method +' / 上界:'+str(p_[2])
    elif processMethod_ == '7':
        method = '不處理'
    elif processMethod_ == '8':
        method = 'hash'
    elif processMethod_ == '9':
        method = '離群值處理'
    else:
        method = ' '
    return method

'''
def main():
    print(getReport_longTask('self', '2QDataMarketDeId', 'N'))   

if __name__ == '__main__':
    main()
'''    
