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

redis_store = FlaskRedis(app)

def GetConfigList():
    suffix=".json"
    path = getConfig().getExportPath('local')
    configPath = os.path.join(path[:-12], 'dataConfig/') 
    filenames = listdir(configPath)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

###itri, for gen data(start)######################
@celery.task(bind=True)
#list dataConfig/ config
def GetConfigList_longTask(self, _jsonBase64,nothing):

    """
    base64_: string ( projName: string, userID: int)
    nothing: 1

    """
    global _vlogger, _errlogger

    _vlogger=_getLogger('verify_GetConfigList')
    _errlogger  =_getLogger('error__GetConfigList')

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
         
    # print cmdStr
    print('userID: ',userID)
    print('projName:',projName)
    try:
        ConfigList = GetConfigList()
        if len(ConfigList)==0:
            Flag = '-1'
            errMsg = 'There is no CSV file in the folder.'
            _vlogger.debug('There is no CSV file in the folder.')
            self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
            return {'Msg':errMsg,'stateno':'-1'}
        print('ConfigList ',ConfigList)
        meta_={'projStep':'GetConfigList','userID':userID,'projName':projName, 'ConfigList':ConfigList}
        print (meta_)
        self.update_state(state="PROGRESS", meta=meta_)
        return meta_ 
    except Exception as err:
        errMsg = 'GetConfigList error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}




