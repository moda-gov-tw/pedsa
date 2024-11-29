# -*- coding: utf-8 -*-
from fastapi import Body, Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi import FastAPI,APIRouter,Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

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

from celery_worker import celery, gen_import_task, gen_getGenTbl_task
from celery_worker import gen_export_task

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

import subprocess
import time
import random
import json
import os
import requests
from app.core.projects.get_subsysbase64 import syn_base64 #call syn api
from app.core.projects.get_subdpbase64 import dp_base64 #call dp api
import asyncio
from fastapi import BackgroundTasks
import uuid

gen_Integration = APIRouter()

task_status = {}

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
                logger.error("fetch project_name fail")
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not find the project: {str(project_name)}"
                logger.error(msg)
                return None
            else:
                return project_name
        else:
            logger.error("fetch project_name fail")
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            return None

    elif privacytype == 'dp':
        sqlStr = f"SELECT project_name FROM DpService.T_Project WHERE project_id  = '{project_id }'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            project_name = resultSampleData['fetchall'][0].get('project_name')
            if not project_name:
                logger.error("fetch project_name fail")
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not find the project: {str(project_name)}"
                logger.error(msg)
                return None
            else:
                return project_name
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            return None


def check_status(project_id, privacy_type, expected_statuses):
    """
    檢查 T_ProjectStatus 中對應 project_id 和 privacy_type 的狀態
    如果狀態是 41 則返回 True，表示成功；如果狀態是 97 則返回 False，表示錯誤。
    """
    if privacy_type == 'syn':
        sqlStr = f"SELECT project_status FROM SynService.T_ProjectStatus WHERE project_id = '{project_id}'"
    
    elif privacy_type == 'dp':
        sqlStr = f"SELECT project_status FROM DpService.T_ProjectStatus WHERE project_id = '{project_id}'"
    try:
        check_conn = ConnectSQL()
        resultSampleData = check_conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            project_status = resultSampleData['fetchall'][0].get('project_status')
            if not project_status:
                check_conn.close()
                return None
            elif project_status in expected_statuses:
                check_conn.close()
                return project_status
            else:
                check_conn.close()
                return None
        else:
            logger.error('fetch DataToMysql fail')
            check_conn.close()
            return None
    except Exception as e:
            logger.error('errTable: get  status from table fail. {0}'.format(str(e)))
            return None

async def run_with_timeout(project_id, privacy_type, expected_statuses, timeout=300, check_interval=5):
    """
    設定超時機制來檢查狀態更新
    - timeout: 超過此時間（秒）後仍未更新狀態，則跳出迴圈並報錯
    - check_interval: 每次檢查狀態的間隔時間（秒）
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = check_status(project_id, privacy_type, expected_statuses)
        if status == expected_statuses[0]:
            logger.info("成功，狀態為 OK，可以進行下一個 API")
            return True
        elif status == expected_statuses[1]:
            logger.info("出錯，狀態為不OK，不進行下一個 API")
            return False
        logger.info(f"等待狀態更新，當前狀態：{status}，重新檢查中...")
        time.sleep(check_interval)
    logger.error("超時，狀態未更新，停止操作")
    return False



def get_select_col(conn,project_name, privacytype,project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT select_colNames FROM SynService.T_ProjectSample5Data WHERE pro_name = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            if not select_colNames:
                logger.error("fetch select_colNames fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

    elif privacytype == 'dp':
        sqlStr = f"SELECT select_colNames FROM DpService.T_ProjectSample5Data WHERE pro_name = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            if not select_colNames:
                logger.error("fetch select_colNames fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

async def run_command(cmd, privacy_type,project_id):
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        check_conn = ConnectSQL()
        update_error_msg(check_conn, privacy_type,project_id)
        check_conn.close()
        raise Exception(f"Command failed with exit code {process.returncode}: {stderr.decode()}")
    return stdout.decode()

async def import_api(project_id, privacy_type, member_id, useraccount,db):
    try:
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
            logger.error('errTable: get projname from table fail. {0}'.format(str(e)))
            return None

            #get select_col
        try:
            check_conn = ConnectSQL()
            #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
            select_cols = get_select_col(check_conn,project_name, privacy_type,project_id) #string to list
            logger.info('get select cols ')
            logger.info(select_cols)
            check_conn.close()
        except Exception as e:
            logger.error('errTable: get select cols from table fail. {0}'.format(str(e)))
            return None


        
        file_ = '/usr/src/app/app/core/projects/delete_config.txt'
        config = configparser.ConfigParser()
        config.read(file_)
        ip = config.get('delete_config', 'ip')
        port = config.get('delete_config', 'port')
        user = config.get('delete_config', 'user')
        passwd = config.get('delete_config', 'passwd')
        
        #icl, 20241025
        passwd_= passwd.strip()

        pets_hadoop_ip = ip #config.get('delete_config', 'pets_hadoop_ip')
        project_gen = project_name + '_' + privacy_type

        if privacy_type == 'syn':
            folderForSynthetic = config.get('delete_config', 'folderForSynthetic')
            pets_hadoop_import_path = config.get('delete_config', 'pets_hadoop_import_path')
            folderForSynthetic_dir = os.path.join(folderForSynthetic, project_name, '')
            folderForSynthetic_input_dir = os.path.join(folderForSynthetic_dir, 'inputRawdata', '')
            synfile_path_file = os.path.join(folderForSynthetic_input_dir, 'df_preview.csv')

            #icl, 20241025
            #remote_command = f"sudo chown -R ubuntu:ubuntu {folderForSynthetic_input_dir}"
            remote_command = f"sudo chown -R 1000:1000 {folderForSynthetic_input_dir}"
            #icl, 20241025
            if(len(passwd_) == 0):
                cmd = [
                    "ssh",
                    "-i", "/id_rsa_itri-pedsa.pem",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    remote_command
                    ]

            else:
                cmd = [
                    'sshpass', '-p', passwd,
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    remote_command
                    ]
            
            await run_command(cmd, privacy_type,project_id)


            remote_command = f"mkdir -p {pets_hadoop_import_path}{project_gen}"
            #icl, 20241025
            if(len(passwd_) == 0):
                cmd = [
                    "ssh",
                    "-i", "/id_rsa_itri-pedsa.pem",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    remote_command
                    ]

            else:
                cmd = [
                    'sshpass', '-p', passwd,
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    remote_command
                    ]
            #cmd = [
            #    'sshpass', '-p', passwd,
            #    "ssh",
            #    "-o", "StrictHostKeyChecking=no",
            #    "-p", "22",
            #    f"{user}@{ip}",
            #    remote_command
            #]
            await run_command(cmd, privacy_type,project_id)

            destination_file = f"{pets_hadoop_import_path}{project_gen}/{project_gen}.csv"
            logger.info(f"Checking file path: {synfile_path_file}")
            logger.info(f"File exists: {os.path.exists(synfile_path_file)}")
            if(len(passwd_) == 0):
                scp_command = [
                    'ssh',  '-i','/id_rsa_itri-pedsa.pem','-o', 'StrictHostKeyChecking=no', '-p', '22',
                    f'{user}@{ip}',
                    'scp',  '-i','/id_rsa_itri-pedsa.pem','-o', 'StrictHostKeyChecking=no', '-P', '22',
                    synfile_path_file,
                    f'{user}@{pets_hadoop_ip}:{destination_file}'
                ]
            else:
                scp_command = [
                    'sshpass', '-p', passwd,
                    'ssh', '-o', 'StrictHostKeyChecking=no', '-p', '22',
                    f'{user}@{ip}',
                    'sshpass', '-p', passwd,
                    'scp', '-o', 'StrictHostKeyChecking=no', '-P', '22',
                    synfile_path_file,
                    f'{user}@{pets_hadoop_ip}:{destination_file}'
                ]
            logger.info('Executing command: %s', ' '.join(scp_command))
            await run_command(scp_command, privacy_type,project_id)

            remote_command = f"chmod -R 755 {pets_hadoop_import_path}"

            #icl, 20241025
            if(len(passwd_) == 0):
                cmd = [
                    "ssh",
                    "-i", "/id_rsa_itri-pedsa.pem",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    remote_command
                ]
            else:
                cmd = [
                    'sshpass', '-p', passwd,
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    remote_command
                ]
            await run_command(cmd, privacy_type,project_id)

        elif privacy_type == 'dp':
            dp_folderForSynthetic = config.get('delete_config', 'dp_folderForSynthetic')
            pets_hadoop_import_path = config.get('delete_config', 'pets_hadoop_import_path')
            dp_folderForSynthetic_dir = os.path.join(dp_folderForSynthetic, project_name, '')
            dp_folderForSynthetic_input_dir = os.path.join(dp_folderForSynthetic_dir, 'inputRawdata', '')
            synfile_path_file = os.path.join(dp_folderForSynthetic_input_dir, 'df_preview.csv')

            #icl, 20241025
            # remote_command = f"sudo chown -R ubuntu:ubuntu {dp_folderForSynthetic_input_dir}"
            # to
            # remote_command = f"sudo chown -R 1000:1000 {dp_folderForSynthetic_input_dir}"
            if(len(passwd_) == 0):
                cmd = [
                    "ssh",
                    "-i", "/id_rsa_itri-pedsa.pem",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    f"sudo chown -R 1000:1000 {dp_folderForSynthetic_input_dir}"
                ]
            else:
                cmd = [
                    'sshpass', '-p', passwd,
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    f"sudo chown -R 1000:1000 {dp_folderForSynthetic_input_dir}"
                ]
            await run_command(cmd, privacy_type,project_id)

            if(len(passwd_) == 0):
                cmd = [
                    "ssh",
                    "-i", "/id_rsa_itri-pedsa.pem",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    f"mkdir -p {pets_hadoop_import_path}{project_gen}"
                ]
            else:
                cmd = [
                    'sshpass', '-p', passwd,
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    f"mkdir -p {pets_hadoop_import_path}{project_gen}"
                ]
            await run_command(cmd, privacy_type,project_id)

            destination_file = f"{pets_hadoop_import_path}{project_gen}/{project_gen}.csv"

            if(len(passwd_) == 0):
                scp_command = [
                    'ssh', '-i','/id_rsa_itri-pedsa.pem','-o', 'StrictHostKeyChecking=no', '-p', '22',
                    f'{user}@{ip}',
                    'scp', '-i','/id_rsa_itri-pedsa.pem','-o', 'StrictHostKeyChecking=no', '-P', '22',
                    synfile_path_file,
                    f'{user}@{pets_hadoop_ip}:{destination_file}'
                ]
            else:
                scp_command = [
                    'sshpass', '-p', passwd,
                    'ssh', '-o', 'StrictHostKeyChecking=no', '-p', '22',
                    f'{user}@{ip}',
                    'sshpass', '-p', passwd,
                    'scp', '-o', 'StrictHostKeyChecking=no', '-P', '22',
                    synfile_path_file,
                    f'{user}@{pets_hadoop_ip}:{destination_file}'
                ]                
            await run_command(scp_command, privacy_type,project_id)

            if(len(passwd_) == 0):
                cmd = [
                    "ssh",
                    "-i", "/id_rsa_itri-pedsa.pem",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    f"chmod -R 755 {pets_hadoop_import_path}"
                ]               
            else:
                cmd = [
                    'sshpass', '-p', passwd,
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    "-p", "22",
                    f"{user}@{ip}",
                    f"chmod -R 755 {pets_hadoop_import_path}"
                ]
            await run_command(cmd, privacy_type,project_id)

        task = gen_import_task.delay(project_id, project_name, member_id, useraccount, privacy_type, select_cols)
        logger.info(f"IMPORT Task started with id: {task.id}")
        task_id = task.id
        await asyncio.sleep(30)
        task_status = celery.AsyncResult(task.id).status
        logger.info(f"Task status: {task_status}")
        if task_status == "SUCCESS":
            task_result = read_task(task_id)
            return {
                "task_id": task_result["task_id"],
                "task_status": task_result["task_status"],
                "status": "success",
                "msg": "",
                "dataInfo": task_result["task_result"],
            }
        elif task_status == 'FAILURE':
            error_message = str(celery.AsyncResult(task.id))
            logger.error(f"Celery task failed with error: {error_message}")
        else:
            logger.error(f"Celery task status: {task_status}")
            logger.error(f"Celery task did not succeed.")
            return {
                "status": "error",
                "message": "Celery task did not succeed."
            }
    except Exception as e:
        logger.error(f"Error in getGenTbl_gen_api: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
        }

class GetGenJsonRep:
    def __init__(self):
        # self.log = logging.getLogger("GetGenJsonRep")
        logger.setLevel(logging.INFO)  # 設置日誌級別為 INFO

    def get_api_select_name(self, select_value):
        get_qi_select_name = ""
        api_name = ""
        # switch case 轉換成 if-elif
        if select_value in ["請選擇", "0"]:
            get_qi_select_name = "請選擇"
        elif select_value == "1":
            get_qi_select_name = "地址"
            api_name = "getGenAddress"
        elif select_value == "2":
            get_qi_select_name = "日期"
            api_name = "getGenDate"
        elif select_value == "3":
            get_qi_select_name = "擷取字串"
            api_name = "getGenString"
        elif select_value in ["4", "5"]:
            get_qi_select_name = "數字大區間" if select_value == "4" else "數字小區間"
            api_name = "getGenNumLevel"
        elif select_value == "6":
            get_qi_select_name = "數字區間含上下界"
            api_name = "getGenNumLevelMinMax"
        elif select_value == "7":
            get_qi_select_name = "不處理"
        
        logger.info(f"概化設定值 : {select_value}")
        logger.info(f"概化設定內容 : {get_qi_select_name}")
        logger.info(f"概化設定API : {api_name}")
        
        return api_name

    def get_qi_select_name_level2(self, select_value, select_level2):
        get_qi_select_name = ""
        api_level = ""
        
        if select_value in ["請選擇", "0"]:
            get_qi_select_name = "請選擇"
        elif select_value == "1":
            get_qi_select_name = "地址"
            if select_level2 == "直轄市、縣、市":
                api_level = "1"
            elif select_level2 == "鄉、鎮、縣轄市、區":
                api_level = "2"
            elif select_level2 == "村、里":
                api_level = "3"
            elif select_level2 == "大道、路、街":
                api_level = "4"
            elif select_level2 == "段":
                api_level = "5"
            elif select_level2 == "巷":
                api_level = "6"
            elif select_level2 == "衖":
                api_level = "7"
            elif select_level2 == "號":
                api_level = "8"
        elif select_value == "2":
            get_qi_select_name = "日期"
            if select_level2 == "西元-YYYY":
                api_level = "Y"
            elif select_level2 == "西元-YYYY-MM":
                api_level = "Mo"
            elif select_level2 == "西元-YYYY-MM-DD":
                api_level = "D"
            elif select_level2 == "民國年":
                api_level = "Y"
            elif select_level2 == "民國年+月":
                api_level = "Mo"
        elif select_value == "3":
            get_qi_select_name = "擷取字串"
            api_level = f"0_{select_level2}"
        elif select_value == "4":
            get_qi_select_name = "數字大區間"
            if select_level2 == "十":
                api_level = "10"
            elif select_level2 == "百":
                api_level = "100"
            elif select_level2 == "千":
                api_level = "1000"
            elif select_level2 == "萬":
                api_level = "10000"
            elif select_level2 == "十萬":
                api_level = "100000"
            elif select_level2 == "百萬":
                api_level = "1000000"
            elif select_level2 == "千萬":
                api_level = "10000000"
            elif select_level2 == "億":
                api_level = "100000000"
            elif select_level2 == "兆":
                api_level = "1000000000000"
        elif select_value == "5":
            get_qi_select_name = "數字小區間"
            api_level = select_level2
        elif select_value == "6":
            get_qi_select_name = "數字區間含上下界"
            api_level = select_level2.replace('#', ',')
        elif select_value == "7":
            get_qi_select_name = ""
        
        logger.info(f"概化設定內容第一層 : {get_qi_select_name}")
        logger.info(f"概化設定內容第二層 : {select_level2}")
        logger.info(f"概化設定API內容第二層 : {api_level}")

        return api_level

    def get_gen_json_api(self, col_en, col_cht, tb, tbname, qi_value, gen_qi_value):
        gen_json = ""
        
        try:
            logger.info("GetGenJsonAPI")
            logger.info(f"col_en : {col_en}")
            logger.info(f"col_cht : {col_cht}")
            logger.info(f"col_cht : {qi_value}")
            logger.info(f"gen_qi_value : {gen_qi_value}")
            
            col_en_array = col_en.split(',')
            col_cht_array = col_cht.split(',')
            col_qi_array = qi_value.split(',')
            col_gentb_arr = gen_qi_value.split('|')
            
            for col_gentb in col_gentb_arr:
                if col_gentb:
                    col_gen_array = col_gentb.split('*')
                    tbnm = col_gen_array[0]
                    col_gen_level1 = col_gen_array[1]
                    col_gen_level2 = col_gen_array[2]
                    
                    logger.info(f"tbname : {tbnm}")
                    
                    gen_level1 = col_gen_level1.split(',')
                    gen_level2 = col_gen_level2.split(',')
                    
                    final_gen_json_col = ""
                    
                    for i, col_cht_item in enumerate(col_cht_array):
                        for x, col_qi_item in enumerate(col_qi_array):
                            qi_item_array = col_qi_item.split('-')
                            
                            if col_cht_item == qi_item_array[0]:
                                if gen_level1[x] not in ["請選擇", "不處理"]:
                                    apiname = self.get_api_select_name(gen_level1[x])
                                    user_rule = self.get_qi_select_name_level2(gen_level1[x], gen_level2[x])
                                    coltb = f"col_{i + 1}"
                                    genjsoncol = f"\"{coltb}\":{{\"colName\":\"{col_en_array[i]}\",\"apiName\":\"{apiname}\",\"userRule\":\"{user_rule}\"}},"
                                    final_gen_json_col += genjsoncol
                    
                    final_gen_json_col = final_gen_json_col[:-1]  # 移除最後一個逗號
                    new_gen_json_tb = f"\"{tb}\":{{\"tblName\":\"{tbname}\",\"col_en\":\"{col_en}\",\"colInfo\":{{{final_gen_json_col}}}}}"
                    gen_json = f"{{{new_gen_json_tb}}}" #new_gen_json_tb
                    
                    logger.info(f"GetGenJsonAPI return Json Str : {gen_json}")
        
        except Exception as msg:
            logger.error(f"{msg}")
        
        return gen_json
    
def get_procolen(conn, gen_project_name,privacytype, project_id ):
    if privacytype == 'syn':
        sqlStr = f"SELECT pro_col_en FROM SynService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_en')
            if not select_colNames:
                logger.error("fetch pro_col_en fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")
    elif privacytype == 'dp':
        sqlStr = f"SELECT pro_col_en FROM DpService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_en')
            if not select_colNames:
                logger.error("fetch pro_col_en fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

def get_procolcht(conn, gen_project_name,privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT pro_col_cht FROM  SynService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_cht')
            if not select_colNames:
                logger.error("fetch pro_col_cht fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")
    elif privacytype == 'dp':
        sqlStr = f"SELECT pro_col_cht FROM  DpService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_cht')
            if not select_colNames:
                logger.error("fetch pro_col_cht fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

def get_qisetting(conn,project_name, privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT gen_qi_settingvalue FROM SynService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('gen_qi_settingvalue')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                logger.error("fetch gen_qi_settingvalue fail")
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")
    elif privacytype == 'dp':
        sqlStr = f"SELECT gen_qi_settingvalue FROM DpService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('gen_qi_settingvalue')
            if not select_colNames:
                logger.error("fetch gen_qi_settingvalue fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

def get_qicol(conn,project_name, privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT qi_col FROM SynService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('qi_col')
            if not select_colNames:
                logger.error("fetch qi_col fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")
    elif privacytype == 'dp':
        sqlStr = f"SELECT qi_col FROM DpService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('qi_col')
            if not select_colNames:
                logger.error("fetch qi_col fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

def get_pro_tb(conn,project_name, privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT pro_tb FROM SynService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_tb')
            if not select_colNames:
                logger.error("fetch pro_tb fail")
                update_error_msg(conn, privacytype, project_id)
            else:
                return select_colNames#.split(',')
        else:
            logger.error("fetch pro_tb fail")
            update_error_msg(conn, privacytype, project_id)
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")
    elif privacytype == 'dp':
        sqlStr = f"SELECT pro_tb FROM DpService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_tb')
            if not select_colNames:
                logger.error("fetch pro_tb fail")
                update_error_msg(conn, privacytype, project_id)
                return None
            else:
                return select_colNames#.split(',')
        else:
            logger.error("fetch pro_tb fail")
            update_error_msg(conn, privacytype, project_id)            
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

async def getGenTbl_gen_api(project_id, privacy_type, member_id, useraccount,db):
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
            logger.error('errTable: get projname from table fail. {0}'.format(str(e)))
            return None
        # 去DB找相關的資訊: genDictEncode: str,doMinMaxEncode: str
        #連線到SYN DB拿qi-col
        try:
            check_conn = ConnectSQL()
            gen_qi_col = get_qicol(check_conn, project_name, privacy_type, project_id)
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))
        #連線到SYN DB拿概化規則
        try:
            check_conn = ConnectSQL()
            gen_qi_settingvalue = get_qisetting(check_conn, project_name, privacy_type, project_id)
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))

        #連線到DeidDB拿pro_col_en欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name #+'_'+privacy_type
            pro_col_en = get_procolen(check_conn, project_gen,privacy_type,project_id) #c_7070_0,c_7070_1,c_7070_2,c_7070_3,c_7070_4,c_7070_5,c_7070_6
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))

        #連線到DeidDB拿pro_col_cht欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name #+'_'+privacy_type
            pro_col_cht = get_procolcht(check_conn, project_gen,privacy_type,project_id) #columns real name
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))      

        try:
            check_conn = ConnectSQL()
            project_gen = project_name #+'_'+privacy_type
            pro_tb = get_pro_tb(check_conn, project_gen,privacy_type,project_id) #columns real name
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))
  

        gen_json_rep = GetGenJsonRep()
        result_rep = gen_json_rep.get_gen_json_api(pro_col_en, pro_col_cht, 'tbl_1', pro_tb,gen_qi_col, gen_qi_settingvalue)
        logger.info('%%%%%%%%%%%%')
        logger.info(type(result_rep))
        #組完打看看
        # "mainInfo": 
        # {"tbl_1":
        #  {"tblName":"gen_0628_single",
        # "col_en":"c_6119_0,c_6119_1,c_6119_2,c_6119_3,c_6119_4,c_6119_5,c_6119_6",
        #   "colInfo":
        #   {"col_1":{"colName":"c_6119_0","apiName":"getGenNumLevel","userRule":"3"},
        #    "col_2":{"colName":"c_6119_1","apiName":"getGenNumLevel","userRule":"100"},
        #    "col_4":{"colName":"c_6119_3","apiName":"getGenString","userRule":"0_3"},
        #    "col_6":{"colName":"c_6119_5","apiName":"getGenNumLevel","userRule":"5"},
        #    "col_7":{"colName":"c_6119_6","apiName":"","userRule":""}
        #    }
        #    }
        # }
        # data = dict()
        # data['mainInfo'] = json.loads(result_rep)
        logger.info('***************************')
        logger.info(project_id)
        logger.info(project_name)
        logger.info(member_id)
        logger.info(useraccount)
        logger.info(privacy_type)
        logger.info('***************************')
        task = gen_getGenTbl_task.delay(project_id, project_name,member_id,useraccount,privacy_type,json.loads(result_rep))
        logger.info(f"GEN Task started with id: {task.id}")
        task_id = task.id
        await asyncio.sleep(30)
        task_status = celery.AsyncResult(task.id).status
        logger.info(f"Task status: {task_status}")
        if task_status == "SUCCESS":
            task_result = read_task(task_id)
            return {
                "task_id": task_result["task_id"],
                "task_status": task_result["task_status"],
                "status": "success",
                "msg": "",
                "dataInfo": task_result["task_result"],
            }
        elif task_status == 'FAILURE':
            error_message = str(celery.AsyncResult(task.id))
            logger.error(f"Celery task failed with error: {error_message}")
        else:
            logger.error(f"Celery task status: {task_status}")
            logger.error(f"Celery task did not succeed.")
            return {
                "status": "error",
                "message": "Celery task did not succeed."
            }
    except Exception as e:
        logger.error(f"Error in getGenTbl_gen_api: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
        }
    

def get_finaltblName(conn, gen_project_name,privacytype):
    if privacytype == 'syn':
        sqlStr = f"SELECT finaltblName FROM  SynService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            finaltblName = resultSampleData['fetchall'][0].get('finaltblName')
            if not finaltblName:
                return None
            else:
                return finaltblName#.split(',')
        else:
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")
    elif privacytype == 'dp':
        sqlStr = f"SELECT finaltblName FROM  DpService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            finaltblName = resultSampleData['fetchall'][0].get('finaltblName')
            if not finaltblName:
                return None
            else:
                return finaltblName#.split(',')
        else:
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")


async def getExport_gen_api(project_id, privacy_type, member_id, useraccount, db):
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
            logger.error('errTable: get projname from table fail. {0}'.format(str(e)))
            return None

        #連線到DeidDB拿  finaltblName 欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name#+'_'+privacy_type
            finaltblName = get_finaltblName(check_conn, project_gen,privacy_type) #c_7070_0,c_7070_1,c_7070_2,c_7070_3,c_7070_4,c_7070_5,c_7070_6
        except Exception as e:
            logger.debug(str(privacy_type),' to DeidDB error : ',str(e))

        #連線到DeidDB拿pro_col_en欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name#+'_'+privacy_type
            pro_col_en = get_procolen(check_conn, project_gen, privacy_type,project_id) #c_7070_0,c_7070_1,c_7070_2,c_7070_3,c_7070_4,c_7070_5,c_7070_6
        except Exception as e:
            logger.debug(str(privacy_type),' to DeidDB error : ',str(e))

        #連線到DeidDB拿pro_col_cht欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name#+'_'+privacy_type
            pro_col_cht = get_procolcht(check_conn, project_gen, privacy_type,project_id) #columns real name
        except Exception as e:
            logger.debug(str(privacy_type),' to DeidDB error : ',str(e))    

        
        logger.info('%%%%%project_id%%%%%%%')
        logger.info(project_id)
        logger.info('%%%%%project_name%%%%%%%')
        logger.info(project_name)
        logger.info('%%%%%finaltblName%%%%%%%')
        logger.info(finaltblName)
        logger.info('%%%%%%%member_id%%%%%')
        logger.info(member_id)
        logger.info('%%%%%%useraccount%%%%%%')
        logger.info(useraccount)
        logger.info('%%%%%%%privacy_type%%%%%')
        logger.info(privacy_type)
        logger.info('%%%%%%pro_col_en%%%%%%')
        logger.info(pro_col_en)
        logger.info('%%%%%%pro_col_cht%%%%%%')
        logger.info(pro_col_cht)


        task = gen_export_task.delay(project_id, project_name, finaltblName, member_id, useraccount, privacy_type, pro_col_en, pro_col_cht)
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
    
def syn_api(syn_pid):
    # URL
    url = "http://flask_syn_compose:5088/genData_async"
    # header
    headers = {
        "Content-Type": "application/json"
    }
    # base64
    data = {
        "jsonBase64": syn_base64(syn_pid)
    }
    # POST request
    logger.info('**************************')
    logger.info(url)
    logger.info(data)
    response = requests.post(url, headers=headers, json=data)
    # respense
    logger.info('**************************')
    logger.info(response.status_code)
    logger.info(response.text)

def dp_api(dp_pid):
    # URL
    url = "http://flaskdp_compose:5088/DP_async"
    # header
    headers = {
        "Content-Type": "application/json"
    }
    # base64
    data = {
        "jsonBase64": dp_base64(dp_pid)
    }
    # POST request
    response = requests.post(url, headers=headers, json=data)
    # respense
    logger.info('**************************')
    logger.info(response.status_code)
    logger.info(response.text)

async def run_import_and_gen_tasks(task_id, project_id, privacy_type, member_id, useraccount, db):
    import_result = await import_api(project_id, privacy_type, member_id, useraccount, db)
    if import_result.get("status") == "error":
        task_status[task_id] = "failed gen_import"
        return
    try:
        check_conn = ConnectSQL()
        project_name =  get_projname(check_conn,project_id, privacy_type) #string to list
        logger.info('get_project_name ')
        logger.info(project_name)
        check_conn.close()
    except Exception as e:
        msg = "Can not find the project." + str(e)
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)    
    

    # 檢查 import 任務狀態
    genimport_except_status = [41, 97]
    status_check_task = asyncio.create_task(run_with_timeout(project_id, privacy_type, expected_statuses=genimport_except_status))
    status_check_result = await status_check_task
    logger.info(f'status_check_result: {status_check_result}')
    if not status_check_result:
        task_status[task_id] = "failed gen_import"
        return 
    else:
        task_status[task_id] = "completed gen_import"
    await asyncio.sleep(random.randint(15, 20))
    ############################################################
    try:
        logger.info(f'Calling getGenTbl_gen_api with params: {project_id}, {privacy_type}, {member_id}, {useraccount}')
        gen_result = await getGenTbl_gen_api(project_id, privacy_type, member_id, useraccount, db)
        logger.info(f'Result from getGenTbl_gen_api: {gen_result}')
    except Exception as e:
        logger.error(f'Exception occurred while calling getGenTbl_gen_api: {e}')
        gen_result = None
        task_status[task_id] = "error gen_getGenTbl"
    
    if gen_result is None:
        logger.error("gen_result is None")
        task_status[task_id] = "error gen_getGenTbl"
        return {
            "status": "error",
            "message": "Failed to get result, gen_result is None."
        }   
    if gen_result.get("status") == "error":
        task_status[task_id] = "error gen_getGenTbl"
        return
    # 檢查 gen 任務狀態
    gen_except_status = [42, 97]
    status_check_task = asyncio.create_task(run_with_timeout(project_id, privacy_type, expected_statuses=gen_except_status))
    status_check_result = await status_check_task
    if not status_check_result:
        task_status[task_id] = "failed gen_getGenTbl"
    else:
        task_status[task_id] = "completed gen_getGenTbl"
    ########################################################
    await asyncio.sleep(random.randint(15, 20))
    try:
        logger.info(f'Calling getGenTbl_gen_api with params: {project_id}, {privacy_type}, {member_id}, {useraccount}')
        genExport_result = await getExport_gen_api(project_id, privacy_type, member_id, useraccount, db)
        logger.info(f'Result from getGenTbl_gen_api: {genExport_result}')
    except Exception as e:
        logger.error(f'Exception occurred while calling genExport_gen_api: {e}')
        genExport_result = None
        task_status[task_id] = "error genExport"
    
    if genExport_result is None:
        logger.error("genExport_result is None")
        task_status[task_id] = "error genExport"
        return {
            "status": "error",
            "message": "Failed to get result, genExport_result is None."
        }   
    if genExport_result.get("status") == "error":
        task_status[task_id] = "error gen_genExport"
        return
    # 檢查 export 任務狀態
    gen_except_status = [43, 97]
    status_check_task = asyncio.create_task(run_with_timeout(project_id, privacy_type, expected_statuses=gen_except_status))
    status_check_result = await status_check_task
    if not status_check_result:
        task_status[task_id] = "failed gen_genExport"
    else:
        task_status[task_id] = "completed gen_genExport"
    #================================================================
    if privacy_type == 'syn':
        syn_api(project_id)
        logger.info('FINISH CALL SYN') 
    elif privacy_type == 'dp':
        dp_api(project_id)
        logger.info('FINISH CALL DP')       

@gen_Integration.get("/gen_task_status/{task_id}")
async def get_task_status(task_id: str):
    status = task_status.get(task_id, "unknown")
    return {"status": status}

def get_projname(conn,project_id, privacytype):
    if privacytype == 'syn':
        sqlStr = f"SELECT project_name FROM SynService.T_Project WHERE project_id = '{project_id}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            project_name = resultSampleData['fetchall'][0].get('project_name')
            if not project_name:
                return None
            else:
                return project_name
        else:
            msg = resultSampleData['msg']
            print('fetch DataToMysql fail: ' + msg)
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

    elif privacytype == 'dp':
        sqlStr = f"SELECT project_name FROM DpService.T_Project WHERE project_id  = '{project_id }'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            project_name = resultSampleData['fetchall'][0].get('project_name')
            if not project_name:
                return None
            else:
                return project_name
        else:
            msg = resultSampleData['msg']
            print('fetch DataToMysql fail: ' + msg)
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

@gen_Integration.post("/genintegration_async")
async def gen_Integration_async(background_tasks: BackgroundTasks, project_id: int, privacy_type: str, db: Session = Depends(get_db)):
# async def gen_Integration_async(background_tasks: BackgroundTasks, project_id: int, privacy_type: str, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = '1'#decode_info['member_id']
    useraccount = 'admin'#decode_info['sub']
    
    task_id = str(uuid.uuid4())
    task_status[task_id] = "processing"
    
    background_tasks.add_task(run_import_and_gen_tasks, task_id, project_id, privacy_type, member_id, useraccount, db)
    
    return {"status": "accepted", "task_id": task_id}
