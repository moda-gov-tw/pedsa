#!/usr/bin/python
# -*- coding: utf-8 -*-

from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from pyspark import SparkContext,SparkConf
from pyspark.sql import SparkSession
import sys
import json
import base64

def getJoinCond( df1, df2, key1, key2 ):
    cond = []
    L = len(key1)
    try:
        for i in range(0,L):
            cond.append( df1[key1[i]]==df2[key2[i]] )
        return cond
    except Exception as err:
        _logger.debug('getJoinCond error! - %s:%s' %(type(err).__name__, err))
        return None

def getHiveData(dbName, tblName,cols):
    sqlContext.sql('use ' + dbName)
    tmpColsStr = ''
    for col_name_ in cols:
        tmpColsStr = tmpColsStr + col_name_
        if col_name_ != cols[len(cols)-1] and col_name_ !='*':
            tmpColsStr = tmpColsStr + ','        
    query_str = 'SELECT {} FROM {}'.format(tmpColsStr, tblName)
    _vlogger.debug('getHiveData_'+query_str)

    df = sqlContext.sql(query_str)
    return df

def changeDFheader( df, changeKey ):
    newColNames = []
    origColNames = df.columns
    for origCol in origColNames:
        newColNames.append(changeKey+origCol)
    mapping = dict(zip( origColNames, newColNames ))
    newColDF = df.select([col(col).alias(mapping.get(col,col)) for col in origColNames])
    return newColDF

def initSparkContext(name):
    appName = name
    #master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()

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

    return sc_,hiveLibs, sqlContext

def registerTempTable_forsparksql(data_frame_, tb_name_):
    data_frame_.registerTempTable(tb_name_)
    return tb_name_

def main():
    global _logger, _vlogger, sc, hiveLibs, sqlContext
    # debug log
    _logger = _getLogger('spark__getJoinData')
    # verify log
    _vlogger = _getLogger('verify__getJoinData')

    _vlogger.debug('projName_'+str(projName))
    _vlogger.debug('jobName_'+str(jobName))

    # spark setting
    appName = 'join'
    sc, hiveLibs, sqlContext = initSparkContext(appName)

    try:
        _vlogger.debug('input : %s' %(data_))
        data = json.loads(base64.b64decode(data_).decode("utf-8"))
        _vlogger.debug('decode inpute : %s' %(data))
        #data = ast.literal_eval(data_)
    except Exception as err:
        errMsg = 'decode error! - %s:%s' %(type(err).__name__, err)
        _logger.debug('errTable:' + errMsg)
        return None

    # get dataInfo,joinType and publicTableName 
    try:
        dataInfo = data['dataInfo'] #type(dataInfo):list
        joinType = data['joinType']
        publicTableName = data['publicTableName']
    except Exception as err:
        errMsg = 'get parameter error! - %s:%s' %(type(err).__name__, err)
        _logger.debug('errTable:' + errMsg)
        return None    
    
    # read data  
    tblNames = []
    j = 1
    for i in dataInfo:
        db = i['dbName']
        tbl = i['tableName']
        cols = i['colNames']
        keys = i['keyNames']
        tblNames.append(tbl)
        
        _vlogger.debug('dbName_'+ str(db))
        _vlogger.debug('tblName_'+ str(tbl))
        _vlogger.debug('cols_'+ str(cols))

        try:
            # t_0 is public table and others will be t_1, t_2,...  
            if tbl == publicTableName:
                _vlogger.debug('publicTable')
                # read from Hive
                t_0 = getHiveData(db,tbl,cols)
                key_0 = keys
                #t_0 = changeDFheader(df_0,'pub_')
            else :
                _vlogger.debug('not publicTable')
                globals()['t_{}'.format(j)] = getHiveData(db,tbl,cols)
                globals()['key_{}'.format(j)] = keys
                j = j+1
        except Exception as err:
            errMsg = 'read data error! - %s:%s' %(type(err).__name__, err)
            _logger.debug('errTable:' + errMsg)
            return None

    # Set output table name
    mergeTblNames = ''
    for tblName in tblNames:        
        if tblName == tblNames[-1]:
            mergeTblNames = mergeTblNames+tblName
        else:
            mergeTblNames = mergeTblNames+tblName+'_'
        
    if joinType == 'inner':
        process = '_ijT_'
    elif joinType == 'outer' or joinType == 'full':
        process = '_fjT_'
    elif joinType == 'left_outer' or joinType == 'left':
        process = '_ljT_'
    elif joinType == 'right_outer' or joinType == 'right':
        process = '_rjT_'
    else : 
        process = '_jT_'

    registTblName = jobName + process + mergeTblNames
    _vlogger.debug('registTblName_'+registTblName)
    _vlogger.debug("sc.applicationId:" + sc.applicationId)

    # join data 
    try:
        # join DF init
        cond = getJoinCond( t_0, t_1, key_0, key_1 )
        joinDF = t_0.join( t_1, cond, joinType )
        _vlogger.debug(joinType +' on - '+ str(cond))
        # if number of join data more than 2 will keep join
        if len(dataInfo) > 2 :
            for i in range( 2, len(dataInfo) ):
                cond = getJoinCond( t_0, globals()['t_%d' %(i)], key_0, globals()['key_%d' %(i)] )
                joinDF = joinDF.join( globals()['t_%d' %(i)], cond, joinType )
                _vlogger.debug(joinType +' on - '+ str(cond))
    except Exception as err:
            errMsg = 'join data error! - %s:%s' %(type(err).__name__, err)
            _logger.debug('errTable:' + errMsg)
            return None
    
    try:
        #write table to hive  
        _vlogger.debug('write table : '+registTblName+' to hive')
        joinDF.write.format('orc').mode('overwrite').saveAsTable( registTblName )
    except Exception as err:
        errMsg = 'write table to Hive error! - %s:%s' %(type(err).__name__, err)
        _logger.debug('errTable:' + errMsg)
        return None
    
    _vlogger.debug(projName+'_'+jobName+'- Get tables '+mergeTblNames+' do '+joinType+' join.')
    #print joinDF.show(5)

if __name__ == '__main__':

    data_ = sys.argv[1]
    projName = sys.argv[2]
    jobName = sys.argv[3]

    print('########')
    print(data_)
    print(projName)
    print(jobName)
    print('#############')
    
    main()