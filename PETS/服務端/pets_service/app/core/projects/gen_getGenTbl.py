# -*- coding: utf-8 -*-
from fastapi import Body, Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi import FastAPI,APIRouter,Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from celery_worker import celery, gen_getGenTbl_task

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


gen_getGenTbl = APIRouter()

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
            logger.info(f"qi_value: {qi_value}")
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

def get_qisetting(conn,project_name, privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT gen_qi_settingvalue FROM SynService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('gen_qi_settingvalue')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch gen_qi_settingvalue of project_name DataToMysql fail')
                logger.error('fetch  gen_qi_settingvalue DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch gen_qi_settingvalue of project_name DataToMysql fail')
            logger.error('fetch  gen_qi_settingvalue DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
    elif privacytype == 'dp':
        sqlStr = f"SELECT gen_qi_settingvalue FROM DpService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('gen_qi_settingvalue')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch gen_qi_settingvalue of project_name DataToMysql fail')
                logger.error('fetch  gen_qi_settingvalue DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch gen_qi_settingvalue of project_name DataToMysql fail')
            logger.error('fetch  gen_qi_settingvalue DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

def get_qicol(conn,project_name, privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT qi_col FROM SynService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('qi_col')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch qi_col of project_name DataToMysql fail')
                logger.error('fetch  qi_col DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch qi_col of project_name DataToMysql fail')
            logger.error('fetch  qi_col DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
    elif privacytype == 'dp':
        sqlStr = f"SELECT qi_col FROM DpService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('qi_col')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch qi_col of project_name DataToMysql fail')
                logger.error('fetch  qi_col DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch qi_col of project_name DataToMysql fail')
            logger.error('fetch  qi_col DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

def get_pro_tb(conn,project_name, privacytype, project_id):
    if privacytype == 'syn':
        sqlStr = f"SELECT pro_tb FROM SynService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_tb')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch pro_tb of project_name DataToMysql fail')
                logger.error('fetch  pro_tb DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch pro_tb of project_name DataToMysql fail')
            logger.error('fetch pro_tb DataToMysql fail')
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
    elif privacytype == 'dp':
        sqlStr = f"SELECT pro_tb FROM DpService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('pro_tb')
            if not select_colNames:
                update_error_msg(conn, privacytype, project_id)
                msg = ('fetch pro_tb of project_name DataToMysql fail')
                logger.error('fetch  pro_tb DataToMysql fail')
                result = Result(msg=msg, status=False)
                return _result_wrapper(result, status_code=400)
            else:
                return select_colNames#.split(',')
        else:
            update_error_msg(conn, privacytype, project_id)
            msg = ('fetch pro_tb of project_name DataToMysql fail')
            logger.error('fetch pro_tb DataToMysql fail')
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

@gen_getGenTbl.post("/gen_getGenTbl")
def getGenTbl_gen(project_id: int, privacy_type: str,db :Session =Depends(get_db)):
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
            msg = 'errTable: get select cols from table fail. {0}'.format(str(e))
            logger.error('errTable: get select cols from table fail. {0}'.format(str(e)))
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
      
        # 去DB找相關的資訊: genDictEncode: str,doMinMaxEncode: str
        #連線到SYN DB拿qi-col
        try:
            check_conn = ConnectSQL()
            gen_qi_col = get_qicol(check_conn, project_name, privacy_type, project_id)
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))
            msg = str(privacy_type),' to DB error : ',str(e)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        #連線到SYN DB拿概化規則
        try:
            check_conn = ConnectSQL()
            gen_qi_settingvalue = get_qisetting(check_conn, project_name, privacy_type, project_id)
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))
            msg = str(privacy_type),' to DB error : ',str(e)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        #連線到DeidDB拿pro_col_en欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name #+'_'+privacy_type
            pro_col_en = get_procolen(check_conn, project_gen,privacy_type, project_id) #c_7070_0,c_7070_1,c_7070_2,c_7070_3,c_7070_4,c_7070_5,c_7070_6
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))
            msg = str(privacy_type),' to DB error : ',str(e)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        #連線到DeidDB拿pro_col_cht欄位
        try:
            check_conn = ConnectSQL()
            project_gen = project_name #+'_'+privacy_type
            pro_col_cht = get_procolcht(check_conn, project_gen,privacy_type, project_id) #columns real name
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))        
            msg = str(privacy_type),' to DB error : ',str(e)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        try:
            check_conn = ConnectSQL()
            project_gen = project_name #+'_'+privacy_type
            pro_tb = get_pro_tb(check_conn, project_gen,privacy_type, project_id) #columns real name
        except Exception as e:
            logger.debug(str(privacy_type),' to DB error : ',str(e))  
            msg = str(privacy_type),' to DB error : ',str(e)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        gen_json_rep = GetGenJsonRep()
        result = gen_json_rep.get_gen_json_api(pro_col_en, pro_col_cht, 'tbl_1', pro_tb,gen_qi_col, gen_qi_settingvalue)
        logger.info('%%%%%%%%%%%%')
        logger.info(type(result))
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
        # data['mainInfo'] = json.loads(result)
        # logger.info('***************************')
        # logger.info(data)
        # logger.info(type(data))

        # for tbl in data['mainInfo']:
        #     genList = ''  # List of all actions on each columns.
        #     colList = data[tbl]['col_en'].split(',')
        #     logger.info(colList)

        task = gen_getGenTbl_task.delay(project_id, project_name,member_id,useraccount,privacy_type,json.loads(result))
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
