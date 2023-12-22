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

from MyLib.connect_sql import ConnectSQL

from logging_tester import _getLogger

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
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        _logger.debug('insertSampleDataToMysql fail: ' + msg)
        return None  
    
def main():
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
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, fileName, 'Initial', 0)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None

    #read raw data    
    raw_df = pd.read_csv(rawDir)
    _vlogger.debug('targetCols : {}'.format(str(targetCols)))
    _vlogger.debug('rawDir : {}'.format(rawDir))
       
    #initial dict
    result_ = {}
    for colName_ in targetCols:
        result_[colName_] = {'fileName':[], 'modelName':[], 'valMean':[]}
    
    n = 0  
    for fileName_ in os.listdir(synDir):
        if fileName_.endswith(".csv"):
            _vlogger.debug("read syn. data from : {}".format(synDir+fileName_))
            syn_df = pd.read_csv(synDir+fileName_)

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
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
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
        syn_df = pd.read_csv(synDir+result_[colName_]['fileName'][max_meanValAcc_indx])
        
        raw_X, raw_y, syn_X, syn_y = preprocess(raw_df, syn_df, colName_)

        if raw_X is None:
            _logger.debug("{} : The number of types is 1".format(colName_))
            continue # continue next targetCols

        try:
            check_conn = ConnectSQL()
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
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
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
            updateToMysql_status(check_conn, userID, projID, projName, fileName, 'training on target col : {}'.format(colName_), 40+p*c)
            check_conn.close()
        except Exception as e:
            _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
            return None

    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
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
    fileName = sys.argv[4]
    rawDir = sys.argv[5] #raw data ex.D:/107/adult/train.csv
    synDir = sys.argv[6] #DeID data folder ex.D:/patent/adultDiffEmbeddingTarget/class/synthetic/
    targetCols = ast.literal_eval(sys.argv[7]) #list of target columns ex.['class']

    main()
    
    
