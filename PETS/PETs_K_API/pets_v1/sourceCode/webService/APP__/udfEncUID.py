#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from pyspark.sql import SparkSession

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



#citc, add for spark 2.0
def readFrom_csv( path_tblName):
    _logger.debug("in readFrom_csv")
    try: 
        #query_str = "(SELECT value1, value2 FROM %s) tmp"%(tblName)
        ddf = spark.read.csv(path_tblName)

        #ddf.show()
        return ddf
    except Py4JJavaError as e:
        print ("read")
        s = e.java_exception.toString()
        _logger.debug(s)
        print (s)
        return None
    except Exception as e:
        print ("Unexcepted excepton", sys.exc_info())
        _logger.debug("error in readFromHive : "+str(e)) 
        return None    



 
#使用udf加密,jar file = dfEncrypt_3.jar, myLogging_1.jar(for java logging)
def udfEncCols(encList, df, key_):
    
    _logger.debug("in udfEncCols")
    #####citc, 20181015 add for spark 2.0############
    df.write.format("orc").mode("overwrite").saveAsTable("DF_Table__")
    sqlContext.sql("create temporary function udfEnc_ as 'citc.udfEncrypt.udfEnc'")
    #######################################################3
    #key_ = "Bar12345Bar12345Bar12345Bar12345"
    cols = df.columns
    tmpStr="select "
    
    
    for colNam_ in cols:
        if colNam_ in cols[-1:]:
            if colNam_ not in encList:
                tmpStr=tmpStr+ colNam_+" from DF_Table__"
            else:
                tmpStr=tmpStr+ "udfEnc_("+colNam_+", \""+key_+"\") as "+colNam_+" from DF_Table__"
            break;
        if colNam_ not in encList:
            tmpStr=tmpStr+ colNam_+","
        else:
            tmpStr=tmpStr+ "udfEnc_("+colNam_+", \""+key_+"\") as "+colNam_+","
    #print (tmpStr)
    _logger.debug(tmpStr)
    
    
    df2=sqlContext.sql(tmpStr)
    #df2.show()

    return df2
    
    
FIXED_INPUT_LEN=4     
def main__(dbName, tblName, colsNum, totalLen):
    global sc, sqlContext, hiveLibs, _logger,spark
    
    ##############3
    key_ = "Bar12345Bar12345Bar12345Bar12345"
    #hiveLibs.dbOperation.registerTempTable_forsparksql(retDF,  "DF_Table__")
    
    ###################
    
    _logger=_getLogger('udfEncUID')
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
    
    #print (sys.argv[-1])
    #print (sys.argv[FIXED_INPUT_LEN])


    columns_=sys.argv[FIXED_INPUT_LEN: -1]
    columns_.append(sys.argv[-1])
    tableName="udfEncTable_"+tblName 
    
    # 本地資源運算
    appName = 'udfEncUID'
    master = 'yarn'
    #master = 'yarn-client'
    #/gau_working/pysparkWorking/sqljdbc4-2.0.jar
    try:
       #citc, for spark 2.0 
       spark_ = SparkSession.builder.enableHiveSupport().master('yarn').appName(appName).getOrCreate()
       sc_ = spark_.sparkContext
       sc_.setSystemProperty("hive.metastore.uris", "thrift://master.bdp.com:10000")
       #df=spark.read.csv("input/test.csv")
       #df.show()

       #self.sc = SparkContext(conf=SparkConf().setAppName(self.appName).setMaster(self.master))
       hiveLibs_ = HiveLibs(sc_)
       sqlContext_ = hiveLibs_.dbOperation.get_sqlContext()
  
            
    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("error in fundation of udfEncUID : "+str(e))
        _logger.debug("errTable_errSC")
        return    
    spark = spark_
    sc= sc_
    sqlContext = sqlContext_
    hiveLibs = hiveLibs_

    #logger.debug("1_______________")
    #columns_ = value1, value2

    ###########20181015, citc mve here for async()############
    #itri, output k table name (does not change the code about_logger code)
    tmp = tableName.split(".")
    _logger.debug('###################out udfEnc table name')
    _logger.debug(tmp[0])
    #print('###################out udfEnc table name')
    #print(tableName)

    #itri, output k application id (does not change the code about_logger code)
    _logger.debug('###################sc.applicationId')
    _logger.debug(sc.applicationId)
    ##########20181015, citc add for async(), end####################################



    try:
        #columns_ = [value1, value2]
        #_logger.debug(columns_)
        #citc 20181015, tblName as path_tblName

        _logger.debug(tblName)
        retDF = readFrom_csv(tblName)
        if retDF is not None:
            retDF.show()
        else:
            print("retDF is null")
            _logger.debug("retDF is null")  
            return  

        ###########20181015, citc mve here for async()############
        #itri, output k table name (does not change the code about_logger code)
        _logger.debug('###################out udfEnc table name')
        _logger.debug(tableName)
        #print('###################out udfEnc table name')
        #print(tableName)

        #itri, output k application id (does not change the code about_logger code)
        _logger.debug('###################sc.applicationId')
        _logger.debug(sc.applicationId)
        ##########20181015, citc add for async(), end####################################

        #_logger.debug("2_______________")
        cols=[]
        
        cols=columns_#['y']
        dfDF=udfEncCols(cols, retDF, key_)
        #_logger.debug("3_______________")
        #_logger.debug(tableName)
        tmp = tableName.split(".")
        #print(tmp)
        tableName =tmp[0] 



        ##20180129, citc add, write to table, then return table name (i.e. tableName) 
        #writeToTable(dfDF, dbName, tableName)

        #dfDF.show()
        #tableName="udfEncTable_"+tblName, in above
        dfDF.write.format("orc").mode("overwrite").saveAsTable(tableName)

        
        #######20180124, citc move here
        #itri, output k table name (does not change the code about_logger code)
        #_logger.debug('###################out udfEnc table name')
        #_logger.debug(tableName)
        #print('###################out udfEnc table name')
        #print(tableName)

        #itri, output k application id (does not change the code about_logger code)
        #_logger.debug('###################sc.applicationId')
        #_logger.debug(sc.applicationId)
        #print('###################sc.applicationId')
        #print(sc.applicationId)

    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromSqlServer()_OR_udfEncCols()")
        return
        #_logger.debug("error in kchecking : "+str(e)) 
           


    

##citc 2011015, dbName is dummy, tblName is csv file path in hdfs
if __name__ == "__main__":
    dbName = sys.argv[1]
   
    tblName = sys.argv[2]
    colsNum = sys.argv[3]
    totalLen = len(sys.argv)
    
    print ('########')
    print (dbName)
    print (tblName)
    print (colsNum)
    print (totalLen)
    print ('#############')
    
    main__(dbName, tblName, colsNum, totalLen)
 