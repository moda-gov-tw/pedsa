#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,length
from py4j.protocol import Py4JJavaError
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.loginInfo import getLoginMysql,getGroupType
import pymysql
import subprocess
from MyLib.parseData import exportData, checkListQuotes,exportDataMac
import os.path
import io , sys


from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#20200318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus


####################################################################################
#20190718, mark for logging error (ValueError: underlying buffer has been detached)

if "UTF-8" in sys.stdout.encoding:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
###################################################################################

#20231108,add group type
def GetGroupType():
    _logger.debug("in GetGroupType")
    
    try:
        group_type = getGroupType('/home/hadoop/proj_/longTaskDir/group_type.txt')   
    except Exception as e:
        errMsg = 'getGroupType_error:'+str(e)
        _logger.debug(errMsg)
        raise Exception('getGroupType_error', errMsg)
    
    return group_type
    
    
    

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

####20230107# remove hdfs tmp file##start#####                
def remove_hdfs_tmp_file(input_file_basename):
    ####20230107# remove hdfs tmp file##start#####
    input_file_basename_ = input_file_basename            
    try:

        #input_file_basename = os.path.basename(path_)
        hdfs_path=os.path.join('/tmp',  input_file_basename_)
        _logger.debug("remove hdfs_path = {}".format(hdfs_path))

        result = doCommand(['hadoop', 'fs', '-rm', '-f', hdfs_path])
        _logger.debug("remove hdfs file result = {}".format(result))
        return 1
    except Exception as e:
        _logger.debug("remove file to hdfs fail: "+str(e))
        return -1
    
####20230107# remove hdfs tmp file###end####



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

        #20230107########icl put local file to hdfs###################3
        hdfs_path=""
        try:
           # tmpPath = getHdfsFilePath('/tmp')
           #  _logger.debug("AAAAAtmpPath = {}".format(tmpPath))
            file_name = os.path.basename(path_)
            hdfs_path=os.path.join('/tmp',  file_name)
            _logger.debug("BBBB hdfs_path = {}".format(hdfs_path))
        
            result = doCommand(['hadoop', 'fs', '-put', '-f', path_spark, hdfs_path])
            _logger.debug("BBBBresult = {}".format(result))
        except Exception as e:
            _logger.debug("put file to hdfs fail: "+str(e))
            return None, None
            #return {'msg': str(e), 'result': 0, 'df': None}    



        df = readLocalData(hdfs_path, sepFormat=sep)

        # Convert col_cht to col_en
        headerRaw = df.columns
        headerTmp = ["col_"+str(i) for i in range(len(headerRaw))]
        headerDict = dict()
        for i in range(len(headerTmp)):
            headerDict[headerTmp[i]] = headerRaw[i]

        _logger.debug("Check headerRaw and headerTmp")
        _logger.debug(headerDict)
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

def udfMacCols(AES_encList=[],MAC_encList=[], df=None,AES_key=None,MAC_key=None, idHashDBName=None, headerDict=None, isEnc_=None):
    
    _logger.debug("in udfMacCols")
    # _logger.debug(encList)
    #####citc, 20181015 add for spark 2.0############
    #sqlContext.sql("use test_import_all")
    #df.write.format("orc").mode("overwrite").saveAsTable("DF_Table__")
    df.registerTempTable("DF_Table__")
    #sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfMac'")

    # MAC_key = AES_key

    # if(isEnc_ == 1):
    #     sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfEnc'")
    # elif(isEnc_ == 0):
    #     sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfDec'")
    # else:    
    #     sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfMac'")
    #     _logger.debug("we are in else")
    
    sqlContext.sql("create temporary function udfMac_ as 'citc.udfEncrypt.udfMac'")
    sqlContext.sql("create temporary function udfAes_ as 'citc.udfEncrypt.udfEnc'")
    


    #######################################################3
    #key_ = "Bar12345Bar12345Bar12345Bar12345"
    cols = df.columns
    tmpStr="select "
    _logger.debug("col finishy")

    _logger.debug("AES and MAC = "+str(AES_encList) + ' ' + str(MAC_encList))
    '''
    select udfMac_(COUNTY_ID, "Bar12345Bar12345Bar12345Bar12345") as COUNTY_ID,
            udfMac_(COUNTY, "Bar12345Bar12345Bar12345Bar12345") as COUNTY,
            FLD01,FLD02,FLD03,INFO_TIME 
            from DF_Table__
    '''

    _logger.debug("col name before")

    _logger.debug("MAC_KEY = " + str(MAC_key))
    for colNam_ in cols:
        if colNam_ in cols[-1:]:
            if colNam_ not in AES_encList and colNam_ not in MAC_encList:
                tmpStr=tmpStr+ colNam_+" from DF_Table__"
            else:
                if colNam_ in AES_encList:
                    tmpStr=tmpStr+ colNam_ + " as "+colNam_+"__, "+"udfAes_("+colNam_+", \""+AES_key+"\") as "+colNam_+" from DF_Table__"

                    # _logger.debug("col -1 in AES_enclist")
                else:
                    tmpStr=tmpStr+ colNam_ + " as "+colNam_+"__, "+"udfMac_("+colNam_+", \""+MAC_key+"\") as "+colNam_+" from DF_Table__"
                    # _logger.debug("col -1 in MAC_enclist")

            break;
        if colNam_ not in AES_encList and colNam_ not in MAC_encList:
            tmpStr=tmpStr+ colNam_+","
        else:
            if colNam_ in AES_encList:
                tmpStr=tmpStr+ colNam_ + " as "+colNam_+"__, "+"udfAes_("+colNam_+", \""+AES_key+"\") as "+colNam_+","
                # _logger.debug("col else in AES_enclist")
            else:
                tmpStr=tmpStr+ colNam_ + " as "+colNam_+"__, "+"udfMac_("+colNam_+", \""+MAC_key+"\") as "+colNam_+","
                # _logger.debug("col -1 in MAC_enclist")

    

    df2=sqlContext.sql(tmpStr)

     
    df3 = df2[cols]

    _logger.debug("df3 head =" + str(df3.columns) )
    ######20190718, mark
    #df3.show()
    
    #CreateMysqlDB(idHashDBName)
    _logger.debug("before extend")
    # enc_list =[]
    # for item in AES_encList:
    #     enc_list.append(item)
    # for item in MAC_encList:
    #     enc_list.append(item)

    _logger.debug(str(AES_encList))

    
    for colNam_ in AES_encList :
        tmpList = []
        
        _logger.debug("before tmpList")

        tmpList.append(colNam_)
        tmpStr = colNam_+"__"
        tmpList.append(tmpStr)

        _logger.debug("after tmpList")
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


def AES_passwordCheck(password):
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
    length_error = len(password) != 64 #32

    # searching for digits
    # digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    # uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    # lowercase_error = re.search(r"[a-z]", password) is None

    # overall result
    # password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error)
    # password_ok = not ( length_error or digit_error or uppercase_error)
    password_ok = not ( length_error )

    # return {
    #     'password_ok' : password_ok,
    #     'length_error' : length_error,
    #     'digit_error' : digit_error,
    #     'uppercase_error' : uppercase_error,
    #     'lowercase_error' : lowercase_error
    # }
    return {
        'password_ok' : password_ok,
        'length_error' : length_error#,
        # 'digit_error' : digit_error,
        # 'uppercase_error' : uppercase_error
    }
    

def Mac_passwordCheck(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        12 characters length or more
        1 digit or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    length_error = len(password) < 12

    password_ok = not ( length_error )

    return {
        'password_ok' : password_ok,
        'length_error' : length_error#,
        # 'digit_error' : digit_error,
        # 'uppercase_error' : uppercase_error
    }
    
    
def readLocalData(filePath, sepFormat=','):
    _logger.debug("In readLocalData")
    if len(sepFormat) == 1:
        try:
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
    
    _logger.debug("header valuse = "+str(headerValues))
    firstRecord = df.take(1)[0]
    recordValues = [str(value) for value in firstRecord]
    if len(headerValues) != len(recordValues):
        errMsg = "Data format error: number of columns and record value are not equal."
        _logger.debug(errMsg)
        raise Exception("Number of headerValues and recordValues are different.")

    _logger.debug("In checkListQuotes header")
    checkListQuotes(headerValues)
    _logger.debug("In checkListQuotes record")
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


def main__(tblName,Mac_hashkey,MAC_columns_mac,projName,projID,dataHash, onlyHash,AES_hashkey,AES_columns_mac,userId,userAccount):
    tets = 11
    global sc, sqlContext, hiveLibs, _logger,spark #,updateAppStatus_,updateTProjectStatus_
    
    _logger=_getLogger('AES_Enc')

    #20190717, citc add for FB log
    #fb_udfMacCols
    _logger_fb=_getLogger('AES_Enc')

    # log input
    _logger.debug('Mac_hashkey:%s',Mac_hashkey)
    _logger.debug('MAC_columns_mac:%s',MAC_columns_mac)
    _logger.debug('AES_hashkey:%s',AES_hashkey)
    _logger.debug('AES_columns_mac:%s',AES_columns_mac)
    _logger.debug('onlyHash:%s',onlyHash)


    _logger.debug('spark_import_dbName_%s',projName)
    _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_projID_%s',projID)

    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_userId_%s',userId)
    
    group_type = GetGroupType()
    
    _logger.debug('group_type = %s',group_type)
    
    ##############
    # try:
     
    #     updateTProjectStatus_ = updateTProjectStatus(projID,userId)
    # except Exception as e:
        
    #     _logger.debug('updateTProjectStatus error: %s', str(e))
    #     return False   
     
    ##############
    
    _logger.debug('AES key : %s', str(AES_hashkey))
    _logger.debug('Mac key : %s', str(Mac_hashkey))
    
    #---------------------------Check the AES_hashkey------------------
    
    if AES_hashkey != None:
        try:
            # Check password strength
            result = AES_passwordCheck(AES_hashkey)

            if result['password_ok'] is True:
                _logger.debug('AES password ok')
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
                _logger.debug('AES Password is not available.')
                raise Exception('AES Password is not available.')
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
            _logger.debug("ERROR: insert AES key err")
            #return

        except Exception as e:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(len(sys.exc_info()))
            #_logger.debug("error in QueryKeyBySchool : "+str(e))
            _logger.debug("error in AES_passwordCheck : " + str(e))
            _logger.debug("errTable_errSC")
    
    
    #---------------------------Check the Mac_hashkey------------------
    
    
    if Mac_hashkey != None:
        
        try:
            # Check password strength
            result = Mac_passwordCheck(Mac_hashkey)

            if result['password_ok'] is True:
                _logger.debug('Mac password ok')
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
                _logger.debug('Mac Password is not available.')
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
            _logger.debug("ERROR: insert Mac key err")
            #return

        except Exception as e:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(len(sys.exc_info()))
            #_logger.debug("error in QueryKeyBySchool : "+str(e))
            _logger.debug("error in Mac_passwordCheck : " + str(e))
            _logger.debug("errTable_errSC")
            
    if AES_columns_mac == "_NODIRDATA":
        AES_columns_ = []
    elif AES_columns_mac == "":
        AES_columns_ = []
    else:
        AES_columns_ = AES_columns_mac.split(',')
        
    _logger_fb.debug("AES columns name will be maced: " + str(AES_columns_))
    
    if MAC_columns_mac == "_NODIRDATA":
        MAC_columns_ = []
    elif MAC_columns_mac == "":
        MAC_columns_ = []
    else:
        MAC_columns_ = MAC_columns_mac.split(',')
        
    _logger_fb.debug("MAC columns name will be maced: " + str(MAC_columns_))
    
    # if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
    #     tableName = "mac_" + tblName
    #     #onlyHash = "No" for encryption
    # else:
    #     tableName = tblName

    #     data_output_project_path = "/home/hadoop/proj_/data/output/"+ projName + "/" + tableName + ".csv"
    #     dataMac_input_path = "/home/hadoop/proj_/dataMac/input"+"/"+tableName+".csv"
    #     doCommand(['cp', data_output_project_path, dataMac_input_path])
    
    tableName = str(group_type) + '_' + tblName + '_enc'
    
    if (not (onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO")):
        tableName = tblName
        data_output_project_path = "/home/hadoop/proj_/data/output/"+ projName + "/" + tableName + ".csv"
        dataMac_input_path = "/home/hadoop/proj_/dataMac/input"+"/"+tableName+".csv"
        doCommand(['cp', data_output_project_path, dataMac_input_path])
        
        
    '''
    get new sc and combining sc and citc hive lib
    '''
    # 本地資源運算
    #appName = 'udfMacUID'
    appName = 'MAC_AES_Enc'
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
        _logger.debug("error in fundation of MAC_AES_Enc : "+str(e))
        _logger.debug("errTable_errSC")
        return    
    spark = spark_
    sc= sc_
    sqlContext = sqlContext_
    hiveLibs = hiveLibs_
    
    
    """
    tblName is used as file path
    """
    # try: #add for checking app status(write to mysql)##############

    #     updateAppStatus_ = updateAppStatus(sc.applicationId, appName,projName,projID,userId)
    # except Exception as e:
        
    #     _logger.debug('updateAppStatus error: %s', str(e))
    #     return False
    # updateAppStatus_.updateToMysql("Init_1","5")

    retDF = None
    
    try:
        #columns_ = [value1, value2]
        #_logger.debug(columns_)
        #citc 20181015, tblName as path_tblName
        
        isEnc = 1
        if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
            # onlyHash = "No" for encryption
            isEnc = 1
            
        else:
            # onlyHash = "yes" for decryption
            isEnc = 0
            #citc, 20220308, change for input path
            #path_ = "/home/hadoop/proj_/dataMac/output/"+"mac_"+ tblName+"/"+"mac_"+ tblName + ".csv"

        path_ = "/home/hadoop/proj_/dataMac/input/" + tblName + ".csv"
        
        cmd = 'echo "citcw200@" | sudo -S chown hadoop:hadoop '+ path_
        # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName
        _logger.debug("cmd is {0}".format(str(cmd)))
        runcode = os.system(cmd)
        _logger.debug("run result is {0}".format(str(runcode)))



        _logger.debug("Input path: " + path_) #Input path: /home/hadoop/proj_/dataMac/output/mac_adult_id/mac_adult_id.csv
        _logger.debug("----for decry----isEnc: " + str(isEnc)) 
        # print("Input path: " + path_) #Input path: /home/hadoop/proj_/dataMac/output/mac_adult_id/mac_adult_id.csv
        # print("----for decry----isEnc: " + str(isEnc))
        
        # _logger.debug("Input path: " + path_)



        #20190717, add fo fb log
        _logger_fb.debug("============start======================")
        _logger_fb.debug("input file: " + path_)
        _logger_fb.debug("MAC columns name will be maced: " + str(MAC_columns_))
        _logger_fb.debug("AES columns name will be maced: " + str(AES_columns_))


        input_file_basename = os.path.basename(path_)


        ret_ = remove_hdfs_tmp_file(input_file_basename)
        if(ret_==1):
            _logger.debug(" AAAAAAAAAA-{0} exist before , rm ok".format(input_file_basename))
        else:
            _logger.debug(" AAAAAAAAAA-{0} do not exist before".format(input_file_basename))    
            
        
        retDF, headerDict = readFrom_csv_wit_NA_Normalize(path_, sep)
        if retDF is not None:
            #retDF.show()
            _logger.debug(" readFrom_csv OK")
        else:
            print("retDF is null")
            _logger.debug("retDF is null, readFrom_csv_wit_NA_Normalize err")

            errmsg = "FileIsNull"
            # updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus
            # updateTProjectStatus_.updateToMysql(projID, 99,"error") #err: update projStatus
            return
        
        
        project_status =20
        # statusname='資料集直接識別AES加密中'
        statusname='AESing'

        # statusname='Hash'
        # updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
        # # updateAppStatus_.updateToMysql("Mac_data","100")
        # updateAppStatus_.updateToMysql("read csv","20")
        
        
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
                    errmsg = "FileIsNull"
                    # updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus
                    # updateTProjectStatus_.updateToMysql(projID, 99,"error") #err: update projStatus
                    return 
            else:
                print("file_path is null")
                _logger.debug("file_path is null, readFrom_csv_wit_NA_Normalize err")  
                errmsg = "FilePathIsNull"
                # updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus
                # updateTProjectStatus_.updateToMysql(projID, 99,"error") #err: update projStatus
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
    project_status =40
    # statusname='資料集直接識別Hash中'
    statusname='AESing'

    # statusname='Hash'
    # updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
    # # updateAppStatus_.updateToMysql("Mac_data","100")
    # updateAppStatus_.updateToMysql("read csv","40")

    try: 
        #_logger.debug("2_______________")

        if AES_columns_ != [] or MAC_columns_ != []:
            if AES_columns_ != []:
                AES_cols=[]
            
                AES_cols=AES_columns_#['y']
                for i in range(len(headerDict)):
                    for j in range(len(AES_cols)):
                        if AES_cols[j] == headerDict["col_"+str(i)]:
                            AES_cols[j] = "col_"+str(i)
                #cols = [headerDict[col] for col in cols]
            else:
                AES_cols=[]
                pass

            if MAC_columns_ != []:
                MAC_cols=[]

                MAC_cols=MAC_columns_#['y']
                for i in range(len(headerDict)):
                    for j in range(len(MAC_cols)):
                        if MAC_cols[j] == headerDict["col_"+str(i)]:
                            MAC_cols[j] = "col_"+str(i)
            else:
                MAC_cols=[]
                pass


            '''
            20190104, citc add
            tableName is used as (id, id hash) database name
                 hence, the tableName can not include '.', otherwise mysql will throw exceptions 
            '''
            tmp = tableName.split(".")
            #print(tmp)
            tableName =tmp[0].replace("/", "_") 
            
            


            if dataHash == "yes" or dataHash == "Y" or dataHash == "y"  or dataHash == "YES"  or dataHash == "Yes"   :
                #_logger.debug("---++++--retDF: {}" + retDF)
                print("----------retDF----------")
                retDF.show()
                print("---++++--cols: {}".format(AES_cols))
                print("---++++--AES key_: {}".format(AES_hashkey))
                print("---++++--isEnc: {}".format(str(isEnc))) 
                _logger.debug("---++++--cols: {}".format(AES_cols))
                _logger.debug("---++++--AES key_: {}".format(AES_hashkey))
                _logger.debug("---++++--isEnc: {}".format(str(isEnc)))

                _logger.debug("---++++--MAC cols: {}".format(MAC_cols))
                _logger.debug("---++++--MAC key_: {}".format(Mac_hashkey))



                _logger.debug("enter") 
                # _logger.debug("df = " ) 
                # out = retDF.head(10)
                # _logger.debug(out) 
                _logger.debug("enter") 
                dfDF=udfMacCols(AES_cols,MAC_cols, retDF, AES_hashkey,Mac_hashkey,tableName, headerDict, isEnc)
                # dfDF=udfMacCols([],MAC_cols, retDF, AES_hashkey,Mac_hashkey,tableName, headerDict, isEnc)
                # dfDF=udfMacCols(AES_cols,[], retDF, AES_hashkey,Mac_hashkey,tableName, headerDict, isEnc)

                # _logger.debug("df = " ) 
                # out = dfDF.head(10)
                # _logger.debug(out) 
                _logger.debug("finish") 
            else : 
                dfDF = retDF
         
        else:
            MAC_cols = []
            AES_cols=[]
            dfDF = retDF
            
        tableName_csv = tableName+".csv"

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
                tableName_ = str(group_type) + '_' + tblName + '_enc'
                
            # output path 
            _logger_fb.debug("---2--dataHash: {}".format(dataHash))
            _logger_fb.debug("---2--onlyHash: {}".format( onlyHash))
            _logger_fb.debug("---33333--tableName_: {}".format( tableName_))
            _logger_fb.debug("Output path: " + path_)


            #20190717, add fo fb log
            #_logger_fb.debug("out file: " + path_)

            # get columns
            headers = dfDF.columns

            _logger_fb.debug("header : " + str(headers))

            headers = [headerDict[headers[i]] for i in range(len(headers))]


            if (onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO") and MAC_columns_mac != []:
                result = exportDataMac(projName, dfDF, headers, tableName_, path_)
                
            else:
                proj_Name = projName
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
                if AES_cols == []:
                    pass
                else:
                    for column_ in AES_cols:
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


                if MAC_cols == []:
                    pass
                else:
                    for column_ in MAC_cols:
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
        
                
                out_key = []
                out_key.append(Mac_hashkey)
                out_key.append(AES_hashkey)
                
                setting_list = []
                for i in range(len(headers)):
                    if headers[i] in AES_columns_mac:
                        setting_list.append("AES")
                    elif headers[i] in MAC_columns_mac:
                        setting_list.append("Hash")
                    else:
                        setting_list.append("No_setting")

                # out_json = {}
                # out_json['enc_key'] = ','.join(out_key)
                # out_json['col_name'] = ','.join(headers)
                # out_json['col_setting'] = ','.join(setting_list)
                # out_json['enc_datasetname'] = tableName
                # out_json['ds_count'] = total_length

                key_str = ','.join(out_key)
                col_name_str = ','.join(headers)
                col_settint_str = ','.join(setting_list)
                out_json = {
                    'enc_key':key_str,
                    'col_name':col_name_str,
                    'col_setting':col_settint_str,
                    'enc_datasetname':str(tableName_)+".csv",
                    'ds_count':str(total_length)
                }



                # df_json = spark.createDataFrame([out_json])
                # re = exportDataJson(proj_Name,df_json,tableName_+'_json',path_)

                # if re['result'] == 0:
                #     _logger.debug("export json error.")
                #     _logger.debug(result['msg'])
                # else:
                #     _logger.debug("export json succeed.")
                

                out_dir_path = path_ +"/"+projName
                out_json_path = out_dir_path +'/'+ tableName_ +'.json'
                with open(out_json_path,'w') as json_file:
                    json.dump(out_json,json_file)

                ###########
                ######itri, output outt_dir_path for task_udfAESUID.py (does not change the code about_logger code)##########
                _logger_fb.debug("============end======================="+out_dir_path) #####################################
                d_i_path = "/home/hadoop/proj_/data/input"
                if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
                    data_input_path_project = os.path.join(d_i_path,projName)
                    _logger_fb.debug(data_input_path_project) 

                    doCommand([ 'mkdir', data_input_path_project])

                    data_input_path_project_table = os.path.join(data_input_path_project,tableName_)

                    os.system('cp -r {} {}'.format(out_dir_path, data_input_path_project_table))
                else: 
                    pass
                    # d_o_path = "/home/hadoop/proj_/data/output"
                    # data_output_path_project = os.path.join(d_o_path,projName)
                    # _logger_fb.debug(data_output_path_project) 
                    # doCommand([ 'mkdir', data_output_path_project])
                    # os.system('cp -r {} {}'.format(out_dir_path, data_output_path_project))
                #############################################################################################################

                ####20230107# remove hdfs tmp file##start#####
                
                ret_ = remove_hdfs_tmp_file(input_file_basename)
                if(ret_==1):
                    _logger.debug(" AAAAAAAAAA-{0} rm ok".format(input_file_basename))
                else:
                    _logger.debug(" AAAAAAAAAA-{0} do not rm, chek /tmp".format(input_file_basename))    
                        
                ####20230107# remove hdfs tmp file###end####
                

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
                # project_status =1
                # # statusname='直接識別Hash完成'
                # statusname='AES_F'

                # updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
                # updateAppStatus_.updateToMysql("AES UID Success","100",progress_state="Finished")

                #加密
                if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
                    project_status = 3
                    # statusname='直接識別Hash完成'
                    statusname='AES_F'

                    # updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
                    # updateAppStatus_.updateToMysql("AES UID Success","100",progress_state="Finished")
                #解密
                else:
                    project_status = 14
                    # statusname='直接識別Hash完成'
                    statusname='AES_F'

                    # updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
                    # updateAppStatus_.updateToMysql("AES UID Success","100",progress_state="Finished")    


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
    # colsNum = sys.argv[4]
    columns_mac = sys.argv[4]
    projName =sys.argv[5]
    projID = sys.argv[6] 
    dataHash = sys.argv[7]
    onlyHash = sys.argv[8]
    AES_key = sys.argv[9]
    AES_columns_mac = sys.argv[10]
    userId = sys.argv[11]
    userAccount = sys.argv[12]
    totalLen = len(sys.argv)




    main__(tblName,key,columns_mac,projName,projID,dataHash,onlyHash,AES_key,AES_columns_mac,userId,userAccount)
