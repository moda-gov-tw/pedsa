#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import gmtime, strftime
import os, sys
from pyspark import SparkConf, SparkContext, StorageLevel
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.connect_sql import ConnectSQL
from MyLib.parseData import doCommand


def initSparkContext(name):
    appName = name
    # master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://master.bdp.com:10000")

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


def checkValueExist(conn_, db_, tbl_, conditionDict):

    conditions = [str(col) + "='" + str(conditionDict[col]) + "'" for col in conditionDict]
    conditions = ' AND '.join(conditions)

    sqlCommand = """
    select * from {0}.{1}
    WHERE {2}
    """.format(db_, tbl_, conditions)

    sqlResult = conn_.doSqlCommand(sqlCommand)
    _logger.debug(sqlCommand)

    if sqlResult['result'] == 0:
        _logger.debug('errTable: Check value exists {0}.{1} fail: {2}'.format(db_, tbl_, sqlResult['msg']))
    elif sqlResult['result'] == 1 and len(sqlResult['fetchall']) > 0 :
        return True
    else:
        return False

def updateValueMysql(conn_, db_, tbl_, conditionDict, setValueDict):
    # Insert or Update
    try:
        tableListResult = checkValueExist(conn_, db_, tbl_, conditionDict)

        if tableListResult:
            # Update
            updateResult = conn_.updateValue(db_, tbl_, conditionDict, setValueDict)
            if updateResult['result'] == 1:
                _logger.debug('Update to {0}.{1} succeed: {2}'.format(db_, tbl_, updateResult['msg']))
                return True
            else:
                _logger.debug('errTable: Update to {0}.{1} fail: {2}'.format(db_, tbl_, updateResult['msg']))
                return False
        else:
            # Insert
            insertResult = conn_.insertValue(db_, tbl_, setValueDict, True)
            if insertResult['result'] == 1:
                _logger.debug('Insert to {0}.{1} succeed: {2}'.format(db_, tbl_, insertResult['msg']))
                return True
            else:
                _logger.debug('errTable: Insert to {0}.{1} fail: {2}'.format(db_, tbl_, insertResult['msg']))
                return False
    except Exception as e:
        _logger.debug('errTable: Insert or Update mysql fail.')
        _logger.debug('errTable: {0}'.format(str(e)))
        return False


def main():
    global _logger, sc, hiveLibs, sqlContext, NAME
    PATH = "/root/data/input_auto_upload"
    NAME = 'createProject'
    _logger = _getLogger(NAME)


    # Log input
    dbNameTime = '{0}_{1}_{2}'.format(dbName, user, strftime("%Y%m%d%H%M%S", gmtime()))
    _logger.debug('spark user name: %s', user)
    _logger.debug('spark dbName: %s', dbNameTime)


    # Spark setting
    sc, hiveLibs, sqlContext = initSparkContext(NAME)

    # Return information
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)

    # Use database & get table list
    sqlContext.sql('USE originaldb')
    _logger.debug('USE originaldb')
    #tableList = sqlContext.sql("show tables in originaldb").collect()
    tableList = sqlContext.tables("originaldb").filter("tableName like '{0}_{1}%'".format(user, dbName)).collect()
    tableList = [tbl[1] for tbl in tableList]

    # Create database
    createDbSql = "CREATE DATABASE IF NOT EXISTS {0}".format(dbNameTime)
    _logger.debug(createDbSql)
    try:
        sqlContext.sql(createDbSql)
        #sqlContext.sql('USE ' + dbNameTime)
    except Exception as e:
        _logger.debug('errTable: Use HIVE database error: {0}'.format(str(e)))

    # Read raw table & save as new table to new database
    tableValidList = list() # Name of originalDB
    failTblList = list() # Name of originalDB
    succeedTblDict = dict() # Key: Name in originalDB; Value: raw table name
    for tbl in tableList:
        _logger.debug(tbl)
        if (user in tbl) and (dbName in tbl):
            user_, rawTblName = tbl.split('_' + dbName + '_')
            tableValidList.append(tbl)

            try:
                # Select table
                selectTblSql = "SELECT * FROM {0}".format(tbl)
                _logger.debug(selectTblSql)
                df = sqlContext.sql(selectTblSql)

                # Save table to new database
                df.write.format("orc").mode("overwrite").saveAsTable(rawTblName)
                df.unpersist

                _logger.debug('Table save succeed: ' + rawTblName)
                succeedTblDict[tbl] = rawTblName

            except Exception as e:
                _logger.debug('Table save fail: {0}. Error: {1}'.format(tbl, str(e)))
                failTblList.append(tbl)
                return

    # Check if there are fail table
    if len(failTblList) > 0:
        msg = """
        errTable:
        Save tables should be: {0}
        Succeed tables were: {1}
        Fail tables were: {2}
        """.format(','.join(tableValidList), ','.join(succeedTblDict.keys()), ','.join(failTblList))
        _logger.debug(msg)
        return
    else:
        _logger.debug('All tables save succeed: {0}'.format(','.join(tableValidList)))


    # Connect mysql
    try:
        conn = ConnectSQL()
    except Exception as e:
        _logger.debug('errTable: Connect mysql error: {0}'.format(str(e)))
        return

    for tbl in succeedTblDict:

        # Get value from T_originTable', tbl)
        sqlCommand = """
        SELECT tableCount, sample, col_en, col_cht
        FROM {0}.{1}
        WHERE tableName='{2}'
        """.format('DeIdService', 'T_originTable', tbl)
        selectResult = conn.doSqlCommand(sqlCommand)
        if selectResult['result'] == 0:
            _logger.debug('errTable: Select value from T_originTable error: {0}'.format(selectResult['msg']))
            _logger.debug('errTable: Can not find {0} in T_originTable'.format(tbl))
            return

        else:
            # Insert or update value to sample data
            condisionSampleData = {
                'project_id': projID,
                'dbname': dbNameTime,
                'tbname': succeedTblDict[tbl]}

            valueSampleData = {
                'project_id': projID,
                'dbname': dbNameTime,
                'tbname': succeedTblDict[tbl],
                'data': selectResult['msg'][0]['sample']}

            result = updateValueMysql(conn, 'DeIdService', 'T_ProjectSampleData', condisionSampleData, valueSampleData)
            if not result:
                return


            # Insert or update value to sample table
            condisionSampleTable = {
                'project_id': projID,
                'pro_db': dbNameTime,
                'pro_tb': succeedTblDict[tbl]}

            valueSampleTable = {
                'project_id': projID,
                'pro_db': dbNameTime,
                'pro_tb': succeedTblDict[tbl],
                'pro_col_en': selectResult['msg'][0]['col_en'],
                'pro_col_cht': selectResult['msg'][0]['col_cht'],
                'pro_path': PATH,
                'tableCount': selectResult['msg'][0]['tableCount']}
            result = updateValueMysql(conn, 'DeIdService', 'T_Project_SampleTable', condisionSampleTable, valueSampleTable)
            if not result:
                return

            # Delete value
            sqlCommand = """
            DELETE FROM {0}.{1}
            WHERE tableName='{2}'
            """.format('DeIdService', 'T_originTable', tbl)
            result = conn.doSqlCommand(sqlCommand)
            if result['result'] == 0:
                _logger.debug('errTable: Delete value from T_originTable error: {0}'.format(result['msg']))
                return

            # Drop table
            try:
                dropTblSql = "drop table {0}.{1}".format("originaldb", tbl)
                sqlContext.sql(dropTblSql)
            except Exception as e:
                _logger.debug('Drop table {0} fail. Error: {1}'.format(tbl, str(e)))
                failTblList.append(tbl)
                return

    # Delete folder
    try:
        path = os.path.join(PATH, user, dbName)
        result = doCommand(["rm", "-f", "-r", path])
        if len(result) > 0:
            _logger.debug('errTable: Delete folder {0} error: {1}'.format(path, result))
            return

        _logger.debug('Create project succeed.')

    except Exception as e:
        _logger.debug('errTable: Delete folder error: {0}'.format(str(e)))
        return


if __name__ == "__main__":
    projID = sys.argv[1]  # str
    user = sys.argv[2]  # str
    dbName = sys.argv[3]  # str
    print('########')
    print(projID)
    print(user)
    print(dbName)
    print('#############')
    main()
