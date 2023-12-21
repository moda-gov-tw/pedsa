# open file
import os

# data analysis and wrangling
import pandas as pd
import numpy as np
import ast
import sys
import math

# ML library
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession

from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateTProjectStatus import updateTProjectStatus

Models=[
    {'Model Name':'XGBoost', 'Model':XGBClassifier(), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'SVM', 'Model':SVC(gamma='auto'), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Random Forest', 'Model':RandomForestClassifier(n_estimators=100), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Linear SVC', 'Model':LinearSVC(), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Logistic Regression', 'Model':LogisticRegression(), 'Training Score':0, 'Validation Score':0}
]

def getCategoryCol(df):
    category_cols = []
    for c in list(df):
        if np.dtype(df[c]).name == 'object':
            category_cols.append(c)
    return category_cols        

#citc, raw_df, syn_df are all padas
#syn_df is an deId datframe
#_vlogger.debug('target - '+ colName_)
def preprocess(raw_df, syn_df, colName):
    #drop the rows that have missing value
    raw_df = raw_df.dropna(axis=0,how='any')#,inplace=True)
    syn_df = syn_df.dropna(axis=0,how='any')#,inplace=True)
    L_raw = len(raw_df)
    
    #_logger.debug("---citc preprocess 1 L_raw: {}".format(L_raw))
    
    if not raw_df.empty and not syn_df.empty:
        L_raw = len(raw_df)
    else:
        _logger.debug("ML preprocess error : {}".format('data has too many Na'))
        raise Excetption("ML preprocess error : "+'data has too many Na')

        #return None
    #_logger.debug("---citc preprocess 2 L_raw: {}".format(L_raw))
    #check number of target types
    catagoryNum_raw = raw_df[colName].nunique()
    catagoryNum_syn = syn_df[colName].nunique()
    
  
    if catagoryNum_raw == 1 or catagoryNum_syn == 1:
        _logger.debug("ML preprocess error : {}".format('number of target types is 1'))
        #return None
        raise Excetption("ML preprocess error : "+'number of target types is 1')

    #combine two dataset for dummy variables
    combine = pd.concat([raw_df,syn_df], axis=0)
    #_logger.debug("---citc preprocess 3 : {}".format("ML test 1"))
    #_logger.debug("---combine shape : {}".format("ML test 1"))

    #convert target col. categories to int
    labelEncode = LabelEncoder()
    labelEncode.fit(combine[colName])
    #_logger.debug("---citc preprocess 4 : {}, ---colName={}".format("ML test 2", colName))
    
    #print(labelEncode.classes_)
    target = labelEncode.transform(combine[colName])
    train = combine.drop(colName, axis=1)
    
    
    train_cols = list(train)
    #_logger.debug("---train_cols = {}, citc preprocess 5 : {}".format(train_cols, "ML test 3"))
    
    #######citc, 20220110 add start##########################################################################################
    col_distict_count = train.nunique(axis = 0)
    cancel_list = []
    for idx in train_cols:
        tmpInt = col_distict_count[idx] *2 #20220110, drop a column with distinct count > train.shape[0](row number)/2 
        #_logger.debug("--tmpInt={}----col_distict_count[{}] = {}".format(tmpInt, idx, col_distict_count[idx]))    
        
        if(tmpInt > train.shape[0]):
            _vlogger.debug("tmpInt: {}, cancel col name : {}".format(tmpInt, idx))
            #categoryCols.remove(idx)
            cancel_list.append(idx)
    
    #citc, #20220110, drop any column with distinct count > train.shape[0](row number)/2
    train = combine.drop(cancel_list, axis=1) 
    #######citc, 20220110 add end##########################################################################################
    
    try:
        #find category columns and convert to dummy variables
        categoryCols = getCategoryCol(train)
 
        #20220110, to one hot encode using pandas get_dummies
        trainDummy = pd.get_dummies(train, columns=categoryCols, drop_first=False)
        #_logger.debug("---citc preprocess 6 : {}".format("ML test 2"))
    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("--- citc errTable:preprocess:" + str(e))
        #citc, 20220316 
        raise Excetption("process err(trainDummy): "+str(e))

        #return null
    #_logger.debug("---trainDummy : {}".format(trainDummy))
    #_logger.debug("---target : {}".format(target))
    #separate data
    raw_X = trainDummy[:L_raw]
    raw_y = target[:L_raw]
    syn_X = trainDummy[L_raw:]
    syn_y = target[L_raw:]
    #_logger.debug("---citc preprocess 7 : {}".format("ML test 4"))
    return raw_X, raw_y, syn_X, syn_y        

#citc, df_raw, df_deid are all pandas dataframs 
def check_columns(df_raw, df_deid):
    missing_col =[]
    row,_ = df_deid.shape
        
    for i in (df_deid.columns):
        missing_count = df_deid[i].isnull().sum()
        #check wether #. NAN is greater than 50%
        if  missing_count >= (row*0.5):
            missing_col.append(i)
                #print("missing col: ",i)
                
    df_deid = df_deid.drop(missing_col, axis = 1)#, inplace=True)
    df_raw = df_raw.drop(missing_col, axis = 1)#, inplace=True)
    return missing_col, df_raw, df_deid

def ML_method(X_train, X_val, Y_train, Y_val):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.fit_transform(X_val)   
    n_classes_ = len(np.unique(Y_train))
    if n_classes_ > 2:
        Models[0]['Model'] = XGBClassifier(objective='multi:softprob', num_class=n_classes_)
    try: 
        for model in Models:
            _vlogger.debug("---citc modle['Model Name']:" + model['Model Name'])
            Model_ = model['Model']
            Model_.fit(X_train, Y_train)
            model['Training Score'] = round(Model_.score(X_train, Y_train) * 100, 2)
            model['Validation Score'] = round(Model_.score(X_val, Y_val) * 100, 2)  
            modelResult = pd.DataFrame(Models,columns=['Model Name', 'Training Score', 'Validation Score'])
    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("--- citc errTable:ML_method:" + str(e))
        #return 'null'
        return null
                
    return modelResult   

def initSparkContext(name):
    appName = name
    # master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _vlogger.debug("sparkContext_succeed.")

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
        _logger.debug("errTable:fundation_getGenNumLevel:" + str(e))
        _logger.debug("errTable:errSC")
        return SparkContext(conf=SparkConf())

    return sc_, hiveLibs, sqlContext

def getHiveData(dbName, tblName, cols):
    sqlContext.sql('use ' + dbName)

    tmpColsStr = ''
    for col_name_ in cols:
        tmpColsStr = tmpColsStr + col_name_
        if col_name_ != cols[len(cols)-1] and col_name_ !='*':
            tmpColsStr = tmpColsStr + ','
    query_str = 'SELECT %s FROM %s' %(tmpColsStr, tblName)

    _vlogger.debug('getHiveData_'+query_str)
    df = sqlContext.sql(query_str)
    return df

    
def main():
    global  _logger, _vlogger, sc, hiveLibs, sqlContext, updateAppStatus_, updateTProjectStatus_
    # debug log
    _logger  =_getLogger('error__MLutility')
    # verify log
    _vlogger =_getLogger('verify__MLutility')

    # spark setting
    appName = 'MLutility'
    sc, hiveLibs, sqlContext = initSparkContext(appName)
    
    _vlogger.debug('------MLutility Start------') 
     
    _vlogger.debug('ML_userAccount_%s',userAccount)
    _vlogger.debug('ML_userId_%s',userId)

    
    #read input data
    _vlogger.debug('projID : '+ str(projID))
    _vlogger.debug('dbName : '+ str(dbName))
    _vlogger.debug('rawTbl : '+ str(rawTbl))
    _vlogger.debug('deIdTbl : '+ str(deIdTbl))
    _vlogger.debug('targetCols : '+ str(targetCols))

    project_id = projID
    try:
        updateTProjectStatus_ = updateTProjectStatus(project_id, userId)
    except Exception as e:
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False

    try:
        #appID, appName
        updateAppStatus_ = updateAppStatus(sc.applicationId, appName,dbName,projID, userId)

        #updateAppStatus_ = updateAppStatus(sc.applicationId, NAME,projName,projID)
    except Exception as e:
        print('updateAppStatus error: %s', str(e))
        return False
    updateAppStatus_.updateToMysql("Init_1","5")

    try:
        #citc, add 20220207
        #Too few rows wiil result in an error 
        #(_logger.debug("ML preprocess error : {}".format('number of target types is 1')) in preprocess())
        checkRowNumForSample = 1

        if(checkRowNumForSample == 1):
            dataDF = getHiveData(dbName,deIdTbl,['*'])
            row_number = dataDF.count()
            column_number = len(dataDF.dtypes)
            
            sample_rate = 1.0 #20220329 (100-> 500)
            sample_rate_ = 1.0 #20220329 (100-> 500)
            if(row_number > 500): #20220329 (100-> 500)
                sample_rate_ = 500 / row_number#20220329 (100-> 500)
                #smaple_rate = round(sample_rate_,5)
                print("-#####--------------------row_number={}".format(row_number))
                print("-#####--------------------sample_rate_={}".format(sample_rate_))
                print("-#####--------------------sample_rate={}".format(sample_rate))
            sample_rate = round(sample_rate_,10) #20220329 (100-> 500)
            
            if(row_number < 10000):
                deId_df_ = dataDF.toPandas().replace({'NULL':None})
            elif (row_number > 9999) and (row_number < 100000):
                deId_df_ = dataDF.sample(False, 0.1, 1).toPandas().replace({'NULL':None})
            elif (row_number > 99999) and (row_number < 1000000):
                deId_df_ = dataDF.sample(False, 0.01, 1).toPandas().replace({'NULL':None})    
            else:
                # read from Hive 2022 sample 0.1 =10%
                deId_df_ = dataDF.sample(False, 0.001, 1).toPandas().replace({'NULL':None})
            
            #sample_rate = 0.05
            ##########citc, 20220317 tmp#############
            _logger.debug("row_number :"+str(row_number))
            sample_number_ = row_number*sample_rate
            _logger.debug("sample number :"+str(sample_number_))
            deId_df_ = dataDF.sample(False, sample_rate, 1).toPandas().replace({'NULL':None}) #20220329 (100-> 500)
            
            deId_cols = list(deId_df_)
            if(row_number < 10000):
                raw_df_ = getHiveData(dbName,rawTbl,deId_cols).toPandas().replace({'NULL':None})
            elif (row_number > 9999) and (row_number < 100000):
                raw_df_ = getHiveData(dbName,rawTbl,deId_cols).sample(False, 0.1, 1).toPandas().replace({'NULL':None})
            elif (row_number > 99999) and (row_number < 1000000):
                raw_df_ = getHiveData(dbName,rawTbl,deId_cols).sample(False, 0.01, 1).toPandas().replace({'NULL':None})
          
            else:
                raw_df_ = getHiveData(dbName,rawTbl,deId_cols).sample(False, 0.001, 1).toPandas().replace({'NULL':None})
            ##########citc, 20220317 tmp#############
            raw_df_ = getHiveData(dbName,rawTbl,deId_cols).sample(False, sample_rate, 1).toPandas().replace({'NULL':None}) #20220329 (100-> 500)
        else:
            #original code, no checking row number
            # read from Hive 2022 sample 0.1 =10%
            deId_df_ = getHiveData(dbName,deIdTbl,['*']).sample(False, 0.01, 1).toPandas().replace({'NULL':None})            
            deId_cols = list(deId_df_)
            raw_df_ = getHiveData(dbName,rawTbl,deId_cols).sample(False, 0.01, 1).toPandas().replace({'NULL':None})          
   
    except Exception as err:
        updateAppStatus_.updateToMysql("Error","100","Stopped")
        _logger.debug('read data error! - %s:%s' % (type(err).__name__, err))
        return None
    _vlogger.debug("sc.applicationId:" + sc.applicationId)
    
    #data cleaning by remove the column too much missing value
    try:
        missing_cols, raw_df, deId_df = check_columns(raw_df_, deId_df_)
        _vlogger.debug("droped columns - {}".format(str(missing_cols)))
        targetCols_drop = list(set(targetCols)-set(missing_cols))
        _vlogger.debug("droped targetCols : {}".format(str(missing_cols)))
        updateAppStatus_.updateToMysql("check data","10")
    except Exception as err:
        updateAppStatus_.updateToMysql("Error","100","Stopped")
        _logger.debug('check column error! - %s:%s' % (type(err).__name__, err))
        return None

    for colName_ in targetCols_drop:
        _vlogger.debug('deIdTbl - '+ str(deIdTbl))
        _vlogger.debug('target - '+ colName_)
        try:
            raw_X, raw_y, deId_X, deId_y = preprocess(raw_df, deId_df, colName_)
        except Exception as err:
            _logger.debug('preprocess error! - %s:%s' % (type(err).__name__, err))
            updateAppStatus_.updateToMysql("Error","100","Stopped")
            continue
        #if raw_X == None:
            #_vlogger.debug("ML preprocess msg : {}".format('number of target types is 1'))
            #continue
        #raw/raw
        _vlogger.debug('model - raw / raw')
        updateAppStatus_.updateToMysql("raw / raw","20")
        
        try:
            X_train_raw,X_val_raw,Y_train_raw,Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2, random_state=42)
            #_vlogger.debug("ML_method citc 123")
            Model_raw = ML_method(X_train_raw, X_val_raw, Y_train_raw, Y_val_raw).set_index('Model Name')
        except Exception as err:
            _logger.debug('raw/raw model error! - %s:%s' % (type(err).__name__, err))
            updateAppStatus_.updateToMysql("Error","100","Stopped")
        
        _vlogger.debug(Model_raw)
        _vlogger.debug('MLresult - '+str(Model_raw.to_dict('index')))
    
        #deId/deId
        _vlogger.debug('model - deId / deId')
        updateAppStatus_.updateToMysql("deId / deId","50")

        try:
            X_train_deId,X_val_deId,Y_train_deId,Y_val_deId = train_test_split(deId_X, deId_y, test_size=0.2, random_state=42)
            Model_deId = ML_method(X_train_deId, X_val_deId, Y_train_deId, Y_val_deId).set_index('Model Name')
        except Exception as err:
            _logger.debug('deId/deId model error! - %s:%s' % (type(err).__name__, err))
            updateAppStatus_.updateToMysql("Error","100","Stopped")

        _vlogger.debug(Model_deId)
        _vlogger.debug('MLresult - '+str(Model_deId.to_dict('index')))
    
    #updateTProjectStatus
    try:
        project_status =10
        statusname='MLutility finished'
        updateTProjectStatus_.updateToMysql(projID, project_status,statusname)

        updateAppStatus_.updateToMysql("Done","100","Finished")
        _vlogger.debug('------MLutility Finished------')

    except Exception as e:
        _logger.debug('update updateTProjectStatus_ error: %s', str(e)) 

#spark-submit /home/hadoop/proj_/longTaskDir/MLutility.py 1 2QDataMarketDeId mac_adult_id g_mac_adult_id_k_job1 "[u'c_2771_15']"
if __name__ == '__main__':
    projID = sys.argv[1]
    dbName = sys.argv[2]
    rawTbl = sys.argv[3]
    deIdTbl = sys.argv[4]
    targetCols = ast.literal_eval(sys.argv[5])
    userAccount = sys.argv[6]  # str
    userId = sys.argv[7]  # str     
    main()
    
    
