#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys

import os
from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SQLContext
from pyspark.sql.functions import col
import logging


from funniest import HiveLibs
from funniest.logging_tester import _getLogger
#from funniest.logging_tester import HiveLibs
#import funniest.HiveLibs import Join
import logging


"""
read data from  ms sql
k-checking
"""
def initSQL():

    print __name__
    properties_ = {
        "user": "gau",
        "password": "Citcw200@",
        "driver":"com.microsoft.sqlserver.jdbc.SQLServerDriver"
    }
    return properties_

#read cols which are indirect columns into a dataframe
def readFromSqlServer(cols, dbName, tblName):
    properties_ = initSQL()
    #_logger.debug(cols)
    tmpColsStr=''
    for col_name_ in cols:
        tmpColsStr=tmpColsStr+col_name_
        if col_name_ != cols[len(cols)-1]:
            tmpColsStr=tmpColsStr+','
    
    mysql_url="jdbc:sqlserver://140.96.81.194:1433;database=%s"%(dbName)
    #kcheckingITRI__ table name in MS sql server
    #query_str = "(SELECT value1, value2 FROM %s) tmp"%(tblName)
    query_str = "(SELECT %s FROM %s) tmp"%(tmpColsStr, tblName)
    _logger.debug(query_str)
    try: 
        ddf = sqlContext.read.format("jdbc")\
            .options(url=mysql_url, dbtable=query_str, **properties_)\
            .load()
        #ddf.show()
        return ddf
    except Py4JJavaError as e:
        print "read"
        s = e.java_exception.toString()
        _logger.debug(s)
        print s
        return None
    except:
        print "Unexcepted excepton", sys.exc_info()
        s = e.java_exception.toString()
        _logger.debug(s)
        # _logger.debug(sys.exc_info())
        return None
        
#20180326, citc add
#read cols which are indirect columns into a dataframe
def readFromHive(cols, dbName, tblName):
    
    #_logger.debug(cols)
    tmpColsStr=''
    for col_name_ in cols:
        tmpColsStr=tmpColsStr+col_name_
        if col_name_ != cols[len(cols)-1]:
            tmpColsStr=tmpColsStr+','
    
    #mysql_url="jdbc:sqlserver://140.96.81.194:1433;database=%s"%(dbName)
    #kcheckingITRI__ table name in MS sql server
    #query_str = "(SELECT value1, value2 FROM %s) tmp"%(tblName)
    query_str = "SELECT %s FROM %s"%(tmpColsStr, tblName)
    _logger.debug(query_str)
    
    try: 
        hiveLibs.dbOperation.use_databases(dbName)
        
        ddf = hiveLibs.dbOperation.print_schema(tblName)
        
        sqlCtx_hive = hiveLibs.dbOperation.get_sqlContext()
        
        print query_str
        ddf = sqlCtx_hive.sql(query_str)
        #ddf.show()
        return ddf
    except Py4JJavaError as e:
        print "read"
        s = e.java_exception.toString()
        _logger.debug(s)
        print s
        return None
    except:
        print "Unexcepted excepton", sys.exc_info()
        s = e.java_exception.toString()
        _logger.debug(s)
        # _logger.debug(sys.exc_info())
        
        return None        
        
 
#df_除了包含groupby欄位,還有其他要distinct的欄位,例如id,可以包含多個欄位
def computKvalue(groupbyCols, df):
    dfDF = hiveLibs.kChking.computKvalue_distnctOtherCols_usingDF(groupbyCols, df)
    #dfDF = dfDF.select(cols)
    dfDF.show()
    dfDF = hiveLibs.kChking.computKvalue_usingDF(groupbyCols, df)
    #dfDF = dfDF.select(cols)
    dfDF.show()
    return dfDF
    
#getKtable(retDF, dfDF, cond,dbName, tblName)    
def getKtable(df, dfDF, cond, dbName, tblName):
    
    #cond=["value1", "value2"]
    #properties_ = initSQL()
    #dbName=building
    #mysql_url="jdbc:sqlserver://140.96.81.194:1433;database=%s"%(dbName)
    kcheckDf = hiveLibs.join_.join2DF_removeDF2Duplication(df,dfDF,cond, cond, "left")
    #kcheckDf.show()
    #kcheckDf.count()       
    tableName="kTable_"+tblName
    hiveLibs.dbOperation.registerRealHiveTable_forsparksql(kcheckDf, tableName)
    #kcheckDf.write.jdbc(mysql_url,table=tableName, mode='overwrite',properties=properties_)
    return tableName
    
FIXED_INPUT_LEN=4     
def main__(dbName, tblName, colsNum, totalLen):
    global sc, sqlContext, hiveLibs, _logger
    
    _logger=_getLogger('kchecking')
    
    colsNum_=0
    try:
        colsNum_=int(colsNum)
    except ValueError:
        _logger.debug("column length error")
        #return
    if totalLen-FIXED_INPUT_LEN != colsNum_:
         _logger.debug("column length error_1")
    
    #argList =str(sys.argv)
    #print argList
    #print sys.argv[-1]
    #print sys.argv[FIXED_INPUT_LEN]
    columns_=sys.argv[FIXED_INPUT_LEN: -1]
    columns_.append(sys.argv[-1])
    tableName="kTable_"+tblName    
    
    # 本地資源運算
    appName = 'kchecking'
    #master = 'local[8]'
    master = 'yarn-client'
    #/gau_working/pysparkWorking/sqljdbc4-2.0.jar
    try:
        #conf=SparkConf().setAppName(appName).setMaster(master).set("sqljdbc4-2.0.jar","/gau_working/pysparkWorking/")
        sc = SparkContext(conf=SparkConf().setAppName(appName).setMaster(master))
        
        #print '#######################out k table name'
        #print tableName
        #itri, output k table name (does not change the code about_logger code)
        #_logger.debug('###################out k table name')
        #_logger.debug(tableName)
        
        #print '#######################sc.applicationId'
        #print sc.applicationId
        #itri, output k application id (does not change the code about_logger code)
        #_logger.debug('###################sc.applicationId')
        #_logger.debug(sc.applicationId)

        #sc = SparkContext(conf)
        # 取得資料庫介面
        #sqlContext = SQLContext(sc)
        hiveLibs = HiveLibs(sc)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        
    except Exception as e:
        
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("error in kchecking : "+str(e))
        _logger.debug("errTable_errSC")
        return    
    
    #columns_ = value1, value2
    try:
        #columns_ = [value1, value2]
        #_logger.debug(columns_)
        #retDF = readFromSqlServer(columns_, dbName, tblName)
        
        retDF = readFromHive(columns_, dbName, tblName)
        if retDF is not None:
            retDF.show()
        
        #else:###20180103
            #itri, output k table name (does not change the code about_logger code)
        
        _logger.debug('###################out k table name')
        _logger.debug(tableName)
        #itri, output k application id (does not change the code about_logger code)
        _logger.debug('###################sc.applicationId')
        _logger.debug(sc.applicationId)
        
          
        cols=[]
        #cols=[col("value1"), col("value2")]
        cols=columns_#['value1','value2']
        dfDF=computKvalue(cols, retDF)
        cond=columns_#["value1", "value2"]
        getKtable(retDF, dfDF, cond,dbName, tblName)
        #cond=["value1", "value2"]
    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromSqlServer")
        return
        #_logger.debug("error in kchecking : "+str(e)) 
           


    


if __name__ == "__main__":
    dbName = sys.argv[1]
   
    tblName = sys.argv[2]
    colsNum = sys.argv[3]
    totalLen = len(sys.argv)
    
    print '########'
    print dbName
    print tblName
    print colsNum
    print totalLen
    print '#############'
    
    main__(dbName, tblName, colsNum, totalLen)
 
        



