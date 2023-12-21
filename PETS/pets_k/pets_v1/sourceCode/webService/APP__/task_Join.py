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

from config.getSparkStatus import checkSparkStatus

import sys
reload(sys)
sys.setdefaultencoding('utf8')


redis_store = FlaskRedis(app)


###itri, for deID (start)######################
@celery.task(bind=True)
def Join(self, json_,nothing):
    
    global _logger, _vlogger
    # _logger=_getLogger('Join')
    # _vlogger=_getLogger('verify__' + 'Join') #verify__Join
    # print("################################################")

    _logger=_getLogger('setJP')
    _vlogger=_getLogger('verify__' + 'setJP') #verify__Join
    print("################################################")
    ts0 = time.time()


    #decode base64
    # jsonAll = getJsonParser(base64_) # return jsons
    # _logger.debug(jsonAll)
    # _logger.debug("------ userAccount  userId --start-------")
    # userAccount = jsonAll['userAccount']
    # userId = jsonAll['userId']
    # _logger.debug('userAccount: %s',userAccount)
    # _logger.debug('userId: %s',userId) 
    # _logger.debug("------ userAccount  userId --end-------")

    # if isinstance(jsonAll,str):
    #     errMsg = 'decode_base64_error: %s',jsonAll
    #     _logger.debug(errMsg)
    #     self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
    #     return

    # get dbName and tblName
    try:
        # #projStep = jsonAll['projStep']
        # projName = jsonAll['project_name']
  
        # #citc, 20200621 fir debug
        # #projName = "2QDataMarketDeId"

        # projID = jsonAll['project_id']
        # _logger.debug("------projStep projName projID---start-------")
        # #_logger.debug(projStep)
        # _logger.debug(projName)
        # _logger.debug(projID)
        # _logger.debug("------projStep projName projID---end-------")

        # projkey = jsonAll['project_key']
        # _logger.debug(projkey)
        # jointype = jsonAll['Join_type']
        # _logger.debug(jointype)
        # joinfunc = jsonAll['Join_func']
        # _logger.debug(joinfunc)
        
        member_id = json_['member_id']
        join_type = json_['join_type']
        join_func_encoded = json_['join_func_encoded']
        project_eng = json_['project_eng']
        project_id = json_['project_id']
        

        #mainInfo = jsonAll['mainInfo']
    except Exception as e:
        errMsg = 'json_format_error: {}'.format(str(e))
        _logger.debug(errMsg)
        self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
        return

    try:
        jarfiles = getConfig().getJarFiles()
        path = getConfig().getImportPath('local')
        sparkCode = getConfig().getSparkCode('joinfile.py')
        ex_path = getConfig().getExportPath('local')

        cmdStr='''spark-submit --jars {0} {1} {2} {3} {4} {5} {6}'''.format(jarfiles,
                                                        sparkCode,
                                                        member_id,
                                                        join_type,
                                                        join_func_encoded,
                                                        project_eng,
                                                        project_id
                                                        )
        


        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

    except Exception as e:
        errMsg = 'ssh connect error: ' + str(e)
        _logger.debug(errMsg)
        self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
        return



    if 0:
        lines = stdout.readlines()
        print(lines)
        print(stderr.readlines())


        for line in lines:
            print(line)

        outList = getSparkAppId_( lines)
        print(outList)
    else:
        ##c. get spark ID, table name##########
        outList = getSparkAppId(self, stdout, False)
        print(outList)

    #self.update_state(self.request.id, state="PROGRESS", meta={'progress': 90})
    #time.sleep(1)

    if len(outList) < 2:
        #appID=app_ID
        appID="9999"
        outTblName="errTable"
    else:
        appID=outList[1]
        outTblName=outList[0]
    print(outTblName)
    print(len(outTblName))
    outTblName = outTblName[:-1]
    appID=appID[:-1]


    ts1 = time.time()
    print(ts1-ts0)
    ##d. close ssh section##########
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
    meta_= dict()

    doneList = []
    tmp_data_path = ''
    tmp_header_en_path = ''
    tmp_header_ch_path = ''

    while True:
        line = stdout_.readline()
        if line == '':
            break
        print(line)

        if "sampleStr_succeed" in line:
            #connect to mysql
            try:
                import_conn = ConnectSQL()
                _logger.debug('start to connectToMysql with table: {}'.format(meta_['tblName']))
            except Exception as e:
                meta_['errMsg'] = str(e)
                _logger.debug('connectToMysql fail: '+meta_['errMsg'])
                self.update_state(state="FAIL_CELERY", meta=meta_)
                break

            #inser to sample table
            condisionSampleTable = {
                'project_id':meta_['projID'],
                'pro_db':meta_['dbName'],
                'pro_tb':meta_['tblName']
            }

            valueSampleTable = {
                'project_id': meta_['projID'],
                'pro_db': meta_['dbName'],
                'pro_tb': meta_['tblName'],
                'pro_col_en': tmp_header_en_path,
                'pro_col_cht': tmp_header_ch_path,
                'pro_path': tmp_data_path,
                'tableCount': meta_['tblCount'],
                'tableDisCount': 'NULL',
                'minKvalue': 'NULL',
                'supRate': 'NULL',
                'supCount': 'NULL',
                'finaltblName': meta_['tblName'],
                'after_col_en': 'NULL',
                'after_col_cht': 'NULL',
                'qi_col': 'NULL',
                'tablekeycol': 'NULL',
                'after_col_value': 'NULL',
                'gen_qi_settingvalue': 'NULL'
            }

            resultSampleTable = import_conn.updateValueMysql('DeIdService',
                                                            'T_Project_SampleTable',
                                                            condisionSampleTable,
                                                            valueSampleTable)
            if resultSampleTable['result'] == 1:
                _logger.debug(resultSampleTable['msg'])
            else:
                meta_['errMsg'] = resultSampleTable['msg']
                _logger.debug('insertSampleTableToMysql fail: '+meta_['errMsg'])
                self.update_state(state="FAIL_CELERY", meta=meta_)
                break

            # close mysql
            import_conn.close()

        if "tblCount_" in  line:
            tblCount_index=line.find('tblCount_')
            tblCount_=line[tblCount_index:][len("tblCount_"):].strip('\n')
            _logger.debug('The tblCount is ' + tblCount_)
            meta_['tblCount'] = tblCount_
            outList.append(tblCount_)

        if "table_save_succeed_" in  line:
            try:
                table_save_index=line.find('table_save_succeed_')
                table_save_=line[table_save_index:][len('table_save_succeed_'):].strip('\n')
                _logger.debug(table_save_index)
                _logger.debug(line)
                _logger.debug(table_save_)
                _logger.debug('table_save_: {}'.format(table_save_))
                doneList.append(table_save_)
                toDoList.remove(table_save_)

                meta_['mainInfo'] = {'toDoList':';'.join(toDoList),
                                     'doneList':';'.join(doneList)}

                self.update_state(state="PROGRESS", meta=meta_)
            except Exception as e:
                errMsg = str(e)
                _logger.debug(errMsg)


        #tblName 20180709  each table
        if "spark_import_table_" in  line:
            spark_import_tblName_index=line.find('spark_import_table_')
            spark_import_tblName_=line[spark_import_tblName_index:][len("spark_import_table_"):].strip('\n')
            _logger.debug('The import_tblName is ' + spark_import_tblName_)
            meta_['tblName'] = spark_import_tblName_
            outList.append(spark_import_tblName_)

        ##20180706 add, citc add for error###########
        if "spark_import_header_en_" in  line:
            header_en_index=line.find('spark_import_header_en_')
            header_en_=line[header_en_index:][len('spark_import_header_en_'):].strip('\n')
            tmp_header_en_path = header_en_

        ##20180706 add, citc add for error###########
        if "spark_import_header_ch_" in  line:
            header_ch_index=line.find('spark_import_header_ch_')
            header_ch_=line[header_ch_index:][len('spark_import_header_ch_'):].strip('\n')
            tmp_header_ch_path = header_ch_

        ##20180706 add, citc add for error###########
        if "spark_import_rawData_" in  line:
            rawData_index=line.find('spark_import_rawData_')
            rawData_=line[rawData_index:][len('spark_import_rawData_'):].strip('\n')
            tmp_data_path = rawData_


        ##20180103 add, citc add for error###########
        if "errTable:" in  line:
            errTable_index=line.find('errTable:')
            errReson_=line[errTable_index:].strip('\n')
            _logger.debug('The errReason_ is ' + errReson_)
            _logger.debug('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            meta_['sparkAppID'] = '9999'
            _logger.debug(errReson_)
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break

        ##20180103 add, citc add for error (end)#######
        if "spark_import_projID_" in  line:
            spark_import_projID_index=line.find('spark_import_projID_')
            spark_import_projID_=line[spark_import_projID_index:][len("spark_import_projID_"):].strip('\n')
            _logger.debug('The import_projID is ' + spark_import_projID_)
            meta_['projID'] = spark_import_projID_
            outList.append(spark_import_projID_)

        #dbName 20180611
        if "spark_import_dbName_" in  line:
            spark_import_dbName_index=line.find('spark_import_dbName_')
            spark_import_dbName_=line[spark_import_dbName_index:][len("spark_import_dbName_"):].strip('\n')
            _logger.debug('The import_dbName is ' + spark_import_dbName_)
            meta_['dbName'] = spark_import_dbName_
            outList.append(spark_import_dbName_)

        #tblName 20180611  # total tables
        if "spark_import_tables_" in  line:
            spark_import_tblNames_index=line.find('spark_import_tables_')
            spark_import_tblNames_=line[spark_import_tblNames_index:][len("spark_import_tables_"):].strip('\n')
            _logger.debug('The import_tblNames are ' + spark_import_tblNames_)
            meta_['tblNames'] = spark_import_tblNames_
            outList.append(spark_import_tblNames_)
            toDoList = list(meta_['tblNames'].split(';'))
            _logger.debug('The toDoList are ' + ';'.join(toDoList))

        if "sc.applicationId:" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            _logger.debug('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            self.update_state(state="PROGRESS", meta=meta_)
            #self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)
            #return outList
            if not viewSparkProcess:
                break

    print('#####meta_######')
    print(len(meta_))
    print(meta_)


    ##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
        self.update_state(state='SparkError', meta=meta_)
        # Celery status from SparkError to SUCCESS, which changing too fast to get Info. from flask.
        # Therefore, set time lag 5 sec to get Info. in flask.
        time.sleep(5)
    else:
        self.update_state(state="PROGRESS", meta=meta_)

    return outList
