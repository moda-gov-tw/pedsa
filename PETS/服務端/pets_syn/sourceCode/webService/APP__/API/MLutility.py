# open file
import os

# data analysis and wrangling
import pandas as pd
import numpy as np
import ast
import sys
import math
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

from logging_tester import _getLogger

import shlex

Models=[
    {'Model Name':'XGBoost', 'Model':XGBClassifier(), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'SVM', 'Model':SVC(gamma='auto'), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Random Forest', 'Model':RandomForestClassifier(n_estimators=100), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Linear SVC', 'Model':LinearSVC(), 'Training Score':0, 'Validation Score':0},
    {'Model Name':'Logistic Regression', 'Model':LogisticRegression(solver='lbfgs'), 'Training Score':0, 'Validation Score':0}
]

def getCategoryCol(df):
    category_cols = []
    for c in list(df):
        if np.dtype(df[c]).name == 'object':
            category_cols.append(c)
    return category_cols        


def preprocess(raw_df, syn_df, colName):
    #drop the rows that have missing value
    raw_df = raw_df.dropna(axis=0,how='any')
    syn_df = syn_df.dropna(axis=0,how='any')
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

def updateToMysql_status(conn,userID,projID, projName, table, step, percentage):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'file_name': table,
            'jobName': "MLutility"
        }

    valueSampleData = {
            'jobName': "MLutility",
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'step': step,
            'percentage':percentage
        }

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                            'T_GANStatus',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug(f"{projName}: Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projName}: insertSampleDataToMysql fail')
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
    if not os.path.isfile(real_path):
        return False
    if not real_path.startswith(base_dir):
        return False
    return True

def validate_column_name(col_name):
    # Allow Chinese characters, English letters, numbers, and underscores
    if not re.match("^[\u4e00-\u9fffA-Za-z0-9_]+$", col_name):
        raise ValueError(f"Invalid column name: {col_name}")
    return col_name
    
def main(userID, projID, projName, fileName, rawDir, synDir, targetCols):
    global  _logger,_vlogger     
    # debug log
    _logger  =_getLogger('error__MLutility')
    # verify log
    _vlogger =_getLogger('verify__MLutility')
    _vlogger.debug('------MLutility Start------')

    #connect MYSQL
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
        check_conn.close()
    except Exception as e:
        _logger.debug('connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return None

    #Initial
    try:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, projName, fileName, 'Initial', 0)
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {str(e)}')
        return None

    #read raw data
    try:    
        raw_df = pd.read_csv(rawDir)
    except Exception as e:
        _logger.debug('Error reading file. {0}'.format(str(e)))

    _vlogger.debug('targetCols : {}'.format(str(targetCols)))
    # _vlogger.debug('rawDir : {}'.format(rawDir))
       
    #initial dict
    result_ = {}
    for colName_ in targetCols:
        result_[validate_column_name(colName_)] = {'fileName':[], 'modelName':[], 'valMean':[]}
    
    n = 0  

    for fileName_ in os.listdir(synDir):
        if fileName_.endswith(".csv"):
            syn_file_path = os.path.join(synDir, fileName_)
            _vlogger.debug("read syn. data from : {}".format(syn_file_path))

            try:
                syn_df = pd.read_csv(syn_file_path)
            except Exception as e:
                _logger.debug('Error reading syn file. {0}'.format(str(e)))  
                return None          

        for colName_ in targetCols:
            raw_X, raw_y, syn_X, syn_y = preprocess(raw_df, syn_df, colName_) 

            if raw_X is None:
                _logger.debug("{} : The number of types is 1".format(colName_))
                continue # continue next targetCols
            else:
                X_train_raw,X_val_raw,Y_train_raw,Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2, random_state=42)
                X_train_syn,X_val_syn,Y_train_syn,Y_val_syn = train_test_split(syn_X, syn_y, test_size=0.2, random_state=42)
            
            randomState = 1
            while( len(np.unique(Y_train_syn)) == 1 ):
                X_train_raw,X_val_raw,Y_train_raw,Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2, random_state=randomState)
                X_train_syn,X_val_syn,Y_train_syn,Y_val_syn = train_test_split(syn_X, syn_y, test_size=0.2, random_state=randomState)
                randomState += 1

            try:
                #syn/raw
                locals()['models_%d' %n] = ML_method(X_train_syn, X_val_raw, Y_train_syn, Y_val_raw)
            except Exception as err:
                _logger.debug("ML_method error! - %s:%s" %(type(err).__name__, err))
                #continue # continue next targetCols
            
            validationMean = locals()['models_%d' %n]['Validation Score'].mean() 
            result_[colName_]['fileName'].append(fileName_)
            result_[colName_]['modelName'].append('models_%d' %n)
            result_[colName_]['valMean'].append(validationMean)
            #_vlogger.debug(result_)
            n = n+1

    try:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, projName, fileName, 'Find best syn. Data', 40)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    _vlogger.debug(result_)

    c = 0
    p = 60/len(targetCols)
    for colName_ in targetCols:
        _vlogger.debug('-----------------------------')
        _vlogger.debug('target - ' + colName_)
        max_meanValAcc_indx = result_[colName_]['valMean'].index(max(result_[colName_]['valMean']))
        _vlogger.debug('best syn. data - ' + result_[colName_]['fileName'][max_meanValAcc_indx]) 
        _vlogger.debug('model - syn / raw')
        ModelResult = locals()[result_[colName_]['modelName'][max_meanValAcc_indx]].set_index('Model Name')
        _vlogger.debug(ModelResult)    
        _vlogger.debug('MLresult - '+str(ModelResult.to_dict('index')))
        
        #read best performance syn. data
        syn_file_path = os.path.join(synDir, result_[colName_]['fileName'][max_meanValAcc_indx])
        try:
            syn_df = pd.read_csv(syn_file_path)
        except Exception as e:
            _logger.debug('Error reading best syn file. {0}'.format(str(e)))
            continue

        raw_X, raw_y, syn_X, syn_y = preprocess(raw_df, syn_df, colName_)

        if raw_X is None:
            _logger.debug("{} : The number of types is 1".format(colName_))
            continue # continue next targetCols

        try:
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn, userID, projID, projName, fileName, 'training on target col : {}'.format(colName_), 40+p*c)
            check_conn.close()
        except Exception as e:
            _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
            return None
        
        #raw/raw
        _vlogger.debug('model - raw / raw')
        X_train_raw,X_val_raw,Y_train_raw,Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2, random_state=42)

        while( len(np.unique(Y_train_raw)) == 1 ):
            X_train_raw,X_val_raw,Y_train_raw,Y_val_raw = train_test_split(raw_X, raw_y, test_size=0.2)

        maxMeanModel_raw = ML_method(X_train_raw, X_val_raw, Y_train_raw, Y_val_raw).set_index('Model Name')
        _vlogger.debug(maxMeanModel_raw)
        _vlogger.debug('MLresult - '+str(maxMeanModel_raw.to_dict('index')))
    
        #syn/syn
        _vlogger.debug('model - syn / syn')
        X_train_syn,X_val_syn,Y_train_syn,Y_val_syn = train_test_split(syn_X, syn_y, test_size=0.2, random_state=42)

        while( len(np.unique(Y_train_syn)) == 1 ):
            X_train_syn,X_val_syn,Y_train_syn,Y_val_syn = train_test_split(syn_X, syn_y, test_size=0.2)

        maxMeanModel_syn = ML_method(X_train_syn, X_val_syn, Y_train_syn, Y_val_syn).set_index('Model Name')
        _vlogger.debug(maxMeanModel_syn)
        _vlogger.debug('MLresult - '+str(maxMeanModel_syn.to_dict('index')))
        
        c = c+1
        try:
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn, userID, projID, projName, fileName, 'training on target col : {}'.format(colName_), 40+p*c)
            check_conn.close()
        except Exception as e:
            _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
            return None

    try:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, projName, fileName, 'finish', 100)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
        
    _vlogger.debug('------MLutility Finished------')
           
if __name__ == '__main__':
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

    fileName = sys.argv[4]
    if not re.match("^[a-zA-Z0-9_ .]+$", fileName)or fileName.isdigit()or '..' in fileName or '/' in fileName:
        print("Invalid fileName format")
        raise ValueError(f"{projName}__errTable:Invalid fileName format")

    rawDir = sys.argv[5] #raw datacsv path
    base_dir = '/app/app/devp'
    if not is_valid_path(rawDir,base_dir):
        print("Invalid or non-existent file path")    
        raise ValueError ("Invalid or non-existent file path")    

    # Validate the directory path
    synDir = validate_directory(sys.argv[6])#DeID data folder path 
    synDir = shlex.quote(synDir)
    if not synDir.startswith(base_dir):
        raise ValueError("Syn directory is outside the allowed base directory.")
    
    try:
        targetCols = ast.literal_eval(sys.argv[7]) #list of target columns ex.['class']
        if not isinstance(targetCols, list):
            raise ValueError("Input should be a list.")
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid input: {e}")

    main(userID, projID, projName, fileName, rawDir, synDir, targetCols)
    
    
