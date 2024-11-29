import sys
# 添加新目录到 sys.path
sys.path.append('/usr/local/lib/python3.10/dist-packages')
import subprocess
def install_package(package_name):
    subprocess.check_call(['pip', 'install', package_name])
from MyLib.loginInfo import getConfig

#from _a_check import check_type, hit_rate
####20180920
# from adult.eva_acc import acc
# from taxi.eva_acc import acc
#from eva_acc import acc
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
from scipy.stats import chi2_contingency, laplace
import pandas as pd
# subprocess.check_call(['pip', 'install', '--upgrade',  'pgmpy' ])
from pgmpy.models import BayesianModel,BayesianNetwork
from pgmpy.inference import VariableElimination
from pgmpy.estimators import MaximumLikelihoodEstimator
from scipy.stats import laplace

import configparser
import json 
os.system('apt install sshpass')
import shlex

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




def updateToMysql_DP_mean_std(conn,projID, projName,mean_std_list): #, select_data):

    # insert to sample data
    condisionSampleData = {
        'project_id': projID,
        'project_name': projName
    }

    valueSampleData = {
        'project_id': projID,
        'project_name': projName,
        'dp_report_data': mean_std_list
    }

    resultSampleData = conn.updateValueMysql('DpService',#'DeIdService',
                                             'T_Project',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        return None
    else:
        msg = resultSampleData['msg']
        _logger.debug(f'{projName}__insertSampleDataToMysql fail: ' + msg)
        return None

def updateToMysql_DP_ob_col(conn,projID, projName,discrete_columns_str): #, select_data):

    # insert to sample data
    condisionSampleData = {
        'project_id': projID,
        'pro_name': projName
    }

    valueSampleData = {
        'project_id': projID,
        'pro_name': projName,
        'ob_col': discrete_columns_str
    }

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



def add_noise(value, epsilon):
    noise = np.random.laplace(scale=1/epsilon)
    return value + noise


# 對於只有兩個類別的添加 noise 判斷 / 進來的 p 會是一個經由 epsilon 計算過的小數點 / 如果隨機產生的 s 大於 p / 會 return跟原本不同的值
def rr(v, p):
    s = np.random.uniform(0, 1)
    if s > p:
        if v == 0:
            return 1
        else:
            return 0
    else:
        return v

# 多個類別型的添加 noise 判斷 /  跟單類別差不多 / return 第一行 是原本給的 ipynb的判斷 /
# 第二行是我寫的 會隨機從配對到的結果選一個 (舉例) column A 的值是 1 而利用這個條件搜尋 column B 可能會有 y or z 那就會從 y or z 中隨機選一個加上原本的value

def grr(v, pc):
    s = np.random.uniform(0, 1)
    if s > pc[0]:
        return ((v + np.random.randint(1, pc[1]))%pc[1])   # 對應到 208 行
        # return ((v + np.random.choice(pc[1]))%(max(pc[1])+1)) # 對應到 210 行
    else:
        return v

# 連續型數據的添加 noise 辦法
def lap(v, p):
    # _vlogger.debug(f'lap:{v+np.random.laplace(0, p)}')
    return (v+np.random.laplace(0, p))



# 計算上面所提到的 p 用的函數 分別對應雙類別以及多類別

def compute_rr_sig(eps):
    return (np.exp(eps)/(np.exp(eps)+1))

def compute_grr_sig(eps, c):
    return (np.exp(eps)/(np.exp(eps)+c-1))

def post_p(v, pc):
    s = round(v)
    if s < pc[0]:
        return pc[0]
    elif s > pc[1]:
        return pc[1]
    else:
        return s

def compute_lap(eps, delta):
    return (delta/eps)


def main(args): 
    global  _logger,_vlogger, check_conn    
    # debug log
    _logger  =_getLogger('error__DPData')
    # verify log
    _vlogger =_getLogger('verify__DPData')

    pppid = os.getpid()
    #varible
    userID = args['userID']
    projID = args['projID']
    projName = args['projName']
    fileName = args['fileName']
    col_name = args['colName'] #ob column for GAN
    select_colNames = args['select_colNames']
    select_colValues = args['select_colValues']
    corr_colValues = args['corr_colValues']
    choose_corr_colValues = args['choose_corr_colValues']
    transfer = args['transfer']
    # conti_col = args['conti_colname'] 
    generate = args['generation']
    sample =args['sample']
    epsilon_str =args['epsilon']
    epsilon = float(epsilon_str) #0.1#


    _vlogger.debug(f'userID:{userID}')
    _vlogger.debug(f'projName:{projName}')
    _vlogger.debug(f'fileName:{fileName}')
    _vlogger.debug(f'epsilon:{epsilon}')
    _vlogger.debug(f'projID:{projID}')
    _vlogger.debug(f'select_colNames:{select_colNames}')
    _vlogger.debug(f'select_colValues:{select_colValues}')
    _vlogger.debug(f'corr_colValues:{corr_colValues}')
    _vlogger.debug(f'choose_corr_colValues:{choose_corr_colValues}')

    # 创建一个空字典用于存储分组后的列名
    grouped_columns = {'D': [], 'C': []}

    # 根据每个值（'D' 或 'C'）将列名分组
    for value, name in zip(select_colValues, select_colNames):
        grouped_columns[value].append(name)

    # 打印分组后的结果
    for key, value in grouped_columns.items():
        print(f"Values '{key}': {value}")

    discrete_columns = grouped_columns["C"]
    continue_columns = grouped_columns["D"]
    _vlogger.debug(f'discrete_columns:{discrete_columns}')
    _vlogger.debug(f'continue_columns:{continue_columns}')
    _vlogger.debug(f'epsilon:{epsilon}')
    
    for item in discrete_columns:
        _vlogger.debug(f'item:{item}')
        _vlogger.debug(f'find:{corr_colValues[0].find(str(item))}')

        if corr_colValues[0].find(str(item)) ==-1:
            try:
                _vlogger.debug(f'Corr_colValuse +  discrete columns before :{corr_colValues}')
                choose_list = discrete_columns.copy()
                choose_list.remove(item)
                # to_be_append =  item+'^' +random.choice(choose_list+continue_columns) 
                to_be_append =  item+'^' +random.choice(choose_list)
                corr_colValues.append(to_be_append)
                _vlogger.debug(f'Corr_colValuse +  discrete columns after :{corr_colValues}')
            except Exception as e:
                _vlogger.debug(f'errer append :{e}')
    
    _vlogger.debug(f'Corr_colValuse +  discrete columns:{corr_colValues}')

    corr_list_corr_colValues = [tuple(item.split('^')) for item in corr_colValues]
    corr_list_corr_choose = [tuple(item.split('^')) for item in choose_corr_colValues]
    # relate_list = corr_list_corr_colValues + corr_list_corr_choose





    if len(discrete_columns) % 2 == 1:  # 如果列表长度为奇数
        result = [(discrete_columns[i], discrete_columns[i+1]) for i in range(len(discrete_columns) - 1)]
    elif len(discrete_columns) % 2 == 0:  # 如果列表长度为偶数
        result = [(discrete_columns[i], discrete_columns[i+1]) for i in range(0, len(discrete_columns), 2)]
    _vlogger.debug(result)    


    relate_list = corr_list_corr_colValues + result

    # 将每个元组内部的元素进行排序，以便识别重复项
    a_sorted = [tuple(sorted(pair)) for pair in relate_list]

    # 使用集合来去除重复项，然后转回列表
    relate_list = list(set(a_sorted))

    _vlogger.debug(f'relate_list:{relate_list}')


    df = pd.read_csv(fileName)
    # df = df[select_colNames]
    df = df[select_colNames].dropna(axis = 0)
    for column in discrete_columns:
        df[column] = df[column].astype(str)
        df[column] = df[column].apply(lambda x: x.split('.')[0])

    _vlogger.debug(f'df:{df}')

    # 存到原始資料目錄  "/app/app/devp/folderForSynthetic/project_name/inputRawdata/df_drop.csv
    # synDataDir = os.path.join('/app', 'app', 'devp', 'folderForSynthetic', projName, 'synProcess', 'synthetic/')
    rawDataDir = os.path.join('/app', 'app', 'devp', 'folderForSynthetic', projName, 'inputRawdata', 'df_drop.csv')
    #export_path
    df.to_csv(rawDataDir, index=False, sep=",", header=True, encoding="utf-8")






    # column_names = df.columns
    # _vlogger.debug(f'df:{column_names}')
    # # 將類別型欄位轉換為數值型
    # df_encoded = df.apply(lambda x: pd.factorize(x)[0])
    #
    # # 計算欄位之間的相關係數
    # corr_matrix = pd.DataFrame(index=df_encoded.columns, columns=df_encoded.columns)
    # for i in df_encoded.columns:
    #     for j in df_encoded.columns:
    #         corr_matrix.loc[i, j] = cramers_v(df_encoded[i], df_encoded[j])
    #
    # corr_matrix_cleaned = corr_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')
    #
    # # 將對角線上的值設為 NaN，以便忽略自身相關性
    # np.fill_diagonal(corr_matrix_cleaned.values, np.nan)
    #
    # # 找出相關性矩陣中的最大值
    # max_corr_value = corr_matrix_cleaned.stack().max()
    # # 找出相關性最高的兩個欄位
    # max_corr_indices = np.where(corr_matrix_cleaned.values == max_corr_value)
    # max_corr_indices = (max_corr_indices[0][0], max_corr_indices[1][0])
    # column_1, column_2 = corr_matrix_cleaned.index[max_corr_indices[0]], corr_matrix_cleaned.columns[max_corr_indices[1]]
    # _vlogger.debug(f'corr:{column_1} and {column_2}')
    # _vlogger.debug(f'corrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorrcorr')


    # select_colValues = ['D', 'C', 'D', 'D']
    # select_colNames = ['RIAGENDR_hr1_employe_enc', 'RIDAGEYR_hr1_employe_enc', 'RIDRETH1_hr1_employe_enc', 'DMDCITZN_hr1_employe_enc']


    discrete_columns_str = ','.join(discrete_columns)
    _vlogger.debug("discrete_columns_str")
    _vlogger.debug(discrete_columns_str)
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        check_conn = ConnectSQL()
        updateToMysql_DP_ob_col(check_conn, projID, projName, discrete_columns_str)
        _vlogger.debug("updateToMysql_DP_ob_col")
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return


    sensitivy_data = discrete_columns + continue_columns

    _vlogger.debug(f'sensitivy_data:{sensitivy_data}')
    # Calculate mean for specified columns


    # 繪製敏感性資料原本的分布 (直方圖) / 如果是數據型應該要使用其他圖形會比較適合

    # for column in sensitivy_data:
    #     plt.clf()
    #     plt.hist(df[column], density=False, color = 'lightblue', cumulative = False, label = "Height")
    #     plt.legend()
    #     plt.xlabel('Height(")')
    #     plt.xticks(rotation=45)
    #     plt.tight_layout()
    #     plt.savefig(f'./data/test/graph/{column}_prev_{epsilon}.jpg')


    # 將有關聯性的 column 儲存 (舉例) 從 A.B column 可以搜尋到 C (關聯性大) 那這邊資料就會是 { C: [A,B] } 紀錄那些欄位可以跟 C 有關聯並放進 list 內

    relate_map={}
    try:
        for column in sensitivy_data:
            ll = [pair[0] for pair in relate_list if pair[1] == column]
            relate_map[column] = ll

        _vlogger.debug("relate_map:")
        _vlogger.debug(relate_map)


        # 使用 pgmpy 估計數據之間的依賴關係，構建概率圖模型

        model = BayesianNetwork(relate_list)

        column_type = {}

        # 紀錄 敏感性資料的類別

        for i in range(len(df.columns)):
            if df.columns[i] in discrete_columns:
                column_type[df.columns[i]] = 0
            else:
                column_type[df.columns[i]] = 1
        _vlogger.debug(f"差分隱私column_type  ：{column_type}")
        # 將類別型資料的類別 mapping 到數字

        column_mappings = {}
    except Exception as e:
        _vlogger.debug(f"model error:{str(e)}") 
    try:
        for column in sensitivy_data:
            unique_values = df[column].unique()

            mapping = {val: i for i, val in enumerate(unique_values)}
            column_mappings[column] = mapping

            for k,v in mapping.items():
                df[column] = df[column].replace(k,v)
            _vlogger.debug(f"差分隱私 column_mappings  ：{column_mappings}")

            '''
            for column in sensitivy_data:
                if column_type[column] == 1:
                    value_list = list(df[column].value_counts().keys())
                    minus = max(value_list) - min(value_list)
                    p = minus / epsilon
                    # print(df[column])

                    if df[column].dtypes == 'int' or df.dtypes[column] == 'int64' or df.dtypes[column] == 'int32':
                        # df[column] = df[column].swifter.apply(lap, args=(p,))
                        df[column] = df[column].swifter.apply(lap, args=(epsilon,))
                        df[column] = df[column].swifter.apply(post_p_int, args=([min(value_list), max(value_list)],))
                    else:
                        # df[column] = df[column].swifter.apply(lap, args=(p,))
                        df[column] = df[column].swifter.apply(lap, args=(epsilon,))
                        df[column] = df[column].swifter.apply(post_p, args=([min(value_list), max(value_list)],))
                else:
                    value_list = list(df[column].value_counts().keys())
                    if len(value_list) == 2:
                        p = compute_rr_sig(epsilon)
                        df[column] = df[column].swifter.apply(rr, args=(p,))
                    else:
                        p = compute_grr_sig(epsilon, len(value_list))
                        print(f'p = {p} column = {column}')
                        df[column] = df[column].swifter.apply(grr, args=([p, len(value_list)],))

                    for k,v in column_mappings[column].items():
                        df[column] = df[column].replace(v,k)


            '''
            _vlogger.debug(f"差分隱私 column  ")
            _vlogger.debug(f"差分隱私 column ：{column}")
            _vlogger.debug(f"差分隱私 column len ：{len(column)}")



            if column in discrete_columns:
                # 估計參數
                model.fit(df, estimator=MaximumLikelihoodEstimator)
                _vlogger.debug(f"差分隱私 model {model} ")
                # 使用 VariableElimination 獲取敏感數據的概率分佈
                infer = VariableElimination(model)
                
            else:
                _vlogger.debug(f"數值差分隱私 NO model column name：{column} ")

            for index, row in df.iterrows():
                # _vlogger.debug(f"差分隱私 index  ：{index}")
                # _vlogger.debug(f"差分隱私 row ：{row}")
                # 根據證據獲取敏感數據的概率分佈

                # evidence 就是剛剛所說的可以用來搜尋 column C 的 column [A,B]

                evidence = {}
                for c in relate_map[column]:
                    evidence[c] = row[c]
                # evidence = {'work_year': row['work_year'], 'number': row['number']}




                # 類別型數據的處理
                # _vlogger.debug(f"差分隱私數據型資料的處理的 column_type[column] ：{column}:{column_type[column]}")
                if column_type[column] == 0 :
                    # 這邊是利用 A 跟 B 搜尋 C column 對應到各資料的機率分布
                    query_result = infer.query(variables=[column], evidence=evidence)

                    value_list = list(df[column].value_counts().keys())

                    # _vlogger.debug(f"差分隱私數據型資料的處理的value_list ：{value_list}")

                    if len(value_list) == 2:    # 雙類別
                        p = compute_rr_sig(epsilon)

                        # df[column][index] = df[column][index].swifter.apply(rr, args=(p,))

                        df.at[index,column] = rr(v=df.at[index,column], p=p)
                        # _vlogger.debug(f"差分隱私數據型資料的處理的df.at[index,column] ：{df.at[index,column] }")

                    else:                       # 多類別
                        infer_list = query_result.state_names[column]
                        p = compute_grr_sig(epsilon, len(value_list))

                        # df[column][index] = df[column][index].swifter.apply(grr, args=([p, infer_list],))
                        # df.at[index,column] = grr(v=df.at[index,column], pc=[p,infer_list])  ##原本的 function 對應到第 32 行的 return 值

                        df.at[index,column] = grr(v=df.at[index,column], pc=[p,len(value_list)]) #我寫的 function 對應到第 33 行 return值
                        # _vlogger.debug(f"差分隱私數據型資料的處理的df.at[index,column] ：{df.at[index,column] }")
                else:
                    value_list = list(df[column].value_counts().keys())
                    minus = max(value_list) - min(value_list)
                    p = minus / epsilon

                    # df[column] = df[column].swifter.apply(lap, args=(p,))
                    # df[column] = df[column].swifter.apply(lap, args=(epsilon,))
                    # df[column] = df[column].swifter.apply(post_p, args=([min(value_list), max(value_list)],))
                    df[column] = df[column].astype(int)
                    # _vlogger.debug(f"df[column].dtypes：{df[column].dtypes}")

                    df.at[index,column] = lap(v=df.at[index,column],p = p)

                    df.at[index,column] = post_p(v=df.at[index,column],pc =[min(value_list), max(value_list)] )




            _vlogger.debug(f"差分隱私數據型資料的處理的df- column：{df[column] }")
    except Exception as e:
        _vlogger.debug(f"差分隱私error：{str(e)}")

    # 數值型差分隱私執行
    num_attr_is_numerical = continue_columns
    attr_list = list(df.columns)
    _vlogger.debug(f" attr_list：{attr_list}")

    attr_is_numerical = [0 if attr not in num_attr_is_numerical else 1  for attr in attr_list]

    _vlogger.debug(f" attr_is_numerical：{attr_is_numerical}")

    for attr_idx in range(len(attr_list)):
        if attr_idx == 0:
            continue
        if attr_is_numerical[attr_idx] == 1:
            name_list = list(df[attr_list[attr_idx]].value_counts().keys())
            _vlogger.debug(f"差分隱私數據型資料的處理的  name_list ：{name_list}")

            max_v = max(name_list)
            min_v = min(name_list)
            delta = max_v - min_v
            _vlogger.debug(f"差分隱私數據型資料的處理的  delta ：{delta}")
            p = compute_lap(epsilon, delta)
            _vlogger.debug(f"差分隱私數據型資料的處理的  p ：{p }")
            _vlogger.debug(f"df[attr_list[attr_idx]]：{df[attr_list[attr_idx]] }")
            _vlogger.debug(f"attr_list[attr_idx]：{attr_list[attr_idx] }")

            df[attr_list[attr_idx]] = df[attr_list[attr_idx]].astype(float)
            _vlogger.debug(f"數值型資料的處理的df[{attr_list[attr_idx]}]：{df[attr_list[attr_idx]]}")
            _vlogger.debug(f"df[attr_list[attr_idx]].dtypes：{df[attr_list[attr_idx]].dtypes}")



            # df[attr_list[attr_idx]] = df[attr_list[attr_idx]].swifter.apply(lap, args=(p,)) ## Need better post-processing
            # _vlogger.debug(f"df[attr_list[attr_idx]]：{df[attr_list[attr_idx]] }")
            # df[attr_list[attr_idx]] = df[attr_list[attr_idx]].swifter.apply(post_p, args=([min_v, max_v],)) ## SIMPLE post-processing

            # # 連續型數據的添加 noise 辦法
            # def lap(v, p):
            #     return (v+np.random.laplace(0, p))

    _vlogger.debug(f"差分隱私數據型資料的處理的df：{df }")







    # 將原本 mapping 的類別再 mapping 回來
    for column in column_mappings:
        for k,v in column_mappings[column].items():
            df[column] = df[column].replace(v,k)
        # print(column_mappings[column])
        _vlogger.debug(f"差分隱私數據 column_mappings[column] ：{column_mappings[column]}")

    # print(df)
    # df.to_csv(f'{filename}_{epsilon}_finish.csv', index=False)
    _vlogger.debug("差分隱私處理後的 DataFrame：")
    _vlogger.debug(f'df:{df}')
    for column in discrete_columns:
        df[column] = df[column].astype(str)
        df[column] = df[column].apply(lambda x: x.split('.')[0])

    _vlogger.debug(f'df:{df}')
    _vlogger.debug("差分隱私處理後的 DataFrame：")
    column_names = df.columns
    _vlogger.debug(f'df:{column_names}')







    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
    except Exception as e:
        _logger.debug(f'{projName}__connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return None

    # fileName = "/app/app/devp/user_upload_folder/work_drink/work_drink_inner.csv"
    csv_name = fileName.split("/")[-1]
    # export_path = "/app/app/devp/export_fordp/" + projName + "/" +"DP_" + str(epsilon) + "_" +csv_name
    shlex.quote(projName)
    folder_name = "/app/app/devp/export_fordp/" + projName

    # 使用subprocess执行mkdir命令创建文件夹
    try:
        shlex.quote(folder_name)
        if os.path.exists(folder_name):
             _logger.debug(f"Folder '{folder_name}' folder exists.")
        else: 
            subprocess.run(["mkdir", folder_name], check=True)
            _logger.debug(f"Folder '{folder_name}' created successfully.")
    except Exception as e:
        _logger.debug(f"Error occurred: {e}")
    shlex.quote(projName)
    shlex.quote(csv_name)
    export_path = "/app/app/devp/export_fordp/" + projName + "/" +"DP_" +csv_name
    #export_path
    df.to_csv(export_path, index=False, sep=",", header=True, encoding="utf-8")



    # 存到原始資料目錄  "/app/app/devp/folderForSynthetic/project_name/inputRawdata/df_drop.csv
    shlex.quote(projName)
    shlex.quote(csv_name)
    synDatasyntheticDir = "/app/app/devp/folderForSynthetic/" + projName + "/synProcess/synthetic/"
    synDataDir = "/app/app/devp/folderForSynthetic/" + projName + "/synProcess/synthetic/" +"DP_" +csv_name

    # 使用subprocess执行mkdir命令创建文件夹
    try:
        if os.path.exists(synDatasyntheticDir):
            _logger.debug(f"Folder '{synDatasyntheticDir}' folder exists.")
        else:
            subprocess.run(["mkdir", synDatasyntheticDir], check=True)
            _logger.debug(f"Folder '{synDatasyntheticDir}' created successfully.")
    except Exception as e:
        _logger.debug(f"Error occurred: {e}")

    # os.path.join('/app', 'app', 'devp', 'folderForSynthetic', projName, 'synProcess', 'synthetic/')
    #export_path
    df.to_csv(synDataDir, index=False, sep=",", header=True, encoding="utf-8")



    file_ = '/app/app/devp/config/Hadoop_information.txt'
    config = configparser.ConfigParser()
    config.read(file_)
    ip = config.get('Hadoop_information', 'ip')
    ip_join = config.get('Hadoop_information', 'ip_join')
    #port = config.get('Hadoop_information', 'port')
    from_path ='/home/hadoop/proj_/final_project/dp/output/'

    user =  config.get('Hadoop_information', 'user')
    passwd = config.get('Hadoop_information', 'passwd')

    _vlogger.debug('---------------------')
    _vlogger.debug(ip)


    hdfsInfo = getConfig().getLoginHdfs()
    user_ = str(hdfsInfo['user'])
    password_ = str(hdfsInfo['password'])

    shlex.quote(from_path)
    shlex.quote(folder_name)

    cmd = [
        'sshpass', '-p', password_,
        'scp', '-o', 'StrictHostKeyChecking=no',
        '-r', folder_name,
        f'{user_}@{ip_join}:{from_path}'
    ]
    _vlogger.debug(f'###############{cmd}')
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    _vlogger.debug(proc.stdout)
    _vlogger.debug(proc.stderr)
    
    try:
        mean_std_list = []


        for c_col in continue_columns:
            mean_std_dict = {}
            mean_std_dict['col'] = c_col
            mean_values = df[c_col].mean()
            mean_std_dict['mean'] = mean_values
            # Calculate standard deviation for specified columns
            std_values = df[c_col].std()
            mean_std_dict['std'] = std_values


            # Print mean and standard deviation for specified columns
            _vlogger.debug("mean_std_dict:")
            _vlogger.debug(mean_std_dict)
            mean_std_list.append(mean_std_dict)
        _vlogger.debug("mean_std_list:")
        _vlogger.debug(mean_std_list)

        json_data = json.dumps(mean_std_list)
    except Exception as e:
        _vlogger.debug("資料生成錯誤")
        updateToMysql_T_ProjectStatus(check_conn,projID,"99","資料生成錯誤")
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return

    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        check_conn = ConnectSQL()
        updateToMysql_DP_mean_std(check_conn, projID, projName, json_data)
        _vlogger.debug("updateToMysql_DP_mean_std")
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return

    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        check_conn = ConnectSQL()
        updateToMysql_T_ProjectStatus(check_conn,projID,"8","查看報表")
        _vlogger.debug("updateToMysql_T_ProjectStatus")
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return

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
    parser.add_argument("-epsilon", "--epsilon", help='epsilon')
    parser.add_argument("-userID", "--userID", help='update user info to mysql')
    parser.add_argument("-select_colValues", "--select_colValues",nargs='+', help='Selected col Values')
    parser.add_argument("-corr_colValues", "--corr_colValues",nargs='+', help='Selected corr col Values')
    parser.add_argument("-choose_corr_colValues", "--choose_corr_colValues",nargs='+', help='Selected choose corr col Values')
    args = vars(parser.parse_args())
    print(args)
    print ("in __main__")
    main(args)
    
    ####command:  python train_feature.py -d adult/adult.csv -col workclass education education_num marital_status occupation relationship race sex native_country class -gen True
    ####command(including conti): python train_feature.py -d adult/adult.csv -col workclass education education_num marital_status occupation relationship race sex native_country class -conti age capital_gain capital_loss hours_per_week fnlwgt -tar_col class -gen True
    
    ####command(wrong type):python train_feature.py -d adult/adult.csv -col education_num occupation relationship race sex native_country class -conti age capital_gain capital_loss hours_per_week fnlwgt workclass education marital_status  -tar_col class -gen True

##1224:update
##python train_feature.py -projName ProAdult -fileName data/adult.csv -colName education education_num marital_status occupation relationship race sex native_country class -keyName workclass

