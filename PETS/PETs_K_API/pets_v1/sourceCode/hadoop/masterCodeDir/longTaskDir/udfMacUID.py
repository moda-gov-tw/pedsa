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

from pyspark import SparkFiles
from os import listdir, path

import time



####################################################################################
#20190718, mark for logging error (ValueError: underlying buffer has been detached)

if "UTF-8" in sys.stdout.encoding:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
###################################################################################

#20190104, citc add
def CreateMysqlDB(dbName):
    _logger.debug("in CreateMysqlDB")
    #print(sch_tag_str)
    #queryStr = 'SELECT * FROM products'+' '+'where school_tag = '+sch_tag_str
    #print(queryStr)

    try:
        #connect to mysql
        #print("ip===================")
        ip, port_, user_, pwd = getLoginMysql('/home/hadoop/proj_/longTaskDir/login_mysql.txt')
        #print("ip===================")
        #print(ip)
        #print(port_)
        connection = pymysql.connect(host=ip,
                                     #port=int(port_),
                                     user=user_,
                                     password=pwd,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor
                                     ) 
        
        
        with connection.cursor() as cursor:
            #創建數據庫test
            #cursor.execute('SET CHARACTER SET utf8mb4;')
            #cursor.execute("set names UTF8")
            sql = "drop database if exists "+dbName
            _logger.debug(sql)
            cursor.execute(sql)  #如果數據庫已經存在，那麼刪除後重新創建

            #sql = "create database " + dbName
            sql = "CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(dbName)
            _logger.debug(sql)
            cursor.execute(sql)

            #sql = "ALTER DATABASE {} CHARACTER SET utf8 COLLATE utf8_general_ci".format(dbName)
            #_logger.debug(sql)
            #cursor.execute(sql)
 
        connection.close()
        

    except Exception as e:
        errMsg = 'Mysql_error:'+str(e)
        _logger.debug(errMsg)
        raise Exception('DFtoMysql', errMsg)
        
#20190104, citc add
def ReadDFFromMysql(tableName, dbName):   
    """
    output the (id, idhash) pairs to tableName under DB (dbName)
    """
    try:
        #connect to mysql
        #print("ip===================")
        ip, port_, user_, pwd = getLoginMysql('/root/proj_/longTaskDir/login_mysql.txt')
        #print("ip===================")
        #print(ip)
        #print(port_)
        
        url_="jdbc:mysql://"+ip+":"+port_+"/"+dbName
        print(url_)       
        source_df = sqlContext.read.format('jdbc').options(
          url=url_,
          driver='com.mysql.jdbc.Driver',
          dbtable=tableName,
          user=user_,
          password=pwd).load()
   
        return source_df

    except Exception as e:
        errMsg = 'Mysql_error:'+str(e)

        _logger.debug(errMsg)
        raise Exception('DFtoMysql', errMsg)
        #self.update_state(state="FAIL_CELERY", meta={'errMsg':errMsg})
        #return errMsg        


#20190103, citc add
def DFtoMysql(df, tableName, dbName):   
    """
    output the (id, idhash) pairs to tableName under DB (dbName)
    """
    try:
        #connect to mysql
        #print("ip===================")
        ip, port_, user_, pwd = getLoginMysql('/root/proj_/longTaskDir/login_mysql.txt')
        #print("ip===================")
        #print(ip)
        #print(port_)
        
        url_="jdbc:mysql://"+ip+":"+port_+"/"+dbName
        url_ += "?characterEncoding=GBK"
        print(url_)
        
        df.write.format('jdbc').options(
            url=url_,
            driver='com.mysql.jdbc.Driver',
            createTableOptions='ENGINE=InnoDB DEFAULT CHARSET=utf8mb4',
            dbtable=tableName,
            user=user_,
            password=pwd).mode('append').save()

        return 

    except Exception as e:
        errMsg = 'Mysql_error:'+str(e)

        _logger.debug(errMsg)
        raise Exception('DFtoMysql', errMsg)
        #self.update_state(state="FAIL_CELERY", meta={'errMsg':errMsg})
        #return errMsg

#20181016, citc add for get key form mySQL
def QueryKeyBySchool(sch_tag_str):
    _logger.debug("in QueryKeyBySchool")
    #print(sch_tag_str)
    #queryStr = 'SELECT * FROM products'+' '+'where school_tag = '+sch_tag_str
    #print(queryStr)
    try:
        #connect to mysql
        #print("ip===================")
        ip, port_, user_, pwd = getLoginMysql('/root/proj_/longTaskDir/login_mysql.txt')
        #print("ip===================")
        #print(ip)
        #print(port_)
        connection = pymysql.connect(host=ip,
                                     #port=int(port_),
                                     user=user_,
                                     password=pwd,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor
                                     ) 
        
        queryStr = 'SELECT * FROM products'+' '+'where tag = '+sch_tag_str
        print("queryStr===================")
        print(queryStr)
        key_='Null'

        with connection.cursor() as cursor:
             cursor.execute("set names utf8mb4")
             cursor.execute("use key_db")
             #cursor.execute(queryStr)
             cursor.execute("SELECT * FROM products;")
             for r in cursor:
                    print(r)
                    print(r.get('tag'))
                    key_ = r.get('key_enc')
             

            # commit to mysql
            #connection.commit()

        connection.close()
        return key_

    except Exception as e:
        errMsg = 'Mysql_error:'+str(e)

        _logger.debug(errMsg)
        raise Exception('citc_keyDB', errMsg)
        #self.update_state(state="FAIL_CELERY", meta={'errMsg':errMsg})
        #return errMsg



#citc, add for spark 2.0
def readFrom_csv( path_tblName):
    _logger.debug("in readFrom_csv")
    try: 
        #query_str = "(SELECT value1, value2 FROM %s) tmp"%(tblName)
        #ddf = spark.read.csv(path_tblName)
        ddf = spark.read.option("header", "true").csv(path_tblName)
        
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

##################readFrom_csv_wit_NA_Normalize (start)#####################################
'''
citc, 20190122 add for fubon
test double character  sep, adult_id_adult_testNA3.csv with double character '^|'
'''
#for rdd map
def transFunc(line):
    line = line.split("^|")
    return line 

def normalizeNA(df):
    try:
        header_en = df.columns
        for col_name in header_en:
            df_2 = df.replace(['\\N'], ['_NA_'], col_name)

        df_2.persist()

        header_en = df_2.columns
        for col_name in header_en:
            df_2 = df_2.replace(['na'], ['_NA_'], col_name)

        df_2.persist()

        header_en = df_2.columns
        for col_name in header_en:
            df_2 = df_2.replace([''], ['_NULL_'], col_name)

        df_2.persist()

        df_2 = df_2.na.fill('_NULL_')
        return df_2
    except Exception as e:
        print ("Unexcepted excepton", sys.exc_info())
        _logger.debug("error in normalizeNA : "+str(e))
        return None

def checkFileExist(paht_):
    if os.path.isfile(paht_):
        return True
    else:
        return False

def readFrom_csv_wit_NA_Normalize(path_, sep):
    _logger.debug("In readFrom_csv_wit_NA_Normalize")
    try:
        # Read data
        path_spark = 'file://' + path_
        _logger.debug("path_: {0}".format(path_))
        _logger.debug("sep: {0}".format(sep))

        fileExist = checkFileExist(path_)
        if not fileExist:
            _logger.debug("File is not exist.")
            _logger.debug("err in readFrom_csv_wit_NA_Normalize")
            return None, None
        
        ###20200630, citc add#######################################
        putHdfsFileTmp(path_) #hdfs://nodemasterS:9000/tmp/**.csv
        time.sleep(11)
        tmpStr_ = path_.split('/' )#path_=/home/hadoop/proj_/dataMac/input/adult_id_ri.csv
        print(tmpStr_[-1])

        tmpPath_ = "hdfs://nodemasterS:9000/tmp/"+tmpStr_[-1]



        #hdfs://nodemasterS:9000/user/hadoop/home/hadoop/.sparkStaging/
        #spark.sparkContext.addFile(path_spark)
        #spark.sparkContext.addFile(tmpPath_)

        #inputfilename=getinputfile(spark)
        #print(">>>>>>>>>>>>>>>>>>>>>>>>input file path is######:",inputfilename)

        #path_spark = tmpPath_
        ##################>>>>>>>>>>>##################################################


        ############################################################

        #df = readLocalData(tmpPath_, sepFormat=sep)#for cluster
        _logger.debug("---path_spark={}".format(path_spark))
        if 1:
            df = readLocalData(path_spark, sepFormat=sep)
        else:
            path__="file:///home/hadoop/proj_/dataMac/input/test3.csv"
            df = readLocalData(path__, sepFormat=sep)


        # Convert col_cht to col_en
        headerRaw = df.columns
        headerTmp = ["col_"+str(i) for i in range(len(headerRaw))]
        headerDict = dict()
        for i in range(len(headerTmp)):
            headerDict[headerTmp[i]] = headerRaw[i]

        _logger.debug("Check headerRaw and headerTmp")
        _logger.debug(headerRaw)
        _logger.debug(headerTmp)

        #_logger.debug("before df_2 = df.toDF(*headerTmp)")
        df_2 = df.toDF(*headerTmp)
        #_logger.debug("after df_2 = df.toDF(*headerTmp)")
        # Normalize NA
        # df_2 = normalizeNA(df_2)
        #_logger.debug("after df_2 = normalizeNA(df_2)")
        return df_2, headerDict

    except Py4JJavaError as e:
        print ("readFrom_csv_wit_NA_Normalize")
        _logger.debug("err in readFrom_csv_wit_NA_Normalize")
        s = e.java_exception.toString()
        _logger.debug(s)
        return None, None
    except Exception as e:
        print ("Unexcepted excepton", sys.exc_info())
        _logger.debug("error in readFrom_csv_wit_NA_Normalize : "+str(e))
        return None, None

###################readFrom_csv_wit_NA_Normalize (end)###################################   

#使用udf mac,jar file = dfEncrypt_6.jar, myLogging_1.jar(for java logging)
def udfMacCols(encList, df, key_, idHashDBName, headerDict):
    
    _logger.debug("in udfMacCols")
    _logger.debug(encList)
    #####citc, 20181015 add for spark 2.0############
    #sqlContext.sql("use test_import_all")
    #df.write.format("orc").mode("overwrite").saveAsTable("DF_Table__")
    df.registerTempTable("DF_Table__")
    sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfMac'")
    #######################################################3
    #key_ = "Bar12345Bar12345Bar12345Bar12345"
    cols = df.columns
    tmpStr="select "
    
    '''
    select udfMac_(COUNTY_ID, "Bar12345Bar12345Bar12345Bar12345") as COUNTY_ID,
            udfMac_(COUNTY, "Bar12345Bar12345Bar12345Bar12345") as COUNTY,
            FLD01,FLD02,FLD03,INFO_TIME 
            from DF_Table__
    '''
    for colNam_ in cols:
        if colNam_ in cols[-1:]:
            if colNam_ not in encList:
                tmpStr=tmpStr+ colNam_+" from DF_Table__"
            else:
                tmpStr=tmpStr+ colNam_ + " as "+colNam_+"__, "+"udfMac_("+colNam_+", \""+key_+"\") as "+colNam_+" from DF_Table__"
            break;
        if colNam_ not in encList:
            tmpStr=tmpStr+ colNam_+","
        else:
            tmpStr=tmpStr+ colNam_ + " as "+colNam_+"__, "+"udfMac_("+colNam_+", \""+key_+"\") as "+colNam_+","
    #print (tmpStr)
    #_logger.debug(tmpStr)
    
    
    df2=sqlContext.sql(tmpStr)
    
    df3 = df2[cols]
    ######20190718, mark
    #df3.show()
    
    #CreateMysqlDB(idHashDBName)
    for colNam_ in encList:
        tmpList = []
        
        tmpList.append(colNam_)
        tmpStr = colNam_+"__"
        tmpList.append(tmpStr)
        df4=df2[tmpList]
        df4=df4[tmpList].distinct()
        ######20190718, mark
        #df4.show()
        colNam_ = headerDict[colNam_]
        tmpTable = colNam_+"_hashTBL"
        #DFtoMysql(df4,tmpTable,idHashDBName)
    #DFtoMysql（df4, "tb1","hashDB"）
        
    

    return df3


#return a file path like Decry_sample.csv/part-00000-6075efb5-55e2-4aa5-b178-723c58299b65-c000.csv]   
#fileName Decry_sample.csv
def getHdfsFilePath(fileName):
    print ("in getHdfsFilePath")
    ##['hadoop', 'fs', '-ls', 'udfEncTable_test.csv']
    hdfsCmdList=['hadoop','fs','-ls',fileName]
    #print(hdfsCmdList)
    hdfsCommand=subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    #[b"ls: `udfEncTable_test.csv': No such file or directory\n"]
    lines = hdfsCommand.stderr.readlines()
    #print("stderr out")
    #print(lines)
    for line in lines:
        #print(line)
        if 'No such file or directory' in  line.decode("utf-8") :  
            return None
    #print(filePath)        
    lines = hdfsCommand.stdout.readlines()
    #print("stdout out")
    #print(lines)
    filePath=''
    for line in lines:
        #print(line)
        if fileName in  line.decode("utf-8") :
        #if fileName in  line :  
            #print("-1")
            tmpStr_ = line.split( )
            print(tmpStr_)
            filePath = tmpStr_[-1]
    #print(filePath)        
    return filePath.decode("utf-8")
    #return filePath


##get file from hadoop into master (namenode)
def getHdfsFile(fileName):
    
    tmpStr_ = fileName.split('/' )
    #tmpStr_ = ['Decry_sample.csv', 'part-00000-6075efb5-55e2-4aa5-b178-723c58299b65-c000.csv']
    #print (tmpStr_)
    hdfsCmdList=['hadoop','fs','-get',fileName,tmpStr_[0]]

    hdfsCommand=subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
           
    return 

##put file to hdfs /tmp, 20200630
def putHdfsFileTmp(fileName):
    
    #tmpStr_ = fileName.split('/' )
    #tmpStr_ = ['Decry_sample.csv', 'part-00000-6075efb5-55e2-4aa5-b178-723c58299b65-c000.csv']
    #print (tmpStr_)
    print("in putHdfsFileTmp")
    hdfsCmdList=['hadoop','fs','-put',fileName,"/tmp"]

    print(hdfsCmdList)

    hdfsCommand=subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print("out putHdfsFileTmp")     
    return    

##rm file from hdfs /tmp, 20200630
def rmHdfsFileTmp(fileName):
    
    #tmpStr_ = fileName.split('/' )
    #tmpStr_ = ['Decry_sample.csv', 'part-00000-6075efb5-55e2-4aa5-b178-723c58299b65-c000.csv']
    #print (tmpStr_)

    print("in rmHdfsFileTmp")
    print("/tmp/"+fileName)
    hdfsCmdList=['hadoop','fs','-rm',"/tmp/"+fileName]

    hdfsCommand=subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print("leave rmHdfsFileTmp")        
    return    


def rm_firstRow(df):
    rdd = df.rdd.map(lambda line: line )

    first = rdd.first()
    #print("----------first = rdd.first()-------------") 
    #print(first)
    #df_content = rdd.filter(lambda line : line != header).toDF(header)
    df_content = rdd.filter(lambda line : line != first).toDF()
    df_content.printSchema()#print (tmp.collect())
    #print(df.schema == df_content.schema) 
    return df_content

#df_schema = df.schema, df_rm = df_SaveAsHiveTable(sqlContext, dfDF, dfDF.schema, tableName)
def df_SaveAsHiveTable(sqlContext_, df_rows, df_schema, tableName):
    try:

        df_rows = sqlContext_.createDataFrame(df_rows.collect(), df_schema)

        tmpStr = "drop table If Exists "+tableName
        sqlContext_.sql(tmpStr)
        df_rows.registerTempTable("my_table")
       
        #tmpStr ="CREATE EXTERNAL TABLE IF NOT EXISTS "+tableName+" AS SELECT * from my_table"
        tmpStr ="CREATE TABLE "+tableName+" AS SELECT * from my_table"
        sqlContext_.sql(tmpStr)
    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("error in df_SaveAsHiveTable : "+str(e))
        return  
    return df_rows


def passwordCheck(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        12 characters length or more
        1 digit or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 12

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error)

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error
    }


def readLocalData(filePath, sepFormat=','):
    _logger.debug("In readLocalData")
    if len(sepFormat) == 1:
        try:
            _logger.debug("before spark.read.csv sep = "+ sepFormat)
            df = spark.read.csv(filePath, header=True, sep=sepFormat)
        except Exception as e:
            _logger.debug("error in readLocalData : " + str(e))
            _logger.debug("errTable_spark.read.csv_error")

    else:
        # for rdd map
        def transFunc(line):
            line = line.split(sepFormat)
            if line == ['']:
                return None
            else:
                return line

        try:
            print(">>>1<<<<<<<<<<<")
            #hdfs://yourcluster/user
            #hdfs://nodemasterS:9000/user/hadoop/
            
            #filePath = 'file://' + filePath
            print(filePath)
            #rdd = sc.textFile(filePath) #adult_id_ri.csv
            #hdfs://nodemasterS:9000/user/hadoop/home/hadoop/.sparkStaging/
            #filePath = ".sparkStaging/"+sc.applicationId+"/adult_id_ri.csv"
            rdd = sc.textFile(filePath)
            #rdd.take(5).foreach(print)
            firstRecord = rdd.take(1)[0]
            print(firstRecord)
            print(">>>2<<<<<<<<<<<")
            rdd1 = rdd.map(transFunc)

            print(">>>3<<<<<<<<<<<")
            rdd1 = rdd1.filter(lambda x: x is not None)
            print(">>>4<<<<<<<<<<<")
            headerRaw = rdd1.first()
            print(">>>5<<<<<<<<<<<")
            rdd2 = rdd1.filter(lambda line: line != headerRaw)
            print(">>>6<<<<<<<<<<<")
        except Exception as e:
            _logger.debug("error in readLocalData : " + str(e))
            _logger.debug("errTable_sc.textFile_error")
            #sys.exit(1)

        # Check columns number:
        headerNum = len(headerRaw)
        firstRecord = rdd2.take(1)[0]
        recordColNum = len(firstRecord)
        if headerNum != recordColNum:
            errMsg = "Data format error: number of columns and record value are not equal."
            _logger.debug(errMsg)
            raise Exception(errMsg, "Headers are {0} cols, record has {1} cols".format(headerNum, recordColNum))

        df = rdd2.toDF(headerRaw)

    # Check Double quotes
    headerValues = df.columns
    firstRecord = df.take(1)[0]
    recordValues = [str(value) for value in firstRecord]
    if len(headerValues) != len(recordValues):
        errMsg = "Data format error: number of columns and record value are not equal."
        _logger.debug(errMsg)
        raise Exception("Number of headerValues and recordValues are different.")

    _logger.debug("In checkListQuotes")
    checkListQuotes(headerValues)
    checkListQuotes(recordValues)

    _logger.debug("leave readLocalData")

    #20200227, for UnicodeEncodeError (ascii' codec can't encode characters in position 363-368)
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    df.show()

    return df




###20181016, citc add for getting key from mysql
##dbName as the school tag e.g. 'ntut'
FIXED_INPUT_LEN=5

#def main__(dbName, tblName, key_, colsNum, totalLen):
def main__(tblName, key_, colsNum, totalLen):
    '''
    get key from mysql, 
    QueryKeyBySchool, get db name & table name from loging_mysql.txt
    dbname is tag
    '''
    global sc, sqlContext, hiveLibs, _logger,spark
    _logger=_getLogger('udfMacCols')

    #20190717, citc add for FB log
    #fb_udfMacCols
    _logger_fb=_getLogger('fb_udfMacCols')

    ##############
    try:
        # Check password strength
        result = passwordCheck(key_)

        if result['password_ok'] is True:
            _logger.debug('password ok')
        else:
            msg = {
                'length_error': 'Length_error: 12 characters length or more.',
                'digit_error': 'Digit_error: 1 digit or more.',
                'uppercase_error': 'Uppercase_error: 1 uppercase letter or more.',
                'lowercase_error': 'Lowercase_error: 1 lowercase or more.',
            }
            for key in result:
                if result[key] is True:
                    _logger.debug(msg[key])
            _logger.debug('Password is not available.')
            return False

        #key_ = QueryKeyBySchool(key_)
        #_logger.debug("tag: "+dbName)
        #_logger.debug(key_)
        #print(key_)
    except ValueError:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        #_logger.debug("ERROR: get key from mysql err")
        _logger.debug("ERROR: insert key err")
        #return

    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        #_logger.debug("error in QueryKeyBySchool : "+str(e))
        _logger.debug("error in passwordCheck : " + str(e))
        _logger.debug("errTable_errSC")
        #return
    #############

    '''
    #key_ = "Bar12345Bar12345Bar12345Bar12345"
    #hiveLibs.dbOperation.registerTempTable_forsparksql(retDF,  "DF_Table__")

    ###20181016, citc add for getting key from mysql
    ##dbName as the school tag e.g. 'ntut'
    try:
        dbName = 'ntut'
        key_ = QueryKeyBySchool(dbName)
        #_logger.debug("school tag"+dbName)
        #_logger.debug(key_)
        #print(key_)
    except ValueError:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("ERROR: get key from mysql err")
        #return

    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("error in QueryKeyBySchool : "+str(e))
        _logger.debug("errTable_errSC")
        #return
    '''
    ###################
    
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
    #tableName="udfMacUID_"+tblName
    tableName = "mac_" + tblName

    
    '''
    get new sc and combining sc and citc hive lib
    '''
    # 本地資源運算
    appName = 'udfMacUID'
    master = 'yarn'
    #master = 'yarn-client'
    #/gau_working/pysparkWorking/sqljdbc4-2.0.jar
    try:
       #citc, for spark 2.0 
       spark_ = SparkSession.builder.enableHiveSupport().master('yarn').appName(appName).config("spark.yarn.preserve.staging.files","false").getOrCreate()
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



        #subprocess.run(["scp", FILE, "USER@SERVER:PATH"])
        #subprocess.run(["scp", path_, "node2:"+path_])
        #scp adult_id.csv  node3:~/proj_/dataMac/input/


        path_ = "/home/hadoop/proj_/dataMac/input/" + tblName + ".csv"
        _logger.debug("Input path: " + path_)

        #20190717, add fo fb log
        _logger_fb.debug("============start======================")
        _logger_fb.debug("input file: " + path_)
        _logger_fb.debug("columns name will be maced: " + str(columns_))

        retDF, headerDict = readFrom_csv_wit_NA_Normalize(path_, sep)
        if retDF is not None:
            #retDF.show()
            _logger.debug(" readFrom_csv OK")
        else:
            print("retDF is null")
            _logger.debug("retDF is null, readFrom_csv_wit_NA_Normalize err")
            return
        _logger_fb.debug("============start2======================")
        if 0:
            tblName = 'input/' + tblName
            file_path = getHdfsFilePath(tblName)
            if file_path is not None:       
                
                print(file_path)
                _logger.debug(file_path)
                print("2_")

                #citc, add 20190122#############################
                retDF = readFrom_csv_wit_NA_Normalize(file_path, sep)
                #retDF = readFrom_csv(file_path)
                ################################################

                if retDF is not None:
                    #retDF.show()
                    _logger.debug(" readFrom_csv OK")
                else:
                    print("retDF is null")
                    _logger.debug("retDF is null, readFrom_csv_wit_NA_Normalize err")  
                    return 
            else:
                print("file_path is null")
                _logger.debug("file_path is null, readFrom_csv_wit_NA_Normalize err")  
                return 


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

    ###########20181015, citc mve here for async()############
    #itri, output k table name (does not change the code about_logger code)
    #str.replace("is", "was");
    tmp = tableName.split(".")
    _logger.debug('###################out udfMac table name')

    return_str = tmp[0].replace("/", "_")
    return_str = "citc____"+return_str

    _logger.debug(return_str)
    #print('###################out udfEnc table name')
    #print(tableName)

    #itri, output k application id (does not change the code about_logger code)
    _logger.debug('###################sc.applicationId')
    return_str= sc.applicationId
    return_str = "citc____"+return_str

    _logger.debug(return_str)
    ##########20181015, citc add for async(), end####################################



    try: 
        #_logger.debug("2_______________")
        cols=[]
        
        cols=columns_#['y']
        for i in range(len(headerDict)):
            for j in range(len(cols)):
                if cols[j] == headerDict["col_"+str(i)]:
                    cols[j] = "col_"+str(i)
        #cols = [headerDict[col] for col in cols]

        '''
        20190104, citc add
        tableName is used as (id, id hash) database name
             hence, the tableName can not include '.', otherwise mysql will throw exceptions 
        '''
        tmp = tableName.split(".")
        #print(tmp)
        tableName =tmp[0].replace("/", "_") 
        dfDF=udfMacCols(cols, retDF, key_,tableName, headerDict)
        
        #####20190718 mark
        #dfDF.show()
        #tableName="udfEncTable_"+tblName, in above
        #dfDF.write.format("orc").mode("overwrite").saveAsTable(tableName)
        tableName_csv = tableName+".csv"
        #dfDF.coalesce(1).write.csv(tableName_csv)
     
        '''
        citc, output DF (result) to 
              1. csv file in hadoop
              2. hive table
              3. csv file in host (master)             
        '''

        if 0:
            #1. output DF to csv file in hadoop
            dfDF.coalesce(1).write.option("header", "true").csv(tableName_csv)
            #2. output DF to hive table
            df_rm = df_SaveAsHiveTable(sqlContext, dfDF, dfDF.schema, tableName)

            #3. output DF to csv file in host (master)
            #output encryption result as csv file and put into master(namenode)
            fileName = getHdfsFilePath(tableName_csv)
            #print(fileName)
            #_logger.debug(fileName)
            getHdfsFile(fileName)
        else:
            # output path
            path_ = "/home/hadoop/proj_/dataMac/output"
            _logger_fb.debug("Output path: " + path_+"/"+tableName)

            #20190717, add fo fb log
            #_logger_fb.debug("out file: " + path_)

            # get columns
            headers = dfDF.columns

            headers = [headerDict[headers[i]] for i in range(len(headers))]
 
            projName = ""
            result = exportData(projName, dfDF, headers, tableName, path_)
            if result['result'] == 0:
                _logger.debug("export data error.")
                _logger.debug(result['msg'])
            else:
                _logger.debug("export data succeed.")
                _logger.debug(result['msg'])

                #print(cols)

                #print(headers)
                #tmpDF= dfDF.select([col(column_) for column_ in cols if size(col(column_)) < 40])
                #tmpDF= dfDF.select([col(column_) for column_ in cols])

                for column_ in cols:
                    #print(sys.stdout.encoding)
                    #print(headerDict[column_])
                    _logger_fb.debug("column name: " + headerDict[column_])
                    tmpDF= dfDF.select(col(column_))
                    total_length = tmpDF.count()
                    tmpDF = tmpDF.where(length(col(column_)) < 40)
                    anormal_length = tmpDF.count()
                    _logger_fb.debug("anormal count: " + str(anormal_length)+" normal count: " + \
                        str(total_length-anormal_length)+" total count: " + str(total_length))
                    #tmpDF.show(10)
                

                rmHdfsFileTmp(tblName + ".csv")
                _logger_fb.debug("============end=======================")
                #returnMsg = [msg for msg in returnMsg if "WARN" not in msg]
                #tmpDF = dfDF.where(size(col(cols[0])) < 40)
                #tmpDF.show(2)

                ##########################################################
                #20190717, citc add for report maced result
                #_logger_fb.debug("export data succeed.")
                #_logger_fb.debug("input file: " + path_)
                #tmpDF = dfDF.where(size(col('col_0')) < 40)
                #tmpDF.show(2)

                ##########################################################
        
    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_err_udfEncCols()")
        return
        #_logger.debug("error in kchecking : "+str(e)) 

if __name__ == "__main__":

    tblName = sys.argv[1]
    key =  sys.argv[2]
    sep = sys.argv[3]
    colsNum = sys.argv[4]
    totalLen = len(sys.argv)
    
    print('########')
    print(tblName)
    print(sep)
    print(colsNum)
    print(totalLen)
    print('#############')
    
    main__(tblName, key, colsNum, totalLen)
 