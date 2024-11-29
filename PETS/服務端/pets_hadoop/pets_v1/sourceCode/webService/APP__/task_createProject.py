#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from app import app
from app import celery
from flask_redis import FlaskRedis
from log.logging_tester import _getLogger
from module.base64convert import getJsonParser, encodeDic
from module.JsonSchema import getCreateProjectSchema,loadJson
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs
from config.connect_sql import ConnectSQL
from celery import states


redis_store = FlaskRedis(app)


###itri, for deID (start)######################
@celery.task(bind=True)
def createProject_longTask(self, base64_,nothing):
    """
    base64_: string
    nothing: 1
    """
    with app.app_context():

        global _logger,_vlogger
        _logger=_getLogger('createProject')
        _vlogger=_getLogger('verify__' + 'createProject')

        #decode base64   回傳error
        jsonAll = getJsonParser(base64_) # return jsons  PS: decode有自己的log
        if isinstance(jsonAll,str):
            errMsg = 'decode_base64_error: {}'.format(jsonAll)
            _logger.debug(errMsg)
            self.update_state(state="FAILURE", meta={'errMsg':errMsg})
            return 

        # get dbName and tblName
        try:
            projStep = jsonAll['projStep']
            projName = jsonAll['projName'] #
            projID = jsonAll['projID']
            mainInfo = jsonAll['mainInfo']
        except Exception as e:
            errMsg = 'json_format_error: {}'.format(str(e))
            _logger.debug(errMsg)
            self.update_state(state="FAILURE", meta={'errMsg':errMsg})
            return        

        # check projStep
        if projStep != 'createProject':
            errMsg = 'celery_import_error_projStep_is_not_export'
            _logger.debug(errMsg)
            self.update_state(state="FAILURE", meta={'errMsg':errMsg})
            return

        # check schema
        schema = getCreateProjectSchema()
        data = loadJson(mainInfo, schema)  # return None if error
        try:
            user = data['user']
            dbName = data['dbName']
        except Exception as e:
            errMsg = 'json_format_error: {}'.format(str(e))
            _logger.debug(errMsg)
            self.update_state(state="FAILURE", meta={'errMsg':errMsg})
            return

        # Logging
        _logger.debug('projID: %s', projID)
        _logger.debug('projStep: %s',projStep)
        _logger.debug('user: %s', user)
        _logger.debug('dbName: %s', dbName)

        _vlogger.debug('projID: %s', projID)
        _vlogger.debug('projStep: %s',projStep)
        _vlogger.debug('user: %s', user)
        _vlogger.debug('dbName: %s', dbName)


        try:
            sparkCode = getConfig().getSparkCode('createProject.py')
            cmdStr = 'spark-submit {0} {1} {2} {3}'.format(sparkCode, projID, user, dbName)
            _logger.debug(cmdStr)
            ssh_for_bash = ssh_hdfs()
            stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

        except Exception as e:
            errMsg = 'ssh connect error: ' + str(e)
            _logger.debug(errMsg)
            self.update_state(state="FAILURE", meta={'errMsg': errMsg})
            return

        if 0:
                lines = stdout.readlines()
                for line in lines:
                    print(line)
                #outList = getSparkAppId_(lines)
                #print(outList)
        else:
                ##c. get spark ID, table name##########
                outDict = getSparkAppId(self, stdout, True)
                print(outDict)

        '''
        if len(outDict) < 3:
            # appID=app_ID
            appID = "9999"
            outTblName = "errTable"
            err_ = 'outList_length_error: Except length >= 3, but get lenthgh: {}'.format(len(outDict))
            outDict['errTable'] = err_

            self.update_state(state="FAILURE", meta=outDict)
            return outDict
        '''

        return outDict

    ##2018/03/30, citc recover###############################
def getSparkAppId(self, stdout_, viewSparkProcess_):
        app_ID = 9999
        outDict = dict()
        print('in getSparkAppId')

        viewSparkProcess = viewSparkProcess_
        meta_ = dict()

        while True:
            line = stdout_.readline()
            if line == '':
                break
            print(line)

            ##20180706 add, citc add for error###########
            if "All tables save succeed: " in line:
                try:
                    table_save_index = line.find('All tables save succeed: ')
                    table_save_ = line[table_save_index:][len('All tables save succeed: '):].strip('\n')
                    _logger.debug(table_save_index)
                    _logger.debug(line)
                    _logger.debug(table_save_)
                    _logger.debug('table_save_: {}'.format(table_save_))
                    meta_['tblName'] = table_save_
                    outDict['tblName'] = table_save_
                    self.update_state(state="PROGRESS", meta=meta_)
                except Exception as e:
                    errMsg = str(e)
                    _logger.debug(errMsg)

            if "spark dbName: " in line:
                dbName_index = line.find('spark dbName: ')
                dbName_ = line[dbName_index:][len("spark dbName: "):].strip('\n')
                _logger.debug('dbName is ' + dbName_)
                meta_['dbName'] = dbName_
                outDict['dbName'] = dbName_

            ##20180103 add, citc add for error###########
            if "errTable:" in line:
                errTable_index = line.find('errTable:')
                errReson_ = line[errTable_index:].strip('\n')
                _logger.debug('The errReason_ is ' + errReson_)
                _logger.debug('task id is ' + self.request.id)
                meta_['errTable'] = errReson_
                outDict['errTable'] = errReson_
                _logger.debug(errReson_)
                break

            if "sc.applicationId:" in line:
                app_ID_index = line.find('application_')
                app_ID = line[app_ID_index:]
                # this gives the app_ID
                _logger.debug('The app ID is ' + app_ID)
                meta_['sparkAppID'] = app_ID
                self.update_state(state="PROGRESS", meta=meta_)
                # self.update_state(state="PROGRESS", meta={'progress': app_ID})
                outDict['sparkAppID'] = app_ID
                # return outList
                if not viewSparkProcess:
                    break

        print('#####meta_######')
        print(meta_)

        if (meta_.has_key('errTable')):
            # self.update_state(state="FAIL", meta=meta_)
            self.update_state(state=states.FAILURE, meta=meta_)
        else:
            self.update_state(state="PROGRESS", meta=meta_)

        return outDict