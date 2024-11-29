#export data
import os
import pandas as pd
from logging_tester import _getLogger
from shutil import copyfile
import ast
import sys
import re
from MyLib.connect_sql import ConnectSQL

import shlex

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
        _vlogger.debug(f"{projName}: Update mysql succeed.")
        return None
    else:
        _logger.debug(f'{projName}__errTable: insertSampleDataToMysql fail.')
        return None

def main():
    global  _logger,_vlogger
    # debug log
    _logger  =_getLogger('error__exportData')
    # verify log
    _vlogger =_getLogger('verify__exportData')
    
    _vlogger.debug('------exportData Start------')


    if not userID.isdigit():
        _logger.debug(f'{projName}__errTable:errTable: Invalid userID format')
        print(f"{projName}__errTable:Invalid userID format")
        return 'FAIL'

    if not projID.isdigit():
        print(f"{projName}__errTable:Invalid projID format")
        _logger.debug(f'{projName}__errTable: Invalid projID format')
        return 'FAIL'

    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName)or projName.isdigit()or '..' in projName or '/' in projName:
        _logger.debug(f'{projName}__errTable:errTable: Invalid projName format')
        print(f"{projName}__errTable:Invalid projName format")
        return 'FAIL'

    try:
        if not isinstance(dataName, list):
            _logger.debug(f'{projName}__errTable: Input should be a list.')
            print("Input should be a list.")
            return 'FAIL'
    except (ValueError, SyntaxError) as e:
        _logger.debug(f'{projName}__errTable: Invalid input')

    _vlogger.debug('userID : {}'.format(userID))
    _vlogger.debug('projID : {}'.format(projID))
    _vlogger.debug('projName : {}'.format(projName))
    _vlogger.debug('dataName : {}'.format(dataName))
    #connect MYSQL
    try:
        check_conn = ConnectSQL()
        _vlogger.debug("Connect SQL")

    except Exception as e:
        _logger.debug(f'{projName}__errTable: connectToMysql fail: - {type(e)}:{str(e)}')
        return None
    
    #Initial
    try:
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'Initial', 0)
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {str(e)}')
        return None

    folderForSynthetic = "folderForSynthetic"
 
    # Construct paths safely
    project_path = os.path.join("app", "devp", folderForSynthetic, projName)+ "/"
    synData_path = os.path.join(project_path, "synProcess", "synthetic")+ "/"
    exportData_path = os.path.join(project_path, "output")+ "/"

    # Canonicalize the paths to avoid directory traversal
    project_path = os.path.realpath(project_path)
    exportData_path = os.path.realpath(exportData_path)

    # Ensure the paths are within the expected base directory
    if not project_path.startswith(os.path.realpath("app/devp")):
        _logger.debug(f'{projName}__errTable: Invalid project path')
        
    try:
        if not os.path.exists(project_path):
            os.mkdir(project_path)
    except Exception as err:
        _logger.debug(f"{projName}__errTable: Wrong project name! - {type(err)}:{str(err)}")

    try:
        if not os.path.exists(exportData_path):
            os.mkdir(exportData_path)
    except Exception as err:
        _logger.debug(f"{projName}__errTable: Export data path error! - {type(err)}:{str(err)}")

    _vlogger.debug('Check path')
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'Check path', 20)
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable: updateToMysql_status fail. {str(e)}')
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
        _logger.debug(f"{projName}__errTable: Export data error! - {type(err).__name__}:{str(err)}")   

    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'finish', 100)
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable:  updateToMysql_status fail. {str(e)}')
        return None 

    _vlogger.debug('------export data complete------')

if __name__ == "__main__":
    userID = sys.argv[1]
    projID = sys.argv[2]
    projName = sys.argv[3]
    projName = shlex.quote(projName)
    dataName = ast.literal_eval(sys.argv[4])

    if not userID.isdigit():
        print(f"{projName}__errTable:Invalid userID format")
        raise ValueError(f"{projName}__errTable: Invalid userID format")

    if not projID.isdigit():
        print(f'{projName}__errTable: Invalid projID format')
        raise ValueError(f'{projName}__errTable: Invalid projID format')

    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName)or projName.isdigit()or '..' in projName or '/' in projName:
        print(f"{projName}__errTable:Invalid projName format")
        raise ValueError(f"{projName}__errTable:Invalid projName format")

    try:
        if not isinstance(dataName, list):
            print("Input should be a list.")
            raise ValueError(f'{projName}__errTable: Input should be a list.')
    except (ValueError, SyntaxError) as e:
        raise ValueError('{projName}__errTable: Invalid input')

    print('+++++++++++++++++++++')
    print ("in __main__")
    main()
