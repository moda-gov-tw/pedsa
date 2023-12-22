#export data
import os
import pandas as pd
from logging_tester import _getLogger
from shutil import copyfile
import ast
import sys

from MyLib.connect_sql import ConnectSQL

def updateToMysql_status(conn,userID,projID, projName, table, step, percentage):
    # update process status to mysql
    condisionSampleData = {
            'project_id': projID,
            'pro_name': projName,
            'file_name': ','.join(table),
            'jobName': "exportData"
        }

    valueSampleData = {
            'jobName': "exportData",
            'project_id': projID,
            'user_id':userID,
            'pro_name': projName,
            'file_name': ','.join(table),
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
    _logger  =_getLogger('error__exportData')
    # verify log
    _vlogger =_getLogger('verify__exportData')
    
    _vlogger.debug('------exportData Start------')

    _vlogger.debug('userID : {}'.format(userID))
    _vlogger.debug('projID : {}'.format(projID))
    _vlogger.debug('projName : {}'.format(projName))
    _vlogger.debug('dataName : {}'.format(dataName))
    #connect MYSQL
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")

    except Exception as e:
        _logger.debug('connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return None
    
    #Initial
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'Initial', 0)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None

    folderForSynthetic = "folderForSynthetic"
 
    project_path = "app/devp/"+folderForSynthetic+"/"+projName+'/'

    synData_path = project_path+"synProcess/synthetic/"
    
    exportData_path = project_path+'output/'
        
    try:
        if not os.path.exists(project_path):
            os.mkdir(project_path)
    except Exception as err:
        _logger.debug("Wrong project name! - %s:%s" %(type(err).__name__, err))

    try:
        if not os.path.exists(exportData_path):
            os.mkdir(exportData_path)
    except Exception as err:
        _logger.debug("Export data path error! - %s:%s" %(type(err).__name__, err))

    _vlogger.debug('Check path')
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'Check path', 20)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None

    p = 80/len(dataName)
    c = 1
    _vlogger.debug('Copy data')
    try:
        #copy syn. data to : APP__/folderForSynthetic/projName/synProcess/synthetic/output/
        for data in dataName:
            copyfile(synData_path+data,exportData_path+data)
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn, userID, projID, projName, dataName, 'copy data : {}'.format(c), 20+p*c)
            check_conn.close()
            c = c+1
    except Exception as err:
        _logger.debug("Export data error! - %s:%s" %(type(err).__name__, err))   

    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'finish', 100)
        check_conn.close()
    except Exception as e:
        _logger.debug('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None 

    _vlogger.debug('------export data complete------')

if __name__ == "__main__":
    #import argparse
    #parser = argparse.ArgumentParser()
    #parser.add_argument("-projName", "--projName", help='projName for output path')
    #parser.add_argument("-dataName", "--dataName", help='output data names')    
    userID = sys.argv[1]
    projID = sys.argv[2]
    projName = sys.argv[3]
    dataName = ast.literal_eval(sys.argv[4])
    #args = vars(parser.parse_args())
    print('+++++++++++++++++++++')
    #print(args)
    print ("in __main__")
    main()
