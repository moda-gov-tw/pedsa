# -*- coding: utf-8 -*-
from fastapi import Body, Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi import FastAPI,APIRouter,Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from celery_worker import celery, gen_export_task

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


gen_getExport = APIRouter()

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
        msg = f"verify token failed: {decode_info}"
        logger.error(f"{msg}")
        raise HTTPException(status_code=401, detail=msg)
    return decode_info

def get_procolen(conn, gen_project_name,privacytype, project_id ):
    if privacytype == 'syn':
        sqlStr = f"SELECT pro_col_en FROM SynService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_en')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not get_procolen of the project: {str(gen_project_name)}"
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch get_procolen of project_name DataToMysql fail')
            logger.error('fetch  get_procolen  DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
    elif privacytype == 'dp':
        sqlStr = f"SELECT pro_col_en FROM DpService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_en')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = f"Can not get_procolen of the project: {str(gen_project_name)}"
                logger.error(msg)
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch get_procolen of project_name DataToMysql fail')
            logger.error('fetch  get_procolen  DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

def get_procolcht(conn, gen_project_name,privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT pro_col_cht FROM  SynService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_cht')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch pro_col_cht of project_name DataToMysql fail')
                logger.error('fetch  pro_col_cht DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch pro_col_cht of project_name DataToMysql fail')
            logger.error('fetch  pro_col_cht DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
    elif privacytype == 'dp':
        sqlStr = f"SELECT pro_col_cht FROM  DpService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_col_cht')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch pro_col_cht of project_name DataToMysql fail')
                logger.error('fetch  pro_col_cht DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch pro_col_cht of project_name DataToMysql fail')
            logger.error('fetch  pro_col_cht DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)


def get_finaltblName(conn, gen_project_name,privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT finaltblName FROM  SynService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            finaltblName = resultSampleData['fetchall'][0].get('finaltblName')
            if not finaltblName:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch finaltblName of project_name DataToMysql fail')
                logger.error('fetch  finaltblName DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return finaltblName#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch finaltblName of project_name DataToMysql fail')
            logger.error('fetch  finaltblName DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
    elif privacytype == 'dp':
        sqlStr = f"SELECT finaltblName FROM  DpService.T_Project_SampleTable WHERE pro_db = '{gen_project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            finaltblName = resultSampleData['fetchall'][0].get('finaltblName')
            if not finaltblName:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch finaltblName of project_name DataToMysql fail')
                logger.error('fetch  finaltblName DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return finaltblName#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch finaltblName of project_name DataToMysql fail')
            logger.error('fetch  finaltblName DataToMysql fail')
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
                msg = ('fetch  project_name DataToMysql fail')
                logger.error('fetch project_name DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return project_name
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch project_name of project_name DataToMysql fail')
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
                msg = ('fetch  project_name DataToMysql fail')
                logger.error('fetch project_name DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return project_name
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch project_name of project_name DataToMysql fail')
            logger.error('fetch project_name DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400) 
        
@gen_getExport.post("/gen_getExport")
def getExport_gen(project_id: int, privacy_type: str,db :Session =Depends(get_db)):
    member_id = '1'#decode_info['member_id']
    useraccount = 'admin'#decode_info['sub']
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
            logger.error('errTable: get select cols from table fail. {0}'.format(str(e)))
            return None

        #連線到DeidDB拿  finaltblName 欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name#+'_'+privacy_type
            finaltblName = get_finaltblName(check_conn, project_gen,privacy_type, project_id) #c_7070_0,c_7070_1,c_7070_2,c_7070_3,c_7070_4,c_7070_5,c_7070_6
        except Exception as e:
            logger.debug(str(privacy_type),' to DeidDB error : ',str(e))

        #連線到DeidDB拿pro_col_en欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name#+'_'+privacy_type
            pro_col_en = get_procolen(check_conn, project_gen, privacy_type, project_id) #c_7070_0,c_7070_1,c_7070_2,c_7070_3,c_7070_4,c_7070_5,c_7070_6
        except Exception as e:
            logger.debug(str(privacy_type),' to DeidDB error : ',str(e))

        #連線到DeidDB拿pro_col_cht欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name#+'_'+privacy_type
            pro_col_cht = get_procolcht(check_conn, project_gen, privacy_type, project_id) #columns real name
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
