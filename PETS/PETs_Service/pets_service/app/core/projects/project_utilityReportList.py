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

Project_utilityReportList = APIRouter()

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

security = HTTPBearer(description="HTTP Bearer token scheme")

def get_reportList(project_id_, db_):
    all_records = db_.query(UtilityResult).filter(UtilityResult.project_id == project_id_).all()
    
    result = []
    for record in all_records:
        report_dict = {}        
        report_dict['privacy_type'] = record.privacy_type
        result.append(report_dict)

    #Use a set to keep track of unique values
    unique_values = set()

    #Use a list to store the result without duplicates   
    reportList = []
    for item in result:
        value = item['privacy_type']
    
        # Check if the value is not in the set (not a duplicate)
        if value not in unique_values:
            #Add the value to the set to mark it as seen
            unique_values.add(value)        
            #Add the item to the result list
            reportList.append(item)

    return reportList


@Project_utilityReportList.get("/utilityreportlist")
def utilityreportlist(project_id:int, db:Session = Depends(get_db)):
    result = {}
    result['status'] = 1
    result['msg'] = "get utility report list"

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
    obj['report_info'] = get_reportList(project_id, db)

    result['obj'] = obj

    return result