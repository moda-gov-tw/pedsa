import random
import time
import os 
import shutil
#from .config_sql.connect_sql import ConnectSQL
from logging_tester import _getLogger
import pymysql
from configparser import ConfigParser
import os.path

from MyLib.connect_sql import ConnectSQL 
from mysql_create_GAN import createTbl_T_GANStatus

import numpy as np
import subprocess
def install_package(package_name):
    subprocess.check_call(['pip', 'install', package_name])

# 使用方式
package_pgmpy = 'pgmpy'  # 更換成你想要安裝的 package 名稱
install_package(package_pgmpy)
package_scipy = 'scipy'  # 更換成你想要安裝的 package 名稱
install_package(package_scipy)
package_pandas = 'pandas'  # 更換成你想要安裝的 package 名稱
install_package(package_pandas)


from scipy.stats import chi2_contingency
import pandas as pd


def updateToMysql_status(conn,userID,projID, projName, table, step,percentage):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'file_name': table,
            'jobName': "GAN"
        }

    valueSampleData = {
            'jobName': "GAN",
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'step': step,
            'percentage':percentage,
            'isRead':0
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
        _logger.debug(f'{projName}__insertSampleDataToMysql fail: ' + msg)
        return None
#update mysql with sampling 5 data from the df after dropped some columns
def updateToMysql_sample(conn,userID,projID, projName, table, select_data):

    # insert to sample data
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'file_name': table
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'select_data': select_data
        }

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
                                                 'T_ProjectSample5Data',
                                                 condisionSampleData,
                                                 valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        _logger.debug(f'{projName}__insertSampleDataToMysql fail: ' + msg)
        return None




def updateToMysql_DP_corr(conn,userID,projID, projName,corr_col): #, select_data):

    # insert to sample data
    condisionSampleData = {
        'project_id': projID,
        'pro_name': projName
    }

    valueSampleData = {
        'project_id': projID,
        'user_id':userID,
        'pro_name': projName,
        'corr_col': corr_col
    }
    # 系統計算相關性欄位: corr_col
    # 自訂相關性欄位: choose_corr_col
    # epsilon數值: epsilon
    resultSampleData = conn.updateValueMysql('DpService',#'DeIdService',
                                             'T_ProjectColumnType',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        _logger.debug(f'{projName}__insertSampleDataToMysql fail: ' + msg)
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

    resultSampleData = conn.updateValueMysql('DpService',#'DeIdService',
                                             'T_ProjectStatus',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        # _logger.debug(f'{projName}__insertSampleDataToMysql fail: ' + msg)
        return None







# 定義計算 Cramér's V 的函數
def cramers_v(x, y):
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    with np.errstate(divide='ignore', invalid='ignore'):
        correlation = np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))
    return correlation if not np.isinf(correlation) else np.nan


def main(args): 
    global  _logger,_vlogger, check_conn    
    # debug log
    _logger  =_getLogger('error__genData')
    # verify log
    _vlogger =_getLogger('verify__genData')

    pppid = os.getpid()
    #varible
    userID = args['userID']
    projID = args['projID']
    projName = args['projName']
    fileName = args['fileName']
    col_name = args['colName'] #ob column for GAN
    select_colNames = args['select_colNames']
    transfer = args['transfer']
    # conti_col = args['conti_colname'] 
    generate = args['generation']
    sample =args['sample']
    keyName =args['keyName'] #ID

    project_path = "app/devp/folderForSynthetic/"+projName+"/"
    file_path = project_path+"inputRawdata/df_drop.csv"#+fileName
    previewFile_path = project_path+"inputRawdata/df_preview.csv"

    _vlogger.debug(f'projID:{projID}')
    _vlogger.debug(f'select_colNames:{select_colNames}')
    df = pd.read_csv(fileName)
    df = df[select_colNames]
    _vlogger.debug(f'df:{df}')
    column_names = df.columns
    _vlogger.debug(f'df:{column_names}')



    # 先預填 corr_col 避免錯誤
    column_1 = select_colNames[0]
    column_2 = select_colNames[1]
    _vlogger.debug(f'corrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorr')
    corr_col = column_1 + "^" + column_2
    _vlogger.debug(f'corr_col:{corr_col}')

    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        check_conn = ConnectSQL()
        updateToMysql_DP_corr(check_conn,userID, projID, projName,corr_col)
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return
    # # 將類別型欄位轉換為數值型
    # df_encoded = df.apply(lambda x: pd.factorize(x)[0])
    # unique_counts = df_encoded.nunique()
    # _vlogger.debug("unique_counts")
    # _vlogger.debug(unique_counts)
    #
    # columns_to_drop = unique_counts[unique_counts >= 10].index
    # df_encoded = df_encoded.drop(columns=columns_to_drop)
    #
    # _vlogger.debug("df_encoded")
    # _vlogger.debug(df_encoded)
    # if df.empty:
    #     _vlogger.debug("df.empty corr_col is first and second col ")
    # else:
    #     # 計算欄位之間的相關係數
    #     corr_matrix = pd.DataFrame(index=df_encoded.columns, columns=df_encoded.columns)
    #     for i in df_encoded.columns:
    #         for j in df_encoded.columns:
    #             corr_matrix.loc[i, j] = cramers_v(df_encoded[i], df_encoded[j])
    #
    #     corr_matrix_cleaned = corr_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')
    #
    #     # 將對角線上的值設為 NaN，以便忽略自身相關性
    #     np.fill_diagonal(corr_matrix_cleaned.values, np.nan)
    #
    #     # 找出相關性矩陣中的最大值
    #     max_corr_value = corr_matrix_cleaned.stack().max()
    #     # 找出相關性最高的兩個欄位
    #     max_corr_indices = np.where(corr_matrix_cleaned.values == max_corr_value)
    #     max_corr_indices = (max_corr_indices[0][0], max_corr_indices[1][0])
    #     column_1, column_2 = corr_matrix_cleaned.index[max_corr_indices[0]], corr_matrix_cleaned.columns[max_corr_indices[1]]
    #     _vlogger.debug(f'corr:{column_1} and {column_2}')
    #     _vlogger.debug(f'corrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorr')
    #     corr_col = column_1 + "^" + column_2
    #     _vlogger.debug(f'corr_col:{corr_col}')
    #
    #     try:
    #         #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
    #         check_conn = ConnectSQL()
    #         _vlogger.debug("Connect SQL")
    #         updateToMysql_DP_corr(check_conn,userID, projID, projName,corr_col)
    #         check_conn.close()
    #     except Exception as e:
    #         _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
    #         return








    # try:
    #     shutil.copy( previewFile_path, file_path)
    # except Exception as e:
    #     #rint('copy file fail: - %s:%s' %(type(e).__name__, e))
    #     _logger.debug(f'{projName}__INsert fail: - %s:%s' %(type(e).__name__, e))
    #     return None
    #
    #
    # directory = project_path+'synProcess/'
    # directory_pkl = directory+"pkl/"
    #
    # if not os.path.exists(directory_pkl):
    #     os.mkdir(directory_pkl)

    # try:
    #     check_conn = ConnectSQL()
    #     _vlogger.debug("Connect SQL")
    # except Exception as e:
    #     _logger.debug(f'{projName}__connectToMysql fail: - %s:%s' %(type(e).__name__, e))
    #     return None

    # try:
    #     result = createTbl_T_GANStatus(check_conn)
    #     if result['result'] == 1:
    #         _vlogger.debug(result['msg'])
    #     else:
    #         print('mysql fail:' + result['msg'])
    #         #return False
    # except:
    #     pass

    # try:
    #     #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
    #     updateToMysql_status(check_conn,userID, projID, projName, fileName, 'Initial', 0)
    #     _vlogger.debug(f'{projName}__syn_progess 0% [Initial].')
    #     _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
    #     check_conn.close()
    # except Exception as e:
    #     _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
    #     return
    #
    # initial_time=time.time()
    #
    # try: #check col type
    #     _vlogger.debug('--------------checktype----------------------------')
    #     col_name, conti_col, unique_att_num, tar_col, df = check_type(select_colNames,col_name,file_path,keyName)
    #     _vlogger.debug('--------------checktype----------------------------')
    #     _vlogger.debug(f'{projName}__col_name: '+','.join(col_name))
    #     _vlogger.debug(f'{projName}__conti_col: '+','.join(conti_col))
    #     _vlogger.debug(f'{projName}__unique_att_num: {unique_att_num}')
    #     _vlogger.debug(f'{projName}__tar_col: '+str(tar_col))
    # except Exception as e:
    #     _logger.debug(f'{projName}__errTable: check_type fail. {0}'.format(str(e)))
    #     return
    #
    # #save df_select.head() to sql
    # select_data = df.head(5).to_json(orient='records')
    # try:
    #     check_conn = ConnectSQL()
    #     updateToMysql_sample(check_conn,userID,projID, projName, fileName, select_data)
    #     check_conn.close()
    #     _vlogger.debug(f'{projName}__update sample5data succeed.')
    # except Exception as e:
    #     _logger.debug(f'{projName}__errTable: update sample5data fail. {0}'.format(str(e)))
    #     return

    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_T_ProjectStatus(check_conn,projID,5,"感興趣欄位設定")
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    _vlogger.debug("citc__DP__Mission Complete")
    print("citc__DP__Mission Complete")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-projName", "--projName", help='projName for make a folder')
    parser.add_argument("-fileName", "--fileName", help='The path of dataset')
    parser.add_argument("-colName", "--colName",nargs='+', help='Categorical attribute name')
    parser.add_argument("-select_colNames", "--select_colNames",nargs='+', help='Selected attribute name')
    parser.add_argument("-keyName", "--keyName",nargs='+', help='Key attribute name')
#     parser.add_argument("-tar_col", "--tar_colname", help='Target attribute name')
    parser.add_argument("-transfer", "--transfer", default="True", help='Transfer target attribute to numerical')
    # parser.add_argument("-conti", "--conti_colname", default='all', nargs='+', help='Conti. attribute name')
    parser.add_argument("-gen", "--generation", default="True", help='Synthetic dataset generation')
    parser.add_argument("-sample", "--sample", default="True", help='Sample from GAN')
    parser.add_argument("-projID", "--projID", help='projID for mysql')
    parser.add_argument("-userID", "--userID", help='update user info to mysql')
    args = vars(parser.parse_args())
    print(args)
    print ("in __main__")
    main(args)
    
    ####command:  python train_feature.py -d adult/adult.csv -col workclass education education_num marital_status occupation relationship race sex native_country class -gen True
    ####command(including conti): python train_feature.py -d adult/adult.csv -col workclass education education_num marital_status occupation relationship race sex native_country class -conti age capital_gain capital_loss hours_per_week fnlwgt -tar_col class -gen True
    
    ####command(wrong type):python train_feature.py -d adult/adult.csv -col education_num occupation relationship race sex native_country class -conti age capital_gain capital_loss hours_per_week fnlwgt workclass education marital_status  -tar_col class -gen True

##1224:update
##python train_feature.py -projName ProAdult -fileName data/adult.csv -colName education education_num marital_status occupation relationship race sex native_country class -keyName workclass

