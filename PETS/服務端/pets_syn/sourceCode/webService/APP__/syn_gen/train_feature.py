from _a_check import check_type, hit_rate
####20180920
from a_preparing_csv2feature import csv2feature
import pandas as pd
from b_embedding_ import embedding
from c_vectodataframe import vec2dataframe
from d_GAN import generation
from e_sample import sampling,recovering_syn
from e_sample_conti import sampling_conti
# from adult.eva_acc import acc
# from taxi.eva_acc import acc
#from eva_acc import acc
import random
import time
import os 
import shutil
import re
#from .config_sql.connect_sql import ConnectSQL
from logging_tester import _getLogger
import pymysql
from configparser import ConfigParser
import os.path
import argparse
from MyLib.connect_sql import ConnectSQL 
from mysql_create_GAN import createTbl_T_GANStatus

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
        _logger.debug("Update mysql succeed.")
        return None
    else:
        # msg = resultSampleData['msg']
        _logger.debug(f'{projName}__insertSampleDataToMysql fail')
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
        _logger.debug("Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projName}__insertSampleDataToMysql fail')
        return None

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

    if not re.match("^[0-9]+$", str(userID)):
        _logger.debug("Invalid userID format")
        return 'Fail'
    
    if not re.match("^[0-9]+$", str(projID)):
        _logger.debug("Invalid projID format")
        return 'Fail'
    
    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName)or projName.isdigit()or '..' in projName or '/' in projName:
        _logger.debug("Invalid projName format")
        return 'Fail'

    if not re.match("^[a-zA-Z0-9_ .]+$", fileName):
        _logger.debug("Invalid fileName format")
        return 'Fail'
        
    if not isinstance(col_name, list):
        _logger.debug("Invalid col_name format")
        return 'Fail'

    if not isinstance(select_colNames, list):
        _logger.debug("Invalid select_colNames format")
        return 'Fail'

    if not isinstance(keyName, list):
        _logger.debug("Invalid keyName format")
        raise 'Fail'


    project_path = os.path.join("app/devp/folderForSynthetic/",projName)
    file_path = os.path.join(project_path,"inputRawdata/df_drop.csv")
    previewFile_path = os.path.join(project_path,"inputRawdata/df_preview.csv")
    
    try:
        shutil.copy( previewFile_path, file_path)
    except Exception as e:
        _logger.debug(f'{projName}__INsert fail: - %s:%s' %(type(e).__name__, e))
        return None


    directory = os.path.join(project_path,"synProcess")
    directory_pkl = os.path.join(directory,"pkl")

    if not os.path.exists(directory_pkl):
        os.mkdir(directory_pkl)

    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")
    except Exception as e:
        _logger.debug(f'{projName}__connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return None

    try:
        result = createTbl_T_GANStatus(check_conn)
        if result['result'] == 1:
            _vlogger.debug('result 1')
        else:
            print('mysql fail')
            #return False
    except:
        pass

    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn,userID, projID, projName, fileName, 'Initial', 0)
        _vlogger.debug(f'{projName}__syn_progess 0% [Initial].')
        _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return
    
    initial_time=time.time()
    
    try: #check col type
        _vlogger.debug('--------------checktype----------------------------')
        col_name, conti_col, unique_att_num, tar_col, df = check_type(select_colNames,col_name,file_path,keyName)
        _vlogger.debug('--------------checktype----------------------------')
        _vlogger.debug(f'{projName}__col_name: '+','.join(col_name))
        _vlogger.debug(f'{projName}__conti_col: '+','.join(conti_col))
        _vlogger.debug(f'{projName}__unique_att_num: {unique_att_num}')
        _vlogger.debug(f'{projName}__tar_col: '+str(tar_col))
    except Exception as e:
        _logger.debug(f'{projName}__errTable: check_type fail. {0}'.format(str(e)))
        return

    #save df_select.head() to sql
    select_data = df.head(5).to_json(orient='records', force_ascii=False)
    try:
        check_conn = ConnectSQL()
        updateToMysql_sample(check_conn,userID,projID, projName, fileName, select_data)
        check_conn.close()
        _vlogger.debug(f'{projName}__update sample5data succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: update sample5data fail. {0}'.format(str(e)))
        return
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn,userID, projID, projName, fileName, 'sample5data', 10)
        check_conn.close()
        _vlogger.debug(f'{projName}__syn_progess 10% [sample5data].')
        _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return


    f_time = open(os.path.join(directory,'time.txt'), 'a')
    if generate == str(True):
        encoding_initial_time=time.time()
        if col_name == ['False']: #when selected cols are all continuous.
            GAN_Flag = 'False'
            try :
                #f = open(directory+'sum_col_num.txt', 'r')
                #sum_col_num = int(f.read())
                #f.close() 
                generation_initial_time=time.time()
                sum_col_num = df.shape[1]
                f = open(os.path.join(directory,'sum_col_num.txt'), 'w')
                f.write(str(sum_col_num))
                f.close()
                generation(directory,file_path,sum_col_num, GAN_Flag)
                GAN_time=time.time()-generation_initial_time
                f_time.write("Generation time: "+str(GAN_time)+"\n")
                _vlogger.debug(f'{projName}__Training GAN succeed')
                try:
                    #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
                    check_conn = ConnectSQL()
                    updateToMysql_status(check_conn,userID, projID, projName, fileName, 'GAN', 60)
                    _vlogger.debug(f'{projName}__syn_progess 60% [GAN].')
                    _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
                    check_conn.close()
                except Exception as e:
                    _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
                    return None
            except Exception as err:
                _logger.debug(f'{projName}__GAN error! - %s:%s' %(type(err).__name__, err))
                return None

        else: 
            try :
                csv2feature(directory,file_path,col_name,tar_col,transfer) ##step1: csv2feature
                _vlogger.debug(f'{projName}__csv2feature succeed~')
            except Exception as err:
                _logger.debug(f'{projName}__csv2feature error! - %s:%s' %(type(err).__name__, err))
                return None

            try :
                embedding(directory,col_name,unique_att_num) ## step2-2: embedding attribute
                encoding_time=time.time()-encoding_initial_time#calculate encoding time
                f_time.write("Encoding time: "+str(encoding_time)+"\n")
                _vlogger.debug(f'{projName}__Entity embedding succeed')
            except Exception as err:
                _logger.debug(f'{projName}__Entity embedding error! - %s:%s' %(type(err).__name__, err))
                return None
            try:    
                sum_col_num = vec2dataframe(directory,df,col_name,conti_col) ##sum_col_num write in to text
                f = open(os.path.join(directory,'sum_col_num.txt'), 'w')
                f.write(str(sum_col_num))
                f.close()
                _vlogger.debug(f'{projName}__Encoding succeed')
                try:
                    #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
                    check_conn = ConnectSQL()
                    updateToMysql_status(check_conn,userID, projID, projName, fileName, 'Encoding', 30)
                    check_conn.close()
                    _vlogger.debug(f'{projName}__syn_progess 30% [Encoding].')
                    _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
                except Exception as e:
                    _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
                    return None
            except Exception as err:
                _logger.debug(f'{projName}__Encoding error! - %s:%s' %(type(err).__name__, err))
                return None
            #######For testing adult embedded to transform back.
            #print(df.head())
            #f = open(directory+'sum_col_num.txt', 'r')
            #sum_col_num = int(f.read())
            #f.close()  
            #recovering_syn(directory,sum_col_num,col_name,conti_col,5)
            #######
      
            try :
                #f = open(directory+'sum_col_num.txt', 'r')
                #sum_col_num = int(f.read())
                #f.close() 
                GAN_Flag = 'True'
                generation_initial_time=time.time()
                generation(directory,file_path,sum_col_num, GAN_Flag)
                GAN_time=time.time()-generation_initial_time
                f_time.write("Generation time: "+str(GAN_time)+"\n")
                _vlogger.debug(f'{projName}__Training GAN succeed')
                try:
                    #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
                    check_conn = ConnectSQL()
                    updateToMysql_status(check_conn,userID, projID, projName, fileName, 'GAN', 60)
                    check_conn.close()
                    _vlogger.debug(f'{projName}__syn_progess 60% [GAN].')
                    _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
                except Exception as e:
                    _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
                    return None
            except Exception as err:
                _logger.debug(f'{projName}__GAN error! - %s:%s' %(type(err).__name__, err))
                return None
    alive=[]
    if sample == str(True):
        f = open(os.path.join(directory,'sum_col_num.txt'), 'r')
        sum_col_num = int(f.read())
        f.close()
        sampling_initial_time=time.time()
        if GAN_Flag == 'False': #all columns are continuous
            random_epoch = [12,24,30]#random.sample(range(99,200, 3), 30)
            hit_counter  = 0
            for e in random_epoch:
                try :
                    sampling_conti(directory,file_path,sum_col_num,e)
                    _vlogger.debug(f'{projName}__Sample & Reverse succeed: all continuous')
                except Exception as err:
                    _logger.debug(f'{projName}__Sample & Reverse error! - %s:%s' %(type(err).__name__, err))
                    return None

                sampling_time=time.time()-sampling_initial_time
                f_time.write("Sampling time: "+str(sampling_time)+"\n")
                   
                try :
                    hit_initial_time=time.time()
                    #check hitting rate: right now just not used!
                    hit_response = hit_rate(directory,df,e,conti_col,"False")
                    hit_tt = time.time()-hit_initial_time
                    f_time.write("hit time: "+str(hit_tt)+"\n")
                    if hit_response=="hit":
                        hit_counter=hit_counter+1
                except Exception as err:
                    _logger.debug(f'{projName}__Hit error! - %s:%s' %(type(err).__name__, err))
                    return None
        elif GAN_Flag == 'True':
            random_epoch = [24,30,39]#random.sample(range(99,200, 3), 30)
            hit_counter  = 0
            for e in random_epoch:
                try :
                    epoch_alive = sampling(directory,sum_col_num,e)
                    _vlogger.debug(f'{projName}__Sample succeed')
                except Exception as err:
                    _logger.debug(f'{projName}__Sample error! - %s:%s' %(type(err).__name__, err))
                    return None
                alive.append(epoch_alive)
                if epoch_alive == 'True':
                    try :    
                        recovering_syn(directory,sum_col_num,col_name,conti_col,e)
                        _vlogger.debug(f'{projName}__Reverse succeed')
                    except Exception as err:
                        _logger.debug(f'{projName}__Reverse error! - %s:%s' %(type(err).__name__, err))
                        return None

                    sampling_time=time.time()-sampling_initial_time
                    f_time.write("Sampling time: "+str(sampling_time)+"\n")
                   
                    try :
                        hit_initial_time=time.time()
                        #check hitting rate: right now just not used!
                        hit_response = hit_rate(directory,df,e,conti_col,"False")
                        hit_tt = time.time()-hit_initial_time
                        f_time.write("hit time: "+str(hit_tt)+"\n")
                        if hit_response=="hit":
                            hit_counter=hit_counter+1
                    except Exception as err:
                        _logger.debug(f'{projName}__Hit error! - %s:%s' %(type(err).__name__, err))
                        return None
                if hit_counter == len(random_epoch):
                    _logger.debug(f'{projName}__Hit error! - too few combinations to release')

        if list(set(alive))==['False']:
            _logger.debug(f'{projName}__GAN error! - too few combinations to release')
            return None

        try:
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn,userID, projID, projName, fileName, 'finish', 100)
            check_conn.close()
            _vlogger.debug(f'{projName}__syn_progess 100% [Finish].')
            _vlogger.debug(f'{projName}__updateToMysql_status succeed.')
        except Exception as e:
            _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {0}'.format(str(e)))
            return None  
                #tar_col='country_destination'
            # print('tar_col',tar_col)
            # satisfied = acc(directory,df,col_name,tar_col,e)
            # if satisfied == "OK" :
            #     print("Epoch: ",e," ,Satisfy the KPI!!")
            #     _vlogger.debug(f'{projName}__Utility finish')
            #     break
            # if (e == random_epoch[-1]):
            #     print("Sorry you have to re-generate!!")
            #     break

#   print("GAN time: ", GAN_time-initial_time)
    _vlogger.debug(f'{projName}__Finished_GEN')
    _vlogger.debug(f'{projName}__PATH:'+str(directory))
    print("citc____genSyncFile_")
    print("finish time: ",time.time()-initial_time)     
    f_time.close()
    
    print("citc____Mission Complete")

def valid_path(value):
    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", value)or value.isdigit()or '..' in value or '/' in value:
        raise argparse.ArgumentTypeError(f'Invalid path: {value}')
    return value

def valid_filename(value):
    if not re.match("^[a-zA-Z0-9_ .]+$", value)or value.isdigit()or '..' in value or '/' in value:
        raise argparse.ArgumentTypeError(f'Invalid filename: {value}')
    return value

def valid_ID(value):
    if not re.match("^[0-9]+$", value):
        raise argparse.ArgumentTypeError(f'Invalid ID: {value}')
    return value

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-projName", "--projName",type=valid_path, help='projName for make a folder')
    parser.add_argument("-fileName", "--fileName",type=valid_filename, help='The path of dataset')
    parser.add_argument("-colName", "--colName",nargs='+', help='Categorical attribute name')
    parser.add_argument("-select_colNames", "--select_colNames",nargs='+', help='Selected attribute name')
    parser.add_argument("-keyName", "--keyName",nargs='+', help='Key attribute name')
#     parser.add_argument("-tar_col", "--tar_colname", help='Target attribute name')
    parser.add_argument("-transfer", "--transfer", default="True", help='Transfer target attribute to numerical')
    # parser.add_argument("-conti", "--conti_colname", default='all', nargs='+', help='Conti. attribute name')
    parser.add_argument("-gen", "--generation", default="True", help='Synthetic dataset generation')
    parser.add_argument("-sample", "--sample", default="True", help='Sample from GAN')
    parser.add_argument("-projID", "--projID", type=valid_ID,help='projID for mysql')
    parser.add_argument("-userID", "--userID", type=valid_ID,help='update user info to mysql')
    args = vars(parser.parse_args())
    # print(args)
    print ("in __main__")
    main(args)
    