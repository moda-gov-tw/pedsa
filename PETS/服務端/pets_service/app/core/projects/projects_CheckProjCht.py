# -*- coding: utf-8 -*-
from fastapi import Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from logging.config import dictConfig
import logging

from sqlalchemy import func
from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group,user_is_active
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

from datetime import datetime, timedelta

Project_CheckProjCht = APIRouter()
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

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

def check_projname_cht(project_name, db: Session):

    porject_name_num = db.query(func.count()).filter(Project.project_name == project_name).scalar()

    if porject_name_num >= 1:
        msg = f'{project_name} Fail, Check_Proj_Cht duplicated.'
        logger.info(msg)
        return False , msg

    msg = f'{project_name} Pass, Check_Proj_Cht did not duplicate.'
    logger.info(msg)
    return True, msg

@Project_CheckProjCht.post("/checkprojcht")
def check_proj_cht(project_name:str, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):

    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    #check parameter is null?
    if project_name == '': 
        msg = 'project_name 不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    try:
        checked, msg = check_projname_cht(project_name, db)
    except Exception as e:    
        msg = f"Member {useraccount} Project_CheckProjCht failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    

    # msg = f"Member {member_id} check project Project_CheckProjCht successful."
    # logger.info(msg)
    result = Result(msg=msg, MemberID=member_id, status=checked)
    return _result_wrapper(result, status_code=200)