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
    
    get_column1 = get_join_column[column1_index+1:sep]
    get_column2 = get_join_column[column2_index+1:end]

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
    NAME = 'setJsonProfile'
    _logger=_getLogger(NAME)
    
    
   
    # ttt = str(base64_)
    # jsonAll = getJsonParser(ttt) # return jsons
    jsonAll = getJsonParser(base64_)
    _logger.debug(jsonAll)
    userAccount = 1
    userId = 1
    projName = 'test_join'
    projID = jsonAll['project_id']

    #path_ = '/home/bruce/deid_env/deid_k/citc_v2/sourceCode/hadoop/masterCodeDir/data/input/'

    _logger.debug('spark_import_userId_%s',userId)
    _logger.debug('spark_import_userAccount_%s',userAccount)
    _logger.debug('spark_import_projName_%s',projName)
    _logger.debug('spark_import_projID_%s',projID)
    _logger.debug('spark_import_path_%s',path_)
    _logger.debug('spark_import_path_%s',expath)
    _logger.debug("spark_import_col:%s " + col_str)
    _logger.debug("spark_import_tbl_:%s " + tbl_str)

    
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


    
    tables = []
    items = tbl_str.split(',')
    for item in items:
        if item[:-len(".csv")] not in tables:
            tables.append(item[:-len(".csv")]) 
            
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
    to_be_compare = {}
    compare_data_output = {}
    compare_data_output['status'] = -1
    compare_data_output['message'] = ""
    importlist = []
    # AES_col = []
    # AES_col_dict = {}
    
    


    
    for tblName in tables:
        try:

            pathData = 'file://' + str(os.path.join(path_, projName, tblName)) +'.csv'

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
            
            _logger.debug("Load json")
            
            with open(os.path.join(projPath,tblName+'.json')) as f:
                read_j = json.load(f)
                to_be_compare[read_j['enc_datasetname']] = read_j
                
            _logger.debug("Load json finish")
            
            to_append = {}
            to_append['dataset'] = read_j['enc_datasetname'] 
            to_append['dataset_count'] = read_j['ds_count']
            
            _logger.debug("Dealing with col_setting")
            
            col_setting = []
            
            cols = read_j['col_name'].split(',')
            cols_set = read_j['col_setting'].split(',')
            
            # AES_col_dict_item = []
            for i in range(len(cols)):
                col_setting_item = {}
                col_setting_item['col'] = cols[i]
                col_setting_item['func'] = cols_set[i]
                # if cols_set[i] == 'AES' and cols[i] not in AES_col:
                #     AES_col.append(cols[i])
                    
                # if cols_set[i] == 'AES':
                #     AES_col_dict_item.append(cols[i])
                col_setting.append(col_setting_item)
                
            # AES_col_dict[tblName] = ','.join(AES_col_dict_item)
                
            to_append['col_setting'] = col_setting
            
            _logger.debug("Dealing with col_setting finish")
                
            importlist.append(to_append)
            
            
            
            
        

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
        
        
    _logger.debug("import_list = %s" ,importlist)
    # _logger.debug("AES_col = %s" ,AES_col)
    
    # AES_col_str = ','.join(AES_col) 
    # _logger.debug("AES_col_str = %s" ,AES_col_str)
    
    # _logger.debug("AES_col_dict = %s" ,AES_col_dict)
    
    
    dataInfo = {}
    dataInfo['importlist'] = importlist
    
    
    tables = tbl_str.split(',')
    columns = col_str.split(',')
    
    datacompare = []
    
    _logger.debug("dealing with datacompare item " )
    
    _logger.debug("table = %s" ,tables)
    _logger.debug("columns = %s" ,columns)
    try:
        for i in range(int(len(tables)/2)):
            _logger.debug("in for loop")
            datacompare_item = {}
            datacompare_item['dataset'] = tables[2*i] + '*' + tables[2*i+1]
            _logger.debug("datacompare_item['dataset'] %s" ,datacompare_item['dataset'])
            datacompare_item['col'] = columns[2*i] + '*' + columns[2*i+1]
            if tables[2*i] in to_be_compare and tables[2*i+1] in to_be_compare :
                datacompare_item['match'] = 'Y'
            else:
                datacompare_item['match'] = 'N'
                datacompare_item['colmatch'] = 'N'
            
            cols = to_be_compare[tables[2*i]]['col_name'].split(',')
            cols2 = to_be_compare[tables[2*i+1]]['col_name'].split(',')
            
            if columns[2*i] in cols and columns[2*i+1] in cols2:
                datacompare_item['colmatch'] = 'Y'
            else:
                datacompare_item['colmatch'] = 'N'
            
            
            datacompare.append(datacompare_item)
            
        _logger.debug("datacompare = %s" ,datacompare)
    except Exception as e:
        _logger.debug("error = %s" ,e)
        
    dataInfo['datacompare'] = datacompare
    compare_data_output['dataInfo'] = dataInfo
    compare_data_output['status'] = 0
    _logger.debug("compare_data_output = %s" ,compare_data_output)
    
    try:
        _logger.debug("save compare data output " )
        with open(os.path.join(expath,projName,str(project_id)+'.json'),'w') as f:
            json.dump(compare_data_output,f)
    except Exception as e:
        _logger.debug("error = %s" ,e)
        
        
    
        
        
        
            
     
        
    
        
        
    
        


  

if __name__ == "__main__":
    # command from celery:
    #'spark-submit --jars gen.jar longTaskDir/getGenTbl.py '+projName+' '+tblName
    base64_ = sys.argv[1] #str #projName = dbName
    path_ = sys.argv[2]
    expath = sys.argv[3]
    col_str = sys.argv[4]
    tbl_str = sys.argv[5]
    
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

                      