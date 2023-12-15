#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.parseData import importData, checkListQuotes_1side
import os, sys
import base64
import pandas as pd
from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#20200318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus
import configparser 


def initSparkContext(name):
    appName = name
    #master_ = 'yarn-client' #yarn
    master_ = 'yarn'
    _logger.debug("0108 master_=:"+master_)
    try:
        #spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()

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

    return sc_,hiveLibs, sqlContext, spark_


def parseCSV(body,headers):

    try:
        # step 1, get header (no need in hdfs)
        colnames = headers

        _logger.debug(colnames)
        #body = rdd.filter(lambda r: r!=header)

        # prepare for step 2
        def parseRow(row):
            #if '^' in row:
            if ',' in row:
                row_list = row.split(',')
                #row_list = row.split('^')
                row_tuple = tuple(row_list)
                return row_tuple
            else:
                row_list = row.split(',')
                row_tuple = tuple(row_list)
                return row_tuple

        # step2, split each row by '^'
        rdd_parsed = body.map(parseRow)


        # step 3, split header by ','
        #colnames = header.split(',')
        return rdd_parsed.toDF(colnames)
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_convert_rdd_to_dataFrame_error:'+str(e))
        return None


def randomSample(df, nRows=5):
    '''
    input: pyspark.dataframe
    return: list of dicts
    '''
    try:
       #sample_ = df.sample(False,0.2).limit(nRows).toPandas().to_dict('records')
       sample_ = df.sample(False,0.2).limit(nRows).toPandas()
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_sample_data_fail: '+str(e))
        return None

    return sample_

def checkFormatBeforeImport(tables):
    try:
        for tblName in tables.split(';'):
            # Check if file exist
            pathData = str(os.path.join(path_, projName, tblName, tblName)) + '.csv'
            fileExists = os.path.isfile(pathData)
            if not fileExists:
                userDataPath = pathData.replace("/home/hadoop/proj_", "citc/sourceCode/hadoop")
                msg = 'errTable: File is not exist in {0}'.format(userDataPath)
                raise msg

            # Check double quotes of each column
            headerValues = pd.read_csv(pathData, index_col=0, nrows=0, sep=',').columns.tolist()
            checkListQuotes_1side(headerValues, tblName)
        return True

    except Exception as e:
        msg = 'errTable: error in checkFormatBeforeImport: {0}'.format(str(e))
        _logger.debug(msg)
        return False

#updateToMysql(projID, projName, tblName, sampleStr)
def updateToMysql(projID, projName, table, data, userId):
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
        'data': data,
        'createMember_Id':userId,
        'updateMember_Id':userId
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

#20191212 add
def getLoopProgress(loop_count, default_value, increas_):
    progress_v = int(default_value/loop_count)
    progress_v = progress_v*increas_
    progress_value = str(progress_v)+"%"
    return progress_value


def main():

    global _logger, sc, hiveLibs, sqlContext, NAME, spark_, updateAppStatus_,updateTProjectStatus_
    NAME = 'import'
    _logger=_getLogger(NAME)


    # steal_cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName
    # _logger.debug("steal_cmd is {0}".format(str(steal_cmd)))
    # runcode = os.system(steal_cmd)
    # _logger.debug("run result is {0}".format(str(runcode)))

    # try:
    #     file_ = '/home/hadoop/proj_/longTaskDir/Hadoop_information.txt'
    #     config = configparser.ConfigParser()
    #     config.read(file_)
    #     ip = config.get('Hadoop_information', 'ip') 
    #     port = config.get('Hadoop_information', 'port') 
    #     out_path = config.get('Hadoop_information', 'out_path')  
    #     _logger.debug(ip)
    #     _logger.debug(port)
    #     _logger.debug(out_path)

    #     cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P ' + port + ' -r hadoop@' + ip + ':/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName
    #     # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName

    #     _logger.debug("cmd is {0}".format(str(cmd)))
    #     runcode = os.system(cmd)
    #     _logger.debug("run result is {0}".format(str(runcode)))
        
    # except Exception as e:
        
    #     _logger.debug('to PETs hadoop error : ',str(e))






    try:
        tables = base64.b64decode(base64_).decode("utf-8") #str
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_'+str(e))
        _logger.debug('errTable:'+NAME+'_decode_base64_error')
        return
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_userId_%s',userId)

    # log input
    _logger.debug('spark_import_dbName_%s',projName)
    _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_projID_%s',projID)
    _logger.debug('spark_import_tables_%s',tables)
    # 20221217
    #userAccount = "deidadmin"
    #userId = "3"
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_userId_%s',userId)

    # Check if project exists
    projPath = str(os.path.join(path_, projName))
    if os.path.exists(projPath):
        _logger.debug("project path: " + projPath)
    else:
        _logger.debug('errTable:'+NAME+'_projName_does_not_exist: '+projName)

    # Start spark job
    sc, hiveLibs, sqlContext, spark_ = initSparkContext(NAME)

    # Check format before import
    if not checkFormatBeforeImport(tables):
        return

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
    
    ###20191210, add for checking app status(write to mysql)##############
    try:
        #20200211 add 
        #appID, appName projID,projName
        updateAppStatus_ = updateAppStatus(sc.applicationId, NAME,projName,projID,userId)
    except Exception as e:
        print('updateAppStatus error: %s', str(e))
        return False
    #1 app status
    #updateToMysql(self,appState, progress,progress_state="Running")
    updateAppStatus_.updateToMysql("Init_1","5") #5%
    ###################################################    
    ####################################################################
    len_c = len(tables.split(';'))
    #i=1
    #def __init__(self, lower, upper, div_in_loop, looop_round):
    updateAppProgress_ = updateAppProgress(10,70,4, len_c)
    for tblName in tables.split(';'):

        try:

            pathData = 'file://' + str(os.path.join(path_, projName, tblName, tblName)) + '.csv'

            create_sql = "create database if not exists {}".format(projName)
            _logger.debug(create_sql)
            sqlContext.sql(create_sql)

            sqlContext.sql('use ' + projName)
            _logger.debug('use ' + projName)

            # return information
            _logger.debug('##################import table name')
            _logger.debug(tables) #mac_adult_id;mac_adult_id_B;mac_adult_id_A

            #2 app status
            #progress_v = int(10/len_c)
            #progress_v = progress_v*i
            #progress_value = str(progress_v)+"%"
            
            progress_str = updateAppProgress_.getLoopProgress(1)#getLoopProgress(len_c, 10, i)
            
            updateAppStatus_.updateToMysql("Import_data",progress_str)
            _logger.debug("0~~~~~~~~~~~~~~~~~~~~~progress_str")
            _logger.debug(projName)
            _logger.debug(pathData)
            _logger.debug(tblName)

            ###################################################
            # Import data
            result = importData(projName, pathData, tblName, spark_)
            if result['result'] == 0:
                _logger.debug("import data error.")
                _logger.debug('errTable:' + NAME + '_read_textFile_fail: ' + result['msg'])
                updateAppStatus_.updateToMysql('import data error',progress_str,"err")
                updateTProjectStatus_.updateToMysql(project_id, 99,"error")               
                
                return
            else:
                _logger.debug("import data succeed.")
                _logger.debug(result['msg'])

            inputData = result['df']
            header_ch = inputData.columns
            tmp_num = str(hash(projName))[1:3] + str(hash(tblName))[1:3]
            header_en = ['c_'+tmp_num+'_'+str(i) for i in range(len(header_ch))]
            inputData = inputData.toDF(*header_en)

            # Convert ch_col_name to en_col_name
            _logger.debug('spark_import_rawData_%s', pathData)
            _logger.debug('spark_import_header_en_%s', ','.join(header_en))
            _logger.debug('spark_import_header_ch_%s', ','.join(header_ch))
            _logger.debug('spark_import_table_%s', tblName)

        except Exception as e:
            if str(e).find('InvalidInputException') != -1:
                index_ = str(e).find('InvalidInputException')
                errMsg = str(e)[index_:].split('\n')[0]
                _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+errMsg)
                updateAppStatus_.updateToMysql(errMsg,progress_str,"err")
                updateTProjectStatus_.updateToMysql(project_id, 99,"error")
                return

            _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+str(e))
            updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 99,"error")
            return

        #normalized NA
        df_filterFD = inputData.cache()
        #try:
        #    for col_name in header_en:
        #        df_filterFD = df_filterFD.replace(['\\N'],['NA'],col_name).replace(['na'],['NA'],col_name).replace([''],['NULL'],col_name)
        #    df_filterFD = df_filterFD.na.fill('NULL')
        #except Exception as e:
        #    _logger.debug('errTable:'+NAME+'_nomalized_na_fail: '+str(e))
        #    return
        
        #3 app status#######################################33
        progress_str = updateAppProgress_.getLoopProgress(2)
        #print("2~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("table_count",progress_str)
        #####################################################3
        #table count
        try:
            tblCount = df_filterFD.count()
            _logger.debug('tblCount_'+str(tblCount))
        except Exception as e:
            _logger.debug('errTable:'+NAME+'_table_count_fail: '+str(e))
            updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 99,"error")
            return


        #4 app status#######################################33
        progress_str = updateAppProgress_.getLoopProgress(3)
        #print("3~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
        updateAppStatus_.updateToMysql("sample_data",progress_str)
        #####################################################3
        #sample
        try:
            sampleDf = randomSample(df_filterFD)
            _logger.debug(sampleDf)
            sampleDf.columns = header_ch
            sampleStr = '[' + ','.join([str(i) for i in sampleDf.to_dict('records')]) + ']'
            sampleStr = str(sampleStr).replace("\'", "\"")
            sampleStr = sampleStr.replace("\": \"", "\":\"")
            sampleStr = sampleStr.replace("\", \"", "\",\"")
            sampleStr = sampleStr.replace("None", "\"None\"")
            sampleStr = sampleStr.replace("\\\\N", "N")
            _logger.debug(sampleStr)
            if sampleStr is None:
                _logger.debug('sampleStr error')
                return
            else:
                updateToMysql(projID, projName, tblName, sampleStr,userId)
                _logger.debug('sampleStr_succeed.')
        except Exception as e:
            _logger.debug('errTable: Sample fail. {0}'.format(str(e)))
            updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 99,"error")
            return
        try:

            #create database
            create_sql = "create database if not exists {}".format(projName)
            _logger.debug(create_sql)
            sqlContext.sql(create_sql)
            sqlContext.sql('use ' + projName)
            _logger.debug('use ' + projName)

            #5 app status#######################################33
            progress_str = updateAppProgress_.getLoopProgress(4)
            #print("4~~~~~~~~~~~~~~~~~~~~~progress_str=%s"%progress_str)
            updateAppStatus_.updateToMysql("save table to HIVE",progress_str)
            #####################################################3        
            #tt= ttt+1
        except :
            _logger.debug('errTable: create database. {0}'.format(sys.exc_info()[0]))
            updateAppStatus_.updateToMysql("save table to HIVE",progress_str, "err")
            updateTProjectStatus_.updateToMysql(project_id, 99,"error")
            return    
        #save table to HIVE
        try:
            df_filterFD.write.format("orc").mode("overwrite").saveAsTable(tblName)
            df_filterFD.unpersist
            _logger.debug('table_save_succeed_' + tblName)
            #tp=tp+1

        except Py4JJavaError as e:
            s = e.java_exception.toString()
            _logger.debug(s)

        except Exception:
            _logger.debug(sys.exc_info()[0])
            _logger.debug(sys.exc_info()[1])
            _logger.debug(sys.exc_info()[2])
            _logger.debug(len(sys.exc_info()))
            _logger.debug("errTable:"+NAME+"_save_hiveTbl")
            updateAppStatus_.updateToMysql("errTable:"+NAME+"_save_hiveTbl",progress_str,"err")
            
            #project_status =3 
            #statusname='去欄位屬性判定'
            updateTProjectStatus_.updateToMysql(project_id, 99,"error")
            
            return
            #_logger.debug("error in kchecking : "+str(e))
        #i=i+1    

    _logger.debug('All_table_save_succeed.')
    
    
    ###################################################  
    ###202000318, add for checking app status(write to mysql)##############
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
    #updateTProjectStatus  
    project_status =3 
    statusname='去欄位屬性判定'
    updateTProjectStatus_.updateToMysql(project_id, project_status,statusname)
    
    
    _logger.debug('finish the process in update mysql')
    ##################################################################################################  

    '''
    #####20200311, add############################################################
    #update T_ProjectStatus set project_status = 99.... 這個語法 @gau
    conn.cursor.execute("set names utf8")
    #OK
    #Update T_ProjectStatus set project_status=10,statusname='感興趣欄位設定',updatetime=now() where project_id=參數
    #sqlStr = "UPDATE {}.{} ".format('DeIdService', 'T_Project_RiskTable')
    #sqlStr = sqlStr + "SET r1={},r2={},r3={},r4={},r5={},rs1={},rs2={},rs3={},rs4={},rs5={},updatetime = now()".format(risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6)
    #sqlStr = sqlStr + " WHERE project_id like \'{}\'".format(project_id)
    sqlStr = "UPDATE {}.{} ".format('DeIdService', 'T_ProjectStatus')
    #project_status =3 ,statusname='欄位屬性判定' => 匯入 CODE
    sqlStr = sqlStr + "SET project_status =3 ,statusname='欄位屬性判定',updatetime = now()"
    sqlStr = sqlStr + " WHERE project_id={}".format(project_id)

    _logger.debug('sqlStr in update mysql')
    _logger.debug(sqlStr)

    conn.cursor.execute(sqlStr)
    conn.connection.commit()

    _logger.debug('finish the process in update mysql')
    ##################################################################################################
    '''

    #6 app status#######################################33
    print("5~~~~~~~~~~~~~~~~~~~~~progress_str")
    updateAppStatus_.updateToMysql("All_table_save_succeed","100","Finished")
    #####################################################3  


if __name__ == "__main__":
    # command from celery:
    #'spark-submit --jars gen.jar longTaskDir/getGenTbl.py '+projName+' '+tblName
    projName = sys.argv[1] #str #projName = dbName
    projID = sys.argv[2] #str #projName = dbName
    base64_ = sys.argv[3] #str
    path_ = sys.argv[4]  # str
    userAccount = sys.argv[5]  # str
    userId = sys.argv[6]  # str    
    print('########')
    print(projName)
    print(projID)
    print(base64_)
    print(path_)
    print(userAccount)
    print(userId)    
    print('#############')

    main()
