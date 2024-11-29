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
from MyLib.updateTProjectStatus_gen import updateTProjectStatus
import configparser
import re
import subprocess
import shlex
def initSparkContext(name):
    appName = name
    # master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemasterSJOIN:9083")

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
    sqlCommand = """
    select pro_tb,pro_col_en,pro_col_cht,qi_col,after_col_value,tablekeycol,gen_qi_settingvalue,minKvalue,supCount,supRate,tableCount,tableDisCount from {0}.{1}
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
        exportConfigPath = os.path.join(path_[:-12], 'dataConfig', tbl[6:-7]) + ".json"
        with open(exportConfigPath, 'w', encoding='utf-8') as outfile:
            json.dump(dict_, outfile, ensure_ascii=False)
        msg = "Write config succeed to {0}".format(exportConfigPath)
        return {'msg': msg, 'result': 1}
    except Exception as e:
        errMsg = "Write config fail: {0}".format(str(e))
        return {'msg': errMsg, 'result': 0}

def install_sshpass():
    try:
        # subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'sshpass'], check=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("sshpass succ")
    except subprocess.CalledProcessError as e:
        print("Fail: {}".format(e))

def main(projName, tblName, path_, projID, pro_col_en, pro_col_cht):
    global _logger, sc, hiveLibs, sqlContext, NAME,updateAppStatus_, updateTProjectStatus_
    NAME = 'export'
    _logger = _getLogger(NAME)
    privacy_type = projName.split('_')[-1]
    # log input
    _logger.debug('spark_export_dbName:%s', projName)
    _logger.debug('spark_export_projName:%s', projName)
    _logger.debug('spark_export_tblInfo:%s', tblName)
    _logger.debug('spark_import_privacy_type_%s',privacy_type)

    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName) or projName.isdigit():
        _logger.debug("Invalid projName format: projName can only contain letters, numbers, and underscores, cannot be all numbers, and cannot start with a number")
        sys.exit(1)
    if not projID.isdigit():
        _logger.debug("Invalid projID format: projID must be an integer")
        sys.exit(1)
    if not re.match("^[a-zA-Z0-9_]+$", str(tblName)):
        _logger.debug("Invalid tblName format")
        return 'Fail'
    if not re.match("^[a-zA-Z0-9_ /]+$", str(path_)):
        _logger.debug("Invalid path_ format")
        return 'Fail'

    sc, hiveLibs, sqlContext = initSparkContext(NAME)

    # return information
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)

    if str(privacy_type) == 'syn':
        sqldbName = 'SynService'
    elif str(privacy_type) == 'dp':
        sqldbName = 'DpService'
    else:
        sqldbName = 'DeIdService'
    ###202000319, move here##############
    project_id = projID
    try:
        updateTProjectStatus_ = updateTProjectStatus(project_id)
    except Exception as e:        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False     
    
    
    ###20200317, add for checking app status(write to mysql)##############
    try:
        #20200211 add 
        #appID, appName projID,projName
        updateAppStatus_ = updateAppStatus(sc.applicationId, NAME,projName,projID)
    except Exception as e:
        print('updateAppStatus error: %s', str(e))
        return False
    #1 app status
    #updateToMysql(self,appState, progress,progress_state="Running")
    updateAppStatus_.updateToMysql("Init_1","5") #5%
    ###################################################
    # _logger.debug('tables = {} '.format(tables))
    #len_c = len(tables.split(';'))
    len_c = 1 #len(tables)
    #i=1
    #def __init__(self, lower, upper, div_in_loop, looop_round):
    updateAppProgress_ = updateAppProgress(10,80,4, len_c)

    # use database
    sqlContext.sql('use ' + projName)
    _logger.debug('use ' + projName)


    progress_str = updateAppProgress_.getLoopProgress(1)#getLoopProgress(len_c, 10, i)
    #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
    updateAppStatus_.updateToMysql("Export_data",progress_str)
    try:
        getAction = """
        SELECT * FROM {}.{}
        """.format(projName, tblName)
        _logger.debug(getAction)     #{}.{} LIMIT 10".format(table_name,table_name))
        df = sqlContext.sql(getAction)
    except Exception as e:

        _logger.debug('errTable: Select * from {projName}.{tblName} error: ' + str(e))
        updateAppStatus_.updateToMysql('errTable: Select * from',progress_str,"err")
        updateTProjectStatus_.updateToMysql(sqldbName, project_id, 97, u"概化錯誤")
        return

    progress_str = updateAppProgress_.getLoopProgress(2)#getLoopProgress(len_c, 10, i)
    #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
    updateAppStatus_.updateToMysql("get header",progress_str)
    # get header
    try:
        pro_col_en_l = pro_col_en.split(',') #['c_6119_0','c_6119_1','c_6119_2','c_6119_3','c_6119_4','c_6119_5','c_6119_6']
        _logger.debug(pro_col_en_l)
        pro_col_cht_l = pro_col_cht.split(',')  # b = ['age_moi_personal_info_sys_gen_0628','fnlwgt_moi_personal_info_sys_gen_0628','race_moi_personal_info_sys_gen_0628','sex_moi_personal_info_sys_gen_0628','marital_status_mof_personal_financial_sys_gen_0628','hours_per_week_mof_personal_financial_sys_gen_0628','income_mof_personal_financial_sys_gen_0628']
        _logger.debug(pro_col_cht_l)
        colCompare = {key: value for key, value in zip(pro_col_en_l, pro_col_cht_l)}
        _logger.debug(colCompare)
        # colCompare = tblInfo[tblName]["colCompare"]
        headers_en = df.columns
        _logger.debug(headers_en)
        headers_ch = [colCompare[col] for col in headers_en]
        _logger.debug(headers_ch)
        #df = df.toDF(*headers_ch).columns
    except Exception as e:
        _logger.debug('errTable: get header error: ' + str(e))
        updateAppStatus_.updateToMysql('errTable: get header error',progress_str,"err")
        updateTProjectStatus_.updateToMysql(sqldbName, project_id,97, u"概化錯誤")
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
            updateTProjectStatus_.updateToMysql(sqldbName, project_id, 97, u"概化錯誤")
            return
        else:
            _logger.debug("Export data succeed: {0}".format(tblName))
            _logger.debug(result['msg'])


    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        updateAppStatus_.updateToMysql(s,progress_str,"err")
        updateTProjectStatus_.updateToMysql(sqldbName, project_id, 97, u"概化錯誤")

    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug('errTable: export csv error')
        updateAppStatus_.updateToMysql('errTable: export csv error',progress_str,"err")
        updateTProjectStatus_.updateToMysql(sqldbName, project_id, 97, u"概化錯誤")
        return
    progress_str = updateAppProgress_.getLoopProgress(4)#getLoopProgress(len_c, 10, i)
    #print("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
    updateAppStatus_.updateToMysql("Export_config",progress_str)

    privacy_type = projName.split("_")[-1]
    p_name = projName[:projName.rfind('_{}'.format(privacy_type))]#projName.rsplit("_",1)[0]
    _logger.debug( '$$$$$$$$$p_name ', p_name)
    privacy_type = shlex.quote(privacy_type)
    p_name = shlex.quote(p_name)

    file_ = '/home/hadoop/proj_/longTaskDir/Hadoop_information.txt'
    config = configparser.ConfigParser()
    config.read(file_)
    syn_path = config.get('Hadoop_information', 'syn_path')
    dp_path = config.get('Hadoop_information', 'dp_path')
    passwd = config.get('Hadoop_information', 'passwd')
    user = config.get('Hadoop_information', 'user')
    ip = config.get('Hadoop_information', 'ip')
    syn_path = shlex.quote(syn_path)
    dp_path = shlex.quote(dp_path)
    passwd = shlex.quote(passwd)
    user = shlex.quote(user)
    ip = shlex.quote(ip)

    if privacy_type == "syn":
        folderForSynthetic = syn_path
    elif privacy_type == "dp":
        folderForSynthetic =dp_path

    projName_quote = shlex.quote(projName)
    tblName_quote = shlex.quote(tblName)
    path__quote = shlex.quote(path_)
    g_path = path__quote +"/"+ projName_quote +"/"+ tblName_quote+".csv"
    _logger.debug("g_path")
    _logger.debug(g_path)
    g_path = shlex.quote(g_path)
    p_name = shlex.quote(p_name)
    folderForSynthetic = shlex.quote(folderForSynthetic)
    folderForSynthetic_dir = os.path.join(folderForSynthetic, p_name, '')

    folderForSynthetic_dir = shlex.quote(folderForSynthetic_dir)
    folderForSynthetic_input_dir = os.path.join(folderForSynthetic_dir, 'inputRawdata', '')

    folderForSynthetic_input_dir = shlex.quote(folderForSynthetic_input_dir)
    synfile_path_file = os.path.join(folderForSynthetic_input_dir, 'df_preview.csv')

    synfile_path_file = shlex.quote(synfile_path_file)
    _logger.debug("synfile_path_file")
    _logger.debug(synfile_path_file)


    # 對變量進行 shlex.quote 處理
    g_path = shlex.quote(g_path)
    user = shlex.quote(user)
    ip = shlex.quote(ip)
    synfile_path_file = shlex.quote(synfile_path_file)

    cmd = [
        'sshpass', '-p', shlex.quote(passwd),
        'ssh', '-o', 'StrictHostKeyChecking=no', '-P', '22',
        f'{user}@{ip}',
        'sudo', 'chown', '-R', f'{user}:{user}',
        f'{folderForSynthetic_input_dir}'
    ]

    # 將 cmd 列表格式化為字符串
    cmd_str = ' '.join(cmd)
    # 使用 logger.info 打印命令
    _logger.info('Executing command: %s', cmd_str)
    #runcode = os.system(cmd)
    result = subprocess.run(cmd, check=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    # 構建命令
    cmd = [
        'sshpass', '-p', passwd,
        'scp', '-o', 'StrictHostKeyChecking=no', '-P', '22', g_path,
        user + '@' + ip + ':' + synfile_path_file
    ]
    # 將 cmd 列表格式化為字符串
    cmd_str = ' '.join(cmd)
    # 使用 logger.info 打印命令
    _logger.info('Executing command: %s', cmd_str)
    try:
        result = subprocess.run(cmd, check=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _logger.debug('Command output: %s', result.stdout)
    except subprocess.CalledProcessError as e:
        _logger.error('Command failed with exit code %d and error: %s', e.returncode, e.stderr)
    except Exception as e:
        _logger.error('Unexpected error: %s', str(e))
    _logger.debug('run finished!')



    #updateTProjectStatus  
    project_status =43
    statusname='完成隱私強化前概化匯出'
    updateTProjectStatus_.updateToMysql(sqldbName, project_id, project_status,statusname)
    
    
    _logger.debug('finish the process in update mysql')




    updateAppStatus_.updateToMysql("All_table_export_succeed","100","Finished")
    # _logger.debug("All dataset export data succeed: {0}".format(','.join(tables)))

if __name__ == "__main__":

    projName = sys.argv[1]  # str
    projName = shlex.quote(projName)
    tblName = sys.argv[2]  # str
    tblName = shlex.quote(tblName)
    path_ = sys.argv[3]  # local path
    path_ = shlex.quote(path_)
    projID = sys.argv[4]
    pro_col_en = sys.argv[5]
    pro_col_cht = sys.argv[6]

    print('########')
    print(projName)
    print(tblName)
    print(path_)
    print('#############')

    main(projName, tblName, path_, projID, pro_col_en, pro_col_cht)
