#!/usr/bin/python
# -*- coding: utf-8 -*-

#import mylib.JsonSchema as JsonSchema
#import sys
#sys.path.append('/data2/itribd/anaconda2/lib/python2.7/site-packages')

from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import desc
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType
import pyspark.sql.functions as f
import sys
import ast
import base64
import json

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


def getHiveData(dbName, tblName, cols):
    sqlContext.sql('use ' + dbName)
    
    tmpColsStr = ''
    for col_name_ in cols:
        tmpColsStr = tmpColsStr + col_name_
        if col_name_ != cols[len(cols)-1] and col_name_ !='*':
            tmpColsStr = tmpColsStr + ','        
    query_str = 'SELECT %s FROM %s' %(tmpColsStr, tblName)
    
    _vlogger.debug('getHiveData_'+query_str)        
    df = sqlContext.sql(query_str)
    return df


def main():
    global _logger, _vlogger, sc, hiveLibs, sqlContext
    # debug log
    _logger = _getLogger('spark__getDistinctData')
    # verify log
    _vlogger = _getLogger('verify__getDistinctData')

    # spark setting
    appName = 'distinct'
    sc, hiveLibs, sqlContext = initSparkContext(appName)
        
    try:
        _vlogger.debug('input : %s' %(data_))
        data = json.loads(base64.b64decode(data_).decode("utf-8"))
        _vlogger.debug('decode inpute : %s' %(data))
        #data = ast.literal_eval(data_)
    except Exception as err:
        _logger.debug('decode error! - %s:%s' %(type(err).__name__, err))
        return None
    
    # get dbName, tableName, colNames and requestFnuction(0:gen/1:job)    
    try:
        db = data['dbName']
        tbl = data['tableName']
        cols = data['colNames']
        #reqFunc = data['reqFunc']
    except Exception as err:
        _logger.debug('get parameter error! - %s:%s' %(type(err).__name__, err))
        return None
    
    _vlogger.debug('jobName_'+ str(jobName))
    _vlogger.debug('dbName_'+ str(db))
    _vlogger.debug('tblName_'+ str(tbl))
    _vlogger.debug('cols_'+ str(cols))
    #_vlogger.debug('reqFunc_'+ str(reqFunc))

    # get tbl name
    registTblNamesDic = dict()
    for col_ in cols:
        name_ = "{}_{}_dis_{}_{}".format(projName, jobName, tbl, col_)
        _vlogger.debug('registTblName_' + name_)
        registTblNamesDic[col_] = name_

    # get spark sc
    _vlogger.debug('###################sc.applicationId')
    _vlogger.debug("sc.applicationId:" + sc.applicationId)

    # read data
    for col_ in cols:
        registTblName = registTblNamesDic[col_]
        #registTblName = "{}_{}_dis_{}_{}".format(projName, jobName, tbl, col)
        #registTblName = projName+'_'+jobName+'_dis_'+tbl+'_'+col
        # _vlogger.debug('registTblName_'+registTblName)

        try:
            # read from Hive
            df = getHiveData(db,tbl,cols)
            #print df.show(10)

        except Exception as err:
            _logger.debug('read data error! - %s:%s' % (type(err).__name__, err))
            return None

        # do col distinct
        try:
            _vlogger.debug(col_)
            #column distinct types and the number of each type
            disColCount = df.select(col_).groupby(col_).count()
            disIntCol = disColCount.withColumn("count", disColCount['count'].cast(IntegerType()))     
            disSortCol = disIntCol.orderBy(desc('count'))
            _vlogger.debug(disSortCol.take(5))
            #disSortCol = df.select(col_).groupby(col_).count().withColumnRenamed('count','Count').sort(desc('Count'))
            #disSortCol = df.groupBy([col_]).count().withColumnRenamed('count','Count').orderBy('Count', ascending=False)
            #disSortCol = df.groupby(col_).count().orderBy('count', ascending=False)
            # disSortCol = disSortCol.withColumn('count', 'Count')
            #disSortCol = df.groupBy(col_).count().select(col_, f.col('count').alias('Count')).orderBy('Count', ascending=False)

        except Exception as err:
            _logger.debug('get distinct and count error! - %s:%s' %(type(err).__name__, err))
            return None

        try:
            #number of distinct types  
            disNum = disSortCol.select(col_).count()
            _vlogger.debug('distinctNum_'+str(disNum))
        except Exception as err:
            _logger.debug('get distinct types error! - %s:%s' %(type(err).__name__, err))
            return None


        try:
            #convert spark dataframe to dictionary
            disDic = disSortCol.toPandas().to_dict('records')
            _vlogger.debug('distinctDic_'+str(disDic))
        except Exception as err:
            _logger.debug('convert spark dataframe to dictionary error! - %s:%s' %(type(err).__name__, err))
            return None


        #write table to hive
        try:
            #disSortCol = disSortCol.withColumn("Number", disSortCol["Count"].cast(StringType()))
            #disSortCol_test = disSortCol.persist()
            disSortCol.write.format('orc').mode('overwrite').saveAsTable(registTblName )
            _vlogger.debug('write table : ' + registTblName + ' to hive')
        except Exception as err:
            _logger.debug('write table to hive error! - %s:%s' %(type(err).__name__, err))
            return None  
    
    
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
