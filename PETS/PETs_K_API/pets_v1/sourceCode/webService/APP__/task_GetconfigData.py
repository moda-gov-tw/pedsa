#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import re
import base64
import os
from app import app
from app import celery
from flask_redis import FlaskRedis
from celery import states
from log.logging_tester import _getLogger
from module.base64convert import getJsonParser
from module.JsonSchema import getImportSchema,loadJson
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig
from config.connect_sql import ConnectSQL
import sys
from os import listdir
import json
redis_store = FlaskRedis(app)

def GetconfigData(configName):
    #check file exists?
    path = getConfig().getExportPath('local')
    configPath = os.path.join(path[:-12], 'dataConfig/') + configName
    dict_data = []
    if os.path.exists(configPath):
        with open(configPath, 'r') as read_file:
            dict_data = json.load(read_file)
    return dict_data

###itri, for gen data(start)######################
@celery.task(bind=True)
#user選了0621.json>回傳config json to bruce
def GetconfigData_longTask(self, _jsonBase64,nothing):

    """
    base64_: string ( projName: string, userID: int, configName: string)
    nothing: 1

    """
    global _vlogger, _errlogger

    _vlogger=_getLogger('verify_GetconfigData')
    _errlogger  =_getLogger('error__GetconfigData')

    _vlogger.debug('input : '+_jsonBase64)


    ts0 = time.time()

    jsonfile = getJsonParser(_jsonBase64)
    if isinstance(jsonfile,str):
            errMsg = 'decode_base64_error: %s',jsonfile
            _errlogger.debug(errMsg)
            self.update_state(state="FAIL", meta={'Msg':errMsg,'state_no':'-1'})
            return {'Msg':errMsg,'stateno':'-1'}

    try:
        userID = jsonfile['userID']
        projName = jsonfile['projName']#.encode('utf-8')
        configName = jsonfile['configName']
    except Exception as err:
        errMsg = 'json error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    if userID == '':
        errMsg = 'userID varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}
    if projName == '':
        errMsg = 'projName varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}
    if configName == '':
        errMsg = 'configName varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    # print cmdStr
    print('userID: ',userID)
    print('projName:',projName)
    print('configName',configName)

    try:
        configData = GetconfigData(configName)
        if len(configData)==0:
            Flag = '-1'
            errMsg = 'There is no {} in the folder.'.format(configName)
            _vlogger.debug(errMsg)
            self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
            return {'Msg':errMsg,'stateno':'-1'}
        print('configData: ', configData)
        meta_={'projStep':'GetconfigData','userID':userID,'projName':projName, 'configData':configData,'configName':configName}
        print (meta_)
        self.update_state(state="PROGRESS", meta=meta_)
        return meta_ 
    except Exception as err:
        errMsg = 'GetconfigData error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}
