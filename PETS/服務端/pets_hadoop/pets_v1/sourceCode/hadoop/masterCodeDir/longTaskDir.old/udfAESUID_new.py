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


from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#20200318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus
#20210119 aes key
import subprocess
####################################################################################
#20190718, mark for logging error (ValueError: underlying buffer has been detached)

if "UTF-8" in sys.stdout.encoding:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
###################################################################################

#20210119 aes key
def doCommand_( hdfsCmdList):
    dp = subprocess.Popen(hdfsCmdList,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True, universal_newlines=True )
    ret = dp.communicate()

    for item in ret:
        item = item[0:-1]
        #print(item)
        #print(len(item))

        if "sudo" not in item:
            if(len(item) > 0):
                ret = item
                break
    return ret

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
        # _logger.debug("path_: {0}".format(path_))
        # _logger.debug("sep: {0}".format(sep))

        fileExist = checkFileExist(path_)
        if not fileExist:
            _logger.debug("File is not exist.")
            _logger.debug("err in readFrom_csv_wit_NA_Normalize")
            #citc, add for file not exist, 20220308
            _logger.debug("errTable_not_fileExist") #citc, 0308, do this return error to tak_udfAESUID.py
            return None, None
        df = readLocalData(path_spark, sepFormat=sep)

        # Convert col_cht to col_en
        headerRaw = df.columns
        headerTmp = ["col_"+str(i) for i in range(len(headerRaw))]
        headerDict = dict()
        for i in range(len(headerTmp)):
            headerDict[headerTmp[i]] = headerRaw[i]

        # _logger.debug("Check headerRaw and headerTmp")
        # _logger.debug(headerDict)
        # _logger.debug(headerRaw)
        # _logger.debug(headerTmp)

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
def udfMacCols(encList, df, key_, idHashDBName, headerDict, isEnc_):
    
    # _logger.debug("in udfMacCols")
    # _logger.debug(encList)
    #####citc, 20181015 add for spark 2.0############
    #sqlContext.sql("use test_import_all")
    #df.write.format("orc").mode("overwrite").saveAsTable("DF_Table__")
    df.registerTempTable("DF_Table__")
    #sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfMac'")
    if(isEnc_ == 1):
        sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfEnc'")
    else:
        sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfDec'")
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
    print (tmpStr)
    # _logger.debug(tmpStr)
    
    
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
    #citc, modified 20220308, 32 -> 64
    # calculating the length
    length_error = len(password) != 64 #32

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    #lowercase_error = re.search(r"[a-z]", password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error )

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        #'lowercase_error' : lowercase_error
    }


def readLocalData(filePath, sepFormat=','):
    _logger.debug("In readLocalData")
    if len(sepFormat) == 1:
        try:
            ##citc, the following instruction rn double quote 20220118
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
            rdd = sc.textFile(filePath)

            rdd1 = rdd.map(transFunc)
            rdd1 = rdd1.filter(lambda x: x is not None)

            headerRaw = rdd1.first()

            rdd2 = rdd1.filter(lambda line: line != headerRaw)
        except Exception as e:
            _logger.debug("error in readLocalData : " + str(e))
            _logger.debug("errTable_sc.textFile_error")

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

    return df

#20200604
#updateToMysql(projID, projName, tblName, sampleStr)
def updateToMysql(projID, projName, table, data):
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False
    # insert to sample data
    condisionSampleData = {
        'project_id': projID,
        'dbname': projName,
        'tbname': table
    }

    valueSampleData = {
        'project_id': projID,
        'dbname': projName,
        'tbname': table,
        'data': data
    }
    # def updateValue(self, dbName, tblName, conditions, setColsValue):
    resultSampleData = conn.updateValueMysql('DeIdService',
                                             'T_ProjectSampleData',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        _logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
    else:
        msg = resultSampleData['msg']
        _logger.debug('insertSampleDataToMysql fail: ' + msg)


#20200608
#updateToMysql(projID, projName, tblName, sampleStr)
def updateToMysql_table(projID, projName, table):
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False
    # insert to sample data
    condisionSampleData = {
        'project_id': projID
    }

    valueSampleData = {
        'project_id': projID,
        'dbname': projName,
        'tbname': table 
    }
    # def updateValue(self, dbName, tblName, conditions, setColsValue):
    resultSampleData = conn.updateValueMysql('DeIdService',
                                             'T_ProjectSampleData',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        _logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
    else:
        msg = resultSampleData['msg']
        _logger.debug('insertSampleDataToMysql fail: ' + msg)

def doCommand(hdfsCmdList):
    hdfsCommand = subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    errLines = hdfsCommand.stderr.readlines()
    print(errLines)
    # _logger.debug(errLines)
    msg = list()
    for line in errLines:
        if line.decode('utf-8') is not None:
            msg.append(str(line))

    return ','.join(msg)



###20181016, citc add for getting key from mysql
##dbName as the school tag e.g. 'ntut'
FIXED_INPUT_LEN=5

#def main__(dbName, tblName, key_, colsNum, totalLen):
# def main__(tblName, key_, colsNum, totalLen,columns_mac):
def main__(tblName, key_,columns_mac,projName,projID,dataHash, onlyHash):

    '''
    get key from mysql, 
    QueryKeyBySchool, get db name & table name from loging_mysql.txt
    dbname is tag
    '''
    global sc, sqlContext, hiveLibs, _logger,spark,updateAppStatus_,updateTProjectStatus_
    _logger=_getLogger('AES_Enc')

    #20190717, citc add for FB log
    #fb_udfMacCols
    _logger_fb=_getLogger('AES_Enc')
    _logger_fb.debug("============AES_Enc start=======================")

    # log input
    _logger.debug('spark_import_dbName_%s',projName)
    _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_projID_%s',projID)
    ##############
    try:
     
        updateTProjectStatus_ = updateTProjectStatus(projID)
    except Exception as e:
        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False    
    

    ############    
    # _logger.debug("----key_ = {}".format(key_))
    # _logger.debug("----key_ length = {}".format(len(key_)))
    try:
        # Check password strength
        result = passwordCheck(key_)

        if result['password_ok'] is True:
            _logger.debug('password ok')
        else:
            msg = {
                'length_error': 'Length_error: 32 characters length.',
                'digit_error': 'Digit_error: 1 digit or more.',
                'uppercase_error': 'Uppercase_error: 1 uppercase letter or more.',
                #'lowercase_error': 'Lowercase_error: 1 lowercase or more.',
            }
            for key in result:
                if result[key] is True:
                    _logger.debug(msg[key])
            _logger.debug('Password is not available.')
            raise Exception('Password is not available.')
            #return False

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
    # colsNum
    # colsNum_=0
    # try:
    #     colsNum_=int(colsNum)
    # except ValueError:
    #     _logger.debug("column length error")
    #     #return


    #
    # update 20200526
    #
    # if totalLen-FIXED_INPUT_LEN != colsNum_:
    #      _logger.debug("column length error_1")
    # #argList =str(sys.argv)
    # #print argList
    
    # #print (sys.argv[-1])
    # #print (sys.argv[FIXED_INPUT_LEN])


    # columns_=sys.argv[FIXED_INPUT_LEN: -1]
    # columns_.append(sys.argv[-1])

    columns_ = columns_mac.split(',')
    _logger_fb.debug("columns name will be maced: " + str(columns_))


    if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
        tableName = "mac_" + tblName
        #onlyHash = "No" for encryption
    else:
        tableName = tblName
    #tableName="udfMacUID_"+tblName
    #tableName = "mac_" + tblName

    
    '''
    get new sc and combining sc and citc hive lib
    '''
    # 本地資源運算
    #appName = 'udfMacUID'
    appName = 'AES_Enc'
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
    try: #add for checking app status(write to mysql)##############

        updateAppStatus_ = updateAppStatus(sc.applicationId, appName,projName,projID)
    except Exception as e:
        
        _logger.debug('updateAppStatus error: %s', str(e))
        return False
    updateAppStatus_.updateToMysql("Init_1","5")

    retDF = None
    try:

        #columns_ = [value1, value2]
        #_logger.debug(columns_)
        #citc 20181015, tblName as path_tblName
        isEnc = 1
###########################################################################
        if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
            # onlyHash = "No" for encryption
            isEnc = 1
            path_ = "/home/hadoop/proj_/dataMac/input/" + tblName + ".csv"
            # _logger.debug("Input path: " + path_) #Input path: /home/hadoop/proj_/dataMac/input/adult_id.csv
        else:
            # onlyHash = "yes" for decryption
            isEnc = 0
            #citc, 20220308, change for input path
            #path_ = "/home/hadoop/proj_/dataMac/output/"+"mac_"+ tblName+"/"+"mac_"+ tblName + ".csv"
            path_ = "/home/hadoop/proj_/dataMac/input/" + tblName + ".csv"
            _logger.debug("Input path: " + path_) #Input path: /home/hadoop/proj_/dataMac/output/mac_adult_id/mac_adult_id.csv
            _logger.debug("----for decry----isEnc: " + str(isEnc)) 
            print("Input path: " + path_) #Input path: /home/hadoop/proj_/dataMac/output/mac_adult_id/mac_adult_id.csv
            print("----for decry----isEnc: " + str(isEnc))

###########################################################################

        #20190717, add fo fb log
        # _logger_fb.debug("============start======================")
        # _logger_fb.debug("input file: " + path_)
        # _logger_fb.debug("columns name will be maced: " + str(columns_))

        retDF, headerDict = readFrom_csv_wit_NA_Normalize(path_, sep)
        if retDF is not None:
            retDF.show()
            _logger.debug(" readFrom_csv OK")
            print(" readFrom_csv OK")
        else:
            print("retDF is null")
            _logger.debug("retDF is null, readFrom_csv_wit_NA_Normalize err")

            errmsg = "FileIsNull"
            updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus
            updateTProjectStatus_.updateToMysql(projID, 99,"error") #err: update projStatus

            return
        # _logger_fb.debug("============start2======================")
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
                    errmsg = "FileIsNull"
                    updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus
                    updateTProjectStatus_.updateToMysql(projID, 99,"error") #err: update projStatus
                    return 
            else:
                print("file_path is null")
                _logger.debug("file_path is null, readFrom_csv_wit_NA_Normalize err")  
                errmsg = "FilePathIsNull"
                updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus
                updateTProjectStatus_.updateToMysql(projID, 99,"error") #err: update projStatus
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
    # _logger.debug('###################out udfAESUID_new table name')

    return_str = tmp[0].replace("/", "_")
    return_str = "citc____"+return_str

    # _logger.debug(return_str)
    #print('###################out udfEnc table name')
    #print(tableName)

    #itri, output k application id (does not change the code about_logger code)
    _logger.debug('###################sc.applicationId')
    return_str= sc.applicationId
    #return_str = "citc____"+return_str #citc____application_****_0001
    #citc, modified for task_udfAESUID.py (line 180)
    #if "sc.applicationId:" in  line: 

    #itri, output k application id (does not change the code about_logger code)##########
    return_str = "sc.applicationId:"+return_str #sc.applicationId:application_****_0001
    _logger.debug(return_str)
    #####################################################################################

    ##########20181015, citc add for async(), end####################################
    project_status =40
    # statusname='資料集直接識別AES加密中'
    statusname='AESing'

    # statusname='Hash'
    updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
    # updateAppStatus_.updateToMysql("Mac_data","100")
    updateAppStatus_.updateToMysql("read csv","40")


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

        #20200611
        #if df some col hash or not 
        # _logger_fb.debug("---1--dataHash: {}" + dataHash)
        if dataHash == "yes" or dataHash == "Y" or dataHash == "y"  or dataHash == "YES"  or dataHash == "Yes"   :
            #_logger.debug("---++++--retDF: {}" + retDF)
            print("----------retDF----------")
            retDF.show()
            print("---++++--cols: {}".format(cols))
            print("---++++--key_: {}".format(key_))
            print("---++++--isEnc: {}".format(str(isEnc))) 
            _logger.debug("---++++--cols: {}".format(cols))
            _logger.debug("---++++--key_: {}".format(key_))
            _logger.debug("---++++--isEnc: {}".format(str(isEnc))) 
            dfDF=udfMacCols(cols, retDF, key_,tableName, headerDict, isEnc)
        else : 
            dfDF = retDF

        #####20190718 mark
        dfDF.show()
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
            # _logger_fb.debug("---0000--onlyHash: {}" + onlyHash)
            #onlyHash = "No"
            if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
                       # _logger_fb.debug("Output path: " + path_+"/"+tableName)
            # onlyHash = "No" for encryption
                path_ = "/home/hadoop/proj_/dataMac/output"
                tableName_ =tableName
            else:
                # onlyHash = "yes" for decryption
                path_ = "/home/hadoop/proj_/dataMac/output"
                tableName_ ="dec_"+tableName
                
            # output path 
            _logger_fb.debug("---2--dataHash: {}".format(dataHash))
            _logger_fb.debug("---2--onlyHash: {}".format( onlyHash))
            _logger_fb.debug("---33333--tableName_: {}".format( tableName_))
            _logger_fb.debug("Output path: " + path_)


            #20190717, add fo fb log
            #_logger_fb.debug("out file: " + path_)

            # get columns
            headers = dfDF.columns

            headers = [headerDict[headers[i]] for i in range(len(headers))]
 
            proj_Name = ""
            result = exportData(proj_Name, dfDF, headers, tableName_, path_)
            if result['result'] == 0:
                _logger.debug("export data error.")
                _logger.debug(result['msg'])
            else:
                _logger.debug("export data succeed.")
                # _logger.debug(result['msg'])
                # _logger.debug(type(result['msg']))

                # b"mkdir: `output': File exists\n";b"mkdir: `output': File exists\n";b"mkdir: `output/dec_mac_adult_id': File exists\n"


                #print(cols)

                #print(headers)
                #tmpDF= dfDF.select([col(column_) for column_ in cols if size(col(column_)) < 40])
                #tmpDF= dfDF.select([col(column_) for column_ in cols])
                if cols == [""]:
                    pass
                else:
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
                '''
                if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
                    try:
                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','itribd:itribd',"/home/hadoop/proj_/data/input"])
                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','1001:1001',"/home/hadoop/proj_/data/input"])

                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','itribd:itribd',"/home/hadoop/proj_/dataMac/output"])
                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','1001:1001',"/home/hadoop/proj_/dataMac/output"])

                        data_input_path_project = "/home/hadoop/proj_/data/input"+"/"+projName
                        doCommand([ 'mkdir', data_input_path_project])
                        # _logger.debug(data_input_path_project)

                        data_input_path_mac = data_input_path_project + "/" + tableName
                        doCommand([ 'mkdir', data_input_path_mac])
                        # _logger.debug(data_input_path_mac)

                        data_input_path_new = data_input_path_mac+"/"+tableName+".csv"
                        path_new = path_ +"/"+tableName+"/"+tableName+".csv"
                        doCommand(['cp', path_new, data_input_path_new])
                        # _logger.debug(data_input_path_new)
                        # _logger.debug("---path_new="+path_new)
                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','hadoop:hadoop',"/home/hadoop/proj_/data/input"])
                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','hadoop:hadoop',"/home/hadoop/proj_/dataMac/output"])

                    except Py4JJavaError as e:
                        # doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','waue:waue',"/home/hadoop/proj_/data/input"])
                        doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','hadoop:hadoop',"/home/hadoop/proj_/data/input"])
                        doCommand([ 'echo','media@scidm','|','sudo','-S','chown','-R','hadoop:hadoop',"/home/hadoop/proj_/dataMac/output"])

                        s = e.java_exception.toString()
                        _logger.debug(s)
        
                else:
                    pass
                '''
                #path_new = path_ +"/"+tableName+"/"+tableName+".csv"
                #out_dir_path = str(result['msg'])
                out_dir_path = path_ +"/"+tableName_

                ###########
                ######itri, output outt_dir_path for task_udfAESUID.py (does not change the code about_logger code)##########
                _logger_fb.debug("============end======================="+out_dir_path) #####################################
                #############################################################################################################

                _logger_fb.debug("============AES_Enc end=======================")
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
                # updateToMysql_table(projID, projName, tblName)
                # updateTProjectStatus  
                project_status =1
                # statusname='直接識別Hash完成'
                statusname='AES_F'

                updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
                updateAppStatus_.updateToMysql("AES UID Success","100",progress_state="Finished")


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

    #citc, 20220117 add
    key =  sys.argv[2]

    sep = sys.argv[3]
    # colsNum = sys.argv[4]
    columns_mac = sys.argv[4]
    projName =sys.argv[5]
    projID = sys.argv[6] 
    dataHash = sys.argv[7]
    onlyHash = sys.argv[8]

    totalLen = len(sys.argv)

    #20220117, citc mark
    #key =  "2B7E151628AED2A6ABF7158809CF4F3C" #doCommand_("echo citcw200@|sudo -S cat /sys/class/dmi/id/board_serial | head -n 1")#"2B7E151628AED2A6ABF7158809CF4F3C"

    print('########')
    print(tblName)
    print(sep)
    # print(colsNum)
    print(totalLen)
    print(key)

    print('#############')
    
    # main__(tblName, key, colsNum, totalLen,columns_mac)
    main__(tblName, key,columns_mac,projName,projID,dataHash, onlyHash)

