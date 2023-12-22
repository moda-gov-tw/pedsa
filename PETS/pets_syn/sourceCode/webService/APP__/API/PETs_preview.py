# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 13:56:16 2019

@author: A70353
"""

import pandas as pd
import numpy as np
    
import shutil
import time
from MyLib.connect_sql import ConnectSQL 

from logging_tester import _getLogger
import pymysql
from mysql_create_api import createDB_SynService, createTbl_T_ProjectSample5Data
from mysql_create_api import createTbl_T_ProjectColumnType, createTbl_T_GANStatus
import configparser 
import os
import subprocess

#check the type of column and drop column with some condition
#return the columns have been dropped 
#return the df after dropped some columns
def check_columns(df):
    id_col = []
    missing_col =[]
    unique_col = []
        
    row,_ = df.shape
        
    for i in (df.columns):
        attr_nunique = df[i].nunique()
        missing_count = df[i].isnull().sum()
        #check ID column
        if  attr_nunique >= (row*0.8):
            id_col.append(i)
            #print("id col: ",i)
        #check wether #. NAN is greater than 60%
        if  missing_count >= (row*0.6):
            missing_col.append(i)
                #print("missing col: ",i)
        #check nunique attribute == 1
        if  attr_nunique == 1:
            unique_col.append(i)
                #print("unique col: ",i)
                
    df.drop(id_col, axis = 1, inplace=True)
    df.drop(missing_col, axis = 1, inplace=True)
    df.drop(unique_col, axis = 1, inplace=True)
    #print("id columns: ",id_col)
    #print("missing columns: ",missing_col)
    #print("att=1 columns: ",unique_col)
    return id_col, missing_col, unique_col , df

#check the type of column, then return categorical column
def check_col_type(df):
    ob_col = []
    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    for col in df_numeric.columns:
        f_nan_sum = df_numeric[col].isnull().sum()
        if f_nan_sum >= int(df_numeric.shape[0]*0.3):
            ob_col.append(col)
    return ob_col

#update mysql with sampling 5 data from the df after dropped some columns
def updateToMysql_sample(conn,userID,projID, projName, table, data):

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
            'data': data
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

#update mysql with df information from the df after dropped some columns
def updateToMysql_colType(conn,userID,projID, projName, table, pro_col_en,pro_col_cht,tableCount,ob_col,ID_column,pro_col_en_nunique):

    print('COLTYPE')
        # insert col type to sql
    condisionSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table
        }

    valueSampleData = {
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': table,
            'pro_col_en': ','.join(pro_col_en),
            'pro_col_cht':','.join(pro_col_cht),
            'tableCount':tableCount,
            'ob_col':','.join(ob_col), #drop_df's categorical columns
            'ID_column':','.join(ID_column), #drop columns with some condition
            'pro_col_en_nunique':','.join(pro_col_en_nunique)#pro_col_en_nunique count
        }

    resultSampleData = conn.updateValueMysql('SynService',#'DeIdService',
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

def updateToMysql_status(conn,userID,projID, projName, table, step,percentage):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'file_name': table,
            'jobName': "Preview"
        }

    valueSampleData = {
            'jobName': "Preview",
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
        _logger.debug(f'{projName}__insertSampleDataToMysql fail: ' + msg)
        return None

def main(args):

    global  _logger,_vlogger, check_conn     
    # debug log
    _logger  =_getLogger('error__preview')
    # verify log
    _vlogger =_getLogger('verify__preview')

    #connect MYSQL
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")

    except Exception as e:
        _logger.debug(f'{projName}__connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return None
    #create DB AND table
    try :
        stepDict = {
            '0': createDB_SynService(check_conn),
            '1': createTbl_T_ProjectSample5Data(check_conn),
            '2': createTbl_T_ProjectColumnType(check_conn),
            '3': createTbl_T_GANStatus(check_conn)
        }
        for i in range(len(stepDict)):
            print(i)
            try:
                result = stepDict[str(i)]
                if result['result'] == 1:
                    _vlogger.debug(result['msg'])
                else:
                    print('mysql fail:' + result['msg'])
                    #return False
            except:
                pass
    except Exception as e:
        _logger.debug(f'{projName}__create DB fail: - %s:%s' %(type(e).__name__, e))
        return None

    userID = args['userID']
    projName = args['projName']
    fileName = args['fileName']
    projID = args['projID']

    _vlogger.debug(f'*******{projName}__{fileName}')



    #Initial
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn,userID, projID, projName, fileName, 'Initial', 0)
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return
    
    user_upload_path = "app/devp/user_upload_folder/"+projName+'/'
    project_path = "app/devp/folderForSynthetic/"+projName+'/'
    inputRawdata_path = project_path+'inputRawdata'+'/'

    #install sshpass
    runcode = os.system('apt install sshpass')

    checked = os.path.isdir(user_upload_path)
    if checked == True:
        shutil.rmtree(user_upload_path)

    # if not os.path.exists(user_upload_path):
    #     _vlogger.debug(f'os.makedirs{user_upload_path}')
    #     os.mkdir(user_upload_path)

    ###scp from PET-hadooop: 將遠端的檔案保留時間與權限複製到本地端
    try:
        file_ = 'app/devp/config/Hadoop_information.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        ip = config.get('Hadoop_information', 'ip') 
        #port = config.get('Hadoop_information', 'port') 
        from_path = config.get('Hadoop_information', 'from_path')  
        user =  config.get('Hadoop_information', 'user')
        passwd = config.get('Hadoop_information', 'passwd')
        _vlogger.debug(ip)
        #_logger.debug(port)
        #_logger.debug(from_path)     
        

        ##有可能檔案太大需要時間搬
        cmd = 'sshpass -p "citcw200@" '+f'scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@{ip}:{from_path}{projName} /app/app/devp/user_upload_folder/{projName}'
        proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
        _vlogger.debug(cmd)

        user_dir = '/home/ubuntu/PETS/pets_syn/pets_syn/sourceCode/webService/APP__/user_upload_folder/'
        cmd = 'sshpass -p \"'+passwd+'\" ssh -o StrictHostKeyChecking=no -p 22 '+user+'@'+ip+ ' sudo chown -R ubuntu:ubuntu '+user_dir+projName+'/'
        runcode = os.system(cmd)
        _vlogger.debug(cmd)
        # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P ' + port + ' -r hadoop@' + ip + ':/home/hadoop/proj_/final_project/syn/input/'+projName+' app/devp/user_upload_folder/'+projName
        # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+' /home/hadoop/proj_/data/input/'+projName
        
        #cmd = 'sshpass -p \"'+passwd+'\" scp -o StrictHostKeyChecking=no -P ' + port + ' -r ' +user+'@' + ip +':'+from_path+projName+' app/devp/user_upload_folder/'

        # proc = subprocess.run(cmd, shell=True,check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #runcode = os.system(cmd)
        # _logger.debug("run result is {0}".format(str(proc)))
        
    except Exception as e:
        _logger.debug(f'{projName}__to PETs hadoop error : ',str(e))

    time.sleep(5)

    #cp data from user's upload folder to projectfolder
    #Copy a file into projectfolder
    userfile = user_upload_path+fileName
    _vlogger.debug(f'{projName}__userfile: ',userfile)

    projectfile = inputRawdata_path+projName+".csv" #fileName

    try:
        #os.rename(userfile, user_upload_path+projName+".csv")
        if userfile != user_upload_path+projName+".csv":
            newPath = shutil.copy( userfile, user_upload_path+projName+".csv")
            os.remove(userfile) 
        _vlogger.debug(f'{projName}__finish copy__{user_upload_path}{projName}.csv ')

    except Exception as e:
        #rint('copy file fail: - %s:%s' %(type(e).__name__, e))
        _logger.debug(f'{projName}__INsert fail(shutil.copy): - %s:%s' %(type(e).__name__, e))
        return None

    try:
        newPath = shutil.copy( user_upload_path+projName+".csv", projectfile)
    except Exception as e:
        #rint('copy file fail: - %s:%s' %(type(e).__name__, e))
        _logger.debug(f'{projName}__INsert fail(shutil.copy2): - %s:%s' %(type(e).__name__, e))
        return None

    try:

        #load data
        df = pd.read_csv(projectfile)
        all_raw_col = df.columns.tolist()
        # Take a look at the first entries
        print("df.shape: ",df.shape)
        print(df.tail(1))

        '''
        # Convert ch_col_name to en_col_name
        header_ch = inputData.columns
        tmp_num = str(hash(projName))[1:3] + str(hash(tblName))[1:3]
        header_en = ['c_'+tmp_num+'_'+str(i) for i in range(len(header_ch))]
        inputData = inputData.toDF(*header_en)
        '''   
                
        id_col, missing_col, unique_col, df_drop = check_columns(df)
        _vlogger.debug(f'{projName}__id columns: {id_col}')
        _vlogger.debug(f'{projName}__missing columns: {missing_col}')
        _vlogger.debug(f'{projName}__att=1 columns: {unique_col}')
    except Exception as e:
        print('check columns type fail: - %s:%s' %(type(e).__name__, e))
        #_logger.debug(f'{projName}__INsert fail: - %s:%s' %(type(e).__name__, e))
        return None

    join_drop_columns = id_col+missing_col+unique_col
    try:
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn,userID, projID, projName, fileName, 'drop_id_column', 30)
            #_vlogger.debug('updateToMysql_status succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None

    try:
        _vlogger.debug(f'{projName}__drop df shape: {df_drop.shape}')
        _vlogger.debug(f'{projName}__#################################1')

            # try:
            #     df_drop = df_drop_tmp.fillna('UNknown',inplace=False)
            # except Exception as e:
            #     _logger.debug(f'{projName}__errTable: df_drop_tmp.fillna. {0}'.format(str(e)))
            #     return None
        _vlogger.debug(f'{projName}__#################################2')

        newPath = shutil.copy( user_upload_path+projName+".csv", inputRawdata_path+'df_preview.csv')
        '''
        if df_drop.shape[0]>900000:
            newPath = shutil.copy( user_upload_path+projName+".csv", inputRawdata_path+'df_preview.csv')
            #df_drop.fillna('NULL',inplace=True)
            #df_drop.to_csv(inputRawdata_path+'df_preview.csv',index=False)
            pass #mask for large file
            #save file after preprocessing
            #df_drop = df_drop.sample(n=1000)
        else:
            df_drop.fillna('NULL',inplace=True)
            df_drop.to_csv(inputRawdata_path+'df_preview.csv',index=False)
        '''
        _vlogger.debug(f'{projName}__#################################3')
            #check file column type
        all_col = df_drop.columns.tolist()
        tableCount,_ = df_drop.shape
        ob_col = check_col_type(df_drop)
        _vlogger.debug(f'{projName}__ob_col columns: {ob_col}')
            #print(df_drop.info())
        pro_col_en_nunique=[]
        for col_nunique in all_col:
            count = df_drop[col_nunique].nunique()
            _vlogger.debug(f'{projName}__{col_nunique},{count}')
            pro_col_en_nunique.append(str(count))
    except Exception as e:
        _logger.debug('check columns type fail: - %s:%s' %(type(e).__name__, e))
        #_logger.debug(f'{projName}__INsert fail: - %s:%s' %(type(e).__name__, e))
        return None

    try:
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn,userID, projID, projName, fileName, 'check_column', 80)
            #_vlogger.debug('updateToMysql_status succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None



    
    #save df_drop.head() to sql
    #data = df_drop.sample(n=5).to_json(orient='records')
    data = df_drop.head(5).to_json(orient='records')
    try:
        updateToMysql_sample(check_conn,userID,projID, projName, fileName, data)
        _vlogger.debug(f'{projName}__sampleStr_succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: Sample fail. {0}'.format(str(e)))
        return

    #save df_drop.ob_columns to sql
    try:
        #list: pro_col_en,pro_col_cht,ob_col
        #updateToMysql_colType(conn,projID, projName, fileName, pro_col_en,pro_col_cht,tableCount,ob_col)
        updateToMysql_colType(check_conn,userID,projID, projName, fileName, all_raw_col, all_col,tableCount,ob_col,join_drop_columns,pro_col_en_nunique)
        _vlogger.debug(f'{projName}__insert column type succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: insert column type fail. {0}'.format(str(e)))
        return
    try:
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn,userID, projID, projName, fileName, 'finish', 100)
            #_vlogger.debug('updateToMysql_status succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    print("citc____Mission Complete")





if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-projName", "--projName", help='projName for make a folder')
    parser.add_argument("-fileName", "--fileName", help='The name of dataset')
    parser.add_argument("-projID", "--projID", help='projID for mysql')
    parser.add_argument("-userID", "--userID", help='update user info to mysql')
    args = vars(parser.parse_args())
    print(args)
    print ("in __main__")
    main(args)
