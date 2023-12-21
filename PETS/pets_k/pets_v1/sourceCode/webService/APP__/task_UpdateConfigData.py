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


def UpdateconfigData(configName, jsonstream):
    #check file exists?
    path = getConfig().getExportPath('local')
    configPath = os.path.join(path[:-12], 'dataConfig/') + configName
    with open(configPath, 'w') as outfile:
        json.dump(jsonstream, outfile)

###itri, for gen data(start)######################
@celery.task(bind=True)
#使用者更新config > bruce回傳更新json>複寫原本的config file
#configname,jsonstream
def UpdateConfigData_longTask(self, _jsonBase64,nothing):

    """
    base64_: string ( projName: string, userID: int, configname: string, jsonstream: json)
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
        jsonstream = jsonfile['jsonstream']

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
    if jsonstream == '':
        errMsg = 'jsonstream varible is None'
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    # print cmdStr
    print('userID: ',userID)
    print('projName:',projName)
    print('configName: ',configName)
    print('jsonstream: ',jsonstream)

    try:
        UpdateconfigData(configName, jsonstream)
        meta_={'projStep':'UpdateconfigData','userID':userID,'projName':projName, 'configName':configName} 
        print (meta_)
        self.update_state(state="PROGRESS", meta=meta_)
        return meta_ 
    except Exception as err:
        errMsg = 'Update error! - %s:%s' %(type(err).__name__, err)
        _errlogger.debug(errMsg)
        self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-1'})
        return {'Msg':errMsg,'stateno':'-1'}

    
