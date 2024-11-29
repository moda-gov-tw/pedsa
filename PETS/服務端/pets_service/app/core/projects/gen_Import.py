# -*- coding: utf-8 -*-
from fastapi import Body, Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi import FastAPI,APIRouter,Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from celery_worker import celery, gen_import_task

from logging.config import dictConfig
import logging
from app.core.config  import LogConfig
from config.base64convert import getJsonParser

from app.core.utils import _result_wrapper, decode_jwt_token
from app.core.config import LogConfig
from app.database import get_db
from app.core.models import ProjectJoinFunc, Project
from app.core.schemas import Result,ProjectJoinFunct, Projectjoin

import subprocess
from config.loginInfo import getConfig
from config.MyLib.connect_sql import ConnectSQL

import configparser

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

import time
import random
import json
import os
import shlex


gen_Import = APIRouter()

def read_task(task_id: str):
    task_result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }

security = HTTPBearer(description="HTTP Bearer token scheme")
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    checked, decode_info = decode_jwt_token(token)
    if not checked:
        # msg = f"verify token failed: {decode_info}"
        msg = "verify token failed"
        logger.error(f"{msg}")
        raise HTTPException(status_code=401, detail=msg)
    return decode_info

def update_error_msg(conn, privacytype, project_id):
    # Choose the database name based on privacy_type
    if str(privacytype) == 'syn':
        sqldbName = 'SynService'
    elif str(privacytype) == 'dp':
        sqldbName = 'DpService'

    # Prepare the SQL update statement
    update_query = f"""
    UPDATE {sqldbName}.T_ProjectStatus
    SET project_status = 97,
        statusname = '概化錯誤'
    WHERE project_id = '{project_id}'  # Assuming project_id is a string
    """
    # Execute the update
    resultUpdate = conn.doSqlCommand(update_query)
    if resultUpdate['result'] == 1:
        logger.info('update status sucess.')
    else:
        msg = ('update status DataToMysql fail')
        logger.error('update status DataToMysql fail')
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    
def get_projname(conn,project_id, privacytype):
    if privacytype == 'syn':
        sqlStr = f"SELECT project_name FROM SynService.T_Project WHERE project_id = '{project_id}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            project_name = resultSampleData['fetchall'][0].get('project_name')
            if not project_name:
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not find the project: {str(project_name)}"
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return project_name
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

    elif privacytype == 'dp':
        sqlStr = f"SELECT project_name FROM DpService.T_Project WHERE project_id  = '{project_id }'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            project_name = resultSampleData['fetchall'][0].get('project_name')
            if not project_name:
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not find the project: {str(project_name)}"
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return project_name
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

def get_select_col(conn,project_name, privacytype,project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT select_colNames FROM SynService.T_ProjectSample5Data WHERE pro_name = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not select_colNames of the project: {str(project_name)}"
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch select_colNames of project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

    elif privacytype == 'dp':
        sqlStr = f"SELECT select_colNames FROM DpService.T_ProjectSample5Data WHERE pro_name = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not select_colNames of the project: {str(project_name)}"
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch select_colNames of project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)



@gen_Import.post("/gen_import")
def Import_gen(project_id: int, privacy_type: str,db :Session =Depends(get_db)):
    member_id = '1'#decode_info['member_id']
    useraccount = 'admin'#decode_info['sub']    
    # member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    # useraccount = decode_info['sub']
    try:
        # catch = getJsonParser(jsonbase64)
        catch = dict()
        catch["project_id"] = project_id
        logger.info(f"***********jsonbase64 info{catch}*********")
        logger.info(catch)

        try:
            check_conn = ConnectSQL()
            project_name =  get_projname(check_conn,project_id, privacy_type) #string to list
            logger.info('get_project_name ')
            logger.info(project_name)
            check_conn.close()
        except Exception as e:
            msg = 'errTable: get select cols from table fail. {0}'.format(str(e))
            logger.error('errTable: get select cols from table fail. {0}'.format(str(e)))
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

        #get select_col
        try:
            check_conn = ConnectSQL()
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
            select_cols = get_select_col(check_conn,project_name, privacy_type,project_id) #string to list
            logger.info('get select cols ')
            logger.info(select_cols)
            check_conn.close()
        except Exception as e:
            msg = 'errTable: get select cols from table fail. {0}'.format(str(e))
            logger.error(msg)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        
        #HERE must scp data to import path needed
        file_ = '/usr/src/app/app/core/projects/delete_config.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        ip = config.get('delete_config', 'ip')
        port = config.get('delete_config', 'port')
        user = config.get('delete_config', 'user')
        passwd = config.get('delete_config', 'passwd')

        ip = shlex.quote(ip)
        port = shlex.quote(port)
        user = shlex.quote(user)
        passwd = shlex.quote(passwd)

        pets_hadoop_ip = config.get('delete_config', 'pets_hadoop_ip')
        pets_hadoop_ip = shlex.quote(pets_hadoop_ip)
        project_name = shlex.quote(project_name)
        project_gen = project_name+'_'+privacy_type
        project_gen = shlex.quote(project_gen)
        if privacy_type == 'syn':
            folderForSynthetic = config.get('delete_config', 'folderForSynthetic')
            pets_hadoop_import_path = config.get('delete_config', 'pets_hadoop_import_path')
            folderForSynthetic_dir = os.path.join(folderForSynthetic, project_name, '')
            folderForSynthetic_input_dir = os.path.join(folderForSynthetic_dir, 'inputRawdata', '')
            synfile_path_file = os.path.join(folderForSynthetic_input_dir, 'df_preview.csv')
            folderForSynthetic_input_dir = shlex.quote(folderForSynthetic_input_dir)
            remote_command = f"sudo chown -R ubuntu:ubuntu {folderForSynthetic_input_dir}"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            # remote_command = shlex.quote(remote_command)
            cmd = ["sshpass", "-p", passwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-p", "22",
                f"{user}@{ip}",
                remote_command
            ]
            # cmd_str = ' '.join(shlex.quote(arg) for arg in cmd)
            # logger.info(f'{cmd_str}')
            try:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                # print("Command output:"+ result.stdout)
            except subprocess.CalledProcessError as e:
                check_conn = ConnectSQL()
                update_error_msg(check_conn, privacy_type,project_id)
                check_conn.close()
                # print("Command failed with exit code"+ e.returncode)
                # print("Error output:"+ e.stderr)
                msg = str(e.stderr)
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)

            # runcode = os.system(cmd)
            # logger.info(f'==============chmod_folder===={cmd}==========')
            pets_hadoop_import_path = shlex.quote(pets_hadoop_import_path)
            project_gen = shlex.quote(project_gen)
            remote_command = f"mkdir {pets_hadoop_import_path}{project_gen}"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            # remote_command = shlex.quote(remote_command)
            cmd = [
                'sshpass', '-p', passwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-p", "22",
                f"{user}@{ip}",
                remote_command
            ]
            try:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                print("Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                if "File exists" in e.stderr:
                    print("Directory already exists, continuing without error.")
                else:
                    check_conn = ConnectSQL()
                    update_error_msg(check_conn, privacy_type,project_id)
                    check_conn.close()
                    print("Command failed with exit code", e.returncode)
                    print("Error output:", e.stderr)
                    msg = e.stderr
                    logger.error(msg)
                    result = Result(msg=msg, status=False)
                    return _result_wrapper(result, status_code=400)
            # runcode = os.system(cmd)
            # logger.info(f'==============mkdir_remote_folder===={cmd}==========')
            pets_hadoop_import_path = shlex.quote(pets_hadoop_import_path)
            project_gen = shlex.quote(project_gen)
            destination_file = f"{pets_hadoop_import_path}{project_gen}/{project_gen}.csv"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            synfile_path_file = shlex.quote(synfile_path_file)
            pets_hadoop_ip = shlex.quote(pets_hadoop_ip)
            destination_file = shlex.quote(destination_file)
            scp_command = [
                'sshpass', '-p', passwd,
                'ssh', '-o', 'StrictHostKeyChecking=no', '-p', '22',
                f'{user}@{ip}',
                'sshpass', '-p', passwd,
                'scp', '-o', 'StrictHostKeyChecking=no', '-P', '22',
                synfile_path_file,
                f'{user}@{ip}:{destination_file}'
            ]      
            logger.info('Executing command: %s', ' '.join(scp_command))
            try:
                result = subprocess.run(scp_command, check=True, text=True, capture_output=True)
                print("Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                check_conn = ConnectSQL()
                update_error_msg(check_conn, privacy_type,project_id)
                check_conn.close()
                print("Command failed with exit code", e.returncode)
                print("Error output:", e.stderr)
                msg = e.stderr
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            # destination_file = pets_hadoop_import_path+project_gen+'/'+project_gen+'.csv'
            # runcode = os.system(cmd)
            logger.info(f'==============scp file to remote_folder===={scp_command }==========')
            # Step 2: Set permissions
            pets_hadoop_import_path = shlex.quote(pets_hadoop_import_path)
            remote_command = f"chmod -R 755 {pets_hadoop_import_path}"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            # remote_command = shlex.quote(remote_command)
            cmd = [
                'sshpass', '-p', passwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-p", "22",
                f"{user}@{ip}",
                remote_command
            ]        
            try:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                print("Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                check_conn = ConnectSQL()
                update_error_msg(check_conn, privacy_type,project_id)
                check_conn.close()
                print("Command failed with exit code", e.returncode)
                print("Error output:", e.stderr)    
                msg = e.stderr
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            # runcode = os.system(cmd)
            logger.info(f'==============scp file to remote_folder===={cmd}==========')

        elif privacy_type == 'dp':
            dp_folderForSynthetic = config.get('delete_config', 'dp_folderForSynthetic')
            pets_hadoop_import_path = config.get('delete_config', 'pets_hadoop_import_path')
            dp_folderForSynthetic_dir = os.path.join(dp_folderForSynthetic, project_name, '')
            dp_folderForSynthetic_input_dir = os.path.join(dp_folderForSynthetic_dir, 'inputRawdata', '')
            synfile_path_file = os.path.join(dp_folderForSynthetic_input_dir, 'df_preview.csv')

            dp_folderForSynthetic_input_dir = shlex.quote(dp_folderForSynthetic_input_dir)
            remote_command = f"sudo chown -R ubuntu:ubuntu {dp_folderForSynthetic_input_dir}"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            # remote_command = shlex.quote(remote_command)
            cmd = [
                'sshpass', '-p', passwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-p", "22",
                f"{user}@{ip}",
                remote_command
            ]
            try:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                print("Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                check_conn = ConnectSQL()
                update_error_msg(check_conn, privacy_type,project_id)
                check_conn.close()
                print("Command failed with exit code", e.returncode)
                print("Error output:", e.stderr)
                msg = e.stderr
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            # runcode = os.system(cmd)
            logger.info(f'==============chmod_folder===={cmd}==========')
            pets_hadoop_import_path = shlex.quote(pets_hadoop_import_path)
            project_gen = shlex.quote(project_gen)
            remote_directory = f"{pets_hadoop_import_path}{project_gen}"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            remote_directory = shlex.quote(remote_directory)
            cmd = [
                'sshpass', '-p', passwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-p", "22",
                f"{user}@{ip}",
                f"mkdir -p {remote_directory}"  # 使用 `-p` 參數來避免錯誤
            ]
            try:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                print("Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                if "File exists" in e.stderr:
                    print("Directory already exists, continuing without error.")
                else:
                    check_conn = ConnectSQL()
                    update_error_msg(check_conn, privacy_type,project_id)
                    check_conn.close()
                    print("Command failed with exit code", e.returncode)
                    print("Error output:", e.stderr)
                    msg = e.stderr
                    logger.error(msg)
                    result = Result(msg=msg, status=False)
                    return _result_wrapper(result, status_code=400)
            # runcode = os.system(cmd)
            logger.info(f'==============mkdir_remote_folder===={cmd}==========')
            pets_hadoop_import_path = shlex.quote(pets_hadoop_import_path)
            project_gen = shlex.quote(project_gen)
            destination_file = f"{pets_hadoop_import_path}{project_gen}/{project_gen}.csv"

            passwd = shlex.quote(passwd)
            user = shlex.quote(user)
            ip = shlex.quote(ip)
            synfile_path_file = shlex.quote(synfile_path_file)
            pets_hadoop_ip = shlex.quote(pets_hadoop_ip)
            destination_file = shlex.quote(destination_file)
            scp_command = [
                'sshpass', '-p', passwd,
                'ssh', '-o', 'StrictHostKeyChecking=no', '-p', '22',
                f'{user}@{ip}',
                'sshpass', '-p', passwd,
                'scp', '-o', 'StrictHostKeyChecking=no', '-P', '22',
                synfile_path_file,
                f'{user}@{ip}:{destination_file}'
            ]
            try:
                result = subprocess.run(scp_command, check=True, text=True, capture_output=True)
                print("SCP Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                check_conn = ConnectSQL()
                update_error_msg(check_conn, privacy_type,project_id)
                check_conn.close()
                print("SCP Command failed with exit code", e.returncode)
                print("Error output:", e.stderr)
                msg = e.stderr
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            # destination_file = pets_hadoop_import_path+project_gen+'/'+project_gen+'.csv'
            # runcode = os.system(cmd)
            logger.info(f'==============scp file to remote_folder===={scp_command }==========')

            remote_command = f"chmod -R 755 {pets_hadoop_import_path}"
            cmd = [
                'sshpass', '-p', passwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-p", "22",
                f"{user}@{ip}",
                remote_command
            ]
            try:
                result = subprocess.run(cmd, check=True, text=True, capture_output=True)
                print("Command output:", result.stdout)
            except subprocess.CalledProcessError as e:
                check_conn = ConnectSQL()
                update_error_msg(check_conn, privacy_type,project_id)
                check_conn.close()
                print("Command failed with exit code", e.returncode)
                print("Error output:", e.stderr)
                msg = e.stderr
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            # Step 2: Set permissions
            # runcode = os.system(cmd)
            logger.info(f'==============scp file to remote_folder===={cmd}==========')



        task = gen_import_task.delay(project_id, project_name,member_id,useraccount,privacy_type,select_cols)
        task_id = task.id
        time.sleep(random.randint(5, 10))
        if celery.AsyncResult(task_id).status == "SUCCESS":
            task_result = read_task(task_id)
            return {
                "task_id": task_result["task_id"],
                "task_status": task_result["task_status"],
                "status": 0 ,
                "msg": "",
                "dataInfo": task_result["task_result"],
            }
    except Exception as e:
        return {
            "task_status": f"ERROR: {e}",
        }