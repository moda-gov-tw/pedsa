# -*- coding: utf-8 -*-

print ('testing 000 not yet')
from risk_core import Base
import json
import base64


#20200207更新
import sys
# from marshmallow import Schema, fields, pprint

#20200211更新SA中數值小數點問題
import numpy as np

from risk_core.Security import get_security
from MyLib.connect_sql import ConnectSQL

#####read data from hive#####
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession

#20200212增加spark狀態
from MyLib.updateAppStatus import updateAppStatus

#20200318, add for dfSA cleaning non numeric col
import random

#202000318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus



#####read data from hive#####
#把SC叫起來
def initSparkContext(name):
    appName = name
    #master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()

        """
        sc = SparkContext(conf=SparkConf().setAppName(appName).setMaster(master))
        hiveLibs = HiveLibs(sc)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        print("sparkContext_succeed.")
        """

    except Exception as e:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        print(len(sys.exc_info()))
        print("errTable:fundation_getGenNumLevel:"+str(e))
        print("errTable:errSC")
        return SparkContext(conf=SparkConf())

    return sc_,hiveLibs, sqlContext

#取得hive資料
def getHiveData(dbName, tblName, cols):
    sqlContext.sql('use ' + dbName)

    tmpColsStr = ''
    for col_name_ in cols:
        tmpColsStr = tmpColsStr + col_name_
        if col_name_ != cols[len(cols)-1] and col_name_ !='*':
            tmpColsStr = tmpColsStr + ','
    query_str = 'SELECT %s FROM %s' %(tmpColsStr, tblName)

    print('getHiveData_'+query_str)

    _vlogger.debug('getHiveData_'+query_str)
    df = sqlContext.sql(query_str)
    return df


#######20200318, add for dfSA cleaning non numeric col####################
def getShuffleIntList(len_):
    
    li=list(range(2, len_+2))
    #print(len(li))
    #print(li)
    random.shuffle(li)
    return li

def pandasSerToDict(series_):
    zipbObj = zip(series_.index.tolist(), series_.values.tolist())
    # Create a dictionary from zip object
    dictOfWords = dict(zipbObj)
    #print(dictOfWords.keys())
    #print(dictOfWords.values())
    return dictOfWords
    #for key in dictOfWords.keys():
    #    print (dictOfWords[key])

def cleaningSADF(dfSA):
    _vlogger.debug('------in cleaningSADF--------------')
    df = dfSA
    SA_typeDic = pandasSerToDict(df.dtypes)
    for keyCol in SA_typeDic.keys():
        if((SA_typeDic[keyCol] == "float64") or (SA_typeDic[keyCol] == "int64") ):
            _vlogger.debug("numeric")
            #print(keyCol)
            #print(df[keyCol].mean())
            _vlogger.debug(keyCol)
            _vlogger.debug(df[keyCol].mean())

            mean_ = df[keyCol].mean()
            df[keyCol].replace({np.nan:mean_}, inplace = True)
        if((SA_typeDic[keyCol] == "object") ):
            _vlogger.debug("object____")
            _vlogger.debug(keyCol)
            relplaceDict_ = getStringToIntDict(df[keyCol])
            df[keyCol].replace(relplaceDict_, inplace = True)
            
    return df        

def getStringToIntDict(colDF):
    print(colDF.values)
    print(len(list(set(colDF.values))))
    
    distinctList = list(set(colDF.values)) 
    assignedList = getShuffleIntList(len(distinctList))
    zipbObj = zip(distinctList, assignedList)
    dictOfWords = dict(zipbObj)
    return dictOfWords

############################################################################    



def main():
    #20200214
    global  sc, hiveLibs, sqlContext, updateAppStatus_, updateTProjectStatus_
    print ('testing 001')
    ##--- Setting--- ##
    detail_setting = False  ## 在U2,U3,S4,S6可以選擇標籤,預設為第一個SA

    #取得風險值:等級1-5
    def getStars(risk_):
        try:
            if risk_ >= 4:
                return '5'
            elif risk_ >= 3:
                return '4'
            elif risk_ >= 2:
                return '3'
            elif risk_ >= 1:
                return '2'
            elif risk_ >= 0:
                return '1'
        except Exception as e:
            return str(e)

    #確認是不是存在風險資料
    def checkAvailable(project_id):
        """
        Check whether tblName of project_id is used or not
        :param project_id: int
        :param tblName: string
        :return: dict
        """
        try:
            sqlStr = "SELECT * FROM DeIdService.T_Project_RiskTable "
            sqlStr = sqlStr + "WHERE project_id='{}' ".format(project_id)

            # execute sql code
            conn.cursor.execute(sqlStr)

            # return True if tbl is used
            if conn.cursor.fetchone() is None:
                return 0
            else:
                return 1

        except Exception as e:
            return {'msg': str(e), 'result': 0, 'used': None}
    # with open('/home/hadoop/proj_/longTaskDir/risk_core/setting.json') as file_object:
    #     #打開JSON檔案
    #     data = json.load(file_object)

    ##--- Setting--- ##

    # print ('testing 002')
    # df_ori = Base.load_df_ori(data['df_ori'])   ##to pandas df ## loading original file
    # df_ano = Base.load_df_ano(data['df_ano'])   ##to pandas df ## loading anonymization file
    # p = Base.load_p(data['p']) ##to pandas df

    # attribute = list(df_ori)
    # QI = data['QI']
    # SA = data['SA']
    # print("QI", QI)
    # print("SA", SA)

    #20200210更新

    
    #從json取得各項參數
    QI = maininfoDIC['qi']
    SA = maininfoDIC['sa']
    dbName = maininfoDIC['dbname']
    rawTbl = maininfoDIC['pro_tb']
    deIdTbl = maininfoDIC['final_tb']
    tblName = maininfoDIC['final_tb']

    _vlogger.debug('QI: ')
    _vlogger.debug(QI)
    _vlogger.debug('SA: ')
    _vlogger.debug(SA)
    _vlogger.debug('dbName: ')
    _vlogger.debug(dbName)
    _vlogger.debug('rawTbl: ')
    _vlogger.debug(rawTbl)
    _vlogger.debug('deIdTbl: ')
    _vlogger.debug(deIdTbl)
    _vlogger.debug('tblName: ')
    _vlogger.debug(tblName)


    print ('testing 002')
    #從CSV取得資料轉換成pandas dataframe處理
    if 0:
        try:
            df_ori = Base.load_df_ori(data['df_ori'])   ##to pandas df ## loading original file
            df_ano = Base.load_df_ano(data['df_ano'])   ##to pandas df ## loading anonymization file
            # p = Base.load_p(data['p']) ##to pandas df index
            p = Base.getP(df_ori)
            print ('p: ')
            print (p)
            print ('df_ori: ')
            print (df_ori)

        except Exception as e:
            print ("pandas df error:getRiskAnalysis:"+str(e))
    #####
    else:
        #從hive取得資料轉換成pandas dataframe處理
        # spark setting

        appName = 'Risk'
        sc, hiveLibs, sqlContext = initSparkContext(appName)
        print ('sc')
        print (sc)
        print ('sqlContext')
        print (sqlContext)

        
        print('------Risk Start------') 

        
        #######20200320, add for Async API################
        #return information
        _logger.debug('###################sc.applicationId')
        _logger.debug("sc.applicationId:" + sc.applicationId)
        ####################################################

                
        #read data
        #hard code

        #20200210更新
        # dbName = '2qdatamarketdeid'
        # rawTbl = 'mac_adult_id'
        # deIdTbl = 'g_mac_adult_id_k_job1'

        print('dbName : '+ str(dbName))
        print('rawTbl : '+ str(rawTbl))
        print('deIdTbl : '+ str(deIdTbl))

        ###202000319, move here#############################3
        #project_id = project_id
        try:
            updateTProjectStatus_ = updateTProjectStatus(project_id)
        except Exception as e:        
            _logger.debug('updateTProjectStatus error: %s', str(e))
            return False
        ###########################################################    
        
        
        
        #20200212增加spark狀態
        #################################################################
        try:
            #appID, appName
            #20200214增加寫入dbName跟project_id
            _vlogger.debug('getting updateAppStatus: ')

            #將spark處理狀態更新到mysql裡面
            updateAppStatus_ = updateAppStatus(sc.applicationId, appName, dbName, project_id)
        except Exception as e:
            print('updateAppStatus error: %s', str(e))
            return False

        updateAppStatus_.updateToMysql("getting the pandas dataframe","5")
        #################################################################        

        try:
            # read from Hive
            _vlogger.debug('getting sparkcontext: ')

            #print ('inside the main.py and in the getHiveDate 1')
            _vlogger.debug('inside the main.py and in the getHiveDate 1')
            df_ano = getHiveData(dbName,deIdTbl,['*']).toPandas()
            df_ori = getHiveData(dbName,rawTbl,['*']).toPandas()

            _vlogger.debug('df_ano.columns: ')
            _vlogger.debug(df_ano.columns)

            _vlogger.debug('df_ori.columns: ')
            _vlogger.debug(df_ori.columns)

            # # #20200211更新將敏感資料轉換#######################################################
            #20200317, citc modified for ValueError:could not convert string to float: 'NULL'

            #######20200318, add for dfSA cleaning non numeric col####################
            #_vlogger.debug("df_ano[SA] =============")
            #_vlogger.debug(SA)
            #_vlogger.debug(df_ano[SA])
            #######20200323, add #########################################
            _vlogger.debug('len(SA) = ')
            _vlogger.debug(len(SA))
            _vlogger.debug(SA)
            if((len(SA) == 1) and (SA[0] == '')):
                _vlogger.debug("no SA columns are selected")
                #project_status = 10
                #statusname='興趣欄位設定'
                #updateTProjectStatus_.updateToMysql(project_id, project_status,statusname)
                updateTProjectStatus_.updateToMysql(project_id, 96,"error")
                _vlogger.debug("finish the process in update mysql")
                #updateAppStatus_.updateToMysql("Done","100","Finished")
                updateAppStatus_.updateToMysql("no SA columns are selected! ","err")
                _vlogger.debug('Finished')
                return None
            #######20200323, add #########################################    



            _vlogger.debug("cleaning non numeric col")
            df_ano[SA] = cleaningSADF(df_ano[SA])

            df_ori[SA] = cleaningSADF(df_ori[SA])
            #_vlogger.debug(df_ano[SA])
            #_vlogger.debug("cleaning non numeric col_2")
            #_vlogger.debug(df_ori[SA])
            ##############################################################################
       

            print ('inside the main.py and in the getHiveDate 2')
            df_ano[SA] = df_ano[SA].astype('float64') 
            df_ori[SA] = df_ori[SA].astype('float64') 

            df_ano[SA] = df_ano[SA].astype('int64') 
            df_ori[SA] = df_ori[SA].astype('int64')
            print ('inside the main.py and in the getHiveDate 3')
            ####################################################################################

            # #20200211更新將敏感資料轉換
            # print ('inside the main.py and in the getHiveDate 2')
            # df_ano[SA] = df_ano[SA].astype(np.int64) 
            # df_ori[SA] = df_ori[SA].astype(np.int64)
            # print ('inside the main.py and in the getHiveDate 3')

            # 20200207隨機取樣跟去識別化一樣多的資料
            df_ori = df_ori.sample(n=len(df_ano.index))
            print ('inside the main.py and in the getHiveDate 4')
            p = Base.getP(df_ori)
            print ('inside the main.py and in the getHiveDate 5')

        except Exception as err:
            print('read data error! - %s:%s' % (type(err).__name__, err))
            updateAppStatus_.updateToMysql("pandas cast type error,or read data error! ","err")
            updateTProjectStatus_.updateToMysql(project_id, 96,"error")
            return None
        ####20200323, citc resulting "time out"
        print("sc.applicationId:" + sc.applicationId)
    #####

  
    #20200212增加spark狀態
    #################################################################
    #citc, move above
    '''
    try:
        #appID, appName
        #20200214增加寫入dbName跟project_id
        _vlogger.debug('getting updateAppStatus: ')

        #將spark處理狀態更新到mysql裡面
        updateAppStatus_ = updateAppStatus(sc.applicationId, appName, dbName, project_id)
    except Exception as e:
        print('updateAppStatus error: %s', str(e))
        return False

    updateAppStatus_.updateToMysql("getting the pandas dataframe","5")

    '''
    #################################################################


    attribute = list(df_ori)
    QI = maininfoDIC['qi']
    SA = maininfoDIC['sa']


    print("QI", QI)
    print("SA", SA)

    print("df_ori before testing 003 top: ")
    print (df_ori)
    print("df_ano before testing 003 top: ")
    print (df_ano)
    print("p before testing 003 top: ")
    print (p)

    _vlogger.debug('getting df_ori(pandas dataframe): ')
    _vlogger.debug(df_ori)
    _vlogger.debug('getting df_ano(pandas dataframe): ')
    _vlogger.debug(df_ano)
    _vlogger.debug('getting p(pandas dataframe): ')
    _vlogger.debug(p)



    print ('testing 003')
    #20200211核心代碼
    #這裡是風險運行主要地方，同時將狀態紀錄更新上MySQL裡面
    ######################################################################################
    print("-"*10, "Security", "-"*10)
    _vlogger.debug('Inside the security functions: ')

    updateAppStatus_.updateToMysql("go into the security 001","10")
    security = get_security(df_ori, df_ano, attribute, SA, QI, p, detail_setting)
    updateAppStatus_.updateToMysql("go into the security 002","15")

    risk_s3 = security.S3()
    #20200212增加spark狀態
    updateAppStatus_.updateToMysql("get the security 001 result","20")
    _vlogger.debug('The security r1: ')
    _vlogger.debug(risk_s3)


    risk_s4_sa = security.S4_SA()
    #20200212增加spark狀態
    updateAppStatus_.updateToMysql("get the security 002 result","30")
    _vlogger.debug('The security r2: ')
    _vlogger.debug(risk_s4_sa)

    risk_s4_sum = security.S4_summation()
    #20200212增加spark狀態
    updateAppStatus_.updateToMysql("get the security 003 result","40")
    _vlogger.debug('The security r3: ')
    _vlogger.debug(risk_s4_sum)

    risk_s5 = security.S5()
    #20200212增加spark狀態
    updateAppStatus_.updateToMysql("get the security 004 result","60")
    _vlogger.debug('The security r4: ')
    _vlogger.debug(risk_s5)

    risk_s6 = security.S6()
    #20200212增加spark狀態
    updateAppStatus_.updateToMysql("get the security 005 result","80")
    _vlogger.debug('The security r5: ')
    _vlogger.debug(risk_s6)

    #getStarts
    rs_risk_s3 = getStars(risk_s3)
    rs_risk_s4_sa = getStars(risk_s4_sa)
    rs_risk_s4_sum = getStars(risk_s4_sum)
    rs_risk_s5 = getStars(risk_s5)
    rs_risk_s6 = getStars(risk_s6)
    #20200211核心代碼
    ######################################################################################

    #將風險分析結果寫入MySQL裡面
    #insert the value into mysql start
    global conn
    conn = ConnectSQL()
    # dbName = 'DeIdService'
    # tblName = 'T_Project_RiskTable'

    #20200211更新mysql內容(判斷是要insert or update)
    #################################################
    checkAvailable = checkAvailable(project_id)
    print ('checkAvailable value: ')
    print (checkAvailable)

    _vlogger.debug('Writting into mysql: ')

    #如果資料裡面已經有該資料，則更新MySQL，若沒有，則新增一筆進去
    if checkAvailable == 0:
        columns = 'project_id,project_name,dbname,tblname,r1,r2,r3,r4,r5,rs1,rs2,rs3,rs4,rs5,createtime,updatetime'
        conn.cursor.execute("set names utf8")

        #OK
        sqlStr = "INSERT INTO {}.{} ".format('DeIdService', 'T_Project_RiskTable')
        sqlStr = sqlStr + " ({}) ".format(columns)
        sqlStr = sqlStr + " VALUES ({},\'{}\',\'{}\',\'{}\',{},{},{},{},{},{},{},{},{},{},NOW(),NOW())".format(project_id,'getRisk',dbName,tblName,risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6)

        print('sqlStr in insert mysql')
        print (sqlStr)

        conn.cursor.execute(sqlStr)
        conn.connection.commit()

        print('finish the process in insert mysql')
    
    elif checkAvailable == 1:
        conn.cursor.execute("set names utf8")
        #OK
        sqlStr = "UPDATE {}.{} ".format('DeIdService', 'T_Project_RiskTable')
        sqlStr = sqlStr + "SET r1={},r2={},r3={},r4={},r5={},rs1={},rs2={},rs3={},rs4={},rs5={},updatetime = now()".format(risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6)
        sqlStr = sqlStr + " WHERE project_id like \'{}\'".format(project_id)

        print('sqlStr in update mysql')
        print (sqlStr)

        conn.cursor.execute(sqlStr)
        conn.connection.commit()

        print('finish the process in update mysql')

    else:
        return True



    # try:
    #     conn.cursor.execute("set names utf8")
    #     #OK
    #     sqlStr = "UPDATE {}.{} ".format('DeIdService', 'T_Project_RiskTable')
    #     sqlStr = sqlStr + "SET r1={},r2={},r3={},r4={},r5={},rs1={},rs2={},rs3={},rs4={},rs5={},updatetime = now()".format(risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6)
    #     sqlStr = sqlStr + " WHERE project_id like \'{}\'".format(project_id)

    #     print('sqlStr in update mysql')
    #     print (sqlStr)

    #     conn.cursor.execute(sqlStr)
    #     conn.connection.commit()

    #     print('finish the process in update mysql')
    
    # except:
    #     columns = 'project_id,project_name,dbname,tblname,r1,r2,r3,r4,r5,rs1,rs2,rs3,rs4,rs5,createtime,updatetime'
    #     conn.cursor.execute("set names utf8")

    #     #OK
    #     sqlStr = "INSERT INTO {}.{} ".format('DeIdService', 'T_Project_RiskTable')
    #     sqlStr = sqlStr + " ({}) ".format(columns)
    #     sqlStr = sqlStr + " VALUES ({},\'{}\',\'{}\',\'{}\',{},{},{},{},{},{},{},{},{},{},NOW(),NOW())".format(project_id,'getRisk',dbName,tblName,risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6)

    #     print('sqlStr in insert mysql')
    #     print (sqlStr)

    #     conn.cursor.execute(sqlStr)
    #     conn.connection.commit()

    #     print('finish the process in insert mysql')
    #################################################



    #20200211原本insert
    #################################################
    # columns = 'project_id,project_name,dbname,tblname,r1,r2,r3,r4,r5,rs1,rs2,rs3,rs4,rs5'
    # conditions = project_id,'getRisk',dbName,tblName,risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6

    # conn.cursor.execute("set names utf8")

    # #OK
    # sqlStr = "INSERT INTO {}.{} ".format('DeIdService', 'T_Project_RiskTable')
    # sqlStr = sqlStr + " ({})  values".format(columns)
    # sqlStr = sqlStr + " {}".format(conditions)
    #################################################

    #20200211原本insert(加上createtime & updatetime)
    #################################################
    # columns = 'project_id,project_name,dbname,tblname,r1,r2,r3,r4,r5,rs1,rs2,rs3,rs4,rs5,createtime,updatetime'

    # conn.cursor.execute("set names utf8")

    # #OK
    # sqlStr = "INSERT INTO {}.{} ".format('DeIdService', 'T_Project_RiskTable')
    # sqlStr = sqlStr + " ({}) ".format(columns)
    # sqlStr = sqlStr + " VALUES ({},\'{}\',\'{}\',\'{}\',{},{},{},{},{},{},{},{},{},{},NOW(),NOW())".format(project_id,'getRisk',dbName,tblName,risk_s3,risk_s4_sa,risk_s4_sum,risk_s5,risk_s6,rs_risk_s3,rs_risk_s4_sa,rs_risk_s4_sum,rs_risk_s5,rs_risk_s6)

    # print('sqlStr')
    # print (sqlStr)
    #################################################
    


    #20200211先拿掉處理
    # conn.cursor.execute(sqlStr)
    # conn.connection.commit()
    #insert the value into mysql end

    #將風險資料顯示在celery上面
    print("method S3-IdRand risk: {0}%, and the threshold is {1}".format(risk_s3, rs_risk_s3))
    print("method S4-IdSA-SA1 risk: {0}%, and the threshold is {1}".format(risk_s4_sa, rs_risk_s4_sa)) 
    print("method S4-IdSA-summation risk: {0}%, and the threshold is {1}".format(risk_s4_sum, rs_risk_s4_sum)) 
    print("method S5-Sort-summation risk: {0}%, and the threshold is {1}".format(risk_s5, rs_risk_s5)) 
    print("method S6-Sort-SA1 risk: {0}%, and the threshold is {1}".format(risk_s6, rs_risk_s6)) 

    # test_content1 = "Method Arbitrary target re-identify risk (QI-based) {0}%, and the threshold is {1} \n".format(risk_s3, rs_risk_s3)
    # test_content2 = "Method Single project re-identify risk (QI-based): {0}%, and the threshold is {1} \n".format(risk_s4_sa, rs_risk_s4_sa)
    # test_content3 = "Method Multiple project re-identify risk (QI-based): {0}%, and the threshold is {1} \n".format(risk_s4_sum, rs_risk_s4_sum)
    # test_content4 = "Method Multiple sequential order conjecture risk: {0}%, and the threshold is {1} \n".format(risk_s5, rs_risk_s5)
    # test_content5 = "Method Single sequential order conjecture risk: {0}%, and the threshold is {1} \n".format(risk_s6, rs_risk_s6)

    # f = open("/home/hadoop/proj_/longTaskDir/risk_core/risk_report.txt",'wb')
    # f.write(test_content1.encode('utf-8'))
    # f.write(test_content2.encode('utf-8'))
    # f.write(test_content3.encode('utf-8'))
    # f.write(test_content4.encode('utf-8'))
    # f.write(test_content5.encode('utf-8'))
    # f.close()


    #202020319, updateTProjectStatus##########################################################  
    project_status = 10 
    statusname='興趣欄位設定'
    updateTProjectStatus_.updateToMysql(project_id, project_status,statusname)
    
    _logger.debug('finish the process in update mysql')
    
    #############################################################################
    
    
    #20200212增加spark狀態
    updateAppStatus_.updateToMysql("Done","100","Finished")
    _vlogger.debug('Finished')

    print ('testing Finished')

if __name__ == "__main__":
    #20200214新增log
    global maininfoDIC, project_id, updateAppStatus_, _logger, _vlogger
    # debug log
    _logger  =_getLogger('error__Risk')
    # verify log
    _vlogger =_getLogger('verify__Risk')

    _vlogger.debug('------Risk Start------') 

    #前端傳入的base64檔案轉換成JSON
    data_ = sys.argv[1]
    data = json.loads(base64.b64decode(data_).decode("utf-8"))

    _vlogger.debug('the base64 code from long task: ') 
    _vlogger.debug(data_)

    _vlogger.debug('the json code from long task: ') 
    _vlogger.debug(data)
    # try:
    #     test_df_ori = data['pro_tb']
    #     test_df_ano = data['final_tb']
    #     test_QI = data['qi']
    #     #reqFunc = data['reqFunc']
    # except Exception as err:
    #     print('get parameter error! - %s:%s' %(type(err).__name__, err))
         

    # print ('testing loading base64 in main.py')
    # print ('test_df_ori: ')
    # print (test_df_ori)
    # print ('test_QI: ')
    # print (test_QI)

    #20200211修正project_id
    project_id = data['project_id']


    print ('######')
    #缺dbname、tbname這兩個
    try:
        maininfo = data['mainInfo']

        #20200213測試問題在哪
        print ('maininfo inside the main.py: ')
        print ('maininfo')
        print (maininfo)

        maininfoDIC =  maininfo[0] #目前是單一table
        df_ori = maininfoDIC['pro_tb']
        df_ano = maininfoDIC['final_tb']
    except Exception as err:
        print('maininfo error! - %s:%s' %(type(err).__name__, err))
    # p = data['p']
    # QI = data['QI']
    # SA = data['SA']

    _vlogger.debug('maininfo: ')
    _vlogger.debug(maininfo)

    print ('df_ori:' + df_ori)
    print ('df_ano:' + df_ano)
    # print ('p:' + p)
    # print ('QI:')
    # print (QI)
    # print ('SA:')
    # print (SA)

    print ('############')
    main()
