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
from app.core.models import Group, Member, AdminRole, ProjectJobList, Project
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group

Project_jobLogList = APIRouter()

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

security = HTTPBearer(description="HTTP Bearer token scheme")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    checked, decode_info = decode_jwt_token(token)
    if not checked:
        msg = f"verify token failed: {decode_info}"
        logger.error(f"{msg}")
        raise HTTPException(status_code=401, detail=msg)
    return decode_info

def get_jobLogList(db_):
    all_records = db_.query(ProjectJobList).all()
    jobLogList = []

    for record in all_records:
        record_dict = {}
        record_dict['project_name'] = record.project_name
        record_dict['project_eng'] = record.project_eng
        record_dict['project_env'] = record.project_env
        record_dict['jobname'] = record.jobname
        record_dict['percentage'] = record.percentage
        record_dict['logcontent'] = record.logcontent
        record_dict['useraccount'] = record.useraccount
        record_dict['createtime'] = record.createtime
        record_dict['updatetime'] = record.updatetime
        record_dict['processtime'] = record.processtime

        jobLogList.append(record_dict)
        
    sorted_jobLogList = sorted(jobLogList, key=lambda x: (x['project_eng'], x['createtime']))
    return sorted_jobLogList


@Project_jobLogList.get("/jobloglist")
def jobloglist(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']

    result = {}
    result['status'] = 1
    result['msg'] = "get job log"
    result['dataInfo'] = get_jobLogList(db)
    return result
