#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.parseData import importData, checkListQuotes_1side
from MyLib.connect_sql import ConnectSQL
import os, sys
import base64
import json
import pandas as pd


def initSparkContext(name):
    appName = name
    master_ = 'yarn-client' #yarn
    #master_ = 'yarn'  # yarn
    try:
        spark_ = SparkSession\
            .builder\
            .enableHiveSupport()\
            .master(master_)\
            .appName(appName)\
            .getOrCreate()

        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        from os.path import abspath
        warehouse_location = abspath('spark-warehouse')
        sc_.setSystemProperty("spark.sql.warehouse.dir", warehouse_location)

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _logger.debug("sparkContext_succeed.")

    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable: "+str(e))
        _logger.debug("errTable: errSC")
        return SparkContext(conf=SparkConf())

    return sc_,hiveLibs, sqlContext, spark_

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


def checkTableList(conn, targetName):
    # Query user list
    db = 'DeIdService'
    tbl = 'T_originTable'
    sqlCommand = """
    select * from {}.{};
    """.format(db, tbl)
    sqlResult = conn.doSqlCommand(sqlCommand)
    tblList = [tbl["tableName"] for tbl in sqlResult["fetchall"]]

    result = dict()
    result["result"] = False

    if targetName in tblList:
        result["result"] = True
        return result
    else:
        #result["error"] = 'mysql fail: ' + result['msg']
        return result

def checkFormatBeforeImport(tables):
    try:
        for tblName in tables.split(';'):
            # Check if file exist
            pathData = str(os.path.join(path_, projName, tblName, tblName)) + '.csv'
            fileExists = os.path.isfile(pathData)
            if not fileExists:
                userDataPath = pathData.replace("/root", "citc/sourceCode/hadoop")
                msg = 'errTable: File is not exist in {0}'.format(userDataPath)
                raise msg

            # Check double quotes of each column
            headerValues = pd.read_csv(pathData, index_col=0, nrows=0, sep=',').columns.tolist()
            checkListQuotes_1side(headerValues, tblName)

    except Exception as e:
        msg = 'errTable: error in checkFormatBeforeImport: {0}'.format(str(e))
        raise msg


def main():

    global _logger, sc, hiveLibs, sqlContext, NAME, spark_
    NAME = 'importAuto'
    _logger=_getLogger(NAME)

    try:
        tables = base64.b64decode(base64_).decode("utf-8") #str
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_'+str(e))
        _logger.debug('errTable:'+NAME+'_decode_base64_error')
        return

    # log input
    _logger.debug('spark import project: {0}'.format(projName))
    _logger.debug('spark import tables: {0}'.format(tables))

    # spark setting
    try:
        _logger.debug('start init spark')
        sc, hiveLibs, sqlContext, spark_ = initSparkContext(NAME)
    except Exception as e:
        _logger.debug('error init spark: ' + str(e))

    # return information
    #itri, output k application id (does not change the code about_logger code)
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)

    try:
        sqlContext.sql('use originalDB')
        _logger.debug('use originalDB')
    except Exception as e:
        _logger.debug('errTable: Can not use originalDB')
        _logger.debug('errTable: {0}'.format(str(e)))

    # Check format before import
    checkFormatBeforeImport(tables)

    for tblName in tables.split(';'):

        imoprtHiveName = "{0}_{1}_{2}".format(user, projName,tblName)
        imoprtHiveName = imoprtHiveName.strip('.csv')

        try:
            # file information
            # local > hdfs > hive
            pathData = 'file://' + str(os.path.join(path_, user, projName, tblName))

            _logger.debug("pathData: {0}".format(pathData))
            result = importData(projName, pathData, tblName, spark_, user)

            if result['result'] == 0:
                _logger.debug("import data error.")
                _logger.debug(result['msg'])
            else:
                _logger.debug("import data succeed.")
                _logger.debug(result['msg'])

            inputData = result['df']

            # Convert ch_col_name to en_col_name
            header_ch = inputData.columns
            tmp_num = str(hash(projName))[1:3] + str(hash(tblName))[1:3]
            header_en = ['c_'+tmp_num+'_'+str(i) for i in range(len(header_ch))]
            inputData = inputData.toDF(*header_en)

            _logger.debug('spark_import_rawData_%s', pathData)
            _logger.debug('spark_import_header_en_%s', ','.join(header_en))
            _logger.debug('spark_import_header_ch_%s', ','.join(header_ch))
            _logger.debug('spark_import_table_%s', tblName)

        except Exception as e:
            if str(e).find('InvalidInputException') != -1:
                index_ = str(e).find('InvalidInputException')
                errMsg = str(e)[index_:].split('\n')[0]
                _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+errMsg)
                return

            _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+str(e))
            return

        #normalized NA
        df_filterFD = inputData.cache()
        inputData.unpersist()
        #try:
        #    for col_name in header_en:
        #        df_filterFD = df_filterFD.replace(['\\N'],['NA'],col_name).replace(['na'],['NA'],col_name).replace([''],['NULL'],col_name)
        #    df_filterFD = df_filterFD.na.fill('NULL')
        #except Exception as e:
        #    _logger.debug('errTable:'+NAME+'_nomalized_na_fail: '+str(e))
        #    return

        #table count
        try:
            tblCount = df_filterFD.count()
            _logger.debug('tblCount_'+str(tblCount))
        except Exception as e:
            _logger.debug('errTable:'+NAME+'_table_count_fail: '+str(e))
            return


        #sample
        try:
            sampleStr = randomSample(df_filterFD)
            sampleStr.columns = header_ch
            sampleStr = sampleStr.to_dict('records')
            sampleStr = str(sampleStr).replace("\'", "\"")
            sampleStr = sampleStr.replace("\": \"", "\":\"")
            sampleStr = sampleStr.replace("\", \"", "\",\"")
            sampleStr = sampleStr.replace("None", "\"None\"")
            if sampleStr is None:
                return
            else:
                _logger.debug('sampleStr')
                _logger.debug(sampleStr)
                _logger.debug('sampleStr_' + sampleStr)

        except Exception as e:
            _logger.debug('errTable: Sample fail. {0}'.format(str(e)))
            return

        # Connect mysql
        try:
            conn = ConnectSQL()
        except Exception as e:
            _logger.debug('Connect mysql error: %s', str(e))
            return

        # Insert or Update
        try:
            tableListResult = checkTableList(conn, imoprtHiveName)
            if tableListResult["result"]:
                # Update
                db = 'DeIdService'
                tbl = 'T_originTable'
                conditions = {
                    'tableName': imoprtHiveName
                }

                setColsValue = {
                    'tableCount': str(tblCount),
                    'sample': sampleStr,
                    'col_en': ','.join(header_en),
                    'col_cht': ','.join(header_ch),
                    'member': user,
                    'project': projName

                }
                updateResult = conn.updateValue(db, tbl, conditions, setColsValue)
                if updateResult['result'] == 1:
                    _logger.debug(updateResult['msg'])
                else:
                    _logger.debug('Insert {0} to T_originTable fail: {1}'.format(imoprtHiveName, updateResult['msg']))
                    return
            else:
                # Insert
                db = 'DeIdService'
                tbl = 'T_originTable'
                colsValue = {
                    'tableName': imoprtHiveName,
                    'tableCount': str(tblCount),
                    'sample': sampleStr,
                    'col_en': ','.join(header_en),
                    'col_cht': ','.join(header_ch),
                    'member': user,
                    'project': projName
                }
                insertResult = conn.insertValue(db, tbl, colsValue, True)
                if insertResult['result'] == 1:
                    _logger.debug(insertResult['msg'])
                else:
                    _logger.debug('Insert {0} to T_originTable fail: {1}'.format(imoprtHiveName, insertResult['msg']))
                    return
        except Exception as e:
            _logger.debug('errTable: Insert or Update mysql fail.')
            _logger.debug('errTable: {0}'.format(str(e)))
            return

        #save table to HIVE
        try:
            #sqlContext.sql('use originalDB')
            #_logger.debug(imoprtHiveName)
            df_filterFD.write.format("orc").mode("overwrite").saveAsTable(imoprtHiveName)
            _logger.debug('table_save_succeed_' + imoprtHiveName)

        except Py4JJavaError as e:
            s = e.java_exception.toString()
            _logger.debug(s)

        except Exception:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(sys.exc_info()[2])
            _logger.debug(len(sys.exc_info()))
            _logger.debug("errTable:"+NAME+"_save_hiveTbl")
            return
            #_logger.debug("error in kchecking : "+str(e))

    _logger.debug('All_table_save_succeed.')
    return


if __name__ == "__main__":
    # spark-submit /root/proj_/longTaskDir/importAuto.py /root/data/input/ user project importListEncode
    path_ = sys.argv[1]  # str
    user = sys.argv[2]  # str
    projName = sys.argv[3]  # str
    base64_ = sys.argv[4]  # str

    print('########')
    print(path_)
    print(user)
    print(projName)
    print(base64_)
    print('#############')

    main()
