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
import re
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
from MyLib.loginInfo import getConfig

from logging_tester import _getLogger

import shlex

Models=[
    {'Model Name':'XGBoost', 'Model':XGBClassifier(), 'Training Score':0, 'Validation Score':0},    
    {'Model Name':'Random Forest', 'Model':RandomForestClassifier(n_estimators=100), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Logistic Regression', 'Model':LogisticRegression(solver='lbfgs'), 'Training Score':0, 'Validation Score':0}
]

#{'Model Name':'Linear SVC', 'Model':LinearSVC(), 'Training Score':0, 'Validation Score':0},
#{'Model Name':'XGBoost', 'Model':XGBClassifier(), 'Training Score':0, 'Validation Score':0},
#{'Model Name':'SVM', 'Model':SVC(gamma='auto'), 'Training Score':0, 'Validation Score':0},

def compare_scores(org_dict, syn_dict, threshold=10):
    # Check if the Validation Score of each model is within the threshold
    high_count = 0
    
    for model in org_dict:
        diff = abs(org_dict[model]['Validation Score'] - syn_dict[model]['Validation Score'])
        if diff <= threshold:
            high_count += 1
    
    if high_count >=2:
        return "High"
    elif high_count >= 1 :
        return "Medium"
    else:
        return "Low"

def get_obcol(conn,pro_name,privacyType):
    if privacyType == 'syn':
        #It will access SYN_DB and retrieve the necessary categorical fields for SYN SETTING.
        sqlStr = f"SELECT ob_col FROM SynService.T_ProjectColumnType WHERE pro_name = '{pro_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
            return resultSampleData['fetchall'][0]['ob_col'].split(',')
        else:
            #msg = resultSampleData['msg']
            _logger.debug('fetch SYN DataToMysql fail: ')# + msg)
            return None
    
    elif privacyType == 'dp': 
        #It will access DP_DB and retrieve the necessary categorical fields for DP SETTING.
        sqlStr = f"SELECT selectcol FROM DpService.T_ProjectColumnType WHERE pro_name = '{pro_name}'"        
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0]['selectcol'].split(',')
        else:
            #msg = resultSampleData['msg']
            _logger.debug('fetch DP DataToMysql fail: ')# + msg)
            return None
        
        sqlStr = f"SELECT selectcolvalue FROM DpService.T_ProjectColumnType WHERE pro_name = '{pro_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:    
            select_colValues = resultSampleData['fetchall'][0]['selectcolvalue'].split(',')
        else:
            #msg = resultSampleData['msg']
            _logger.debug('fetch DP DataToMysql fail: ')# + msg)
            return None


        try:
            grouped_columns = {'D': [], 'C': []}
            #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
            # group by ('D':vale/'C':categorical)
            for value, name in zip(select_colValues, select_colNames):
                grouped_columns[value].append(name)
            # group
            for key, value in grouped_columns.items():
                print(f"Values '{key}': {value}")
            discrete_columns = grouped_columns["C"]
            continue_columns = grouped_columns["D"]
            _vlogger.debug(f'discrete_columns:{discrete_columns}')
            _vlogger.debug(f'continue_columns:{continue_columns}')
            return discrete_columns
        except Exception as e:
            _logger.debug('DP preprocess error : {}'.format(str(e)))
            return None   
    
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

def preprocess(deidtype, raw_df, syn_df, colName, categorical_col=None):
    # Concatenate two datasets and then encode.
    if deidtype=='k':
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
                # check_conn = ConnectSQL()
                # updateToMysql_status(check_conn, userID, projID, 91)
                # check_conn.close()
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
    elif deidtype=='syn' or deidtype == 'dp':
        if categorical_col is not None:
            try:
                #drop the rows that have missing value
                raw_df = raw_df.dropna(axis=0,how='any')
                syn_df = syn_df.dropna(axis=0,how='any')
            
                #drop ID like columns
                raw_df = dropIDlikeCol(raw_df)
                syn_df = syn_df[raw_df.columns]

                L_raw = len(raw_df)
                _logger.debug('ML raw_df : {}'.format(str(raw_df.columns.to_list())))
                _logger.debug('ML syn_df : {}'.format(str(syn_df.columns.to_list())))
            
                #check number of target types
                catagoryNum_raw = raw_df[colName].nunique()
                catagoryNum_syn = syn_df[colName].nunique()
                if catagoryNum_raw == 1 or catagoryNum_syn == 1:
                    _logger.debug("ML preprocess error : {}".format('number of target types is 1'))
                    # check_conn = ConnectSQL()
                    # updateToMysql_status(check_conn, userID, projID, 91)
                    # check_conn.close()
                    return None

                #combine two dataset for dummy variables
                combine = pd.concat([raw_df,syn_df], axis=0, sort=True)

                #convert target col. categories to int
                labelEncode = LabelEncoder()
                labelEncode.fit(combine[colName])
            
                #print(labelEncode.classes_)
                target = labelEncode.transform(combine[colName])
                train = combine.drop(colName, axis=1)

                combine_columns_set = set(combine.columns.to_list())
                #categoryCols = getCategoryCol(train) ## ==categorical_col
                categorical_col_set = set(categorical_col)
                common_columns = combine_columns_set.intersection(categorical_col_set)
                categoryCols_list = list(common_columns - {colName})
                trainDummy = pd.get_dummies(train, columns=categoryCols_list, drop_first=False)
                #separate data
                raw_X = trainDummy[:L_raw]
                raw_y = target[:L_raw]
                syn_X = trainDummy[L_raw:]
                syn_y = target[L_raw:]
                return raw_X, raw_y, syn_X, syn_y     
            except Exception as e:
                _logger.debug('ML preprocess error : {}'.format(str(e)))
                return None         
        else:
            _logger.debug('ML preprocess error : {}'.format(str('Syn categorical_col is NONE.' )))
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

def updateToMysql_utilityResult(conn, projID_, targetCol, privacy_type, model, MLresult, utilitylevel=None):
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
            'utilitylevel': utilitylevel,
            'MLresult': MLresult#','.join(errorlog)
        }
    print(valueSampleData)

    resultSampleData = conn.updateValueMysql('PetsService',#'DeIdService',
                                            'T_Pets_UtilityResult',
                                            conditionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug(f"{projID_}: Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projID_}: insertSampleDataToMysql fail')
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
        _vlogger.debug(f"{projID_}: Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projID_}: insertSampleDataToMysql fail')
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
        _vlogger.debug(f"{projName_}: Update mysql succeed.")
        return None
    else:
        #msg = resultSampleData['msg']
        _logger.debug(f'{projName_}: insertSampleDataToMysql fail')
        return None  
    
def validate_directory(directory_path):
    real_path = os.path.realpath(directory_path)
    if not os.path.isdir(real_path):
        raise ValueError("Invalid directory")
    return real_path

def is_valid_path(path, base_dir):
    real_path = os.path.realpath(path)
    if not os.path.isabs(path):
        return False
    if not real_path.startswith(base_dir):
        return False
    return True

def is_valid_file(path, base_dir):
    real_path = os.path.realpath(path)
    if not os.path.isabs(path):
        return False
    if not os.path.isfile(real_path):
        return False
    if not real_path.startswith(base_dir):
        return False
    return True

def main(userID, projID, projName, privacyType, targetCols, dir_):

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

        dir_privacyType = os.path.join(dir_,privacyType)
        base_dir = '/app/app/devp/PETs_data/'
        if not is_valid_path(dir_privacyType ,base_dir):
            print("Invalid or non-existent path**1")    
            raise ValueError ("Invalid or non-existent path**1")  
        if not dir_privacyType.startswith(base_dir):
            raise ValueError("directory is outside the allowed base directory.")  

        privacyDataName = os.listdir(dir_privacyType)[0]
        privacycsvdir = os.path.join(dir_privacyType, privacyDataName)
        if not is_valid_file(privacycsvdir,base_dir):
            print("Invalid or non-existent file**2")    
            raise ValueError ("Invalid or non-existent file**2")    

        privacy_df = pd.read_csv(privacycsvdir)
        dataCols = privacy_df.columns

        check_conn = ConnectSQL()
        updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'read data', privacyType, 5)
        check_conn.close()

        #read raw data
        _vlogger.debug('read raw data')
        dir_raw = os.path.join(dir_, 'raw')
        if not is_valid_path(dir_raw ,base_dir):
            print("Invalid or non-existent path**3")    
            raise ValueError ("Invalid or non-existent path**3")  
        if not dir_raw.startswith(base_dir):
            raise ValueError("directory is outside the allowed base directory.")  
        
        rawDataName = os.listdir(dir_raw)[0]
        rawcsvdir = os.path.join(dir_raw, rawDataName)
        if not is_valid_file(rawcsvdir,base_dir):
            print("Invalid or non-existent file**4")    
            raise ValueError ("Invalid or non-existent file**4")    
        raw_df_all = pd.read_csv(rawcsvdir)
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

    if privacyType=='k':
        for colName_ in targetCols:
            _vlogger.debug('-----------------------------')
            _vlogger.debug('target - ' + colName_)
            
            check_conn = ConnectSQL()
            c+=1
            updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'training ML model', privacyType, 5+p*c)
            check_conn.close()
                    
            preprocessData = preprocess(privacyType, raw_df, privacy_df, colName_)

            if preprocessData is None:
                _logger.debug("{} : The number of types is 1".format(colName_))
                continue
                #     check_conn = ConnectSQL()
                #     updateToMysql_status(check_conn, userID, projID, 91)
                #     check_conn.close()
                #     _logger.debug("---ERROR---" + "{} : The number of types is 1".format(colName_))
                #     sys.exit()
                # else:
                #     continue # continue next targetCols
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

    elif privacyType=='syn' or privacyType == 'dp':
        for colName_ in targetCols:
            #colName_:target column
            _vlogger.debug('-----------------------------')
            _vlogger.debug('target - ' + colName_)
            
            #get ob_col
            try:
                check_conn = ConnectSQL()
                c+=1
                obcol = list(set(get_obcol(check_conn,projName,privacyType))) #string to list
                _vlogger.debug('------{}__MLobcol: {}------'.format(projName,obcol))
                updateToMysql_jobSyslog(check_conn, userID, projID, projName, 'training ML model', privacyType, 5+p*c)
                check_conn.close()
            except Exception as e:
                check_conn = ConnectSQL()
                updateToMysql_status(check_conn, userID, projID, 91)
                check_conn.close()
                errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
                _logger.debug(errMsg)

            #syn_preprocess:Encode according to the categorical types defined by SYNDB.                   
            preprocessData = preprocess(privacyType, raw_df, privacy_df, colName_, obcol)

            if preprocessData is None:
                _logger.debug("{} : The number of types is 1".format(colName_))
                if len(targetCols)==1:
                    continue
                #     check_conn = ConnectSQL()
                #     updateToMysql_status(check_conn, userID, projID, 91)
                #     check_conn.close()
                #     _logger.debug("---ERROR---" + "{} : The number of types is 1".format(colName_))
                #     sys.exit()
                # else:
                #     continue # continue next targetCols
            else:
                raw_X, raw_y, privacy_X, privacy_y = preprocessData

            #raw/raw
            _vlogger.debug('model - raw / raw')
            X_train_raw, X_val_raw, Y_train_raw, Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2, random_state=42)

            while( len(np.unique(Y_train_raw)) == 1 ):
                X_train_raw, X_val_raw, Y_train_raw, Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2)

            raw_result = ML_method(X_train_raw, X_val_raw, Y_train_raw, Y_val_raw).set_index('Model Name')
            _vlogger.debug(raw_result)
            r_r_dict = raw_result.to_dict('index')
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
            p_p_dict = privacy_result.to_dict('index')
            _vlogger.debug('MLresult - '+str(privacy_result.to_dict('index'))) 
            json_string = json.dumps(privacy_result.to_dict('index'))
            MLresult_b64 = base64.b64encode(json_string.encode()).decode()
            try:
                check_conn = ConnectSQL()
                updateToMysql_utilityResult(check_conn, projID, colName_, privacyType, 'privacy/privacy', MLresult_b64, str(compare_scores(r_r_dict, p_p_dict)))
                _vlogger.debug('updateToMysql_utilityResult succeed.')
                check_conn.close()
            except Exception as e:
                check_conn = ConnectSQL()
                updateToMysql_status(check_conn, userID, projID, 91)
                check_conn.close()
                errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
                _logger.debug(errMsg)   

            #privacy / raw
            _vlogger.debug('model - privacy / raw')
            privacy_result = ML_method(X_train_privacy, X_val_raw, Y_train_privacy, Y_val_raw).set_index('Model Name')
            _vlogger.debug(privacy_result)
            p_r_dict = privacy_result.to_dict('index')
            _vlogger.debug('MLresult - '+str(privacy_result.to_dict('index'))) 
            json_string = json.dumps(privacy_result.to_dict('index'))
            MLresult_b64 = base64.b64encode(json_string.encode()).decode()
            try:
                check_conn = ConnectSQL()
                updateToMysql_utilityResult(check_conn, projID, colName_, privacyType, 'privacy/raw', MLresult_b64, str(compare_scores(r_r_dict, p_r_dict)))
                _vlogger.debug('updateToMysql_utilityResult succeed.')
                check_conn.close()
            except Exception as e:
                check_conn = ConnectSQL()
                updateToMysql_status(check_conn, userID, projID, 91)
                check_conn.close()
                errMsg = 'updateToMysql_utilityResult fail. {0}'.format(str(e))
                _logger.debug(errMsg) 
            
            _vlogger.debug('###utility level####r_r_dict_vs_p_r_dict {0}'.format(str(compare_scores(r_r_dict, p_r_dict))))
            _vlogger.debug('###utility level####r_r_dict_vs_p_p_dict {0}'.format(str(compare_scores(r_r_dict, p_p_dict))))
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
    projName = shlex.quote(projName)

    if not userID.isdigit():
        print(f"{projName}__errTable:Invalid userID format")
        raise ValueError(f"{projName}__errTable: Invalid userID format")

    if not projID.isdigit():
        print(f'{projName}__errTable: Invalid projID format')
        raise ValueError(f'{projName}__errTable: Invalid projID format')

    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName)or projName.isdigit()or '..' in projName or '/' in projName:
        print(f"{projName}__errTable:Invalid projName format")
        raise ValueError(f"{projName}__errTable:Invalid projName format")

    privacyType = sys.argv[4]
    privacyType = shlex.quote(privacyType)
    valid_projIDs = {"dp", "k", "syn"}
    if privacyType not in valid_projIDs:
        print(("Invalid privacyType format"))
        raise ValueError("Invalid privacyType format")

    
    try:
        targetCols = ast.literal_eval(sys.argv[5]) #list of target columns ex.['class']
        if not isinstance(targetCols, list):
            raise ValueError("Input should be a list.")
    except (ValueError, SyntaxError) as e:
        print(f"Invalid input: {e}")
    
    _vlogger.debug('userID : {}'.format(userID))
    _vlogger.debug('projID : {}'.format(projID))
    _vlogger.debug('projName : {}'.format(projName))
    _vlogger.debug('privacyType : {}'.format(privacyType))
    _vlogger.debug('targetCols : {}'.format(str(targetCols)))

    dir_ = '/app/app/devp/PETs_data/'+projName+'/'
    base_dir = '/app/app/devp/PETs_data/'
    if not is_valid_path(dir_,base_dir):
        print("Invalid or non-existent file path**0")    
        raise ValueError ("Invalid or non-existent file path**0")  
    if not dir_.startswith(base_dir):
        raise ValueError("directory is outside the allowed base directory.")
        
    #get project raw data name
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("=====get join data name")
        sqlStr = 'select jointablename from PetsService.T_Pets_Project where project_id={}'.format(projID)
        rawDataName = check_conn.doSqlCommand(sqlStr)['fetchall'][0]['jointablename']
        _vlogger.debug('=====rawDataName : {}'.format(rawDataName))
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
        join_ip = config.get('Hadoop_information', 'ip_join') 
        hdfsInfo = getConfig().getLoginHdfs()
        user_ = str(hdfsInfo['user']) #user of join
        password_ = str(hdfsInfo['password'])
        

        # Safely construct the directory path and create it using subprocess without shell=True
        raw_dir_ = os.path.join(dir_, 'raw')
        proc = subprocess.run(['mkdir', '-p', raw_dir_], check=True)

        #copy raw data csv to /app/app/devp/PETs_data/projName/raw
        #0911#1####################################
        scp_command = ['sshpass', '-p', password_, 
           'scp', '-o', 'StrictHostKeyChecking=no', '-r',
           f'{user_}@{join_ip}:{os.path.join(rawDataDir, projName, rawDataName, rawDataName)}.csv',
           os.path.join(dir_, 'raw/')
        ]
        proc = subprocess.run(scp_command,check=True)
    

        #create privacyType data folder : /app/app/devp/PETs_data/projName/privacyType
        privacy_dir_ = os.path.join(dir_, privacyType)
        proc = subprocess.run(['mkdir', '-p', privacy_dir_],check=True)

        if privacyType=='k':
            privacyDataDir = privacyDataDir+'k/input/'+projName
        elif privacyType=='syn':
            privacyDataDir = privacyDataDir+'syn/output/'+projName
        else:
            privacyDataDir = privacyDataDir+'dp/output/'+projName

        if not is_valid_path(privacyDataDir,'/home/hadoop/proj_/'):
            print("Invalid or non-existent file path**00")    
            raise ValueError ("Invalid or non-existent file path**00")  
        if not privacyDataDir.startswith('/home/hadoop/proj_/'):
            raise ValueError("directory is outside the allowed base directory.")      

        privacy_dir = os.path.join(dir_, privacyType)
        privacy_data_dir = os.path.join(privacyDataDir, '*.csv')
        # Securely run the scp command
        scp_command = [
           'sshpass', '-p', password_,
           'scp', '-o', 'StrictHostKeyChecking=no', '-r',
           f'{user_}@{join_ip}:{privacy_data_dir}',
           privacy_dir
        ]
        # copy privacy data csv to /app/app/devp/PETs_data/projName/privacyType
        proc = subprocess.run(scp_command,check=True)


    except Exception as e:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, 91)
        check_conn.close()
        _logger.debug("---ERROR---" + str(e))
        sys.exit()

    main(userID, projID, projName, privacyType, targetCols,dir_)
    
    
