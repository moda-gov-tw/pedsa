#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,length
from py4j.protocol import Py4JJavaError
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.loginInfo import getLoginMysql
import pymysql
import subprocess
from MyLib.parseData import exportData, checkListQuotes
import os.path
import io , sys

####################################################################################
#20190718, mark for logging error (ValueError: underlying buffer has been detached)

if "UTF-8" in sys.stdout.encoding:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
###################################################################################

def checkInputData_(filePath, sepFormat=','):
    _logger.debug("In checkInputData_")
    #_logger_fb=_getLogger('fb_checkInputData')
    _logger_fb=_getLogger('fb_checkInputData')
    

    # for rdd map
    def transFunc(line):
        line = line.split(sepFormat)
        if line == ['']:
            return None
        else:
            return line

    try:
        rdd = sc.textFile(filePath)

        rdd1 = rdd.map(transFunc)
        rdd1 = rdd1.filter(lambda x: x is not None)

        headerRaw = rdd1.first()
        headerNum = len(headerRaw)

        rdd2 = rdd1.filter(lambda line: line != headerRaw)
        
        print()
        for row in rdd2.collect():
            if(len(row) < headerNum):
                _logger.debug(row)
                _logger.debug("length less than : " + str(headerNum))
                _logger_fb.debug(row)
                _logger_fb.debug("length less than : " + str(headerNum))
    except Exception as e:
        _logger.debug("error in readLocalData : " + str(e))
        _logger.debug("errTable_sc.textFile_error")

###20181016, citc add for getting key from mysql
##dbName as the school tag e.g. 'ntut'
FIXED_INPUT_LEN=5

def checkFileExist(paht_):
    if os.path.isfile(paht_):
        return True
    else:
        return False

#def main__(dbName, tblName, key_, colsNum, totalLen):
def main__(tblName, totalLen):
    '''
    get key from mysql, 
    QueryKeyBySchool, get db name & table name from loging_mysql.txt
    dbname is tag
    '''
    global sc, sqlContext, hiveLibs, _logger,spark
    _logger=_getLogger('checkInputData')

    #20190717, citc add for FB log
    #fb_udfMacCols
    _logger_fb=_getLogger('fb_checkInputData')


    
    
    '''
    get new sc and combining sc and citc hive lib
    '''
    # 本地資源運算
    appName = 'checkInputData'
    master = 'yarn'
    #master = 'yarn-client'
    #/gau_working/pysparkWorking/sqljdbc4-2.0.jar
    try:
       #citc, for spark 2.0 
       spark_ = SparkSession.builder.enableHiveSupport().master('yarn').appName(appName).getOrCreate()
       sc_ = spark_.sparkContext
       sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")
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

    """
    tblName is used as file path
    """
    retDF = None
    try:
        #columns_ = [value1, value2]
        #_logger.debug(columns_)
        #citc 20181015, tblName as path_tblName

        path_ = "/home/hadoop/proj_/dataMac/input/" + tblName + ".csv"
        _logger.debug("Input path: " + path_)

        path_spark = 'file://' + path_
        _logger.debug("path_: {0}".format(path_))
        #_logger.debug("sep: {0}".format(sep))

        fileExist = checkFileExist(path_)
        if not fileExist:
            _logger.debug("File is not exist.")
            _logger.debug("err in readFrom_csv_wit_NA_Normalize")
            return None, None



        #20190717, add fo fb log
        _logger_fb.debug("============start======================")
        _logger_fb.debug("input file: " + path_)
        #_logger_fb.debug("columns name will be maced: " + str(columns_))

        #_logger=_getLogger('checkInputData')
        sep="^|"
        #path_spark = "input/adult_id.csv"

        checkInputData_(path_spark, sepFormat=sep)
        _logger_fb.debug("============start2======================")
        


    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromSqlServer()")
        return

 
    return
        #_logger.debug("error in kchecking : "+str(e)) 
#spark-submit --jars myLogging_1.jar checkInputData.py adult_id
#docker exec -u hadoop -it nodemaster spark-submit --jars /home/hadoop/proj_/longTaskDir/myLogging_1.jar /home/hadoop/proj_/longTaskDir/checkInputData.py adult_id

if __name__ == "__main__":

    tblName = sys.argv[1]
    #key =  sys.argv[2]
    #sep = sys.argv[3]
    #colsNum = sys.argv[4]
    totalLen = len(sys.argv)
    
    print('########')
    print(tblName)
    #print(sep)
    #print(colsNum)
    print(totalLen)
    print('#############')
    
    main__(tblName, totalLen)
 
