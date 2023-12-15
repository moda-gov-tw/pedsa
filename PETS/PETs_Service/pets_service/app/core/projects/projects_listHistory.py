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
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole,ViewsDetails,HistoryProject
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

Project_listHistory = APIRouter() ##need to edit

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

from typing import Optional, Union, List
def get_project_list_history(member_id, db: Session):
        logger.info(f"***********get_project_list_history*********")
        logger.info(f"***********project user{member_id}*********")

        all_project = db.query(HistoryProject).filter().all() 
        project_ls = []
        for proj in all_project  :
        #     user_dict = user.model_dump()
            proj_dict = dict()
            proj_dict['project_id'] = proj.project_id
            proj_dict['project_name'] = proj.project_name
            proj_dict['project_eng'] = proj.project_eng
            proj_dict['project_desc'] = proj.project_desc
            proj_dict['createtime'] = proj.createtime
            proj_dict['updatetime'] = proj.updatetime
            proj_dict['enc_key'] = proj.enc_key
            proj_dict['jointablename'] = proj.jointablename
            proj_dict['jointablecount'] = proj.jointablecount
            proj_dict['join_func'] = proj.join_func
            proj_dict['join_func_content'] = proj.join_func_content
            proj_dict['project_role_content'] = proj.project_role_content
            proj_dict['group_id'] = proj.group_id
            proj_dict['createMember_Id'] = proj.createMember_Id
            proj_dict['updateMember_Id'] = proj.updateMember_Id
            proj_dict['aes_col'] = proj.aes_col
            project_ls.append(proj_dict)
        return True, project_ls


## 使用者登入後，想要看歷史刪除專案裡的資訊
@Project_listHistory.get("/ListDelHistory") ##need to edit
def detail_listhistory(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    logger.info(f"***********Project_List_DelHistory*************")
    try:
        checked, history_detail = get_project_list_history(member_id, db)
    except Exception as e:    
        checked, msg = f"Member {useraccount} view Delete History failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


    msg = f"Member {useraccount} view Delete History successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, obj=history_detail, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
