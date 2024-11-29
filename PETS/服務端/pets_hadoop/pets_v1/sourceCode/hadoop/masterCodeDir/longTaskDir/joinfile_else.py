#!/usr/bin/python
# -*- coding: utf-8 -*-

from email.header import Header
from mimetypes import suffix_map
from unittest import result
from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from pyspark.sql import SparkSession
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.parseData import importData, checkListQuotes_1side,exportData,exportDataJoin
import os, sys
import base64,json
import pandas as pd
from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#from module.base64convert import getJsonParser

#20200318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus

#2023/11/15
from os import path



#2023/0927

def FindTable(join_list):
    print('in Find table function')
    out_table = []
    
    for item in join_list:
        get_join_tables = str(item['link_col'])
        
        table1_index = get_join_tables.find('.')
        sep = get_join_tables.find('_',table1_index)
        table2_index = get_join_tables.find('.',sep)
        
        get_table1 = get_join_tables[0:table1_index]
        get_table2 = get_join_tables[sep+1:table2_index]
        print(get_table1)
        print(get_table2)
        if not (get_table1 in out_table):
            out_table.append(get_table1)
            
        if not (get_table2 in out_table):
            out_table.append(get_table2)
    
    return out_table


def join(df1,df2,df1_column,df2_column,join_type):
    d1 = df1.copy()
    d2 = df2.copy()
    
    if isinstance(df1_column,list) and isinstance(df2_column,list):    
        print('in list merge')
        for col1,col2 in zip(df1_column,df2_column):
            d2.rename(columns={col2:col1},inplace = True)
        return pd.merge(d1,d2,on=df1_column,how=join_type)
    else:
        if df1_column == df2_column:
            if df1_column =='index':
                return pd.merge(df1,df2,left_index=True,right_index=True,how=join_type)
            else:
                return pd.merge(df1,df2,on=df1_column,how=join_type)
        else:
            d2.rename(columns={df2_column:df1_column},inplace = True)
            return pd.merge(d1,d2,on=df1_column,how=join_type)
        

def combine(df1,df2,join_type):
    d1 = df1.copy()
    d2 = df2.copy()
    
    s = (set(d1.columns)&set(d2.columns))
    column = list(s)
    print(column)
    return pd.merge(d1,d2,on=column,how=join_type)

def Join_Table(join_info):

    out_table = []
    get_join_tables = str(join_info['link_col'])
    
    table1_index = get_join_tables.find('.')
    sep = get_join_tables.find('_',table1_index)
    table2_index = get_join_tables.find('.',sep)
    
    get_table1 = get_join_tables[0:table1_index]
    get_table2 = get_join_tables[sep+1:table2_index]

    out_table.append(get_table1)
    out_table.append(get_table2)
    
    return out_table

def FindJoinColumn(join_info):
    out_column = []
    get_join_column = str(join_info['link_col'])
    
    column1_index = get_join_column.find('.')
    sep = get_join_column.find('_',column1_index)
    column2_index = get_join_column.find('.',sep)
    end = len(get_join_column)
    
    get_column1 = get_join_column[column1_index+1:sep].lower()
    get_column2 = get_join_column[column2_index+1:end].lower()

    get_table1 = get_join_column[0:column1_index]
    get_table2 = get_join_column[sep+1:column2_index]

    out_column.append(get_column1+'_'+get_table1)
    out_column.append(get_column2+'_'+get_table2)
    
    return out_column

def JoinColumns(join_info):
    out_column = []
    get_join_column = str(join_info['link_col'])
    
    column1_index = get_join_column.find('.')
    sep = get_join_column.find('_',column1_index)
    column2_index = get_join_column.find('.',sep)
    end = len(get_join_column)
    
    get_column1 = get_join_column[column1_index+1:sep]
    get_column2 = get_join_column[column2_index+1:end]

    out_column.append(get_column1)
    out_column.append(get_column2)
    
    return out_column



def getJsonParser(jsonBase64__):
    if jsonBase64__ is None:
        return 'input error! getJsonParser input is None!'
    # decode base64
    try:
        de_b64 = base64.b64decode(jsonBase64__).decode('utf-8')
    except Exception as err:
        return 'decode base64 error! - %s:%s' % (type(err).__name__, err)
    # json parser
    try:
        jsonDic__ = json.loads(de_b64)
        #print("Before getJsonParser: ")
        #print(jsonBase64__)
        #print("After getJsonParser result: ")
        #print(jsonDic__)
    except Exception as err:
        return 'json parser error! - %s:%s' % (type(err).__name__, err)
    return jsonDic__


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


#2023/09/27 revised
def checkFormatBeforeImport(tables,projName):
    try:
        for tblName in tables:
            # Check if file exist
            _logger.debug('check wefwe, test = ')
            pathData = str(os.path.join(path_, projName, str(tblName))) + '.csv'
            fileExists = os.path.isfile(pathData)
            _logger.debug(pathData)
            _logger.debug('22222')
            if not fileExists:
                userDataPath = pathData.replace("/home/hadoop/proj_", "citc/sourceCode/hadoop")
                _logger.debug('23333332')
                msg = 'errTable: File is not exist in {0}'.format(userDataPath)
                raise msg
            _logger.debug('255552')
            # Check double quotes of each column
            headerValues = pd.read_csv(pathData, index_col=0, nrows=0, sep=',',encoding='utf8').columns.tolist()
            

            test = pd.read_csv(pathData, sep=',',encoding='utf8').columns.tolist()
            _logger.debug('2334444445552')
            _logger.debug('check FormatBeforeImport, HeaderValuers = %s', headerValues)
            _logger.debug('check FormatBeforeImport, test = %s', test)
            
            checkListQuotes_1side(headerValues, tblName)
        return True

    except Exception as e:
        msg = 'errTable: error in checkFormatBeforeImport: {0}'.format(str(e))
        _logger.debug(msg)
        return False

#updateToMysql(projID, projName, tblName, sampleStr)
def updateToMysql(projID, jointablename, jointablecount, aes_col):
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
        'jointablename': jointablename,
        'jointablecount': jointablecount,
        'aes_col': aes_col
    }
    # def updateValue(self, dbName, tblName, conditions, setColsValue):
    resultSampleData = conn.updateValueMysql('PetsService',
                                             'T_Pets_Project',
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
    NAME = 'join'
    _logger=_getLogger(NAME)
    
    
   
    # ttt = str(base64_)
    # jsonAll = getJsonParser(ttt) # return jsons
    jsonAll = getJsonParser(base64_)
    _logger.debug(jsonAll)
    userAccount = jsonAll['userAccount']
    userId = jsonAll['userId']
    projName = jsonAll['project_name']
    projID = jsonAll['project_id']
    projkey = jsonAll['project_key']
    jointype = jsonAll['Join_type']
    joinfunc = jsonAll['Join_func']
    
    #path_ = '/home/bruce/deid_env/deid_k/citc_v2/sourceCode/hadoop/masterCodeDir/data/input/'

    _logger.debug('spark_import_userId_%s',userId)
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_projID_%s',projID)
    _logger.debug('spark_import_projkey_%s',projkey)
    _logger.debug('spark_import_jointype_%s',jointype)
    _logger.debug('spark_import_joinfunc_%s',joinfunc)
    _logger.debug('spark_import_path_%s',path_)
    _logger.debug('spark_import_path_%s',expath)

    
    # 20221217
    #userAccount = "deidadmin"
    #userId = "3"
   
    # Check if project exists
    projPath = os.path.join(path_, projName)
    ## to_be_update
    
    if os.path.exists(projPath):
        _logger.debug("project path: " + projPath)
    else:
        try:
            os.makedirs(projPath)
        except Exception as err:
            return _logger.debug('make error - %s:%s' % (type(err).__name__, err))
        #os.makedir(projPath)
        _logger.debug("project path: " + projPath)
        _logger.debug('errTable:'+NAME+'_projName_does_not_exist: '+projName)

    # Start spark job
    sc, hiveLibs, sqlContext, spark_ = initSparkContext(NAME)

    #2023/09/27
    tables = FindTable(joinfunc)
    _logger.debug('tables = %s',tables)
    # Check format before import
    # if not checkFormatBeforeImport(tables,projName):
    #     return
    


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
    
    ## to_be_update
    #len_c = len(tables.split(';'))
    len_c = 15
    
    #i=1
    #def __init__(self, lower, upper, div_in_loop, looop_round):
    updateAppProgress_ = updateAppProgress(10,70,4, len_c)
    
    ## to_be_update
    #for tblName in tables.split(';'):
    
    df_to_be_upload = {}


    
    # for tblName in tables:
    #     try:

    #         pathData = 'file://' + str(os.path.join(path_, projName, tblName)) + '.csv'

    #         create_sql = "create database if not exists {}".format(projName)
    #         _logger.debug(create_sql)
    #         sqlContext.sql(create_sql)

    #         sqlContext.sql('use ' + projName)
    #         _logger.debug('use ' + projName)

    #         # return information
    #         _logger.debug('##################import table name')
    #         _logger.debug(tables) #mac_adult_id;mac_adult_id_B;mac_adult_id_A

    #         #2 app status
    #         #progress_v = int(10/len_c)
    #         #progress_v = progress_v*i
    #         #progress_value = str(progress_v)+"%"
            
    #         progress_str = updateAppProgress_.getLoopProgress(1)#getLoopProgress(len_c, 10, i)
            
    #         updateAppStatus_.updateToMysql("Import_data",progress_str)
    #         _logger.debug("0~~~~~~~~~~~~~~~~~~~~~progress_str")
    #         _logger.debug(projName)
    #         _logger.debug(pathData)
    #         _logger.debug(tblName)


    #         ###################################################
    #         # Import data
    #         result = importData(projName, pathData, tblName, spark_)
    #         if result['result'] == 0:
    #             _logger.debug("import data error.")
    #             _logger.debug('errTable:' + NAME + '_read_textFile_fail: ' + result['msg'])
    #             updateAppStatus_.updateToMysql('import data error',progress_str,"err")
    #             updateTProjectStatus_.updateToMysql(project_id, 99,"error")               
                
    #             return
    #         else:
    #             _logger.debug("import data succeed.")
    #             _logger.debug(result['msg'])

    #         inputData = result['df']
    #         header_ = [col+'_'+tblName for col in inputData.columns]
    #         inputData = inputData.toDF(*header_)
    #         df_to_be_upload[tblName]=inputData
    #         #df_to_be_upload.append(inputData)
            
    for tblName in tables:
        try:
            inputData = spark_.read.csv(path.join('input', projName, tblName+'.csv'), header=True, sep=",")
            header_ = [col+'_'+tblName for col in inputData.columns]
            inputData = inputData.toDF(*header_)
            df_to_be_upload[tblName]=inputData
            

        except Exception as e:
            if str(e).find('InvalidInputException') != -1:
                index_ = str(e).find('InvalidInputException')
                errMsg = str(e)[index_:].split('\n')[0]
                _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+errMsg)
                # updateAppStatus_.updateToMysql(errMsg,progress_str,"err")
                updateTProjectStatus_.updateToMysql(project_id, 99,"error")
                return

            _logger.debug('errTable:'+NAME+'_read_textFile_fail: '+str(e))
            # updateAppStatus_.updateToMysql(str(e),progress_str,"err")
            updateTProjectStatus_.updateToMysql(project_id, 99,"error")
            return
        
        #df_filterFD = inputData.cache()
        '''
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
        '''
    _logger.debug('number of uploaded table : '+str(len(df_to_be_upload)))


    if jointype == 0:
        join_str = 'inner'
    elif jointype ==1:
        join_str = 'outer'

    _logger.debug('join_str = '+join_str)

    df = pd.DataFrame()
    df_list = []

    for item in joinfunc:
        join_table = Join_Table(item)
        join_column = FindJoinColumn(item)
        try:
            _logger.debug('join column = '+str(join_column))
            _logger.debug('join table = '+str(join_table))
            
            dd = df_to_be_upload[join_table[0]].toPandas()
            dd2 = df_to_be_upload[join_table[1]].toPandas()

            df = join(dd,dd2,join_column[0],join_column[1],join_str)
            df_list.append(df)
            
        except Exception as e:
            return _logger.debug('join error - %s' ,str(e))
    try:
        df = pd.DataFrame()
        
    except Exception as e:
        return _logger.debug('pandas error - %s' ,str(e))
    
   
    for item in df_list:
        try:
            if item.equals(df_list[0]):
                df = item
            else:
                df = combine(df,item,join_type='outer')
                df = df.fillna('NULL')
                _logger.debug('item len = '+str(len(item.index)))
                _logger.debug('df len = '+str(len(df.index)))
            #print("merge column = " + str(item.columns.tolist()))
        except Exception as e:
                _logger.debug(e)
    try:

        outstr = ''
        df_v = spark_.createDataFrame(df.astype(str))
        header_en = df_v.columns
        

        for item in tables:
            outstr = outstr+str(item)+'_'
            
        outstr = outstr + join_str
            
        #exportpath = os.path.join(expath,projName)
        
        _logger.debug(df)
        
    except Exception as e:
        return _logger.debug('data frame error - %s' ,str(e))
    
    try:
        rr = exportDataJoin(projName, df_v,header_en,outstr,expath)
        _logger.debug('make error - %s' ,str(rr))
    except Exception as e:
        _logger.debug('make error - %s' ,str(e))

    
    AES_cols = []
    AES_cols_str = ""
    AES_out_cols =[]
    _logger.debug('AES_cols -pre ')
    try:
        for tblName in tables:
            with open(os.path.join(projPath,tblName+'.json')) as f:
                    read_j = json.load(f)
                    
            cols = read_j['col_name'].split(',')
            cols_set = read_j['col_setting'].split(',')
            
            for i in range(len(cols)):
                if cols_set[i] == 'AES':
                    AES_cols.append(cols[i] + '_' + tblName)
                    
        _logger.debug('AES_cols - %s' ,str(AES_cols))
        
        for item in df.columns:
            if item in AES_cols:
                AES_out_cols.append(item)
            
        
        
        AES_cols_str = ','.join(AES_out_cols)
        
    except Exception as e:
        _logger.debug('AES Col error - %s' ,str(e))
                
        
                
    
    
    
    
    try:
        updateToMysql(projID, outstr, (len(df.index)), AES_cols_str)
    except Exception as e:
        _logger.debug('update To Mysql error - %s' ,str(e))

        
    







"""
            
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
    project_status =5 
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
"""

if __name__ == "__main__":
    # command from celery:
    #'spark-submit --jars gen.jar longTaskDir/getGenTbl.py '+projName+' '+tblName
    base64_ = sys.argv[1] #str #projName = dbName
    path_ = sys.argv[2]
    expath = sys.argv[3]
    
    '''
    userId= sys.argv[1]
    userAccount = sys.argv[2] #str #projName = dbName
    projName = sys.argv[3] #str
    projID = sys.argv[4]  # str
    projkey = sys.argv[5]  # str
    jointype = sys.argv[6]  # str    
    joinfunc = sys.argv[7]  # str   
    print('########')
    print(userId) 
    print(userAccount)
    print(projName)
    print(projID)
    print(projkey)
    print(jointype)
    print(joinfunc)
    
    print('#############')
    '''
    main()

                      