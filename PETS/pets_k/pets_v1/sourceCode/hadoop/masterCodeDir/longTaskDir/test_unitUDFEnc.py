# -*- coding: utf-8 -*-
''' Unittest '''
import unittest
from datetime import datetime
#from types import BooleanType
#from types import NoneType

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

class udfEncTestCase(unittest.TestCase):
    """
    read data from  ms sql
    udfEnc
    """
    
    
    def setUp(self):
        global _logger
        _logger=_getLogger('udfEncUID')
        self.appName="udfEncTest"
        self.master = 'yarn'
        
        #citc, for spark 2.0 
        self.spark = SparkSession.builder.enableHiveSupport().master('yarn').appName(self.appName).getOrCreate()
        self.sc = self.spark.sparkContext
        self.sc.setSystemProperty("hive.metastore.uris", "thrift://master.bdp.com:10000")
        #df=spark.read.csv("input/test.csv")
        #df.show()

        #self.sc = SparkContext(conf=SparkConf().setAppName(self.appName).setMaster(self.master))
        self.hiveLibs = HiveLibs(self.sc)
        self.sqlContext = self.hiveLibs.dbOperation.get_sqlContext()
       
    def tearDown(self):
         self.sc.stop()
         
    def initSQL(self):

       #print __name__
        properties_ = {
            "user": "gau",
            "password": "Citcw200@",
            "driver":"com.microsoft.sqlserver.jdbc.SQLServerDriver"
        }
        return properties_

    #citc, add for spark 2.0
    def readFrom_csv(self, path_tblName):
        _logger.debug("in readFrom_csv")
        try: 
            #query_str = "(SELECT value1, value2 FROM %s) tmp"%(tblName)
            ddf = self.spark.read.csv(path_tblName)

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


    def readFromSqlServer(self, tblName):
        properties_ = self.initSQL()
        print (properties_)
        mysql_url="jdbc:sqlserver://140.96.81.194:1433;database=building"
        #kcheckingITRI__ table name in MS sql server
        
        try: 
            #query_str = "(SELECT value1, value2 FROM %s) tmp"%(tblName)
            ddf = self.sqlContext.read.format("jdbc")\
                .options(url=mysql_url, dbtable=tblName, **properties_)\
                .load()
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
            _logger.debug("error in readFromSqlServer : "+str(e)) 
            return None
        
        
    #使用udf加密,jar file = dfEncrypt_3.jar, myLogging_1.jar(for java logging)
    def udfEncCols(self,encList, df, key_):
        ######20180121 citc add, ##############################################
        #self.hiveLibs.dbOperation.registerTempTable_forsparksql(df,  "DF_Table__")
        #self.sqlContext.sql("create temporary function udfEnc_ as 'citc.udfEncrypt.udfEnc'")
        ######20180121 citc add (end) ##########################################

        #####citc, 20181015 add for spark 2.0############
        df.write.format("orc").mode("overwrite").saveAsTable("DF_Table__")
        self.sqlContext.sql("create temporary function udfEnc_ as 'citc.udfEncrypt.udfEnc'")
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
        _logger.debug(tmpStr)
        
        
        
        df2=self.sqlContext.sql(tmpStr)
        df2.show()

        return df2
    

    #####for sqlServer###################    
    def writeToTable(self,df, dbName, tblName):
        
        properties_ = self.initSQL()
        
        mysql_url="jdbc:sqlserver://140.96.81.194:1433;database=%s"%(dbName)
        #kcheckDf = hiveLibs.join_.join2DF_removeDF2Duplication(df,dfDF,cond, cond, "left")
               
        tableName="udfEnc__"+tblName
        df.write.jdbc(mysql_url,table=tableName, mode='overwrite',properties=properties_)
        return tableName            
        
    def ___test_readMSSql(self):
        retDF = self.readFromSqlServer("kcheckingITRI__")
        #retDF.show()
        self.assertIsNotNone(retDF)
        
    def test_udfEncCols(self):
        try:
            key_ = "Bar12345Bar12345Bar12345Bar12345"
            #retDF = self.readFrom_csv("input/test.csv")
            retDF = self.readFrom_csv("test.csv")
            if retDF is not None:
                retDF.show()
                
            cols=['_c0','_c3']
            #udfEncCols(encList, df, key_)
            dfDF=self.udfEncCols(cols, retDF, key_)
            dfDF.show()
            dfDF.write.format("orc").mode("overwrite").saveAsTable("encTBL")
            #cond=["_C0", "_C1"]
            #self.sqlContext(self.sc).
            #self.tblStr = self.writeToTable(dfDF, "default","kcheckingITRI__")
            #_logger.debug(tblStr)
        except Py4JJavaError as e:
            s = e.java_exception.toString()
            _logger.debug(s)
            
        except Exception as e:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(len(sys.exc_info()))
            _logger.debug("error in test_udfEncCols : "+str(e))     
        self.assertIsNotNone(dfDF)
        #self.assertEqual(self.tblStr,'udfEnc__kcheckingITRI__')

if __name__ == '__main__':
    unittest.main()
