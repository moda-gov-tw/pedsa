#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.parseData import importData, checkListQuotes_1side

#20220901, add######################################
from MyLib.updateAppStatus import updateAppStatus
#from MyLib.updateAppStatus import updateAppProgress
##################################################

from MyLib.connect_sql import ConnectSQL
import os, sys
import base64
import json
import pandas as pd

import subprocess


def initSparkContext(name):
    appName = name
    master_ = 'yarn-client' #yarn
    #master_ = 'yarn'  # yarn
    try:
        spark_ = SparkSession\
            .builder\
            .enableHiveSupport()\
            .master(master_)\
            .appName(appName)\
            .getOrCreate()

        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        from os.path import abspath
        warehouse_location = abspath('spark-warehouse')
        sc_.setSystemProperty("spark.sql.warehouse.dir", warehouse_location)

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _logger.debug("sparkContext_succeed.")

    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable: "+str(e))
        _logger.debug("errTable: errSC")
        return SparkContext(conf=SparkConf())

    return sc_,hiveLibs, sqlContext, spark_


def rmLocalHostDir(dirName):
    print ("in rmLocalHostDir")
    
    #hdfsCmdList=['hadoop','fs','-ls',dirName]
    #hadoop fs -rm -r -f  file:/home/hadoop/proj_/data/output/T_item_202102221141/
    #hdfsCmdList=['hadoop','fs','-rm','-r','-f',dirName]
    hdfsCmdList=['hadoop','fs','-rm','-r',dirName]
    print(hdfsCmdList)
    hdfsCommand=subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    #[b"ls: `udfEncTable_test.csv': No such file or directory\n"]
    #lines=[]
    #lines = hdfsCommand.stderr.readlines()
    #print("stderr out")
    #print(lines)
    #for line in lines:
        #print(line)
    #    if 'No such file or directory' in  line.decode("utf-8") :  
    #        return 'LocalHost_NoSuchDir'
    while True:
        line = hdfsCommand.stderr.readline()
        #print (line.rstrip())
        if not line:
            break
        #the real code does filtering here
        #print (line.rstrip())
        if 'No such file or directory' in  line.decode("utf-8") :
            return 'LocalHostNoSuchDir'
        
    return 'LocalHostDeleteDirOK'


def rmLocalHostByTime_T_ProjectDataFilter(DB_list_): 

    print("------------rmHdfsDirByTime_T_ProjectDataFilte\n-----{}---------------".format(DB_list_))
    #DB_list = getDBListByTime_T_ProjectDataFilter(dateTime)
    DB_list =DB_list_
    #print("------------DB_list=\n{}---------------".format(DB_list))
    resultDic={}    
    
    #['Fcst_MLData_76053', 'Fcst_MLData_76053', 'Fcst_MLData_76053', 'Fcst_MLData_76053', 
    #'T_item_202012010000', 'T_item_202012010000', 'Fcst_MLData_76053', 'Fcst_MLData_0312']
    
    #local_import_path = /home/hadoop/proj_/data/input
    #local_export_path = /home/hadoop/proj_/data/output
    #

    for dataBaseName in DB_list:
        ######citc, +0 for test#############3
        #1
        projName = "file:/home/hadoop/proj_/data/input/"+dataBaseName       
        retStr = rmLocalHostDir(projName)
        #if 'No such file or directory' in  line.decode("utf-8") :
            #return 'LocalHost_NoSuchDir'        
        #return 'Local_Host_DeleteDirOK'

        resultDic["rmLocalHostDir_inputResult"]=retStr    
        #2
        projName = "file:/home/hadoop/proj_/data/output/"+dataBaseName       
        retStr = rmLocalHostDir(projName)
        resultDic["rmLocalHostDir_outputResult"]=retStr
        #3
        #hadoop@nodemasterS:/$ ls ~/proj_/dataMac/output/
        #mac_Fcst_MLData_76053  mac_MLdata  mac_adult_id  mac_fcst_mldata_error  mac_item_202012010000  mac_item_202012230000

        projName = "file:/home/hadoop/proj_/dataMac/output/"+"mac_"+dataBaseName      
        retStr = rmLocalHostDir(projName)
        resultDic["rmLocalHostDir_dataMac_outputResult"]=retStr    
        #print("DB={} tabList={}".format(projName,tabList))
    return resultDic     

#return a file path like Decry_sample.csv/part-00000-6075efb5-55e2-4aa5-b178-723c58299b65-c000.csv]   
#fileName Decry_sample.csv
def rmHdfsDir(dirName):
    print ("in rmHdfsDir")
    ##['hadoop', 'fs', '-ls', 'udfEncTable_test.csv']
    #hdfsCmdList=['hadoop','fs','-ls',fileName]
    #dirName = "output/test123"
    #hdfsCmdList=['hadoop','fs','-rmdir',dirName]
    #-f, without 'NoSuchDir' reponse
    #hdfsCmdList=['hadoop','fs','-rm','-r','-f',dirName]
    hdfsCmdList=['hadoop','fs','-rm','-r',dirName]
    #print(hdfsCmdList)
    hdfsCommand=subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
  
    ####################################
    while True:
        line = hdfsCommand.stderr.readline()
        #print (line.rstrip())
        if not line:
            break
        #the real code does filtering here
        #print (line.rstrip())
        if 'No such file or directory' in  line.decode("utf-8") :
            return 'NoSuchHDFSDir'
    ###################################
    return 'DeleteHDFSDirOK'

def rmHdfsDirByTime_T_ProjectDataFilter(DB_list_): 

    #print("------------rmHdfsDirByTime_T_ProjectDataFilte\n-----{}---------------".format(DB_list_))
    #DB_list = getDBListByTime_T_ProjectDataFilter(dateTime)
    print("------------rmHdfsDirByTime_T_ProjectDataFilte\n-----{}---------------".format(DB_list_))

    DB_list = DB_list_
    #print("------------DB_list=\n{}---------------".format(DB_list))
    resultDic={}    
    
    #['Fcst_MLData_76053', 'Fcst_MLData_76053', 'Fcst_MLData_76053', 'Fcst_MLData_76053', 
    #'T_item_202012010000', 'T_item_202012010000', 'Fcst_MLData_76053', 'Fcst_MLData_0312']
    for dataBaseName in DB_list:
        ######citc, +0 for test#############3
        #1
        projName = "output/"+"mac_"+dataBaseName        
        retStr = rmHdfsDir(projName)
        #return 'NoSuchDir'
        #'DeleteDirOK'
        resultDic["rm_projName_out"]=retStr    
        #2
        projName = "input/"+dataBaseName       
        retStr = rmHdfsDir(projName)
        resultDic["rm_projName_input"]=retStr    
        #print("DB={} tabList={}".format(projName,tabList))
    return resultDic     





#DROP DATABASE IF EXISTS userdb;



def dropDatabase(dataBase):
    
    
   projName = dataBase
 
   
   #print('use ' + projName)
   try:
       # drop database
       sqlContext.sql('DROP DATABASE IF EXISTS ' + projName+' cascade;')
       #sqlContext.sql('DROP DATABASE ' + projName)
       return "DorpDatabaseOK"
   except Exception as e:
       #_logger.debug('errTable: dropDatabase error: ' + str(e))
       if 'There is no database named' in  str(e) :  
            return 'NoSuchDatabase'
       if 'NoSuchObjectException' in  str(e) :  
            return 'NoSuchDatabase'            
       
       return "DorpDatabaseErr"
       
       #updateAppStatus_.updateToMysql('errTable: get table name',progress_str,"err")
       #updateTProjectStatus_.updateToMysql(project_id, 94,"error")   
    
def dropHiveDBByTime_T_ProjectDataFilter(DB_list_):
    
    print("------------dropHiveDBByTime_T_ProjectDataFilter0--------------------")
    	
    #DB_list = getDBListByTime_T_ProjectDataFilter(dateTime)
    DB_list = DB_list_
    resultDic={}

    for dataBaseName in DB_list:
        #projName = dataBaseName
        
        retStr = dropDatabase(dataBaseName)
        #retStr return as follows
        #"DorpDatabaseOK"
        #'NoSuchDatabase'
        #'NoSuchDatabase'
        #"DorpDatabaseErr"
        resultDic[dataBaseName]=retStr
    return resultDic    



def showTables(dataBase):
   	
   projName = dataBase
   # use database
   sqlContext.sql('use ' + projName)
   #_logger.debug('use ' + projName)
   
   #print('use ' + projName)
   try:
      getTabName = "SHOW tables"
      tabListDf = sqlContext.sql(getTabName)
      #tabListDf.show()
      tabList = sqlContext.sql(getTabName).toPandas()['tableName'].values.tolist()
      #print(tabList)
      #colList = sqlContext.sql(getColName).toPandas()['col_name'].values.tolist()
        
      return tabList
   except Exception as e:
       _logger.debug('errTable: get table name error: ' + str(e))
       #updateAppStatus_.updateToMysql('errTable: get table name',progress_str,"err")
       #updateTProjectStatus_.updateToMysql(project_id, 94,"error")  
 

     
       

def showTablesByTime_T_ProjectDataFilter(dateTime):
    
    print("------------showTablesByTime_T_ProjectDataFilter0--------------------")
 
    	
    DB_list = getDBListByTime_T_ProjectDataFilter(dateTime)
    resultDic={}    	
    	
    for dataBaseName in DB_list:
        projName = dataBaseName
        
        tabList = showTables(projName)
        resultDic[projName]=tabList    
        #print("DB={} tabList={}".format(projName,tabList))
    return resultDic   

def getProjectId(DB_list_):
    # Connect mysql
    conn=None
    try:
      
      conn = ConnectSQL()
      #project_id,project_name
      sqlCommand = "select project_id from DeIdService.T_Project where project_name in {}".format(DB_list_)
      sqlCommand=sqlCommand.replace("[", "(")
      sqlCommand=sqlCommand.replace("]", ")")  
      _logger.debug("sqlCommand={}".format(sqlCommand))   
      sqlResult = conn.doSqlCommand(sqlCommand)
    
     
      #{'result': 1, 
      #'msg': "select project_id from DeIdService.T_Project where project_name in 
      #    ('2021_03_12_06_54_53_4207231', '2021_03_12_07_10_43_0047411', '2021_03_12_07_10_43_0047412', 
      #   '2021_03_12_07_18_17_6292531', '2021_03_12_07_18_17_6292532', '2021_03_12_07_18_17_6292533', '2021_03_12_07_18_17_6292534', 
      #    '2021_03_12_07_18_17_6292535', '2021_03_12_07_18_17_6292536')", 
      #'fetchall': 
      #        [{'project_id': 16}, {'project_id': 17}, {'project_id': 18}, {'project_id': 19}, 
      #        {'project_id': 20}, {'project_id': 21}, {'project_id': 22}, {'project_id': 23}, 
      #        {'project_id': 24}]}
      #print(sqlResult)
    
      fetchallList = sqlResult["fetchall"]      
      
      
    except Exception as e:
      _logger.debug('Connect mysql error: %s', str(e))
      print("----------in -getProjectId deleteMariaDataByProjectId--------------------"+str(e))
      return 0

    projectIdList = []
    
    resultDic={}
    
    for item in fetchallList:
      #print(item["project_id"])
      projectIdList.append(item["project_id"])

    
    return projectIdList[0] 

def deleteMariaDataByProjectId(DB_list_):
    # Connect mysql
    conn=None
    try:
      
      conn = ConnectSQL()
      #project_id,project_name
      sqlCommand = "select project_id from DeIdService.T_Project where project_name in {}".format(DB_list_)
      sqlCommand=sqlCommand.replace("[", "(")
      sqlCommand=sqlCommand.replace("]", ")")  
      _logger.debug("sqlCommand={}".format(sqlCommand))   
      sqlResult = conn.doSqlCommand(sqlCommand)
    
     
      #{'result': 1, 
      #'msg': "select project_id from DeIdService.T_Project where project_name in 
      #    ('2021_03_12_06_54_53_4207231', '2021_03_12_07_10_43_0047411', '2021_03_12_07_10_43_0047412', 
      #   '2021_03_12_07_18_17_6292531', '2021_03_12_07_18_17_6292532', '2021_03_12_07_18_17_6292533', '2021_03_12_07_18_17_6292534', 
      #    '2021_03_12_07_18_17_6292535', '2021_03_12_07_18_17_6292536')", 
      #'fetchall': 
      #        [{'project_id': 16}, {'project_id': 17}, {'project_id': 18}, {'project_id': 19}, 
      #        {'project_id': 20}, {'project_id': 21}, {'project_id': 22}, {'project_id': 23}, 
      #        {'project_id': 24}]}
      #print(sqlResult)
    
      fetchallList = sqlResult["fetchall"]
      print("=====================fetchallList")
      print(fetchallList)
      
      
    except Exception as e:
      _logger.debug('Connect mysql error: %s', str(e))
      print("------------2 deleteMariaDataByProjectId--------------------"+str(e))
      return 0

    projectIdList = []
    print("--------projectIdList----------------------")

    print(projectIdList)
    print("--------projectIdList----------------------")
    
    resultDic={}
    
    for item in fetchallList:
    	#print(item["project_id"])
    	projectIdList.append(item["project_id"])
    


    print("--------projectIdList----------------------")

    print(projectIdList)
    print("--------projectIdList----------------------")
    tableList = ["T_Project_SparkStatus_Management", "T_Project_SampleTable","T_ProjectStatus","T_ProjectSampleData","T_ProjectJobStatus","T_Project","T_Pro_DistinctTB","T_Project_FinalTable","T_Project_NumStatValue"]
    #tableList = ["T_ProjectStatus","T_ProjectSampleData","T_ProjectJobStatus","T_Project","T_Pro_DistinctTB","T_Project_FinalTable","T_Project_NumStatValue"]
    
    proj_id_tableList=["T_Project_FinalTable","T_Project_NumStatValue"]
    deleteSql=""    
    for id_ in projectIdList:
        for table_ in tableList:
            #sqlCommand = "delete id_ from DeIdService.{} where project_id= {}".format(table_,id_)
            if table_ in proj_id_tableList:
                sqlCommand = "delete from DeIdService.{} where proj_id = {}".format(table_,id_)
            else:
                sqlCommand = "delete from DeIdService.{} where project_id = {}".format(table_,id_)
            print("sqlCommand={}".format(sqlCommand))
            #deleteSql = deleteSql+ sqlCommand+";"
            print("---------sqlCommand={}".format(sqlCommand))
            sqlResult = conn.doSqlCommand(sqlCommand)
            print("======sqlResult========")
            print(sqlResult["msg"])
            print(sqlResult["result"])
            print("==============")
    #print("------deleteSql={}".format(deleteSql))        
    #sqlResult = conn.doSqlCommand(deleteSql)
    
    #print(sqlResult["msg"])
    
    
    return sqlResult["result"]
            

def getDBListByTime_T_ProjectDataFilter(dateTime):
    
    # Connect mysql
    try:
      
      conn = ConnectSQL()
      sqlCommand = "select project_name,createtime from DeIdService.T_Project where createtime <'{}'".format(dateTime)
      sqlResult = conn.doSqlCommand(sqlCommand)
    
      #{'result': 1, 'msg': "select project_name,createtime from DeIdService.T_ProjectDataFilter where createtime <'2021-03-12'", 
      #'fetchall': [{'project_name': 'Fcst_MLData_76053', 'createtime': datetime.datetime(2021, 3, 11, 18, 0, 22)}, 
      #            {'project_name': 'Fcst_MLData_76053', 'createtime': datetime.datetime(2021, 3, 11, 18, 13, 49)}, 
      #            {'project_name': 'Fcst_MLData_76053', 'createtime': datetime.datetime(2021, 3, 11, 18, 18, 53)}]}
      print(sqlResult)
    
      fetchallList = sqlResult["fetchall"]      
      
      
    except Exception as e:
      _logger.debug('Connect mysql error: %s', str(e))
      _logger.debug("------------2--------------------"+str(e))
      print("------------2--------------------"+str(e))
      return

    projectNameList = []
    
    resultDic={}
    
    for item in fetchallList:
    	print(item["project_name"])
    	projectNameList.append(item["project_name"])
    	
    return projectNameList  	
           
#icl, 20220623, add for rm data by proj name, as follows
     ##response = SparkJobManager.rm_T_Project_DataByTime("0-0-0___"+proj_name)   
def main():

    global _logger, sc, hiveLibs, sqlContext, NAME, spark_,updateAppStatus_
    NAME = 'removeT_Project_Data'
    _logger=_getLogger(NAME)


    _logger.debug('spark_removeProject_userAccount_%s',userAccount)
    _logger.debug('spark_removeProject_userId_%s',userId)

    try:
        
    	print("-----------------------test"+NAME)
        #tables = base64.b64decode(base64_).decode("utf-8") #str
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_'+str(e))
        
        #_logger.debug('errTable:'+NAME+'_decode_base64_error')
        return

    # log input
    #_logger.debug('spark import project: {0}'.format(projName))
    #_logger.debug('spark import tables: {0}'.format(tables))

    # spark setting
    try:
        _logger.debug('start init spark')
        sc, hiveLibs, sqlContext, spark_ = initSparkContext(NAME)
    except Exception as e:
        _logger.debug('error init spark: ' + str(e))
        retDict={"err": "start init spark error "}

    # return information
    #itri, output k application id (does not change the code about_logger code)
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)



 

    
    #resultDic_ = showTablesByTime_T_ProjectDataFilter('2021-03-12')   
    
    #print('resultDic =\n{}'.format(resultDic_))  
    #dropDatabase("database") 
    #DB_list_ = getDBListByTime_T_ProjectDataFilter(dateBefore_)
    try:
        #icl, 20220623, add for rm data by proj name, as follows
             #response = SparkJobManager.rm_T_Project_DataByTime("0-0-0")
        if("0-0-0___" in dateBefore_):
          x = dateBefore_.split("0___")
          DB_list_ = [x[1]]
          _logger.debug("---for rm data by proj name--DB_list_ = {}".format(DB_list_[0]))
          #print("---for rm data by proj name--DB_list_ = {}".format(DB_list_[0]))
        else:
          DB_list_ = getDBListByTime_T_ProjectDataFilter(dateBefore_)
    except Exception as e:
        retDict={"err": "get DB_list_ error, error for mysql"}
        print('Error retDict = {}'.format(retDict))
        return
    _logger.debug("-----DB_list_ = {}".format(DB_list_))
    if DB_list_ is None:
        retDict={"err": "DB_list_ is none"}
        _logger.debug('Error retDict = {}'.format(retDict))
        return
    if len(DB_list_)==0:
        retDict={"err": "DB_list_ is empty"}
        _logger.debug('Error retDict = {}'.format(retDict))
        #print('Error retDict = {}'.format(retDict))
        #print('rmHdfsDirByTime retDict = {}'.format(retDict))
        return        
    
    #ICL add, 20220901########################################
    try: #add for checking app status(write to mysql)##############
        #projID=999
        projID = getProjectId(DB_list_)
        projName=DB_list_[0]
        updateAppStatus_ = updateAppStatus(sc.applicationId, NAME,projName,projID,userId)
    except Exception as e:
        
        _logger.debug('updateAppStatus error: %s', str(e))
        return False
    ###########################################################
    #updateAppStatus_.updateToMysql("Init_1","5")
    errmsg=""
    #ICL add, 20220901########################################
    updateAppStatus_.updateToMysql(errmsg,"10","start")
    #####################################################################################            
    #FileIsNull      | 10       | err 
    #|AES UID Success| 100      | Finished       |
    #App_State       | Progress | Progress_State
    #errmsg = "FileIsNull"
    #updateAppStatus_.updateToMysql(errmsg,"10","err") #pei err:update APPstatus




    #print()
    retDict = dropHiveDBByTime_T_ProjectDataFilter(DB_list_)

    #retStr return as follows
        #"DorpDatabaseOK"
        #'NoSuchDatabase'
        #'NoSuchDatabase'
        #"DorpDatabaseErr"
        #resultDic[dataBaseName]=retStr
    #print('dropHiveDBByTime_T_ProjectDataFilter retDict = {}'.format(retDict))
    print('dropHiveDBByTime_T_ProjectDataFilter retDict = {}'.format(retDict[DB_list_[0]]))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+retDict[DB_list_[0]]
    updateAppStatus_.updateToMysql(errmsg,"20","hive")   
    

    retDict = rmHdfsDirByTime_T_ProjectDataFilter(DB_list_)
     
    #retStr = rmHdfsDir(projName)
      #return 'NoSuchDir'
      #'DeleteDirOK'
      #resultDic["rm_projName_out"]=retStr    
        #2
      #projName = "input/"+dataBaseName       
      #retStr = rmHdfsDir(projName)
      #resultDic["rm_projName_input"]=retStr 

    print('rmHdfsDirByTime output retDict = {}'.format(retDict["rm_projName_out"]))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+retDict["rm_projName_out"]
    updateAppStatus_.updateToMysql(errmsg,"30","hdfs")  
    print('rmHdfsDirByTime input retDict = {}'.format(retDict["rm_projName_input"]))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+retDict["rm_projName_input"]
    updateAppStatus_.updateToMysql(errmsg,"40","hdfs") 
    
    retDict =  rmLocalHostByTime_T_ProjectDataFilter(DB_list_)
    print('rmLocalHostDir_Result intput retDict = {}'.format(retDict["rmLocalHostDir_inputResult"]))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+retDict["rmLocalHostDir_inputResult"]
    updateAppStatus_.updateToMysql(errmsg,"50","local") 
    print('rmLocalHostDir_Result output retDict = {}'.format(retDict["rmLocalHostDir_outputResult"]))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+retDict["rmLocalHostDir_outputResult"]
    updateAppStatus_.updateToMysql(errmsg,"60","local") 
    print('rmLocalHostDir_Result dataMac output retDict = {}'.format(retDict["rmLocalHostDir_dataMac_outputResult"]))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+retDict["rmLocalHostDir_dataMac_outputResult"]
    updateAppStatus_.updateToMysql(errmsg,"80","local")
    
    
    # 0: err, 1: sql OK
    ret = deleteMariaDataByProjectId(DB_list_)
    print('deleteMariaDataByProjectId return id = {}, id=1 is ok'.format(ret))
    #ICL add, 20220901########################################
    errmsg=errmsg+"__"+str(ret)
    updateAppStatus_.updateToMysql(errmsg,"100","DB")
    
    print("==removeProject end==")

    print("END end")

    
    
#icl, 20220623, add for rm data by proj name, as follows
     #response = SparkJobManager.rm_T_Project_DataByTime("0-0-0")    
if __name__ == "__main__":
 	
    # spark-submit /home/hadoop/proj_/longTaskDir/removeData.py DBName tableName dateBefore(format: '2021-03-12') 
    #DBName_ = sys.argv[1]  # str
    #tableName_ = sys.argv[2]  # str
    dateBefore_ = sys.argv[1]  # str
    userAccount = sys.argv[2]  # str
    userId = sys.argv[3]  # str    

    #base64_ = sys.argv[4]  # str

    print('########')
    #print(DBName_)
    #print(tableName_)
    print(dateBefore_)
    print(userAccount)
    print(userId)    
    #print(base64_)
    print('#############')

    main()   
    
    
