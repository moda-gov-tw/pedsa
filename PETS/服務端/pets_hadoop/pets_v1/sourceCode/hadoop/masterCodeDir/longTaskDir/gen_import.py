#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
                                                                  #0921 加上
from MyLib.parseData import gen_importData, checkListQuotes_1side,importData
import os, sys, re
import base64
import pandas as pd
from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress


import shlex
from MyLib.updateTProjectStatus_gen import updateTProjectStatus



def initSparkContext(name):
    appName = name
    #master_ = 'yarn-client' #yarn
    master_ = 'yarn'
    _logger.debug("0108 master_=:"+master_)
    try:
        #spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        
        #warehouse_location = "hdfs://nodemaster:9000/user/hive/warehouse"
        warehouse_location = "hdfs://nodemasterSJOIN:9000/user/hive/warehouse"
        #warehouse_location = "hdfs:///user/hive/warehouse"

        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName) \
                     .config("spark.sql.warehouse.dir", warehouse_location) \
                                     .getOrCreate()
        sc_ = spark_.sparkContext
        #sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")
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
        _logger.debug("errTable:fundation_getGenNumLevel:"+str(e))
        _logger.debug("errTable:errSC")
        return SparkContext(conf=SparkConf())

    return sc_,hiveLibs, sqlContext, spark_


def parseCSV(body,headers):

    try:
        # step 1, get header (no need in hdfs)
        colnames = headers

        _logger.debug(colnames)
        #body = rdd.filter(lambda r: r!=header)

        # prepare for step 2
        def parseRow(row):
            #if '^' in row:
            if ',' in row:
                row_list = row.split(',')
                #row_list = row.split('^')
                row_tuple = tuple(row_list)
                return row_tuple
            else:
                row_list = row.split(',')
                row_tuple = tuple(row_list)
                return row_tuple

        # step2, split each row by '^'
        rdd_parsed = body.map(parseRow)


        # step 3, split header by ','
        #colnames = header.split(',')
        return rdd_parsed.toDF(colnames)
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_convert_rdd_to_dataFrame_error:'+str(e))
        return None


def randomSample(df, nRows=5):
    '''
    input: pyspark.dataframe
    return: list of dicts
    '''
    try:
       #sample_ = df.sample(False,0.2).limit(nRows).toPandas().to_dict('records')
       sample_ = df.sample(False,0.2).limit(nRows).toPandas()
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_sample_data_fail: '+str(e))
        return None

    return sample_

def checkFormatBeforeImport(tables):
    try:
        for tblName in tables.split(';'):
            # Check if file exist
            pathData = str(os.path.join(path_, projName, tblName)) + '.csv'
            _logger.debug("___________________:"+str(pathData))
            fileExists = os.path.isfile(pathData)
            if not fileExists:
                userDataPath = pathData.replace("/home/hadoop/proj_", "citc/sourceCode/hadoop")
                msg = 'errTable: File is not exist in {0}'.format(userDataPath)
                raise msg

            # Check double quotes of each column
            headerValues = pd.read_csv(pathData, index_col=0, nrows=0, sep=',').columns.tolist()
            checkListQuotes_1side(headerValues, tblName)
        return True

    except Exception as e:
        msg = 'errTable: error in checkFormatBeforeImport: {0}'.format(str(e))
        _logger.debug(msg)
        return False

#updateToMysql(projID, projName, tblName, sampleStr)
def updateToMysql(dbName, projID, projName, table, data, userId):
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False
    # insert to sample data
    condisionSampleData = {
        'project_id': projID,
        'dbname': projName,
        'tbname': table
    }

    valueSampleData = {
        'project_id': projID,
        'dbname': projName,
        'tbname': table,
        'data': data,
        'createMember_Id':userId,
        'updateMember_Id':userId
    }
    # def updateValue(self, dbName, tblName, conditions, setColsValue):
    resultSampleData = conn.updateValueMysql(dbName,
                                             'T_ProjectSampleData',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        _logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
    else:
        msg = resultSampleData['msg']
        _logger.debug('insertSampleDataToMysql fail: ' + msg)


    # projName = sys.argv[1] #str #projName = dbName
    # projID = sys.argv[2] #str #projName = dbName
    # base64_ = sys.argv[3] #str
    # path_ = sys.argv[4]  # str
    # userAccount = sys.argv[5]  # str
    # userId = sys.argv[6]  # str    
    # privacy_type = sys.argv[7]

#updateToMysql(projID, projName, tblName, sampleStr)
def updateToMysql_sampletable(dbName, projID, projName, table, tmp_header_en_path, tmp_header_ch_path,tmp_data_path,tblCount,tblName):
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False
    # insert to sample data
    condisionSampleTable = {
        'project_id': projID,
        'pro_db': projName,
        # 'pro_tb': table
    }
    valueSampleTable = {
                'project_id': projID,
                'pro_db':  projName,
                'pro_tb': table,
                'pro_col_en': tmp_header_en_path,
                'pro_col_cht': tmp_header_ch_path,
                'pro_path': tmp_data_path,
                'tableCount': tblCount,
                'finaltblName': tblName
            }

    resultSampleTable = conn.updateValueMysql(dbName,
                                            'T_Project_SampleTable',
                                            condisionSampleTable,
                                            valueSampleTable)

    if resultSampleTable['result'] == 1:
        _logger.debug("Update mysql succeed. {0}".format(resultSampleTable['msg']))
    else:
        msg = resultSampleTable['msg']
        _logger.debug('insertSampleTableToMysql fail: ' + msg)

#20191212 add
def getLoopProgress(loop_count, default_value, increas_):
    progress_v = int(default_value/loop_count)
    progress_v = progress_v*increas_
    progress_value = str(progress_v)+"%"
    return progress_value


def main(projName,projID,base64_,path_,userAccount,userId,privacy_type,select_cols_b64):

    global _logger, sc, hiveLibs, sqlContext, NAME, spark_, updateAppStatus_,updateTProjectStatus_
    NAME = 'import'
    _logger=_getLogger(NAME)
    _logger.debug(base64_)
    try:
        tables = base64.b64decode(base64_).decode("utf-8") #str
        select_cols = base64.b64decode(select_cols_b64).decode("utf-8").split(',')
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_'+str(e))
        _logger.debug('errTable:'+NAME+'_decode_base64_error')
        return
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_userId_%s',userId)
    _logger.debug('spark_import_privacy_type_%s',privacy_type)
    _logger.debug('spark_import_-----------------')
    # log input
    # _logger.debug('spark_import_dbName_%s',projName)
    # _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_projID_%s',projID)
    _logger.debug('spark_import_tables_%s',tables)
    _logger.debug('spark_import_select_cols_%s',select_cols)

    # _logger.debug('spark_import_dbName_%s',projName)
    # _logger.debug('spark_import_projName_%s',projName)
    # _logger.debug('spark_import_projID_%s',projID)
    # _logger.debug('spark_import_tables_%s',tables)
    # _logger.debug('spark_import_select_cols_%s',select_cols)
    # 20221217
    #userAccount = "deidadmin"
    #userId = "3"
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_userId_%s',userId)

    if str(privacy_type) == 'syn':
        sqldbName = 'SynService'
    elif str(privacy_type) == 'dp':
        sqldbName = 'DpService'
    else:
        sqldbName = 'DeIdService'

    _logger.debug('---------------------------------------')

    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName) or projName.isdigit():
        _logger.debug("Invalid projName format: projName can only contain letters, numbers, and underscores, cannot be all numbers, and cannot start with a number")
        sys.exit(1)
    if not projID.isdigit():
        _logger.debug("Invalid projID format: projID must be an integer")
        sys.exit(1)

    if not re.match("^[a-zA-Z0-9_ /]+$", str(path_)):
        _logger.debug("Invalid path_ format")
        return 'Fail'
    # 定義Base64正則表達式
    # Base64 字符集包括 A-Z, a-z, 0-9, +, / 和可能的結尾 = 符號
    base64_pattern = r'^[A-Za-z0-9+/]+={0,2}$'
    if not re.match(base64_pattern, str(base64_)):
        _logger.debug("Invalid base64_ format")
        return 'Fail'
    if not re.match(base64_pattern, str(select_cols_b64)):
        _logger.debug("Invalid select_cols_b64 format")
        return 'Fail'

    if not userId.isdigit():
        _logger.debug("Invalid userID format: userID must be an integer")
        sys.exit(1)

    if not re.match("^[a-zA-Z0-9_]+$", str(userAccount)):
        _logger.debug("Invalid userAccount format")
        return 'Fail'
    if not re.match("^[a-zA-Z0-9_]+$", str(privacy_type)):
        _logger.debug("Invalid privacy_type format")
        return 'Fail'


    # Check if project exists
    projPath = str(os.path.join(path_, projName))
    if os.path.exists(projPath):
        _logger.debug("project path: " + projPath)
    else:
        _logger.debug('errTable:'+NAME+'_projName_does_not_exist: '+projName)

    # Start spark job
    sc, hiveLibs, sqlContext, spark_ = initSparkContext(NAME)

    # Check format before import
    if not checkFormatBeforeImport(tables):
        return

    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)
    
    
    ###################################################  
    ###202000318, add for checking app status(write to mysql)##############
    ###202000319, move here##############
    project_id = projID
    try:
     
        updateTProjectStatus_ = updateTProjectStatus(project_id, userId)
    except Exception as e:
        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False    
    
    ###20191210, add for checking app status(write to mysql)##############
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
    ####################################################################
    len_c = len(tables.split(';'))
    #i=1
    #def __init__(self, lower, upper, div_in_loop, looop_round):
    updateAppProgress_ = updateAppProgress(10,70,4, len_c)
    for tblName in tables.split(';'):

        try:
            projName = shlex.quote(projName)
            tblName = shlex.quote(tblName)
            path_ = shlex.quote(path_)
            pathData = 'file://' + str(os.path.join(path_, projName, tblName)) + '.csv'

            create_sql = "create database if not exists {}".format(projName)
            _logger.debug(create_sql)
            sqlContext.sql(create_sql)

            sqlContext.sql('use ' + projName)
            _logger.debug('use ' + projName)

            # return information
            _logger.debug('##################import table name')
            _logger.debug(tables) #mac_adult_id;mac_adult_id_B;mac_adult_id_A

            #2 app status
            #progress_v = int(10/len_c)
            #progress_v = progress_v*i
            #progress_value = str(progress_v)+"%"
            progress_str = 0
            progress_str = updateAppProgress_.getLoopProgress(1)#getLoopProgress(len_c, 10, i)
            
            updateAppStatus_.updateToMysql("Import_data",progress_str)
            _logger.debug("0~~~~~~~~~~~~~~~~~~~~~progress_str")
            _logger.debug(projName)
            _logger.debug(pathData)
            _logger.debug(tblName)

            ###################################################
            # Import data
            #0921 shlex.quote拿掉可以完成+importData可以順利向下
            projName = shlex.quote(projName)
            tblName = shlex.quote(tblName)
            result = gen_importData(projName, pathData, tblName, spark_,select_cols)

            #0921
            #result = importData(projName, pathData, tblName, spark_)
            if result['result'] == 0:
                _logger.debug("import data error.")
                _logger.debug('errTable:' + NAME + '_read_textFile_fail: ' + result['msg'])
                updateAppStatus_.updateToMysql('import data error',progress_str,"err")
                updateTProjectStatus_.updateToMysql(sqldbName,project_id, 97, u"概化錯誤")               
                
                return
            else:
                _logger.debug("import data succeed.")
                _logger.debug(result['msg'])

            inputData = result['df']
            header_ch = inputData.columns
            tmp_num = str(hash(projName))[1:3] + str(hash(tblName))[1:3]
            header_en = ['c_'+tmp_num+'_'+str(i) for i in range(len(header_ch))]
            inputData = inputData.toDF(*header_en)

            # Convert ch_col_name to en_col_name
            _logger.debug('spark_import_rawData_%s', pathData)
            _logger.debug('spark_import_header_en_%s', ','.join(header_en))
            _logger.debug('spark_import_header_ch_%s', ','.join(header_ch))
            _logger.debug('spark_import_table_%s', tblName)

        except Exception as e:
            if str(e).find('InvalidInputException') != -1:
                index_ = str(e).find('InvalidInputException')
                errMsg = str(e)[index_:].split('\n')[0]
                _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+errMsg)
                updateAppStatus_.updateToMysql(errMsg,progress_str,"err")
                updateTProjectStatus_.updateToMysql(sqldbName,project_id, 97, u"概化錯誤")
                return

            _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+str(e))
            updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(sqldbName,project_id, 97, u"概化錯誤")
            return

        #normalized NA
        df_filterFD = inputData.cache()
        #try:
        #    for col_name in header_en:
        #        df_filterFD = df_filterFD.replace(['\\N'],['NA'],col_name).replace(['na'],['NA'],col_name).replace([''],['NULL'],col_name)
        #    df_filterFD = df_filterFD.na.fill('NULL')
        #except Exception as e:
        #    _logger.debug('errTable:'+NAME+'_nomalized_na_fail: '+str(e))
        #    return
        
        #3 app status#######################################33
        progress_str = updateAppProgress_.getLoopProgress(2)
        #print("2~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("table_count",progress_str)
        #####################################################3
        #table count
        try:
            tblCount = df_filterFD.count()
            _logger.debug('tblCount_'+str(tblCount))
        except Exception as e:
            _logger.debug('errTable:'+NAME+'_table_count_fail: '+str(e))
            updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(sqldbName,project_id,97, u"概化錯誤")
            return


        #4 app status#######################################33
        progress_str = updateAppProgress_.getLoopProgress(3)
        #print("3~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("sample_data",progress_str)
        #####################################################3
        #sample
        try:
            sampleDf = randomSample(df_filterFD)
            _logger.debug(sampleDf)
            sampleDf.columns = header_ch
            sampleStr = '[' + ','.join([str(i) for i in sampleDf.to_dict('records')]) + ']'
            sampleStr = str(sampleStr).replace("\'", "\"")
            sampleStr = sampleStr.replace("\": \"", "\":\"")
            sampleStr = sampleStr.replace("\", \"", "\",\"")
            sampleStr = sampleStr.replace("None", "\"None\"")
            sampleStr = sampleStr.replace("\\\\N", "N")
            _logger.debug(sampleStr)
            if sampleStr is None:
                _logger.debug('sampleStr error')
                return
            else:
                updateToMysql(sqldbName, projID, projName, tblName, sampleStr,userId)
                _logger.debug('sampleStr_succeed.')
        except Exception as e:
            _logger.debug('errTable: Sample fail. {0}'.format(str(e)))
            updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(sqldbName,project_id, 97, u"概化錯誤")
            return
        try:

            #create database
            create_sql = "create database if not exists {}".format(projName)
            _logger.debug(create_sql)
            sqlContext.sql(create_sql)
            sqlContext.sql('use ' + projName)
            _logger.debug('use ' + projName)

            #5 app status#######################################33
            progress_str = updateAppProgress_.getLoopProgress(4)
            #print("4~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
            updateAppStatus_.updateToMysql("save table to HIVE",progress_str)
            #####################################################3        
            #tt= ttt+1
        except :
            _logger.debug('errTable: create database. {0}'.format(sys.exc_info()[0]))
            updateAppStatus_.updateToMysql("save table to HIVE",progress_str, "err")
            updateTProjectStatus_.updateToMysql(sqldbName,project_id, 97, u"概化錯誤")
            return    
        #save table to HIVE
        try:
            df_filterFD.write.format("orc").mode("overwrite").saveAsTable(tblName)
            df_filterFD.unpersist
            _logger.debug('table_save_succeed_' + tblName)
            #tp=tp+1

        except Py4JJavaError as e:
            s = e.java_exception.toString()
            _logger.debug(s)

        except Exception:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(sys.exc_info()[2])
            _logger.debug(len(sys.exc_info()))
            _logger.debug("errTable:"+NAME+"_save_hiveTbl")
            updateAppStatus_.updateToMysql("errTable:"+NAME+"_save_hiveTbl",progress_str,"err")
            
            #project_status =3 
            #statusname='去欄位屬性判定'
            updateTProjectStatus_.updateToMysql(sqldbName,project_id,97, u"概化錯誤")
            
            return
            #_logger.debug("error in kchecking : "+str(e))
        #i=i+1   
        try:
            tmp_header_en_path = ','.join(header_en)
            tmp_header_ch_path = ','.join(header_ch)
            tmp_data_path = pathData

            projNamesql = projName[:projName.rfind('_{}'.format(privacy_type))]
            
            updateToMysql_sampletable(sqldbName, projID, projNamesql , tblName, tmp_header_en_path, tmp_header_ch_path,tmp_data_path,str(tblCount),tblName)
        except Exception as e:
            _logger.debug('errTable: SampleTable fail. {0}'.format(str(e)))
            updateTProjectStatus_.updateToMysql(sqldbName,project_id, 97, u"概化錯誤")
            return
    _logger.debug('All_table_save_succeed.')
    
    
    ###################################################  
    ###202000318, add for checking app status(write to mysql)##############
    '''
    project_id = projID
    try:
        #appID, appName
        
        #updateAppStatus_ = updateAppStatus(sc.applicationId, NAME)
        updateTProjectStatus_ = updateTProjectStatus(project_id)
    except Exception as e:
        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False  
    '''      
    #updateTProjectStatus  
    project_status =41
    statusname=u'完成隱私強化前概化匯入'
    _logger.debug('================================')
    _logger.debug('spark_import_%s',sqldbName)
    _logger.debug('spark_import_%s',project_id)
    _logger.debug('spark_import_%s',project_status)
    _logger.debug('spark_import_%s',statusname)
    updateTProjectStatus_.updateToMysql(sqldbName,project_id, project_status,statusname)
    
    
    _logger.debug('finish the process in update mysql')
    ##################################################################################################  

    #6 app status#######################################33
    print("5~~~~~~~~~~~~~~~~~~~~~progress_str")
    updateAppStatus_.updateToMysql("All_table_save_succeed","100","Finished")
    #####################################################3  


if __name__ == "__main__":
    # command from celery:
    #'spark-submit --jars gen.jar longTaskDir/getGenTbl.py '+projName+' '+tblName
    projName = sys.argv[1] #str #projName = dbName
    projName = shlex.quote(projName)
    projID = sys.argv[2] #str #projName = dbName
    base64_ = sys.argv[3] #str
    path_ = sys.argv[4]  # str
    path_ = shlex.quote(path_)
    userAccount = sys.argv[5]  # str
    userId = sys.argv[6]  # str    
    privacy_type = sys.argv[7]
    select_cols_b64 = sys.argv[8]
    print('########')
    print(projName)
    print(projID)
    print(base64_)
    print(path_)
    print(userAccount)
    print(userId)  
    print(privacy_type) 
    print(select_cols_b64)
    print('#############')

    main(projName,projID,base64_,path_,userAccount,userId,privacy_type,select_cols_b64)
