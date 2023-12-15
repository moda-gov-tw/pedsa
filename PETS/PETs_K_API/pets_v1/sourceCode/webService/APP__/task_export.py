#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import base64
from app import app
from app import celery
from celery import states
from flask_redis import FlaskRedis
from log.logging_tester import _getLogger
from module.base64convert import getJsonParser, encodeDic
from module.JsonSchema import getExportSchema,loadJson
from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs
from config.connect_sql import ConnectSQL


redis_store = FlaskRedis(app)


def getColoumnsFromMysql(projName, tblOutput):
    # get input table name

    '''
    m = re.search("gen_(.+?)_final", tblOutput)
    if m:
        tblInput = m.group(1)
        _logger.debug("tblInput: {0}".format(tblInput))
    '''


    # connect to mysql
    try:
        export_conn = ConnectSQL()
        #_logger.debug('start to connectToMysql with (input table / output table): ({} / {})'.format(tblInput,tblOutput))
    except Exception as e:
        _logger.debug('connectToMysql fail: ' + str(e))
        return

    # query columns name
    colCompare = dict()

    '''
    sqlCommand = """
    SELECT pro_col_en,pro_col_cht
    FROM {}.{}
    WHERE pro_db='{}'
    AND pro_tb='{}'
    """.format('DeIdService', 'T_Project_SampleTable', projName, tblInput)    
    '''
    sqlCommand = """
    SELECT pro_col_en,pro_col_cht
    FROM {0}.{1}
    WHERE pro_db='{2}'
    AND finaltblName='{3}'
    """.format('DeIdService', 'T_Project_SampleTable', projName, tblOutput)

    _logger.debug(sqlCommand)

    result = export_conn.doSqlCommand(sqlCommand)

    if len(result['fetchall']) == 0:
        errMsg = 'Can not find finaltblName: {}'.format(tblOutput)
        return errMsg

    pro_col_en = [col.strip(' ') for col in result['fetchall'][0]['pro_col_en'].split(',')]
    pro_col_cht = [col.strip(' ') for col in result['fetchall'][0]['pro_col_cht'].split(',')]

    for i in range(len(pro_col_en)):
        colCompare[pro_col_en[i]] = pro_col_cht[i]

    return encodeDic(colCompare)

###itri, for deID (start)######################
@celery.task(bind=True)
def export_longTask(self, base64_,nothing):
    """
    base64_: string
    nothing: 1
    """
    with app.app_context():
        ts0 = time.time()
        global _logger,_vlogger
        _logger=_getLogger('export')
        _vlogger=_getLogger('verify__' + 'export')

        #decode base64   回傳error
        jsonBase64 = getJsonParser(base64_) # return jsons
        jsonAll = getJsonParser(jsonBase64['jsonBase64']) # return jsons
        _logger.debug(jsonAll)
        _logger.debug("------ userAccount  userId --start-------")
        userAccount = jsonAll['userAccount']
        userId = jsonAll['userId']
        _logger.debug('userAccount: %s',userAccount)
        _logger.debug('userId: %s',userId) 
        _logger.debug("------ userAccount  userId --end-------")

        if isinstance(jsonAll,str):
            errMsg = 'decode_base64_error: {}'.format(jsonAll)
            _logger.debug(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg':errMsg})
            return 

        # get dbName and tblName
        try:
            projStep = jsonAll['projStep']
            projName = jsonAll['projName']
            projID = jsonAll['projID']
            mainInfo = jsonAll['mainInfo']
        except Exception as e:
            errMsg = 'json_format_error: {}'.format(str(e))
            _logger.debug(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return        

        # check projStep
        if projStep != 'export':
            errMsg = 'celery_import_error_projStep_is_not_export'
            _logger.debug(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return

        # logging
        _logger.debug('jobName: %s',projStep)
        _logger.debug('dbName: %s',projName)
        _logger.debug('mainInfo: %s',str(mainInfo))
        _vlogger.debug('jobName: %s',projStep)
        _vlogger.debug('dbName: %s',projName)
        _vlogger.debug('mainInfo: %s',str(mainInfo))

        # updat state for response to front
        meta_ = dict()
        toDoList = [mainInfo[tbl]['finaltblName'] for tbl in mainInfo]
        doneList = []

        # export
        schema = getExportSchema()
        jarfiles = getConfig().getJarFiles()
        sparkCode = getConfig().getSparkCode('getExport_CFH.py')
        path = getConfig().getExportPath('local')
        tblColDict = dict()
        for tbl in mainInfo:
            # check tableInfo
            data = loadJson(mainInfo[tbl], schema)  # return None if error
            _logger.debug("Get json data: {0}".format(data))
            if data is None:
                errMsg = 'Celery export error getExport json mainInfo error'
                _logger.debug(errMsg)
                self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
                return
            # response for front-end
            try:
                rawTblName = data['pro_tb']
                tblName = data['finaltblName']
                location = data['location']
                _logger.debug("tblName: {0}".format(tblName))
            except KeyError as key_error:
                errMsg = 'Celery export error: Json mainInfo key error, cannot find key {0}'.format(str(key_error))
                _logger.debug(errMsg)
                self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
                time.sleep(1)
                return

            if str(location) == 'local':
                try:
                    exportColEncode = getColoumnsFromMysql(projName, tblName)
                    if "Can not find finaltblName" in exportColEncode:
                        _logger.debug(exportColEncode)
                        self.update_state(state="FAIL_CELERY", meta={'errMsg': exportColEncode})
                        time.sleep(1)
                        return
                    # "finaltblName": {"exportColEncode": exportColEncode, "rawTblName": rawTblName}
                    tblColDict[tblName] = {"exportColEncode": exportColEncode, "rawTblName": rawTblName}

                except Exception as e:
                    errMsg = 'ssh_connect_error: ' + str(e)
                    _logger.debug(errMsg)
                    meta_['errMsg'] = errMsg
                    self.update_state(state="FAIL_CELERY", meta=meta_)
                    time.sleep(1)
                    return

            elif str(location) == 'hdfs':
                #TO-DO
                pass

            else:
                errMsg = "location_error: should be \'hdfs\' or \'local\'"
                _logger.debug(errMsg)
                meta_['errMsg'] = errMsg
                self.update_state(state="FAIL_CELERY", meta=meta_)
                return

        exportDictEncode = encodeDic(tblColDict)
        _logger.debug("projID")
        _logger.debug(projID)
        cmdStr = '''
        spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7}'''.format(jarfiles,
                                                          sparkCode,
                                                          projName,
                                                          exportDictEncode,
                                                          path,
                                                          projID,
                                                          userAccount,
                                                          userId)
        _logger.debug(cmdStr)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

        if 0:
            lines = stdout.readlines()

            for line in lines:
                print(line)

            outList = getSparkAppId_(lines)
            print(outList)
        else:
            ##c. get spark ID, table name##########
            outList = getSparkAppId(self, stdout, True)
            print(outList)

        if len(outList) < 3:
            # appID=app_ID
            appID = "9999"
            outTblName = "errTable"
            err_ = 'outList_length_error: Except length >= 3, but get lenthgh: {}'.format(len(outList))
            self.update_state(state="FAIL_CELERY", meta={'sparkAppID': appID, 'errMsg': err_})

        else:
            exportDbName = outList[0]
            exportTblName = outList[1]
            appID = outList[2]

        # update state
        _logger.debug('Export {} done.'.format(tblName))

        toDoList.remove(tblName)
        doneList.append(tblName)
        meta_['mainInfo'] = {'toDoList': ';'.join(toDoList),
                             'doneList': ';'.join(doneList)}

        self.update_state(state="PROGRESS", meta=meta_)

        print('Export total tables done.')
        ts1 = time.time()
        print(ts1-ts0)
        return outList


def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID = 9999
    outList = []
    _logger.debug('in getSparkAppId')
    viewSparkProcess = viewSparkProcess_
    meta_ = dict()
    while True:
        line = stdout_.readline()
        _logger.debug(line)
        if line == '':
           break


        if "spark_export_dbName:" in line:
            exportDbName_index = line.find('spark_export_dbName:')
            exportDbName_ = line[exportDbName_index:][len("spark_export_dbName:"):].strip('\n')
            _logger.debug('The export dbName is ' + exportDbName_)
            _logger.debug('task id is ' + self.request.id)
            # self.update_state(self.request.id, state="PROGRESS", meta={'progress': gebTable_})
            meta_['dbName'] = exportDbName_
            # self.update_state( state="PROGRESS", meta={'progress': gebTable_})
            outList.append(exportDbName_)

        ##20180103 add, citc add for error###########
        if "errTable:" in line:
            errTable_index = line.find('errTable:')
            errReson_ = line[errTable_index:].strip('\n')
            _logger.debug('The errReason_ is ' + errReson_)
            _logger.debug('task id is ' + self.request.id)
            # self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            # self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break

        if "spark_export_tblName:" in line:
            exportTblName_index = line.find('spark_export_tblName:')
            exportTblName_ = line[exportTblName_index:][len("spark_export_tblName:"):].strip('\n')
            _logger.debug('The export tblName is ' + exportTblName_)
            meta_['tblName'] = exportTblName_
            # self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(exportTblName_)

        if "sc.applicationId:" in line:
            app_ID_index = line.find('application_')
            app_ID = line[app_ID_index:].strip('\n')
            # this gives the app_ID
            _logger.debug('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            self.update_state(state="PROGRESS", meta=meta_)
            # self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)

            # return outList
            if not viewSparkProcess:
                break

    print('#####meta_######')
    print(len(meta_))
    print(meta_)
    print(meta_.has_key('errTable'))
    ##20180103 add, citc add for error#############
    if (meta_.has_key('errTable')):
        self.update_state(state="FAIL_SPARK", meta=meta_)
        time.sleep(1)

    return outList

