#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import base64
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
import re
import shlex
from MyLib.loginInfo import getConfig
from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#20200318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus
import configparser
import os
# import paramiko
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.serialization import load_ssh_public_key
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
        # path_spark = 'file://' + path_
        path_spark = path_
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
    # hdfsCmdList=['hadoop','fs','-ls',fileName]
    hdfsCmdList=['hadoop','fs','-ls',shlex.quote(fileName)]
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


def updateToMysql_PETs(userId, project_id, project_status, statusname,service_ip,dataset_name):
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False
    # insert to sample data
    condisionSampleData = {
        'project_id': project_id,
        'project_status' : project_status,
        'createMember_Id':userId   
    }

    valueSampleData = {
        'project_id' : project_id,
        'project_status' : project_status,
        'statusname' : statusname,
        'updateMember_Id': userId,
        'service_ip':service_ip,
        'dataset_name':dataset_name,
        'createMember_Id':userId
                          
    }
    # def updateValue(self, dbName, tblName, conditions, setColsValue):
    resultSampleData = conn.updateValueMysql('PetsService',
                                             'T_Pets_ProjectStatus',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        _logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
    else:
        msg = resultSampleData['msg']
        _logger.debug('insert T_Pets_ProjectStatus fail: ' + msg)



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
    # 匹配命令（例如 'cp'）
    command_pattern = r'^[a-zA-Z0-9_]+$'

    # 匹配路径（例如 '/home/user/data/output/project/'）
    # path_pattern = r'^[a-zA-Z0-9_\-/.]+$'

    # 检查第一个元素是否匹配命令
    if re.match(command_pattern, hdfsCmdList[0]):
        print("命令格式正确")
    else:
        print("Invalid hdfsCmdList[0] format")
        return 'Fail'

    # 检查其余元素是否匹配路径格式
    # paths_match = all(re.match(path_pattern, path) for path in hdfsCmdList[1:])
    # if not paths_match:
    #     print("Invalid paths_match format")
    #     return 'Fail'

    # 检查每个列表元素
    quoted_commands  = [shlex.quote(cmd) for cmd in hdfsCmdList]
    hdfsCommand = subprocess.Popen(quoted_commands ,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    errLines = hdfsCommand.stderr.readlines()
    print(errLines)
    # _logger.debug(errLines)
    msg = list()
    for line in errLines:
        if line.decode('utf-8') is not None:
            msg.append(str(line))

    return ','.join(msg)

def getJsonParser(jsonBase64__):
    if jsonBase64__ is None:
        return 'input error! getJsonParser input is None!'
    # decode base64
    try:
        de_b64 = base64.b64decode(jsonBase64__)
    except Exception as err:
        return 'decode base64 error! - %s:%s' % (type(err).__name__, err)
    # json parser
    try:
        jsonDic__ = json.loads(de_b64.decode("utf-8"))
        #print("Before getJsonParser: ")
        #print(jsonBase64__)
        #print("After getJsonParser result: ")
        #print(jsonDic__)
    except Exception as err:
        return 'json parser error! - %s:%s' % (type(err).__name__, err)
    return jsonDic__



    ##############  0718 enc解密  ##############
def dec(base64_encrypted):

    keyPath="/home/hadoop/proj_/longTaskDir/sftp_keys/"
    # key_private = paramiko.RSAKey.from_private_key_file(keyPath+"sftp_key.pem",password="iclw200@")
    private_key = load_ssh_private_key(open(keyPath+"sftp_key.pem", "rb").read(), b"iclw200@")
    ciphertext = base64.b64decode(base64_encrypted)
    de_ciphertext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return de_ciphertext.decode('utf-8')

    ##############  enc解密  ##############


def main__(projName,projID,identifier,onlyHash,userId,userAccount):
    global sc, sqlContext, hiveLibs, _logger,spark,updateAppStatus_,updateTProjectStatus_
    
    _logger=_getLogger('AES_Enc')

    _logger_fb=_getLogger('AES_Enc')

    _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_userId_%s',userId)
    _logger.debug('spark_import_identifier_%s',identifier)
    _logger.debug('onlyHash:%s',onlyHash)
    _logger.debug('spark_import_projID_%s',projID)

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
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemasterSCLIENT:9083")
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

    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName) or projName.isdigit():
        _logger.debug("Invalid projName format: projName can only contain letters, numbers, and underscores, cannot be all numbers, and cannot start with a number")
        sys.exit(1)
    projName = shlex.quote(projName)
    try:

        updateTProjectStatus_ = updateTProjectStatus(projID,userId)
    except Exception as e:
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False

    try:

        # 2024/01/08 09:34:39 - AES_Enc - DEBUG - ============end=======================/home/hadoop/proj_/dataMac/output/test0103
        path_ = "/home/hadoop/proj_/dataMac/output"
        out_dir_path = path_ +"/"+projName

        file_ = '/home/hadoop/proj_/longTaskDir/Hadoop_information.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        user_name = config.get('Hadoop_information', 'user_name')
        sftp_folder = config.get('Hadoop_information', 'sftp_folder')

        pets_service_ip = config.get('Hadoop_information', 'ip')
        #_logger.debug(pets_service_ip)
        _logger.debug(user_name)
        _logger.debug(sftp_folder)
        _logger.debug("%%%%%%%%%%%%%%%%%%")

        #20240823 add for DNS 1######## pedsas.moda.gov.tw , data-privacy.com.tw#######
        if(pets_service_ip=="pedsas.moda.gov.tw"):
            pets_service_ip="34.81.119.49"
        if(pets_service_ip=="data-privacy.com.tw"):
            pets_service_ip="34.81.71.21"
        #20240823 add for DNS 2######## pedsas.moda.gov.tw , data-privacy.com.tw#######


        key_path = "/home/hadoop/proj_/longTaskDir/sftp_keys/sftp_key.pem"

        cmd_send = "scp -i " + key_path + " -P 22 -r " + out_dir_path + " "+ user_name +"@"+pets_service_ip + ":" + sftp_folder

        _logger_fb.debug("============cmd_send=======================")
        _logger_fb.debug("cmd_send:%s",cmd_send)
        try:
            S_Command = subprocess.run(cmd_send, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            errLines = S_Command.stdout
            _logger_fb.debug(errLines)
            stderrLines = S_Command.stderr
            _logger_fb.debug(stderrLines)
            # subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as err:
            _logger.debug("err:%s",err)

        _logger_fb.debug("============AES_Enc end=======================")


        #加密
        if onlyHash == 'N' or onlyHash == 'n' or onlyHash == "no" or onlyHash == "No" or onlyHash == "NO":
            project_status = 3
            statusname='直接識別Hash完成'
            # statusname='AES_F'
            # updateTProjectStatus_.updateToMysql(projID, project_status,statusname)
            projID = 99999
            updateTProjectStatus_.updateToMysql(projID, project_status,statusname,"","","")
            # updateAppStatus_.updateToMysql("AES UID Success","100",progress_state="Finished")
        #解密
        else:
            project_status = 14
            statusname='直接識別Hash完成'
            # statusname='AES_F'
            projID = 99999
            updateTProjectStatus_.updateToMysql_resend(projID, project_status,statusname,identifier)

    except Exception as err:
        _logger.debug("err:%s",err)



if __name__ == "__main__":

    projName = sys.argv[1]
    projID =sys.argv[2]
    identifier = sys.argv[3]
    onlyHash = sys.argv[4]
    userId = sys.argv[5]
    userAccount= sys.argv[6]

    totalLen = len(sys.argv)


    main__(projName,projID,identifier,onlyHash,userId,userAccount)
