#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


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

#20200205, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus


import requests
import configparser 
#reload(sys)
#sys.setdefaultencoding('utf-8')


#sys.stdout.write("Your content....")


def createTempFunction(sqlContext):
    # udf list
    udfs = ['getGenNumLevel',
            'getGenNumInterval',
            'getGenUdf',
            'getGenAddress',
            'getGenString',
            'getGenDate']


    for udf_ in udfs:
        try:
            if udf_ == 'getGenAddress':
                sqlAction = "create temporary function " + udf_ + "_ as 'citc.deid.gen.fubon." + udf_ + "'"
            else:
                sqlAction = "create temporary function " + udf_ + "_ as 'citc.deid." + udf_ + "'"
            sqlContext.sql(sqlAction)
            _logger.debug(sqlAction)
        except Exception as e:
            _logger.debug('errTable:'+NAME+'_'+str(e))
            _logger.debug('errTable:'+NAME+'_udf_{}_cannot_be_created'.format(udf_))


def initSparkContext(name):
    appName = name
    #master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        #20200309, modified foe hive warehouse (located in hdfs)#################################
        #spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()

        warehouse_location = "hdfs://nodemaster:9000/user/hive/warehouse"
        #warehouse_location = "hdfs:///user/hive/warehouse"

        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName) \
                     .config("spark.sql.warehouse.dir", warehouse_location) \
                                     .getOrCreate()
        ###################################################################################                             
        
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

    return sc_,hiveLibs, sqlContext

def generlizedIndirectColumns(list_, ttb_name__):
    tmpStr='           \n'
    tmpStr = tmpStr+ '           select '
    idx = 1
    for col_name_ in list_:
        if(idx < len(list_)):
            #print list_.count(col_name_)
            tmpStr = tmpStr+col_name_+','
        else:
            tmpStr = tmpStr+col_name_
        idx = idx+1;
        #tmpStr=tmpStr[0:len(tmpStr)]    
    tmpStr = tmpStr+' from '+ ttb_name__+'\n'
    _logger.debug(tmpStr)
    return tmpStr

def doMinMaxCheck(df_, colsDict):
    # colsDict = {col: 'min, max'}
    _logger.debug("Start doMinMaxCheck")
    _logger.debug(colsDict)

    for col_ in colsDict:
        min_bound, max_bound = colsDict[col_].split(',')
        _logger.debug("(min,max) = ({0},{1})".format(min_bound, max_bound))
        min_bound = float(min_bound)
        max_bound = float(max_bound)

        # UDF
        def convertOutlier(rawValue):
            try:
                rawValue = float(rawValue)
            except:
                return 'NULL'
            if rawValue > max_bound:
                return str(max_bound)
            elif rawValue < min_bound:
                return str(min_bound)
            else:
                return str(rawValue)

        convertOutlier_udf_float = udf(lambda z: convertOutlier(z), StringType())
        df_ = df_.withColumn(col_, convertOutlier_udf_float(col_))
    return df_


def main():

    global _logger, sc, hiveLibs, sqlContext, NAME, updateAppStatus_,updateTProjectStatus_
    # api name
    NAME = 'gen'
    _logger=_getLogger(NAME)

    _logger.debug("------ userAccount  userId --start-------")
    _logger.debug('spark_gen_userAccount_%s',userAccount)
    _logger.debug('spark_gen_userId_%s',userId)
    _logger.debug("------ userAccount  userId --end-------")

    # log input
    _logger.debug('spark_gen_dbName_%s', dbName)
    _logger.debug('spark_gen_genDictEncode_%s', genDictEncode)
    _logger.debug('spark_gen_doMinMaxEncode_%s', doMinMaxEncode)


    # 20221217
    # userAccount = "deidadmin"
    # userId = "1"
    # _logger.debug('spark_gen_userAccount_%s',userAccount)
    # _logger.debug('spark_gen_userId_%s',userId)

    # Decode genDictEncode
    try:
        tblInfo = getJsonParser(str(genDictEncode))
        tblNames = ','.join([tbl for tbl in tblInfo])
        _logger.debug(tblInfo)
        _logger.debug('spark_gen_tblName_%s', tblNames)
    except Exception as e:
        _logger.debug('errTable: Decode base64 error. {0}'.format(str(e)))
        return

    # Decode doMinMaxEncode
    try:
        minMaxTblInfo = getJsonParser(str(doMinMaxEncode))
        doMinMaxColTbls = ','.join([tbl for tbl in minMaxTblInfo])
        _logger.debug(minMaxTblInfo)
        _logger.debug('spark_gen_doMinMaxtblName: %s', doMinMaxColTbls)
    except Exception as e:
        _logger.debug('errTable: Decode base64 error. {0}'.format(str(e)))
        return

    # spark setting
    sc, hiveLibs, sqlContext = initSparkContext(NAME)

    #return information
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)
    
    ###################################################  
    ###202000318, add for checking app status(write to mysql)##############
    ###202000319, move here##############
    project_id = projID
    try:
     
        updateTProjectStatus_ = updateTProjectStatus(project_id,userId)
    except Exception as e:
        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False 

    ###20200205, add for checking app status(write to mysql)##############
    try:
        #appID, appName
        
        #updateAppStatus_ = updateAppStatus(sc.applicationId, NAME)
        updateAppStatus_ = updateAppStatus(sc.applicationId, NAME,dbName, projID,userId)
    except Exception as e:
        
        _logger.debug('updateAppStatus error: %s', str(e))
        return False
        
  
        
    #1 app status
    #updateToMysql(self,appState, progress,progress_state="Running")
    updateAppStatus_.updateToMysql("Init_1","5") #5%
    #_logger.debug("------20200206-3-------------")
    #####################################################################

    # use database
    try:
        #_logger.debug("------20200206-4.5-------------")
        sqlContext.sql('use ' + dbName)
        _logger.debug('use ' + dbName)
        #_logger.debug("------20200206-4-------------")
    except Exception as e:
        #_logger.debug("------20200206 sqlContext.sql-------------")
        #print('sqlContext.sql error: %s', str(e))   
        _logger.debug('sqlContext.sql error: %s', str(e)) 
        updateAppStatus_.updateToMysql("sqlContext.sql error" ,"5","err")
        updateTProjectStatus_.updateToMysql(project_id, 98,"error")
    # create temp udf 
    createTempFunction(sqlContext)

    # Connect mysql
    try:
        conn = ConnectSQL()
        conn.close() #citc, 20220325, conn mv to line 348
    except Exception as e:
        msg = 'errTable: Connect mysql error: %s', str(e)
        _logger.debug('errTable: Mysql connect error. {0}'.format(msg))
        updateAppStatus_.updateToMysql("errTable: Mysql connect error" ,"5","err")
        updateTProjectStatus_.updateToMysql(project_id, 98,"error")
        return

    #20200206 get the len of tblInfo
    len_c = len(tblInfo)
    _logger.debug("0~~~~~~~~~~~~~~~~~~~~~len_c=%s"%len_c)
    #20200206, get progress
    #def __init__(self, lower, upper, div_in_loop, looop_round):
    updateAppProgress_ = updateAppProgress(10,80,5, len_c)


    # Generalize table
    for tbl in tblInfo:
        #####citc add, 20200205############################3
        _logger.debug("------20200206-4-------------")
        _logger.debug("----------tbl= ")
        _logger.debug("tbl= {0}".format(tbl))
        ###################################################
        #1. Decode base64
        progress_str = updateAppProgress_.getLoopProgress(1)#getLoopProgress(len_c, 10, i)
        _logger.debug("1~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Decode base64",progress_str)
        ###################################################
        try:
            #tblInfo is a dict
            base64_ = tblInfo[tbl]
            genList = base64.b64decode(base64_).decode("utf-8").split("^") #list of action(str)
        except Exception as e:
            _logger.debug("Get encode from {0}: {1}".format(tbl, tblInfo[tbl]))

            updateAppStatus_.updateToMysql("Get encode from {0}: {1}".format(tbl, tblInfo[tbl]) ,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")
            return
        #####citc add, 20200205############################3
        _logger.debug("------20200206-5-------------")
        _logger.debug("----------genList= ")
        _logger.debug("genList= {0}".format(genList))
        ###################################################
        #2. Do generalization
        progress_str = updateAppProgress_.getLoopProgress(2)#getLoopProgress(len_c, 10, i)
        _logger.debug("2~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Do generalization",progress_str)
        ###################################################        
        try:
            outTblName = 'g_' + tbl
            genAction = generlizedIndirectColumns(genList, tbl)
            df2 = sqlContext.sql(genAction)
            _logger.debug('generlize ' + tbl + ' succeed.')
        except Py4JJavaError as e:
            s = e.java_exception.toString()
            _logger.debug(s)
            updateAppStatus_.updateToMysql("Py4JJavaError" ,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")    
            return
        except Exception:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(sys.exc_info()[2])
            _logger.debug(len(sys.exc_info()))
            _logger.debug("errTable:errReadFromSqlServer()_OR_getGen()")

            updateAppStatus_.updateToMysql("errTable:errReadFromSqlServer()_OR_getGen()" ,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")
            return

        #3. Do Min Max outlier check if need
        progress_str = updateAppProgress_.getLoopProgress(3)#getLoopProgress(len_c, 10, i)
        _logger.debug("3~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Do Min Max outlier check if need",progress_str)
        ###################################################                
        try:
            if minMaxTblInfo[tbl]:
                df3 = doMinMaxCheck(df2, minMaxTblInfo[tbl])
                _logger.debug('doMinMaxCheck:' + tbl + ' succeed.')
            else:
                df3 = df2
        except Exception as e:
            errMsg = str(e)
            _logger.debug('errTable:minMaxTblInfo error, ' + errMsg)
            updateAppStatus_.updateToMysql('errTable:minMaxTblInfo error' ,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")
            return

        #4. Save hive table
        progress_str = updateAppProgress_.getLoopProgress(4)#getLoopProgress(len_c, 10, i)
        _logger.debug("4~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("Save hive table"+outTblName,progress_str)
        ###################################################                        
        try:
            df3.write.format("orc").mode("overwrite").saveAsTable(outTblName)
            _logger.debug('Save hive table:' + tbl + ' succeed.')
        except Exception as e:
            errMsg = str(e)
            _logger.debug('errTable: save hive table error' + errMsg)
            updateAppStatus_.updateToMysql('errTable: save hive table error' ,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")
            return

        #5. Update final table name to sample data
        progress_str = updateAppProgress_.getLoopProgress(5)#getLoopProgress(len_c, 10, i)
        _logger.debug("5~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        #_logger.debug('spark_import_rawData_%s', pathData)
        updateAppStatus_.updateToMysql("Update final table name to sample data",progress_str) #default is Running
        ###################################################                              
        conditions = {
            'pro_db': dbName,
            'pro_tb': tbl
        } 

        setColsValue = {
            'finaltblName': outTblName
        }
        
        #citc, 20220325, from line 230 mv here
        # Connect mysql
        try:
            conn = ConnectSQL()
        except Exception as e:
            msg = 'errTable: Connect mysql error: %s', str(e)
            _logger.debug('errTable: Mysql connect error. {0}'.format(msg))
            updateAppStatus_.updateToMysql("errTable: Mysql connect error" ,"98","err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")
            return
        
        resultSampleData = conn.updateValue('DeIdService', 'T_Project_SampleTable', conditions, setColsValue)
        #_logger.debug(conn.updateValue('DeIdService', 'T_Project_SampleTable', conditions, setColsValue))
        if resultSampleData['result'] == 1:
            _logger.debug("insertSampleDataToMysql succeed. {0}".format(resultSampleData['msg']))
            conn.close() #citc, 20220325
        else:
            _logger.debug("errTable: insertSampleDataToMysql fail. {0}".format(resultSampleData['msg']))
            updateAppStatus_.updateToMysql('errTable: save hive table error' ,progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 98,"error")
            return
    #####20200311, add############################################################
    
    ###202000316, add for checking app status(write to mysql)##############
    '''
    project_id = projID
    try:
        #appID, appName
        
        #updateAppStatus_ = updateAppStatus(sc.applicationId, NAME)
        updateTProjectStatus_ = updateTProjectStatus(project_id)
    except Exception as e:
        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False  
    '''      
    #updateTProjectStatus#######################################################  
    try:
        project_status =7
        statusname='去識別化與風險設定'
        updateTProjectStatus_.updateToMysql(project_id, project_status,statusname)
    
        _logger.debug('finish the process in update mysql')
    except Exception as e:
        _logger.debug('update updateTProjectStatus_ error: %s', str(e))
    ############################################################################    
    


    try:
        file_ = '/home/hadoop/proj_/longTaskDir/Hadoop_information.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        web_ip = config.get('Hadoop_information', 'web_ip') 
        web_port = config.get('Hadoop_information', 'web_port')  
        _logger.debug(web_ip)
        _logger.debug(web_port)  
    except Exception as e:
        _logger.debug('to PETs hadoop error : ',str(e))


    _logger.debug('project_id: %s', str(project_id))
    _logger.debug('pname: %s', str(dbName))
    _logger.debug('jobname: %s', str("job1"))
    _logger.debug('finaltablename: %s', str(outTblName))


    #API: GetKChecking
    try:  
        k_GetKChecking_para = { "pid": project_id,"pname": dbName,"jobname": "job1","finaltablename": outTblName}
        _logger.debug('k_GetKChecking_para: %s',k_GetKChecking_para)
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/GetKChecking", params=k_GetKChecking_para,timeout=None, verify=False)
        response_dic = response_g.json()
        _logger.debug("k_GetKChecking_para DATA JSON: %s",response_dic)
    except Exception as e:
        _logger.debug('errTable: k_GetKChecking_para error. {0}'.format(str(e)))





    _logger.debug("All tables generalized succeed.")

    updateAppStatus_.updateToMysql("All_table_save_succeed","100","Finished")
    #####################################################3  

if __name__ == "__main__":
    # command from celery:
    #'spark-submit --jars gen.jar longTaskDir/getGenTbl.py '+dbName+' '+genDictEncode
    dbName = sys.argv[1] #str
    genDictEncode = sys.argv[2]  # key: tblName, value: encode
    doMinMaxEncode = sys.argv[3]  # key: tblName, value: encode
    projID = sys.argv[4]
    userAccount = sys.argv[5]  # str
    userId = sys.argv[6]  # str  
    print('########')
    print(dbName)
    print(genDictEncode)
    print(doMinMaxEncode)
    print(projID)
    print(userAccount)
    print(userId)    
    print('#############')
    main()
 
