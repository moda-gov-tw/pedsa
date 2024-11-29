# open file
import os

# data analysis and wrangling
import pandas as pd
import numpy as np
import ast
import sys
import math
import re
from collections import Counter

from MyLib.connect_sql import ConnectSQL
from logging_tester import _getLogger

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import logging
import sys
 
class UTF8Formatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        return msg.encode('utf-8').decode('utf-8')
 
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(UTF8Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
 
logging.basicConfig(level=logging.INFO, handlers=[handler])
 

import base64,json
import shlex

def updateToMysql_status(conn,userID,projID, projName, table, step, percentage):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'file_name': table,
            'jobName': "utility"
        }

    valueSampleData = {
            'jobName': "utility",
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


def updateToMysql_T_ProjectStatus(conn,projID,project_status,statusname):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID
        }

    valueSampleData = {
            'project_id': projID,
            'project_status': project_status,
            'statusname': statusname
        }

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                            'T_ProjectStatus',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug(f"{projID}: Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projID}: insertSampleDataToMysql fail')
        return None


def updateToMysql_T_utilityResult(conn,projID,target,syn_data,statistic,MLresult):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID
        }

    valueSampleData = {
            'project_id': projID,
            'target_col':target,
            'select_csv':syn_data,
            'model':statistic,
            'MLresult': MLresult
        }

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                            'T_utilityResult',
                                            condisionSampleData,
                                            valueSampleData)
    if resultSampleData['result'] == 1:
        _vlogger.debug(f"{projID}: Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projID}: insertSampleDataToMysql fail')
        return None





def get_obcol(conn,projID):
    sqlStr = f"SELECT ob_col FROM SynService.T_ProjectColumnType WHERE project_id = '{projID}'"

    resultSampleData = conn.doSqlCommand(sqlStr)
    if resultSampleData['result'] == 1:
        return resultSampleData['fetchall'][0]['ob_col'].split(',')
    else:
        _logger.debug(f'{projID}: fetch DataToMysql fail')
        return None

def statisticResult(df, colList, obcols):
    result = {}
    for col in colList:
        result[col]={}
        if np.dtype(df[col]).name == 'object':
            result[col]['type'] = 'category'
            result[col]['value'] = getTop5category(df, col) #get top 5 category{}
        elif col in obcols:
            result[col]['type'] = 'category'
            result[col]['value'] = getTop5category(df, col) #get top 5 category{}
        else:
            result[col]['type'] = 'numerical'
            result[col]['value'] = getNumStatistic(df, col) #get {min,max,mean,median,std}
    return result

def getTop5category(df, col):
    top5category = df.groupby(col)[col].count().sort_values(ascending=False)[:5]
    top5category_list = top5category.tolist()
    # top5category_list = df.groupby(col)[col].count().sort_values(ascending=False).tolist()
    # top5category_dict = top5category.to_dict()
    top5category_dict = top5category.to_dict()
    def encode_utf8(data):
        if isinstance(data, dict):
            return {k: encode_utf8(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [encode_utf8(item) for item in data]
        elif isinstance(data, str):
            return data.encode('utf-8').decode('utf-8')
        else:
            return data
 
    top5category_dict = encode_utf8(top5category_dict)
    top5category_dict = {str(k): v for k, v in top5category_dict.items()}



    #top5category_dict = {str(k): v for k, v in top5category.to_dict().items()}
    if len(top5category_list)  <= 5:
        #print('============1',top5category_dict)
        return top5category_dict
    else:
        top5category_dict['others'] = len(df)-top5category.sum()
        #print('============2',top5category_dict)
        return top5category_dict

def getNumStatistic(df, col):
    statistics_dict = {}
    statistics_dict['min'] = df[col].min().round(3)
    statistics_dict['max'] = df[col].max().round(3)
    statistics_dict['mean'] = df[col].mean().round(3)
    statistics_dict['median'] = df[col].median().round(3)
    statistics_dict['std'] = df[col].std().round(3)
    return statistics_dict

def getAbsDiff(raw_dict, syn_dict, obcol_list):
    diffIndex = 0
    keys = raw_dict.keys()
    # print('***********keys: ',keys)
    select_col_ls = []
    ob_count = 0
    for key in list(keys):
        if key in obcol_list:
            select_col_ls.append(key)
            ob_count = ob_count + 1
    if len(select_col_ls) > int(len(list(keys))/2): #類別多
        # print('**********************categorical: ',select_col_ls)
        for key in select_col_ls:
            X,Y = Counter(raw_dict[key]['value']),Counter(syn_dict[key]['value'])
            Z = dict(X-Y)
            abs_dict = {key: abs(value) for key, value in Z.items()}
            # print('***********abs_dict: ',abs_dict)
            diffIndex = diffIndex+sum(abs_dict.values())
            return diffIndex
    else:   #數值多
        # print('**********************numerical: ',list(set(keys) - set(select_col_ls)))
        for key in list(set(keys) - set(select_col_ls)):
            # print('@@@@@@@@@@key: ',key)
            X,Y = Counter(raw_dict[key]['value']),Counter(syn_dict[key]['value'])
            # print('@@@@@@@@@@X: ',X)
            # print('@@@@@@@@@@Y: ',Y)
            Z = Counter()
            for key, value in X.items():
                # 如If the key is 'mean' or 'std', subtract the corresponding value from Y from X
                if key in ["mean", "std"]:
                    Z[key] = value - Y[key]
            abs_dict = {key: abs(value) for key, value in Z.items()}
            # print('***********abs_dict: ',abs_dict)
            diffIndex = diffIndex+sum(abs_dict.values())
        return diffIndex

def validate_directory(directory_path):
    real_path = os.path.realpath(directory_path)
    if not os.path.isdir(real_path):
        raise ValueError("Invalid directory")
    return real_path

def is_valid_path(path, base_dir):
    real_path = os.path.realpath(path)
    if not os.path.isabs(path):
        return False
    # if not os.path.isfile(real_path):
    #     return False
    if not real_path.startswith(base_dir):
        return False
    return True

def main(userID, projID, projName, fileName, rawDir, synDir, targetCols):
    global  _logger,_vlogger     
    # debug log
    _logger  =_getLogger('error__MLutility')
    # verify log
    _vlogger =_getLogger('verify__MLutility')
    _vlogger.debug('------{}__Statistic Utility Start------'.format(projName))
    
    
    #connect MYSQL
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("{}__Connect SQL".format(projName))
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
    

    #get ob_col
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        obcol = get_obcol(check_conn,projID) #string to list
        _vlogger.debug('------{}__Statistic Utility obcol: {}------'.format(projName,obcol))
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None

    #data list
    rawDataName = rawDir.split('\\')[-1]
   
    synDataList = [fileName_ for fileName_ in os.listdir(validate_directory(synDir)) if fileName_.endswith(".csv")]
    _vlogger.debug('------__syndatalist: {}------'.format(synDataList))
    _vlogger.debug('------__rawDir: {}------'.format(rawDir))

    result_ = {}
    diff_ = {}
    #raw data statistic
    try:
        df = pd.read_csv(rawDir,encoding='utf-8') # dtype={col: 'object' for col in obcol}, encoding='utf8')
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    _vlogger.debug('------__utf8------')

    #_vlogger.debug("df.columns.to_list, ",df.dtypes)
    _vlogger.debug("##############RAWDIR, ",df.head(2).to_dict(orient='records'))
    _vlogger.debug('------__targetCols: {}------'.format(targetCols))
    _vlogger.debug('------__obcol: {}------'.format(obcol))

    try:
        result_[rawDataName] = statisticResult(df, targetCols,obcol)
    except Exception as e:
        _logger.debug('Error statisticResult(raw). {0}'.format(str(e)))
    _vlogger.debug('------__utf8------')
    
    #syn data statistic
    for synDataName in synDataList:
        # print('###############################', synDir+synDataName )
        syn_file_path = os.path.join(synDir, synDataName)
        try:
            df = pd.read_csv(syn_file_path,encoding='utf-8')
        except Exception as e:
            _logger.debug('Error reading file(syn). {0}'.format(str(e)))
        #print("##############SYNDIR, ", df.head(2).to_dict(orient='records'))
        try:
            result_[synDataName] = statisticResult(df, targetCols,obcol)
        except Exception as e:
            _logger.debug('Error statisticResult(syn). {0}'.format(str(e)))

        diff_[synDataName] = getAbsDiff(result_[rawDataName], result_[synDataName],obcol)

    #get minium statistic result difference between raw data and syn data  
    bestSynData = min(diff_, key=diff_.get)

    final = {'raw data' : result_[rawDataName], 'syn. data':result_[bestSynData]}

    #_vlogger.debug('{}__result_[rawDataName] - '.format(result_[rawDataName]))
    #_vlogger.debug('{}__result_[bestSynData]'.format(result_[bestSynData]))

    target = '*'.join(targetCols)
    _vlogger.debug('{}__target - '.format(target))
    syn_data = bestSynData
    _vlogger.debug('{}__best syn. data - '.format(projName) + bestSynData)
    _vlogger.debug('{}__model - statistic'.format(projName))
 

##############################################
# PROBLEM ####################################
    # json_data_str = '{"raw data": {"Sex_sys_TP_3000": {"type": "category", "value": {"\\u7537": 1514, "\\u5973": 1486}}, "MaritalStatus_sys_TP_3000": {"type": "category", "value": {"\\u5df2\\u5a5a": 1005, "\\u672a\\u63d0\\u4f9b": 998, "\\u672a\\u5a5a": 997}}, "NoOfChildren_sys_TP_3000": {"type": "numerical", "value": {"min": 0, "max": 30, "mean": 15.122, "median": 15.0, "std": 8.963}}}, "syn. data": {"Sex_sys_TP_3000": {"type": "category", "value": {"\\u7537": 1514, "\\u5973": 1486}}, "MaritalStatus_sys_TP_3000": {"type": "category", "value": {"\\u5df2\\u5a5a": 1005, "\\u672a\\u63d0\\u4f9b": 998, "\\u672a\\u5a5a": 997}}, "NoOfChildren_sys_TP_3000": {"type": "numerical", "value": {"min": 2.0, "max": 27.0, "mean": 14.623, "median": 16.0, "std": 7.102}}}}'
    # final = json.dumps(final)
    final = str(final).encode('utf-8')
    # cleaned_str = data_str.replace("\'", "").replace("\\", "")
    # json_data_str = '"'+ final + '"'
    _vlogger.debug('{}: final_str - '.format(final))
    _vlogger.debug('{}: final_str_type - '.format(type(final)))
    # _vlogger.debug('{}: json_data_str - '.format(json_data_str))

#################################################
    # 将 JSON 数据字符串解析为 Python 对象
    # json_obj = json.loads(final)
    # _vlogger.debug('{}: json_obj_type - '.format(type(json_obj)))
    # json_str = json.dumps(json_obj, ensure_ascii=False)
    # _vlogger.debug('{}: json_str_type - '.format(type(json_str)))

    # json_bytes = json_str.encode('utf-8')
    # _vlogger.debug('{}: json_bytes_type - '.format(type(json_bytes)))

    # 使用 base64 对 UTF-8 字节流进行编码
    encoded_data = base64.b64encode(final).decode('utf-8')
    _vlogger.debug('{}__encoded_data - '.format(encoded_data))

    #finalbase64 = base64.b64encode(final.encode('utf-8')).decode('utf-8')

    # _vlogger.debug('{}__result - '.format(projName) + str(finalbase64))

    #finish
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_T_ProjectStatus(check_conn,projID,8,"資料相似度報表")
        updateToMysql_status(check_conn, userID, projID, projName, fileName, 'finish', 100)
        updateToMysql_T_utilityResult(check_conn,projID,target,syn_data,"statistic",encoded_data)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    _vlogger.debug('------{}__Statistic Utility Finished------'.format(projName))
           
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

    rawDir = sys.argv[5] #raw data ex.D:/107/adult/train.csv
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
        print(f"Invalid input: {e}")
        raise ValueError(f"Invalid input: {e}")

    main(userID, projID, projName, fileName, rawDir, synDir, targetCols)
