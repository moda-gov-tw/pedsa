#export data
import os
import pandas as pd
from logging_tester import _getLogger
from shutil import copyfile
import ast
import sys, re

from MyLib.connect_sql import ConnectSQL
import time
import configparser 
import os
import subprocess
from MyLib.loginInfo import getConfig

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

    resultSampleData = conn.updateValueMysql('DpService',#'DeIdService',
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
    project_path = os.path.realpath(project_path)+ "/"
    exportData_path = os.path.realpath(exportData_path)+ "/"

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
            copyfile(synData_path+data,exportData_path+'syn_'+projName+'.csv')
            check_conn = ConnectSQL()
            updateToMysql_status(check_conn, userID, projID, projName, dataName, 'copy data : {}'.format(c), 20+p*c)
            check_conn.close()
            c = c+1
    except Exception as err:
        _logger.debug(f"{projName}__errTable: Export data error! - %s:%s" %(type(err).__name__, err))

        #install sshpass
    runcode = os.system('apt install sshpass')
    ###scp from PET-hadooop: 將本地端的檔案複製到遠端
    try:
        file_ = 'app/devp/config/Hadoop_information.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        ip = config.get('Hadoop_information', 'ip')
        to_path = config.get('Hadoop_information', 'to_path')

        hdfsInfo = getConfig().getLoginHdfs()
        user_ = str(hdfsInfo['user'])
        password_ = str(hdfsInfo['password'])
        #need to rm dest. path folder
        #0911修改
        cmd_rm = [
            'sshpass', '-p', password_,
            'ssh', '-o', 'StrictHostKeyChecking=no', '-p', '22',
            f'{user_}@{ip}', 'rm', '-r', shlex.quote(f'{to_path}{projName}/')
        ]
        # 使用 subprocess.run 來執行命令
        result = subprocess.run(cmd_rm)
        time.sleep(10)
        ip="168.17.8.252"
        # 對變量進行 shlex.quote 處理
        quoted_project_path = shlex.quote(project_path + 'output')
        quoted_to_path = shlex.quote(to_path)
        quoted_proj_name = shlex.quote(projName)
        quoted_user = shlex.quote(user_)
        quoted_ip = shlex.quote(ip)

        # 構建命令
        #0911修改
        scp_command = [
            'sshpass', '-p', shlex.quote(password_),
            'scp', '-o', 'StrictHostKeyChecking=no', '-P', '22', '-r',
            quoted_project_path,
            f'{quoted_user}@{quoted_ip}:{quoted_to_path}{quoted_proj_name}'
        ]
        # _vlogger.debug(f'*****************{projName}__t{scp_command}')
        proc = subprocess.run(scp_command,check=True)
        if proc.returncode != 0:
            _logger.debug(f"{projName}__errTable:cmd failed")




    except Exception as e:
        _logger.debug(f'{projName}__to PETs hadoop error :  {str(e)}')

    try:
        check_conn = ConnectSQL()
        updateToMysql_status(check_conn, userID, projID, projName, dataName, 'finish', 100)
        check_conn.close()
    except Exception as e:
        _logger.debug(f'{projName}__errTable:  updateToMysql_status fail. {str(e)}')
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
    #args = vars(parser.parse_args())
    print('+++++++++++++++++++++')
    #print(args)
    print ("in __main__")
    main()
