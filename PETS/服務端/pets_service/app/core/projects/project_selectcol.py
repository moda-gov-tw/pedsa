# -*- coding: utf-8 -*-
from fastapi import Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from logging.config import dictConfig
import logging

from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole, UtilityResult, Project
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group

from config.MyLib.connect_sql import ConnectSQL


    
Project_selectcol = APIRouter()

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")
security = HTTPBearer(description="HTTP Bearer token scheme")

def get_select_col(conn,project_name, privacytype):
    if privacytype == 'k':
        sqlStr = f"SELECT after_col_cht FROM DeIdService.T_Project_SampleTable WHERE pro_db = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('after_col_cht')
            if not select_colNames:
                return None
            else:
                return select_colNames.split(',')
        else:
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

    elif privacytype == 'syn':
        sqlStr = f"SELECT select_colNames FROM SynService.T_ProjectSample5Data WHERE pro_name = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            if not select_colNames:
                return None
            else:
                return select_colNames.split(',')
        else:
            msg = resultSampleData['msg']
            print('fetch DataToMysql fail: ' + msg)
            logger.error('fetch DataToMysql fail: ' +f"{msg}")

    elif privacytype == 'dp':
        sqlStr = f"SELECT select_colNames FROM DpService.T_ProjectSample5Data WHERE pro_name = '{project_name}'"
        resultSampleData = conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            if not select_colNames:
                return None
            else:
                return select_colNames.split(',')
        else:
            msg = resultSampleData['msg']
            logger.error('fetch DataToMysql fail: ' +f"{msg}")            

def get_colsList(project_name):
    logger.info('----------------------get_colsList')
    #get k select_col
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        k_cols = get_select_col(check_conn,project_name,'k') #string to list
        logger.info('get k cols')
        check_conn.close()
    except Exception as e:
        logger.error('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    #get select_col
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        syn_cols = get_select_col(check_conn,project_name,'syn') #string to list
        logger.info('get syn cols ')
        check_conn.close()
    except Exception as e:
        logger.error('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    try:
        check_conn = ConnectSQL()
        #updateToMysql_status(check_conn, projID, projName, fileName, step, percentage)
        dp_cols = get_select_col(check_conn,project_name,'dp') #string to list
        logger.info('get dp cols ')
        check_conn.close()
    except Exception as e:
        logger.error('errTable: updateToMysql_status fail. {0}'.format(str(e)))
        return None
    
    report_dict = {}        
    # report_dict['privacy_type'] = 'syn'
    report_dict['k'] = k_cols
    report_dict['syn'] = syn_cols
    report_dict['dp'] = dp_cols

    return report_dict


@Project_selectcol.get("/getselectcol")
def getselectcol(project_id:int, db:Session = Depends(get_db)):
    result = {}
    result['status'] = 1
    result['msg'] = "get K/syn/dp select cols"

    obj = {}
    obj['project_id'] = project_id
    
    #判斷專案是否存在
    try:
        obj['project_name'] = db.query(Project).filter(Project.project_id == project_id).first().project_name
    except:
        result = {}
        result['status'] = -1
        result['msg'] = "project id {} doesn't exist".format(project_id)
        return result
    
    #若專案存在，查詢專案報表list
    obj['project_eng'] = db.query(Project).filter(Project.project_id == project_id).first().project_eng
    obj['report_info'] = get_colsList(obj['project_eng'])

    result['obj'] = obj
    return result