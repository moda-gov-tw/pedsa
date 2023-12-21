#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import base64
from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType, StringType
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from lib.base64convert import getJsonParser
from MyLib.connect_sql import ConnectSQL
#20200205, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

from MyLib.parseData import exportData, checkListQuotes, importData

import os.path
import io , sys

import chardet


####################################################################################
#20190718, mark for logging error (ValueError: underlying buffer has been detached)

if "UTF-8" in sys.stdout.encoding:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

#20200227, for UnicodeEncodeError when calling df.show()
#(ascii' codec can't encode characters in position 363-368)
# default encoding is "ANSI_X3.4-1968"
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)    
###################################################################################


#reload(sys)
#sys.setdefaultencoding('utf-8')


def createTempFunction(sqlContext):
    # udf list
    udfs = ['getGenAddressWithConfig']

    #hive> ADD JAR ./udfEncrypt_0306.jar;
    #Added [./udfEncrypt_0306.jar] to class path
    #Added resources: [./udfEncrypt_0306.jar]
    #hive> CREATE TEMPORARY FUNCTION contains as 'citc.udfEncrypt.ComplexUDFExample';
    #select name, ComplexUDFExample_(name_list,name_list[0]), name_list from peoplelist;
    #citc.udfEncrypt.ComplexUDFExample


    for udf_ in udfs:
        try:
            if udf_ == 'getGenAddress':
                sqlAction = "create temporary function " + udf_ + "_ as 'citc.deid." + udf_ + "'"
            else:
                sqlAction = "create temporary function " + udf_ + "_ as 'citc.deid." + udf_ + "'"
            sqlAction = "CREATE TEMPORARY FUNCTION genaddr_ as 'citc.deid.getGenAddressWithConfig'"
            #CREATE TEMPORARY FUNCTION contains as 'citc.udfEncrypt.ComplexUDFExample'
            _logger.debug("0330-----------")
            _logger.debug(sqlAction)
            sqlContext.sql(sqlAction)
            
        except Exception as e:
            _logger.debug('errTable:'+NAME+'_'+str(e))
            _logger.debug('errTable:'+NAME+'_udf_{}_cannot_be_created'.format(udf_))


def initSparkContext(name):
    appName = name
    #master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        #2020027, save hive table into /home/hadoop/proj_/longTaskDir/spark-warehouse
        #                              is a local dir (in nodemaster)
        #spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()        

        #2020027, save hive table into hdfs://nodemaster:9000/user/hive/warehous
        # defined in hive-site.xml
        warehouse_location = "hdfs://nodemaster:9000/user/hive/warehouse"
        #warehouse_location = "hdfs:///user/hive/warehouse"

        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName) \
                     .config("spark.sql.warehouse.dir", warehouse_location) \
                                     .getOrCreate()



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
        _logger.debug("errTable:fundation_getGenNumLevel:"+str(e))
        _logger.debug("errTable:errSC")
        return SparkContext(conf=SparkConf())

    return sc_, spark_, hiveLibs, sqlContext



def main(dbName, tableName, sepFormat):

    global _logger, sc, spark, hiveLibs, sqlContext, NAME, updateAppStatus_
    # api name
    NAME = 'udafWithConfig'
    _logger=_getLogger(NAME)

    tblName = tableName


    # log input
    _logger.debug('spark_gen_dbName_%s', dbName)
    _logger.debug('spark_gen_genTableNane%s', tableName)
   

     # spark setting
    sc, spark , hiveLibs, sqlContext = initSparkContext(NAME)

    #return information
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)
    



    # create temp udf 
    _logger.debug("============start2 createTempFunction===============")
    createTempFunction(sqlContext)
    #----------genList= 
    #genList= ['getGenNumLevel_(c_2771_1, "10") as c_2771_1', 'getGenUdf_(c_2771_6, "Divorced:Single;Never-married:Single;Separated:Single;Widowed:Single;Married-civ-spouse:Married;Married-AF-spouse:Married;Married-spouse-absent:Married", "True", "others") as c_2771_6', 'getGenNumLevel_(c_2771_11, "50") as c_2771_11', 'getGenNumLevel_(c_2771_12, "100") as c_2771_12', 'getGenNumLevel_(c_2771_13, "10") as c_2771_13', 'c_2771_0', 'c_2771_2', 'c_2771_3', 'c_2771_4', 'c_2771_5', 'c_2771_7', 'c_2771_8', 'c_2771_9', 'c_2771_10', 'c_2771_14', 'c_2771_15']
    #select getGenNumLevel_(c_2771_1, "10") as c_2771_1,getGenUdf_(c_2771_6, "Divorced:Single;Never-married:Single;Separated:Single;Widowed:Single;Married-civ-spouse:Married;Married-AF-spouse:Married;Married-spouse-absent:Married", "True", "others") as c_2771_6,getGenNumLevel_(c_2771_11, "50") as c_2771_11,getGenNumLevel_(c_2771_12, "100") as c_2771_12,getGenNumLevel_(c_2771_13, "10") as c_2771_13,c_2771_0,c_2771_2,c_2771_3,c_2771_4,c_2771_5,c_2771_7,c_2771_8,c_2771_9,c_2771_10,c_2771_14,c_2771_15 from mac_adult_id

    

    try:
        #hive> desc userupload;
        #data                    string                                      
        #id                      string                                      
        #income                  string                                      
        #address                 string
        #genAction = "select name, contains(name_list,name_list[0],1), name_list from default.peoplelist"
        #genAction = "select id, genaddr_(address,'5'), address from default.userupload"

        #genAction = "select id, genaddr_(address,'5'), address from default.userupload"
        genAction = "select id, genaddr_(address,"
        genAction = genAction+"\'"+level_num+"\'"+"), address from default.userupload"
        
        #genAction = "select name, name_list from default.peoplelist"
        #genAction = "select name, contains(name_list,'a'), name_list from default.peoplelist"

        _logger.debug('genAction =  ' + genAction)
        df2 = sqlContext.sql(genAction)
        df2.show()
        #_logger.debug('generlize ' + tbl + ' succeed.')
    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        return
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable:errReadFromSqlServer()_OR_getGen()")
        return    

    

    #updateAppStatus_.updateToMysql("All_table_save_succeed","100","Finished")
    #####################################################3  

if __name__ == "__main__":
    #spark-submit --jars udfGen_0330.jar,java-json.jar,myLogging_1.jar,mysql-connector-java-8.0.13.jar udfWithConfig.py default userupload "2"

    dbName = sys.argv[1] #str
    tableName = sys.argv[2]    
    level_num = sys.argv[3]
    #genDictEncode = sys.argv[2]  # key: tblName, value: encode
    #doMinMaxEncode = sys.argv[3]  # key: tblName, value: encode
    print('########')
    print(dbName)
    print(tableName)
    print(level_num)
    print("sys.stdout.encoding ="+sys.stdout.encoding)
    print('#############')

    
    main(dbName, tableName, level_num)

