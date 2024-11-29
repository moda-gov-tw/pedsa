#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import base64
import json
import os
from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from lib.base64convert import getJsonParser
from MyLib.parseData import exportData
from MyLib.connect_sql import ConnectSQL

#20200317, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#202000318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus
#202109, add
from datetime import datetime
import shlex

def initSparkContext(name):
    appName = name
    # master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _logger.debug("sparkContext_succeed.")

        """
        sc = SparkContext(conf=SparkConf().setAppName(appName).setMaster(master))
        hiveLibs = HiveLibs(sc)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _logger.debug("sparkContext_succeed.")
        """

    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable:fundation_getGenNumLevel:" + str(e))
        _logger.debug("errTable:errSC")
        return SparkContext(conf=SparkConf())

    return sc_, hiveLibs, sqlContext

def exportConfig(dbName, tbl, path_):
    # tbl is rawTblName in mysql table
    # Connect mysql
    try:
        conn = ConnectSQL()
    except Exception as e:
        msg = 'errTable: Connect mysql error: %s', str(e)
        _logger.debug(msg)
        return {'msg': msg, 'result': 0}

    conditionDict = dict()
    conditionDict['pro_db'] = dbName
    conditionDict['finaltblName'] = tbl

    # Check file exist;
    try:
        _logger.debug("Check config file exist condition: {0}".format(str(conditionDict)))
        checkResult = conn.checkValueExist("DeIdService", "T_Project_SampleTable", conditionDict)
        if checkResult['result'] == 0:
            msg = 'errTable: Cannot find table in mysql: {0}'.format(checkResult['msg'])
            _logger.debug(msg)
            return {'msg': msg, 'result': 0}
    except Exception as e:
        msg = 'errTable: checkValueExist error: {0}'.format(str(e))
        _logger.debug(msg)
        return {'msg': msg, 'result': 0}    


    # Export config
    conditions = [str(col) + "='" + str(conditionDict[col]) + "'" for col in conditionDict]
    conditions = ' AND '.join(conditions)
    #20220112 Add k_risk,t1,t2,r_value,max_t
    sqlCommand = """
    select pro_tb,pro_col_cht,qi_col,after_col_value,tablekeycol,gen_qi_settingvalue,minKvalue,target_col,k_risk,cast(t1 as char) as t1,cast(t2 as char) as t2,cast(r_value as char) as r_value,cast(max_t as char) as max_t
    from {0}.{1}
    WHERE {2}
    """.format("DeIdService", "T_Project_SampleTable", conditions)

    #_logger.debug("Export SQL command: {0}".format(sqlCommand))
    sqlResult = conn.doSqlCommand(sqlCommand)
    _logger.debug(sqlResult)
    if sqlResult['result'] == 0:
        err = 'errTable: Select value from {0}.{1} fail: {2}'.format(dbName, tbl, sqlResult['msg'])
        return {'msg': str(err), 'result': 0}
    elif sqlResult['result'] == 1 and len(sqlResult['fetchall']) > 0:
        # Write to file
        writeResult = writeConfig(path_, dbName, tbl, sqlResult['fetchall'][0])
        if writeResult['result'] == 1:
            return {'msg': True, 'result': 1}
        else:
            return {'msg': writeResult['msg'], 'result': 0}
    else:
        return {'msg': False, 'result': 1}

def writeConfig(path_, dbName, tbl, dict_):
    try:
        #exportConfigPath = os.path.join(path_[:-12], 'dataConfig', tbl[6:-7]) + ".json"
        # exportConfigPath = os.path.join(path_, dbName, tbl[6:-7]) + ".json"
        path_ = shlex.quote(path_)
        tbl = shlex.quote(tbl)
        dict_ = shlex.quote(dict_)
        dbName = shlex.quote(dbName)
        exportConfigPath = os.path.join(path_, dbName, tbl) + ".json"

        with open(exportConfigPath, 'w', encoding='utf-8') as outfile:
            dict_['timeStamp'] = datetime.now().timestamp()#.strftime("%Y-%m-%d %H:%M:%S %p")
            dict_['csv_name'] = dict_['pro_tb'][4:]
            dict_['gen_qi_settingvalue'] = dict_['gen_qi_settingvalue'][len(dict_['pro_tb'])+1:]
            json.dump(dict_, outfile, ensure_ascii=False)
        msg = "Write config succeed to {0}".format(exportConfigPath)
        return {'msg': msg, 'result': 1}
    except Exception as e:
        errMsg = "Write config fail: {0}".format(str(e))
        return {'msg': errMsg, 'result': 0}

def main():
    global _logger, sc, hiveLibs, sqlContext, NAME,updateAppStatus_, updateTProjectStatus_
    NAME = 'export'
    _logger = _getLogger(NAME)

    try:
        _logger.debug(exportDictEncode)
        tblInfo = getJsonParser(exportDictEncode)
        _logger.debug(tblInfo)
        tables = list()
        for tbl in tblInfo:
            # "finaltblName": {"exportColEncode": exportColEncode, "rawTblName": rawTblName}
            tblInfo[tbl]["colCompare"] = getJsonParser(tblInfo[tbl]["exportColEncode"])
            tables.append(tbl)
            _logger.debug(tbl)
            _logger.debug(tblInfo[tbl]["colCompare"])

    except Exception as e:
        _logger.debug('errTable:' + NAME + '_' + str(e))
        _logger.debug('errTable:' + NAME + '_decode_base64_error')
        return

    # log input
    _logger.debug('spark_export_userAccount_%s',userAccount)
    _logger.debug('spark_export_userId_%s',userId)    


    _logger.debug('spark_export_dbName:%s', projName)
    _logger.debug('spark_export_projName:%s', projName)
    _logger.debug('spark_export_tblInfo:%s', tblInfo)
    _logger.debug('spark_export_tblName:%s', ','.join(tables))

    # 20221217
    #userAccount = "deidadmin"
    #userId = "8"
    #_logger.debug('spark_export_userAccount_%s',userAccount)
    #_logger.debug('spark_export_userId_%s',userId)


    # spark setting
    sc, hiveLibs, sqlContext = initSparkContext(NAME)

    # return information
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)

    ###202000319, move here##############
    project_id = projID
    try:
        updateTProjectStatus_ = updateTProjectStatus(project_id,userId)
    except Exception as e:        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False     
    
    
    ###20200317, add for checking app status(write to mysql)##############
    try:
        #20200211 add 
        #appID, appName projID,projName
        updateAppStatus_ = updateAppStatus(sc.applicationId, NAME,projName,projID,userId)
    except Exception as e:
        print('updateAppStatus error: %s', str(e))
        return False
    #1 app status
    #updateToMysql(self,appState, progress,progress_state="Running")
    updateAppStatus_.updateToMysql("Init_1","5") #5%
    ###################################################
    _logger.debug('tables = {} '.format(tables))
    #len_c = len(tables.split(';'))
    len_c = len(tables)
    #i=1
    #def __init__(self, lower, upper, div_in_loop, looop_round):
    updateAppProgress_ = updateAppProgress(10,80,4, len_c)    

    # use database
    sqlContext.sql('use ' + projName)
    _logger.debug('use ' + projName)

    # get df
    for tblName in tblInfo:
        # "finaltblName": {"exportColEncode": exportColEncode, "rawTblName": rawTblName}
        progress_str = updateAppProgress_.getLoopProgress(1)#getLoopProgress(len_c, 10, i)
        #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Export_data",progress_str)
        try:
            getAction = """
            SELECT * FROM {}
            """.format(tblName)
            _logger.debug(getAction)
            df = sqlContext.sql(getAction)
        except Exception as e:

            _logger.debug('errTable: Select * from {projName}.{tblName} error: ' + str(e))
            updateAppStatus_.updateToMysql('errTable: Select * from',progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 94,"error")
            return

        progress_str = updateAppProgress_.getLoopProgress(2)#getLoopProgress(len_c, 10, i)
        #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("get header",progress_str)
        # get header
        try:
            colCompare = tblInfo[tblName]["colCompare"]
            headers_en = df.columns
            headers_ch = [colCompare[col] for col in headers_en]
            _logger.debug(headers_ch)
            #df = df.toDF(*headers_ch).columns
        except Exception as e:
            _logger.debug('errTable: get header error: ' + str(e))
            updateAppStatus_.updateToMysql('errTable: get header error',progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 94,"error")
            return
        progress_str = updateAppProgress_.getLoopProgress(3)#getLoopProgress(len_c, 10, i)
        #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Export_data",progress_str)
        

        # export data
        try:
            #path_ = /root/data/output
            _logger.debug(path_)
            result = exportData(projName, df, headers_ch, tblName, path_)
            if result['result'] == 0:
                _logger.debug("Export data error.")
                _logger.debug(result['msg'])
                updateAppStatus_.updateToMysql('Export data error.',progress_str,"err")
                updateTProjectStatus_.updateToMysql(project_id, 94,"error")
                return                
            else:
                _logger.debug("Export data succeed: {0}".format(tblName))
                _logger.debug(result['msg'])


        except Py4JJavaError as e:
            s = e.java_exception.toString()
            _logger.debug(s)
            updateAppStatus_.updateToMysql(s,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 94,"error")

        except Exception:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(sys.exc_info()[2])
            _logger.debug(len(sys.exc_info()))
            _logger.debug('errTable: export csv error')
            updateAppStatus_.updateToMysql('errTable: export csv error',progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 94,"error")
            return
        progress_str = updateAppProgress_.getLoopProgress(4)#getLoopProgress(len_c, 10, i)
        #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Export_config",progress_str)

        # Export config
        try:
            result = exportConfig(projName, tblName, path_)
            _logger.debug("Export config succeed: {0}".format(str(result)))
        except Exception as e:
            _logger.debug('errTable: Export config error: ' + str(e))
            updateAppStatus_.updateToMysql('errTable: Export config error',progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 94,"error")
            return
    #print("3~~~~~~~~~~~~~~~~~~~~~progress_str")
    #move data to bak
   
        # try:
        #     _logger.debug('move config')
        #     _logger.debug(tblName)
        #     _logger.debug(tbl)
        #     _logger.debug(tbl[6:-7])

        #     # config_src =  os.path.join(path_, projName, tbl[6:-7]) + ".json"
        #     # # config_src = os.path.join(path_[:-12], 'dataConfig', tbl[6:-7]) + ".json" # os.path.join(path_, projName, tbl[6:-7]) + ".json"
        #     # config_bak = os.path.join(path_[:-12], 'dataConfig_bak', tbl[6:-7]) + ".json"
        #     #

        #     config_src =  os.path.join(path_, projName, tbl) + ".json"
        #     # config_src = os.path.join(path_[:-12], 'dataConfig', tbl[6:-7]) + ".json" # os.path.join(path_, projName, tbl[6:-7]) + ".json"
        #     config_bak = os.path.join(path_[:-12], 'dataConfig_bak', tbl) + ".json"



        #     _logger.debug('config_src : '+config_src)
        #     _logger.debug('config_bak : '+config_bak)
        #     shutil.copyfile(config_src, config_bak)
        #     #shutil.move(config_src, config_bak)
        # except Exception as e:
        #     _logger.debug('errTable: move config error: ' + str(e))
        #     updateAppStatus_.updateToMysql('errTable: move config error',progress_str,"err")
        #     updateTProjectStatus_.updateToMysql(project_id, 94,"error")
        #     return

        # try:
        #     _logger.debug('move data')
        #     # data_src = os.path.join(path_[:-12], 'dataMac/input', tbl[6:-7]) + ".csv"
        #     data_src = os.path.join(path_, projName,tblName, tblName) + ".csv"
        #     # data_bak = os.path.join(path_[:-12], 'data_bak', tbl[6:-7]) + ".csv"
        #     data_bak = os.path.join(path_[:-12], 'data_bak', tbl) + ".csv"
        #     _logger.debug('data_src : '+data_src)
        #     _logger.debug('data_bak : '+data_bak)
        #     shutil.copyfile(data_src, data_bak)
        #     #shutil.move(data_src, data_bak)
        # except Exception as e:
        #     _logger.debug('errTable: move data error: ' + str(e))
        #     updateAppStatus_.updateToMysql('errTable: move data error',progress_str,"err")
        #     updateTProjectStatus_.updateToMysql(project_id, 94,"error")
        #     return

        # try:
        #     _logger.debug('move data for Decrypt')
        #     # data_src = os.path.join(path_[:-12], 'dataMac/input', tbl[6:-7]) + ".csv"
        #     data_src = os.path.join(path_, projName,tblName, tblName) + ".csv"
        #     # data_bak = os.path.join(path_[:-12], 'data_bak', tbl[6:-7]) + ".csv"
        #     data_Mac = os.path.join(path_[:-12], 'dataMac/input', tbl) + ".csv"
        #     _logger.debug('data_src : '+data_src)
        #     _logger.debug('data_Mac : '+data_Mac)
        #     shutil.copyfile(data_src, data_Mac)
        #     #shutil.move(data_src, data_bak)
        # except Exception as e:
        #     _logger.debug('errTable: move data Decrypt error: ' + str(e))
        #     updateAppStatus_.updateToMysql('errTable: move data error',progress_str,"err")
        #     updateTProjectStatus_.updateToMysql(project_id, 94,"error")
        #     return
    
    #updateTProjectStatus  
    project_status =11
    statusname='export data finished'
    updateTProjectStatus_.updateToMysql(project_id, project_status,statusname)
    
    
    _logger.debug('finish the process in update mysql')




    updateAppStatus_.updateToMysql("All_table_export_succeed","100","Finished")
    _logger.debug("All dataset export data succeed: {0}".format(','.join(tables)))

if __name__ == "__main__":

    projName = sys.argv[1]  # str
    projName = shlex.quote(projName)
    exportDictEncode = sys.argv[2]  # str
    path_ = sys.argv[3]  # local path
    path_ = shlex.quote(path_)
    projID = sys.argv[4]
    userAccount = sys.argv[5]  # str
    userId = sys.argv[6]  # str          
    print('########')
    print(projName)
    print(exportDictEncode)
    print(path_)
    print(userAccount)
    print(userId)
    print('#############')

    main()
