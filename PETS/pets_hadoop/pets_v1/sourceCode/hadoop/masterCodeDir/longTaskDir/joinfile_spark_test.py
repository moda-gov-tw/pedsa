#!/usr/bin/python
# -*- coding: utf-8 -*-

from email.header import Header
from mimetypes import suffix_map
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

import requests
import configparser 
from functools import reduce


#2023/0927

def FindTable(join_list):
    print('in Find table function')
    out_table = []
    main_table = ''
    # for item in join_list:
    #     get_join_tables = str(item['link_col'])
        
    #     table1_index = get_join_tables.find('.')
    #     sep = get_join_tables.find('_',table1_index)
    #     table2_index = get_join_tables.find('.',sep)
        
    #     get_table1 = get_join_tables[0:table1_index]
    #     get_table2 = get_join_tables[sep+1:table2_index]
    #     print(get_table1)
    #     print(get_table2)
    #     if not (get_table1 in out_table):
    #         out_table.append(get_table1)
            
    #     if not (get_table2 in out_table):
    #         out_table.append(get_table2)

    for item in join_list:

        if item['left_dataset'].endswith('.csv'):
            if item['left_dataset'][:-len('.csv')] not in out_table:
                if main_table =='':
                    main_table = item['left_dataset'][:-len('.csv')]

                out_table.append(item['left_dataset'][:-len('.csv')])

        else:
            if item['left_dataset'] not in out_table:
                out_table.append(item['left_dataset'])
                if main_table =='':
                    main_table = item['left_dataset']

        if item['right_dataset'].endswith('.csv'):
            if item['right_dataset'][:-len('.csv')] not in out_table:
                out_table.append(item['right_dataset'][:-len('.csv')])

        else:
            if item['right_dataset'] not in out_table:
                out_table.append(item['right_dataset'])
    
    return out_table,main_table


def join(df1,df2,df1_column,df2_column,join_type):
    # d1 = df1.copy()
    # d2 = df2.copy()
    d1 = df1.select(*df1.columns)
    d2 = df2.select(*df2.columns)
    
    if isinstance(df1_column,list) and isinstance(df2_column,list):    
        print('in list merge')
        for col1,col2 in zip(df1_column,df2_column):
            d2.rename(columns={col2:col1},inplace = True)
        join_conditions = [(d1[col] == d2[col]) for col in df1_column]
        join_condition = reduce(lambda df1, df2: df1 & df2, join_conditions)
        return d1.join(df2, join_condition,how = join_type)
        # return pd.merge(d1,d2,on=df1_column,how=join_type)
    # else:
    #     if df1_column == df2_column:
    #         if df1_column =='index':
    #             return pd.merge(df1,df2,left_index=True,right_index=True,how=join_type)
    #         else:
    #             return pd.merge(df1,df2,on=df1_column,how=join_type)
    #     else:
    #         d2.rename(columns={df2_column:df1_column},inplace = True)
    #         return pd.merge(d1,d2,on=df1_column,how=join_type)
        

def combine(df1,df2,join_type):
    d1 = df1.copy()
    d2 = df2.copy()
    
    s = (set(d1.columns)&set(d2.columns))
    column = list(s)
    print(column)
    return pd.merge(d1,d2,on=column,how=join_type)

def Join_Table(join_info):

    out_table = []
    # get_join_tables = str(join_info['link_col'])
    
    # table1_index = get_join_tables.find('.')
    # sep = get_join_tables.find('_',table1_index)
    # table2_index = get_join_tables.find('.',sep)
    
    # get_table1 = get_join_tables[0:table1_index]
    # get_table2 = get_join_tables[sep+1:table2_index]
    if join_info['left_dataset'].endswith('.csv'):
        get_table1 = join_info['left_dataset'][:-len('.csv')]
    else:
        get_table1 = join_info['left_dataset']

    if join_info['right_dataset'].endswith('.csv'):
        get_table2 = join_info['right_dataset'][:-len('.csv')]
    else:
        get_table2 = join_info['right_dataset']

    out_table.append(get_table1)
    out_table.append(get_table2)
    
    return out_table

def FindJoinColumn(join_info):
    out_column = []
    # get_join_column = str(join_info['link_col'])
    
    # column1_index = get_join_column.find('.')
    # sep = get_join_column.find('_',column1_index)
    # column2_index = get_join_column.find('.',sep)
    # end = len(get_join_column)
    
    # get_column1 = get_join_column[column1_index+1:sep].lower()
    # get_column2 = get_join_column[column2_index+1:end].lower()

    # get_table1 = get_join_column[0:column1_index]
    # get_table2 = get_join_column[sep+1:column2_index]

    # out_column.append(get_column1+'_'+get_table1)
    # out_column.append(get_column2+'_'+get_table2)
    if join_info['left_dataset'].endswith('.csv'):
        out_column.append(join_info['left_col']+ '_' + join_info['left_dataset'][:-len('.csv')])
    else:
        out_column.append(join_info['left_col']+ '_' + join_info['left_dataset'])

    if join_info['right_dataset'].endswith('.csv'):
        out_column.append(join_info['right_col']+ '_' + join_info['right_dataset'][:-len('.csv')])
    else:
        out_column.append(join_info['right_col']+ '_' + join_info['right_dataset'])
    
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
                     .config("spark.rpc.message.maxSize", "1024") \
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
def updateToMysql(projID, jointablename, jointablecount, aes_col, userId):
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
        'aes_col': aes_col,
        'updateMember_Id':userId
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

def updateToMysqlStatus(projID,  project_status, userId):
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
        'project_status': project_status,
        'updateMember_Id':userId
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
        _logger.debug('insertSampleDataToMysql fail: ' + msg)


def updateToMysqlSample(projID, sampleStr):
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
        'join_sampledata': sampleStr
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



def main():

    global _logger, sc, hiveLibs, sqlContext, NAME, spark_, updateAppStatus_,updateTProjectStatus_
    NAME = 'join'
    _logger=_getLogger(NAME)
    
    # member_id = sys.argv[1] 
    # join_type = sys.argv[2] 
    # join_func = sys.argv[3] 
    # project_eng = sys.argv[4] 
    # path = sys.argv[5]
    # expath = sys.argv[6]

    
    _logger.debug('spark_import_member_id:%s',member_id)
    _logger.debug('spark_import_project_eng:%s',project_eng)
    _logger.debug('spark_import_join_type:%s',join_type)
    _logger.debug('spark_import_projID:%s',projID)

    join_func_str = base64.b64decode(join_func).decode()
    join_func_list = eval(join_func_str) 
    _logger.debug('spark_import_join_func:%s',join_func_list)

    # _logger.debug('spark_import_path:%s',path_)
    # _logger.debug('spark_import_expath:%s',expath)
    _logger.debug('***************')

    path_ = "/home/hadoop/proj_/data/input"
    _logger.debug('spark_import_path:%s',str(path_))
    expath = "/home/hadoop/proj_/data/output"
    _logger.debug('spark_import_expath:%s',expath)


    path_ = path_
    projName = project_eng
    userId = member_id
    jointype = int(join_type)
    joinfunc = join_func_list
    # projID = 1



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
    tables,main_table = FindTable(joinfunc)
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


    
    for tblName in tables:
        try:

            pathData = 'file://' + str(os.path.join(path_, projName, tblName)) + '.csv'

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
            header_ = [col+'_'+tblName for col in inputData.columns]
            inputData = inputData.toDF(*header_)
            df_to_be_upload[tblName]=inputData
            #df_to_be_upload.append(inputData)
            
        

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
        

    _logger.debug('number of uploaded table : '+str(len(df_to_be_upload)))


    if jointype == 0:
        join_str = 'inner'
    elif jointype ==1:
        join_str = 'outer'

    _logger.debug('join_str = '+join_str)

    # df = pd.DataFrame()

    for item in joinfunc:
        join_table = Join_Table(item)
        join_column = FindJoinColumn(item)
        try:
            _logger.debug('join column = '+str(join_column))
            _logger.debug('join table = '+str(join_table))
             
            dd = df_to_be_upload[join_table[0]]
            dd2 = df_to_be_upload[join_table[1]]

            df_to_be_upload[join_table[0]] = join(dd,dd2,join_column[0],join_column[1],join_str)
            # df_list.append(df)
            
        except Exception as e:
            return _logger.debug('join error - %s' ,str(e))
    try:
        df = df_to_be_upload[main_table].fillna("NULL")
        
    except Exception as e:
        return _logger.debug('pandas error - %s' ,str(e))
    
    try:

        outstr = ''
        df_v = spark_.createDataFrame(df.astype(str))
        header_en = df_v.columns

        # for item in tables:
        #     outstr = outstr+str(item)+'_'
            
        # outstr = outstr + join_str

        outstr = 'PP_'+ projName + '_enc'
            
        #exportpath = os.path.join(expath,projName)
        
        # _logger.debug(df)
        
    except Exception as e:
        return _logger.debug('data frame error - %s' ,str(e))
    
    #sample
    try:
        sampleDf = randomSample(df_v, 20)
        _logger.debug(sampleDf)
        sampleDf.columns = header_en
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
            updateToMysqlSample(projID, sampleStr)
            _logger.debug('sampleStr_succeed.')
    except Exception as e:
        _logger.debug('errTable: Sample fail. {0}'.format(str(e))) 
        return

    try:
        rr = exportDataJoin(projName, df_v,header_en,outstr,expath)
        _logger.debug('exportDataJoin success - %s' ,str(rr))
    except Exception as e:
        _logger.debug('make error - %s' ,str(e))

    
    # syn/input
    data_output = os.path.join(expath,projName)
    join_output = os.path.join(data_output, outstr, outstr+".csv")
    syn_path = "/home/hadoop/proj_/final_project/syn/input"
    syn_mkdir = os.path.join(syn_path, projName)
    syn_input = os.path.join(syn_path, projName, outstr+".csv")

    mkdircmd = 'mkdir ' + syn_mkdir
    # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName
    _logger.debug("mkdircmd is {0}".format(str(mkdircmd)))
    runcode = os.system(mkdircmd)

    cmd = 'cp ' + join_output + ' ' + syn_input
    # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName
    _logger.debug("cmd is {0}".format(str(cmd)))
    runcode = os.system(cmd)



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

    
    df_count = len(df.index)
                

    try:
        updateToMysql(projID, outstr, df_count, AES_cols_str, userId)
        # updateToMysqlStatus(projID,  "4", userId)
    except Exception as e:
        _logger.debug('update To Mysql error - %s' ,str(e))


#########################################
# 20231201
#########################################

    try:
        file_ = '/home/hadoop/proj_/longTaskDir/Hadoop_information.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        web_ip = config.get('Hadoop_information', 'web_ip') 
        web_port = config.get('Hadoop_information', 'web_port')
        ip = config.get('Hadoop_information', 'ip') 
        k_port = config.get('Hadoop_information', 'k_port') 
        out_path = config.get('Hadoop_information', 'out_path')  
        gan_ip = config.get('Hadoop_information', 'gan_ip') 
        gan_port = config.get('Hadoop_information', 'gan_port')  
        _logger.debug(gan_ip)
        _logger.debug(gan_port)
        _logger.debug(web_ip)
        _logger.debug(web_port)  
        _logger.debug(ip)
        _logger.debug(k_port)
        _logger.debug(out_path)
    except Exception as e:
        _logger.debug('to PETs hadoop error : ',str(e))

    # #API:checkstatus
    # try:
    #     k_checkstatus_para = { "project_name": project_name}
    #     print('k_checkstatus_para: ',k_checkstatus_para)
    #     response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/k_checkstatus", params=k_checkstatus_para,timeout=None)
    #     response_dic = response_g.json()
    #     print("k_checkstatus DATA JSON: ",response_dic)
    #     # response['ImportData_flag']=response_dic
    #     # _vlogger.debug('ImportData_flag: '+ str(response_dic))
    # except Exception as e:
    #     _logger.debug('errTable: checkstatus error. {0}'.format(str(e)))

    cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P ' + k_port + ' -r /home/hadoop/proj_/data/output/'+projName+' hadoop@' + ip + ':/home/hadoop/proj_/data/input/'+projName
    # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName

    _logger.debug("cmd is {0}".format(str(cmd)))
    runcode = os.system(cmd)

    #API:k_conn
    try:  
        k_conn_para = { "project_name": projName}
        _logger.debug('k_conn_para: %s',k_conn_para)
        response_g = requests.get("https://"+web_ip+":"+web_port+"/api/WebAPI/k_conn", params=k_conn_para,timeout=None, verify=False)
        response_dic = response_g.json()
        _logger.debug("k_conn DATA JSON: %s",response_dic)
    except Exception as e:
        _logger.debug('errTable: k_conn error. {0}'.format(str(e)))


    #API:gan_conn
    gan_file_name = outstr+".csv"
    try:  
        gan_conn_para = { "project_name": projName ,"file_name":gan_file_name}
        _logger.debug('gan_conn_para:%s ',gan_conn_para)
        response_g = requests.get("http://"+gan_ip+":"+gan_port+"/api/WebAPI/syn_conn", params=gan_conn_para,timeout=None, verify=False)
        response_dic = response_g.json()
        _logger.debug("gan_conn DATA JSON: ",response_dic)
    except Exception as e:
        _logger.debug('errTable: k_conn error. {0}'.format(str(e)))



if __name__ == "__main__":

    member_id = sys.argv[1] 
    join_type = sys.argv[2] 
    join_func = sys.argv[3] 
    project_eng = sys.argv[4] 
    # path_ = sys.argv[5]
    # expath = sys.argv[6]
    projID = sys.argv[5]
    
    main()

                      