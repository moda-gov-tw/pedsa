# open file
import os
import subprocess
import configparser

# data analysis and wrangling
import pandas as pd
import numpy as np
import ast
import sys
import math
import json
import base64

# ML library
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from MyLib.connect_sql import ConnectSQL

from logging_tester import _getLogger

Models=[
    {'Model Name':'XGBoost', 'Model':XGBClassifier(), 'Training Score':0, 'Validation Score':0},    
    {'Model Name':'Random Forest', 'Model':RandomForestClassifier(n_estimators=100), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Logistic Regression', 'Model':LogisticRegression(solver='lbfgs'), 'Training Score':0, 'Validation Score':0}
]

#{'Model Name':'Linear SVC', 'Model':LinearSVC(), 'Training Score':0, 'Validation Score':0},
#{'Model Name':'XGBoost', 'Model':XGBClassifier(), 'Training Score':0, 'Validation Score':0},
#{'Model Name':'SVM', 'Model':SVC(gamma='auto'), 'Training Score':0, 'Validation Score':0},

def getCategoryCol(df):
    category_cols = []
    for c in list(df):
        if np.dtype(df[c]).name == 'object':
            category_cols.append(c)
    return category_cols        

def dropIDlikeCol(df):
    df_= df
    for col in df.columns:
        try: 
            pd.to_numeric(df[col])
        except:
            if df[col].nunique()>=len(df)*0.8:
                df_ = df_.drop(col, axis=1)            
    return df_

def preprocess(raw_df, syn_df, colName):
    try:
        #drop the rows that have missing value
        raw_df = raw_df.dropna(axis=0,how='any')
        syn_df = syn_df.dropna(axis=0,how='any')
    
        #drop ID like columns
        raw_df = dropIDlikeCol(raw_df)
        syn_df = syn_df[raw_df.columns]

        L_raw = len(raw_df)
    
        #check number of target types
        catagoryNum_raw = raw_df[colName].nunique()
        catagoryNum_syn = syn_df[colName].nunique()
        if catagoryNum_raw == 1 or catagoryNum_syn == 1:
            _logger.debug("ML preprocess error : {}".format('number of target types is 1'))
            return None

        #combine two dataset for dummy variables
        combine = pd.concat([raw_df,syn_df], axis=0, sort=True)

        #convert target col. categories to int
        labelEncode = LabelEncoder()
        labelEncode.fit(combine[colName])
    
        #print(labelEncode.classes_)
        target = labelEncode.transform(combine[colName])
        train = combine.drop(colName, axis=1)
    
        categoryCols = getCategoryCol(train)
        trainDummy = pd.get_dummies(train, columns=categoryCols, drop_first=False)

        #separate data
        raw_X = trainDummy[:L_raw]
        raw_y = target[:L_raw]
        syn_X = trainDummy[L_raw:]
        syn_y = target[L_raw:]
        return raw_X, raw_y, syn_X, syn_y     
    except Exception as e:
        _logger.debug('ML preprocess error : {}'.format(str(e)))
        return None   

def ML_method(X_train, X_val, Y_train, Y_val):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.fit_transform(X_val)  
    n_classes_ = len(np.unique(Y_train))
    if n_classes_ > 2:
        Models[0]['Model'] = XGBClassifier(objective='multi:softprob', num_class=n_classes_)
    for model in Models:
        Model_ = model['Model']
        Model_.fit(X_train, Y_train)
        model['Training Score'] = round(Model_.score(X_train, Y_train) * 100, 2)
        model['Validation Score'] = round(Model_.score(X_val, Y_val) * 100, 2)  
        modelResult = pd.DataFrame(Models,columns=['Model Name', 'Training Score', 'Validation Score'])
    return modelResult   

def updateToMysql_utilityResult(conn, projID_, targetCol, privacy_type, model, MLresult):
    # update process status to mysql

    print('########updateToMysql_status###########')
    conditionSampleData = {
            'project_id': projID_,
            'privacy_type': privacy_type,
            'target_col': targetCol,
            'model': model
        }

    valueSampleData = {
            'project_id': projID_,
            'privacy_type': privacy_type,
            'target_col': targetCol,
            'model': model,
            'MLresult': MLresult#','.join(errorlog)
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('PetsService',#'DeIdService',
                                            'T_Pets_UtilityResult',
                                            conditionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        errMsg ='insertUtilityResultToMysql fail: ' + msg
        _logger.debug(errMsg)
        #self.update_state(state="FAIL", meta={'Msg':errMsg,'stateno':'-2'})
        return "Fail" 

def updateToMysql_status(conn, userID_, projID_, step_):
    # update process status to mysql
    conditionSampleData = {
            'project_id': projID_
        }

    valueSampleData = {
            'project_id': projID_,
            'createMember_Id':userID_,
            'project_status': step_
        }

    resultSampleData = conn.updateValueMysql('PetsService',#'DeIdService',
                                            'T_Pets_ProjectStatus',
                                            conditionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        _logger.debug('insertProjectStatusToMysql fail: ' + msg)
        return None

def deleteExistReport(conn, projID_, privacyType_):
    del_result = conn.deleteValue('PetsService', 'T_Pets_UtilityResult', {'project_id':projID_, 'privacy_type':privacyType_})
    return del_result

def updateToMysql_jobSyslog(conn, userID_, projID_, projName_, step_, privacy_type_, percentage_):
    # update process status to mysql
    conditionSampleData = {
            'project_id': projID_,
            'jobname' : 'ML utility'
        }

    valueSampleData = {
            'project_id': projID_,
            'jobname' : 'ML utility',
            'member_id': userID_,
            'project_step' : step_,
            'percentage' : percentage_,
            'log_type' : 2,
            'logcontent' : 'Member ID:{} execute {} {} data ML utility'.format(userID_, projName_, privacy_type_)
        }

    resultSampleData = conn.updateValueMysql('PetsService',#'DeIdService',
                                            'T_Pets_JobSyslog',
                                            conditionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        _logger.debug('insertProjectStatusToMysql fail: ' + msg)
        return None  
    

def main():

    _vlogger.debug('------MLutility Start------')

    #delete exist report with same projID and privacyType
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
        deleteExistReport(check_conn, projID, privacyType)
        check_conn.close()
    except Exception as e:
        _logger.debug('connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return None

    #Initial T_Pets_ProjectStatus
    try:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, 8)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    #Initial T_Pets_JobSyslog
    try:
        check_conn = ConnectSQL()
        updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'initial', privacyType, 0)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    try:
        #read privacy data
        _vlogger.debug('read privacy data')
        privacyDataName = os.listdir(dir_+privacyType)[0]
        privacy_df = pd.read_csv(dir_+privacyType+'/'+privacyDataName)
        dataCols = privacy_df.columns

        check_conn = ConnectSQL()
        updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'read data', privacyType, 5)
        check_conn.close()

        #read raw data
        _vlogger.debug('read raw data')
        rawDataName = os.listdir(dir_+'raw')[0]
        raw_df_all = pd.read_csv(dir_+'raw/'+rawDataName)
        raw_df = raw_df_all[dataCols]
    except Exception as e:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, 91)
        _logger.debug('errTable: read data error - {}'.format(str(e)))
        check_conn.close()
        return None

    _vlogger.debug('targetCols : {}'.format(str(targetCols)))
       
    c = 0
    p = 60/len(targetCols)
    for colName_ in targetCols:
        _vlogger.debug('-----------------------------')
        _vlogger.debug('target - ' + colName_)
        
        check_conn = ConnectSQL()
        c+=1
        updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'training ML model', privacyType, 5+p*c)
        check_conn.close()
                
        preprocessData = preprocess(raw_df, privacy_df, colName_)

        if preprocessData is None:
            _logger.debug("{} : The number of types is 1".format(colName_))
            continue # continue next targetCols
        else:
            raw_X, raw_y, privacy_X, privacy_y = preprocessData

        #raw/raw
        _vlogger.debug('model - raw / raw')
        X_train_raw, X_val_raw, Y_train_raw, Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2, random_state=42)

        while( len(np.unique(Y_train_raw)) == 1 ):
            X_train_raw, X_val_raw, Y_train_raw, Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2)

        raw_result = ML_method(X_train_raw, X_val_raw, Y_train_raw, Y_val_raw).set_index('Model Name')
        _vlogger.debug(raw_result)
        _vlogger.debug('MLresult - '+str(raw_result.to_dict('index')))

        json_string = json.dumps(raw_result.to_dict('index'))
        MLresult_b64 = base64.b64encode(json_string.encode()).decode()
        
        try:
            check_conn = ConnectSQL()
            updateToMysql_utilityResult(check_conn, projID, colName_, privacyType, 'raw/raw', MLresult_b64)
            _vlogger.debug('updateToMysql_utilityResult succeed.')
            check_conn.close()
        except Exception as e:
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn, userID, projID, 91)
            check_conn.close()
            errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
            _logger.debug(errMsg)
            
    
        #privacy / privacy
        _vlogger.debug('model - privacy / privacy')
        X_train_privacy, X_val_privacy, Y_train_privacy, Y_val_privacy = train_test_split(privacy_X, privacy_y, test_size=0.2, random_state=42)

        while( len(np.unique(Y_train_privacy)) == 1 ):
            X_train_privacy, X_val_privacy, Y_train_privacy, Y_val_privacy = train_test_split(privacy_X, privacy_y, test_size=0.2)

        privacy_result = ML_method(X_train_privacy, X_val_privacy, Y_train_privacy, Y_val_privacy).set_index('Model Name')
        _vlogger.debug(privacy_result)
        _vlogger.debug('MLresult - '+str(privacy_result.to_dict('index'))) 

        json_string = json.dumps(privacy_result.to_dict('index'))
        MLresult_b64 = base64.b64encode(json_string.encode()).decode()
        
        try:
            check_conn = ConnectSQL()
            updateToMysql_utilityResult(check_conn, projID, colName_, privacyType, 'privacy/privacy', MLresult_b64)
            _vlogger.debug('updateToMysql_utilityResult succeed.')
            check_conn.close()
        except Exception as e:
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn, userID, projID, 91)
            check_conn.close()
            errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
            _logger.debug(errMsg)

    try:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, 9)
        updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'finish', privacyType, 100)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
        
    _vlogger.debug('------MLutility Finished------')
           
if __name__ == '__main__':
    global  _logger,_vlogger     
    # debug log
    _logger  =_getLogger('error__MLutility')
    # verify log
    _vlogger =_getLogger('verify__MLutility')

    userID = sys.argv[1]
    projID = sys.argv[2]
    projName = sys.argv[3]
    privacyType = sys.argv[4]
    targetCols = ast.literal_eval(sys.argv[5]) #list of target columns ex.['class']
    
    _vlogger.debug('userID : {}'.format(userID))
    _vlogger.debug('projID : {}'.format(projID))
    _vlogger.debug('projName : {}'.format(projName))
    _vlogger.debug('privacyType : {}'.format(privacyType))
    _vlogger.debug('targetCols : {}'.format(str(targetCols)))

    dir_ = '/app/app/devp/PETs_data/'+projName+'/'

    #get project raw data name
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("get join data name")
        sqlStr = 'select jointablename from PetsService.T_Pets_Project where project_id={}'.format(projID)
        rawDataName = check_conn.doSqlCommand(sqlStr)['fetchall'][0]['jointablename']
        _vlogger.debug('rawDataName : {}'.format(rawDataName))
        check_conn.close()
    except Exception as e:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, 91)
        check_conn.close()
        _logger.debug('get jointablename fail: - %s:%s' %(type(e).__name__, e))
        sys.exit()

    #install sshpass
    runcode = os.system('apt install sshpass')
    try:
        file_ = 'app/devp/config/Hadoop_information.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        user = config.get('Hadoop_information', 'user')
        passwd = config.get('Hadoop_information', 'passwd')
        ip = config.get('Hadoop_information', 'ip')
        port = config.get('Hadoop_information', 'hdfs_port')
        rawDataDir = config.get('Hadoop_information', 'rawData_path')
        privacyDataDir = config.get('Hadoop_information', 'privacyData_path')
        
        #create raw data folder : /app/app/devp/PETs_data/projName/raw
        cmd = 'mkdir -p '+dir_+'raw'
        proc = subprocess.run(cmd, shell=True,check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #copy raw data csv to /app/app/devp/PETs_data/projName/raw
        #cmd = 'sshpass -p \"'+passwd+'\" scp -o StrictHostKeyChecking=no -P '+port+' -r '+user+'@'+ip+':'+rawDataDir+projName+'/'+rawDataName+'/'+rawDataName+'.csv'+' /app/app/devp/PETs_data/'+projName+'/raw/'
        cmd = 'sshpass -p "citcw200@" '+f'scp -o StrictHostKeyChecking=no -P {port} -r hadoop@{ip}:{rawDataDir}{projName}/{rawDataName}/{rawDataName}.csv {dir_}raw/'
        proc = subprocess.run(cmd, shell=True,check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #create privacyType data folder : /app/app/devp/PETs_data/projName/privacyType
        cmd = 'mkdir -p '+dir_+privacyType
        proc = subprocess.run(cmd, shell=True,check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if privacyType=='k':
            privacyDataDir = privacyDataDir+'k/input/'+projName
        elif privacyType=='syn':
            privacyDataDir = privacyDataDir+'syn/output/'+projName
        else:
            privacyDataDir = privacyDataDir+'dp/output/'+projName
            
        #copy privacy data csv to /app/app/devp/PETs_data/projName/privacyType
        #cmd = 'sshpass -p \"'+passwd+'\" scp -o StrictHostKeyChecking=no -P '+port+' '+user+'@'+ip+':'+privacyDataDir+'/*.csv '+dir_+privacyType
        cmd = 'sshpass -p "citcw200@" '+f'scp -o StrictHostKeyChecking=no -P {port} -r hadoop@{ip}:{privacyDataDir}/*.csv {dir_}{privacyType}/'
        proc = subprocess.run(cmd, shell=True,check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, 91)
        check_conn.close()
        _logger.debug("---ERROR---" + str(e))
        sys.exit()

    main()
    
    
