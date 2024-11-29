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
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group,user_is_active
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

Project_ProjMemGroupId = APIRouter()

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


# def get_group_ls(db: Session):
#     db_groups = db.query(Group).filter().all()
#     group_list_ser = dict(GroupList.model_validate(db_groups))
#     return group_list_ser
from typing import Optional, Union, List
def get_proj_groupid(project_id, db: Session):
        allmember_project = db.query(MemberProjectRole).filter(MemberProjectRole.project_id == project_id).all() 
        groupid_ls = []
        for mem in allmember_project  :
            group_dict= dict()
            group_id = db.query(Member).filter(Member.id == mem.member_id).first().group_id
            group_dict['group_id'] = group_id
            group_dict['group_name'] = db.query(Group).filter(Group.id == group_id).first().group_name
            group_dict['group_type'] = db.query(Group).filter(Group.id == group_id).first().group_type
            groupid_ls.append(group_dict)  

        group_return_ls = [dict(t) for t in set([tuple(d.items()) for d in groupid_ls])]
        return sorted(group_return_ls, key=lambda x: x["group_id"])


@Project_ProjMemGroupId.get("/membergroupid")
def ProjMemGroupId_projects(project_id:int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    
    is_proj_exit = db.query(Project).filter(Project.project_id == project_id).first()
    if not is_proj_exit:
        msg = f"projmemgroupid fail, Member {useraccount} attend to get projectid {project_id} not exist"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    

    try:
        groupid_list = get_proj_groupid(project_id,db)
    except Exception as e:    
        msg = f"Member {useraccount} get project member group id failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    # test_ans['admin'] = tmp_dict['admin']
    # checked = check_permissions(member_id, ['create_group'], db)


    # checked = check_permissions(member_id, ['project_list'], db)
    # if not checked:
    #     msg = f"List projects failed: Member {useraccount} does not have project_list permission"
    #     logger.error(msg)
    #     result = Result(msg=msg, status=False)
    #     return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} get project member group id successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, obj=groupid_list, status=True) ##for check member id
    
    
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
