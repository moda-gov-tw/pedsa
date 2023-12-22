#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 20210924
監控"dataConfig" "dataMac/input/"
datacheck
檢查有沒有JOB在做

@author: A70353
"""
import pandas as pd
import numpy as np
    
import requests

from config.connect_sql import ConnectSQL 
from config.loginInfo import getConfig

# from log.logging_tester import _getLogger

from datetime import datetime

import time
import sys
import os
import json
import io
import base64
import datetime as dt
import math
import warnings

#:function:到mariadb獲取table資訊
def check_appstatus():
    try: #connection SQL
        check_conn = ConnectSQL()
    except Exception as e:
        print('***errTable: connect sql error [check_watchFolder]. {0}'.format(str(e)))
    try: # fetch parameter: pid
        #sqlStr = "SELECT Progress  FROM `spark_status`.`appStatus` where proj_id like '{}';".format(proj_id,Application_Name)
        # sqlStr = "SELECT Progress  FROM `spark_status`.`appStatus` where proj_id like '{}' AND Application_Name like '{}';".format(proj_id, Application_Name)
        try:
            sqlStr = "SELECT  project_id FROM `DeIdService`.`T_ProjectStatus` ORDER BY ps_id DESC LIMIT 1;"
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                proj_id = resultCheck["fetchall"][0]['project_id']
            sqlStr = "SELECT  project_name FROM `DeIdService`.`T_Project` where project_id like '{}';".format(proj_id)
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                project_name = resultCheck["fetchall"][0]['project_name']
        except:
            project_name = ""

        try:
            sqlStr = "SELECT  project_status FROM `DeIdService`.`T_ProjectStatus` ORDER BY ps_id DESC LIMIT 5;"
            resultCheck = check_conn.doSqlCommand(sqlStr)
            # print("resultCheck: {} ".format(resultCheck))
            if int(resultCheck['result'])==1:
                Progress = []
                for i in range(len(resultCheck["fetchall"])):
                    Progress.append(resultCheck["fetchall"][i]['project_status'])
            # print("Progress: {} ".format(Progress))
        except:
            Progress = []

        try:
            sqlStr = "SELECT statusname  FROM `DeIdService`.`T_ProjectStatus` ORDER BY ps_id DESC LIMIT 1;"
            resultCheck = check_conn.doSqlCommand(sqlStr)
            if int(resultCheck['result'])==1:
                Progress_State = resultCheck["fetchall"][0]['statusname']
        except:
            Progress_State = ""

        check_conn.close()
        return project_name, Progress, Progress_State
    except Exception as e:
        print('***errTable: check_watchFolder error-2. {0}'.format(str(e)))

#function:獲取資料夾文件列表
def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = os.listdir(path_to_dir)
    # print(filenames)
    time = os.path.getmtime(path_to_dir)
    # print(time)
    filenames.sort(key=lambda fn:os.path.getmtime(path_to_dir + fn))#按時間排序    filenames = os.path.join(path_to_dir,filenames[-1])      #獲取最新的文件保存到file_new
    # print(filenames)
    return [ os.path.splitext(filename)[0] for filename in filenames if filename.endswith( suffix ) ]

#function: read json
def checkJson(checkjson):
    with io.open(checkjson, 'r',encoding="utf-8") as reader:
        jf = json.loads(reader.read())
    try:
        C_flag = True
        pro_col_cht = jf['pro_col_cht'] #column name
        col_cht_ = pro_col_cht.split(',')

        if jf['target_col'] is not None:
            targetCols = jf['target_col'] #targetCols: JADE
            targetCols_ = targetCols.split(',')
        else:
            targetCols = "None" #targetCols: JADE
            targetCols_ = targetCols.split(',')

        after_col_value = jf['after_col_value'] #after_col_value
        after_col_value_ = after_col_value.split(',')

        qi_col = jf['qi_col'] #qi_col
        qi_col_ = qi_col.split(',')

        return col_cht_, targetCols_, after_col_value_, qi_col_, C_flag
    except Exception as e:
        C_flag = False
        print('*** 讀取config出錯 checkJson error: {0}.'.format(str(e)))
        print('***請檢查 data 和 config file.')
        # sys.exit(1)
        return "_","_","_", C_flag
        ##這邊有其他的處置嗎?

#function:檢查資料規則
def checkData(dataToDoPath,col_cht_, targetCols_, after_col_value_, qi_col_):
    TFlag1 = False
    TFlag2 = False
    TFlag3 = False
    TFlag3_2 = False
    #step2.1: df's column name same as config
    # 特殊符號分隔
    # df = pd.read_csv(dataToDoPath, sep = "\^\|")
    # 逗號分隔
    df = pd.read_csv(dataToDoPath, sep = ",")
    df_cols_ = df.columns.tolist()
    # print("df_cols_: {}".format(df_cols_))
    # print("col_cht_: {}".format(col_cht_))
    if set(df_cols_) == set(col_cht_):
        TFlag1 = True
        print("step1 check: 檢查欄位命名對應 [OK]")
    else:
        TFlag1 = False
        print("step1 check: 檢查欄位命名對應 [ERROR]")
        # print('命名欄位有誤: {}'.format(set(df_cols_) ^ set(col_cht_)))

    if len(targetCols_)<=3:
        TFlag2 = True
        print("step2 check: 檢查ML欄位<=3 [OK]")
    else:
        TFlag2 = False
        print("step2 check: 檢查ML欄位<=3 [ERROR]")
        # print("ML欄位<=3: {}".format(targetCols_))

    if '1' in after_col_value_:
        TFlag3 = True
        print("step3-1 check: 檢查去識別欄位有設定間接識別欄位 [OK]")
    else:
        TFlag3 = False
        print("step3-1 check: 檢查去識別欄位有設定間接識別欄位 [ERROR]")
        # print("去識別欄位沒有1: {}".format(after_col_value_))

    tmp_ = []
    for i in range(len(after_col_value_)):
        if str(after_col_value_[i])== '3' or str(after_col_value_[i])== '4' or str(after_col_value_[i])== '0' :
            pass
        else:   
            combined_qi = col_cht_[i]+'-'+after_col_value_[i]
            tmp_.append(combined_qi)
            # print(i, combined_qi)
    # print("tmp_: {}".format(tmp_))
    # print("qi_col_: {}".format(qi_col_))

    if len(list(set(qi_col_) ^ set(tmp_))) == 0:
        TFlag3_2 = True
        print("step3-2 check: 檢查去識別欄位有對應去識別化條件 [OK]")
    else:
        TFlag3_2 = False
        print("step3-2 check: 檢查去識別欄位有對應去識別化條件 [ERROR]")
        # print("去識別欄位沒有對應去識別化條件:{}".format(list(set(qi_col_) ^ set(tmp_))))

    if TFlag1==True and TFlag2==True and TFlag3==True and TFlag3_2 == True:
        return "True"
    else:
        return "False"

def call_DeidAPI(fileToDo, time_stamp, columns_mac): 
    DeidAPI_para = {
      "columns_mac": "id",
      "configName": "adult_id.json",
      "dataHash": "yes",
      "hashTableName": "adult_id",
      "hashkey": "HSM used",
      "p_dsname": "DeId_adult_hash_20220510",
      "pname": "DeId_adult_hash_20220510",
      "prodesc": "describe: DeId-project with hash on adult dataset.",
      "sep": ","
      # "sep": "^|"
    }
    ###輸入客制化的資訊:要傳json進來?
    ### time_stamp:int 
    struct_time = time.localtime(time_stamp)
    timeString = time.strftime("%Y%m%d%H%M%S", struct_time)
    prodescTime = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)

    DeidAPI_para["columns_mac"] = columns_mac
    DeidAPI_para["configName"] = fileToDo+".json"
    DeidAPI_para["hashTableName"] = fileToDo
    DeidAPI_para["p_dsname"] = fileToDo #+"_"+ timeString
    DeidAPI_para["pname"] = fileToDo #+"_"+ timeString
    DeidAPI_para["prodesc"] = "describe: DeId-project  {}.".format(fileToDo)
    ###要檢查確定不會有重複專案命名?
    # print('DeidAPI_para: ',DeidAPI_para)
    # response_g = requests.get("http://140.96.111.204:5997/setAutoDeId_Async", params=DeidAPI_para,timeout=None)
    # response_g = requests.post("http://flask5997_compose:5088/setAutoDeId_Async", json=DeidAPI_para,timeout=None)
    response_g = requests.post("https://140.96.111.204:5997/setAutoDeId_Async", json=DeidAPI_para, timeout=None, verify=False)
    # response_dic = response_g.json()
    # print("DeidAPI JSON: ",response_dic)

def modified_time(dataConfig, checkjson):
    with io.open(checkjson, 'r',encoding="utf-8") as reader:
        jf = json.loads(reader.read())
    timeStamp = jf['timeStamp'] # original timestamp in json
    struct_time = time.localtime(timeStamp)
    timeString = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
    # print("原時間戳 in json: {}".format(timeString ))
    # print("(INT)原時間戳 in json: {} ".format(timeStamp))
    now = datetime.now() #os current time
    timestring = now.strftime('%Y-%m-%d %H:%M:%S')
    # print("現在時間 = {}".format(timestring))
    # timestring = "2021-09-27 08:00:00"
    struct_time = time.strptime(timestring, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(struct_time))
    jf['timeStamp'] = time_stamp
    # print("(INT)現在時間 = {}".format(time_stamp))
    with open(dataConfig+'test_modifiedTime.json', 'w') as fp:
        json.dump(jf, fp)
    with open(checkjson, 'w') as fp:
        json.dump(jf, fp)
    columns_mac = jf['tablekeycol']
    return time_stamp, columns_mac

def main():
    #step1: loop path find the same name file
    path = getConfig().getExportPath('local')
    # dataPath = os.path.join(path[:-12], 'dataMac/input/')
    # dataConfig = os.path.join(path[:-12], 'dataConfig/')
    datapath = os.path.join(path[:-12], 'data_check/')
    # print("datapath: {}".format(datapath))
    dataerrorpath = os.path.join(path[:-12], 'data_error/')
    # print("dataerrorpath: {}".format(dataerrorpath))
    # print("dataPath: {}".format(dataPath))

    # data_ = find_csv_filenames(dataPath,".csv")
    data_ = find_csv_filenames(datapath,".csv")#先進來的檔案先做
    # print("文件列表: {}".format(data_))
    # config_ = find_csv_filenames(dataConfig,".json")
    config_ = find_csv_filenames(datapath,".json")#先進來的檔案先做
    # print("Config列表: {}".format(config_))
    CommonFileName_ = list(set(data_).intersection(config_))
    print("有命名相符的資料: {}".format(CommonFileName_))
    
    if len(CommonFileName_) != 0 : #只要有共同擋名就進行下一步規則比對
        #1.1 Get a last modified data file >>data會定期匯入
        # Get file's Last modification time stamp only in terms of seconds since epoch 
        fileTime_ = []
        for file in CommonFileName_: #先進來的檔案先做

            # modTimesinceEpoc = os.path.getmtime(dataPath+file+".csv")
            modTimesinceEpoc = os.path.getmtime(datapath+file+".csv")
            # Convert seconds since epoch to readable timestamp
            # modificationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))
            # print("Last Modified Time : ", modificationTime )
            fileTime_.append(modTimesinceEpoc)
        min_idx = np.argmin(fileTime_) 
        fileToDo = CommonFileName_[min_idx]
        # dataToDoPath = dataPath+fileToDo+".csv"
        dataToDoPath = datapath+fileToDo+".csv"
        # configToDoPath = dataConfig+fileToDo+".json"
        configToDoPath = datapath+fileToDo+".json"
        # print( "有命名相符的資料，最早被修改的: {0}, {1}".format(fileToDo+".csv", fileToDo+".json"))
        print("執行去識別化資料名稱: {}".format(fileToDo))
        #step2:data check (問bruce有沒有網頁擋的規則)
        # print("讀取config檔案內容▼▼▼")
        col_cht_, targetCols_, after_col_value_, qi_col_, C_flag = checkJson(configToDoPath) #C_flag:True成功做完/False:移除資料到error,需要mountfolder
        # print("col_cht_: {}".format(col_cht_))
        # print("targetCols_: {}".format(targetCols_))
        # print("after_col_value_: {}".format(after_col_value_))
        # print("qi_col_: {}".format(qi_col_))
        # print("C_flag: {}".format(C_flag))


        if C_flag == True:
            # print("檢查資料和config是否符合資料規則▼▼▼")
            Flag = checkData(dataToDoPath,col_cht_, targetCols_, after_col_value_, qi_col_)
            if Flag == "True":
                dataMacpath = os.path.join(path[:-12], 'dataMac/input/')
                dataConfigpath = os.path.join(path[:-12], 'dataConfig/')
                dataToDoPath_new = dataMacpath+fileToDo+".csv"
                configToDoPath_new = dataConfigpath+fileToDo+".json"
                # print("dataToDoPath_new: {}".format(dataToDoPath_new))
                # print("configToDoPath_new: {}".format(configToDoPath_new))
                os.system('cp {} {}'.format(dataToDoPath, dataToDoPath_new))
                os.system('cp {} {}'.format(configToDoPath, configToDoPath_new))
            else:
                print("資料有誤，請至error folder檢查.")
                dataNotToDoPath = dataerrorpath+fileToDo+".csv"
                configNotToDoPath = dataerrorpath+fileToDo+".json"
                os.system('mv {} {}'.format(dataToDoPath, dataNotToDoPath))
                os.system('mv {} {}'.format(configToDoPath, configNotToDoPath))
                sys.exit(0)
        else:
            print("資料有誤，請至error folder檢查.")
            dataNotToDoPath = dataerrorpath+fileToDo+".csv"
            configNotToDoPath = dataerrorpath+fileToDo+".json"
            os.system('mv {} {}'.format(dataToDoPath, dataNotToDoPath))
            os.system('mv {} {}'.format(configToDoPath, configNotToDoPath))
            sys.exit(0)

        if Flag == "True":
            project_name, Progress, Progress_State = check_appstatus()
            # print("Progress :{} ".format(Progress))
            valueToBeRemoved = 15
            Progress = [value for value in Progress if value != valueToBeRemoved]
            print("Progress :{} ".format(Progress))
            # print("最近一次的專案 {0} 列表狀態 ({1}, {2}) ".format(project_name, Progress, Progress_State))
            if len(Progress) < 5 :
                print("目前尚可執行 {} 個專案，準備執行資料去識別化.".format(5-len(Progress)))
                #沒有JOB，就可以改config timeStamp，call deid API
                # time_stamp, columns_mac = modified_time(dataConfig, configToDoPath)
                time_stamp, columns_mac = modified_time(datapath, configToDoPath)
                call_DeidAPI(fileToDo, time_stamp, columns_mac)
            elif len(Progress) == 0:
                print("目前尚可執行 {} 個專案，準備執行資料去識別化.".format(5-len(Progress)))
                time_stamp, columns_mac = modified_time(datapath, configToDoPath)
                call_DeidAPI(fileToDo, time_stamp, columns_mac)

            # print("最近一次的專案 {0} 列表狀態 ({1}, {2}) ".format(project_name, Progress, Progress_State))
            # if str(Progress)==str(15) and Progress_State=='export data finished':
            #     print("目前沒有正在執行的專案，準備執行資料去識別化.")
            #     #沒有JOB，就可以改config timeStamp，call deid API
            #     # time_stamp, columns_mac = modified_time(dataConfig, configToDoPath)
            #     time_stamp, columns_mac = modified_time(datapath, configToDoPath)
            #     call_DeidAPI(fileToDo, time_stamp, columns_mac)
            else:
                print('JOB Wait, 還有專案尚未執行完畢.')
        #
        # elif Flag == "False": #要在哪註明?是哪種錯誤嗎?
        #     print("資料有誤，請至error folder檢查.")
        #     dataNotToDoPath = dataerrorpath+fileToDo+".csv"
        #     configNotToDoPath = dataerrorpath+fileToDo+".json"
        #     os.system('mv {} {}'.format(dataToDoPath, dataNotToDoPath))
        #     os.system('mv {} {}'.format(configToDoPath, configNotToDoPath))
        #     sys.exit(0)
    else:
        print("***在監控資料夾中，沒有相符命名的資料.")

    if CommonFileName_== []:
        print("\n----完 成 1 次 監 控----\n")
        pass
    elif len(Progress) == 5:
        print("\n----完 成 1 次 監 控----\n")
        pass
    else:
        os.system('rm {}'.format(dataToDoPath))
        os.system('rm {}'.format(configToDoPath))
        print("\n----完 成 1 次 監 控----\n")

if __name__ == "__main__":
    print("\n----WatchFolder Service ON----\n")
    warnings.filterwarnings("ignore")
    main()