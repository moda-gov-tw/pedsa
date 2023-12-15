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
    get_user, is_group_owner, get_group
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

Project_List = APIRouter()

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
def get_project_ls(member_id, db: Session):
    
    #fix statusname by Bruce; PEI;
    status_trans={ 0:'建立專案及設定',
                    1 :'資料匯入及鏈結設定檢查',
                    2 :'安全資料鏈結處理',
                    3 :'安全資料鏈結處理中',
                    4 :'安全資料鏈結處理已完成',
                    5 :'隱私安全服務強化處理',
                    6 :'產生安全強化資料',
                    7 :'感興趣欄位選擇',
                    8 :'可用性分析處理中',
                    9 :'查看可用性分析報表'
                    }
    
    data = {}
    is_super_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.super_admin.value).first()
    if not is_super_admin: #Groupadmin or user
        is_group_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        if not is_group_admin:
            logger.info(f"***********project user*********")
            logger.info(f"***********project user{member_id}*********")
            all_project = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id).all() 
            project_ls = []
            for proj in all_project  :
            #     user_dict = user.model_dump()
                proj_dict = dict()
                proj_dict['project_id'] = proj.project_id
                proj_dict['project_name'] = db.query(Project).filter(Project.project_id == proj.project_id).first().project_name
                proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == proj.project_id).first()
                proj_dict['project_status'] =proj_status.project_status
                proj_dict['project_statusname']  = status_trans[proj_status.project_status]    

                proj_dict['member_role'] = None
                proj_dict['project_role'] = proj.project_role

                if proj_status.updatetime is None:
                    proj_dict['project_time'] =proj_status.createtime
                else:
                    proj_dict['project_time'] =proj_status.updatetime

                proj_dict['project_group_id'] =db.query(Project).filter(Project.project_id == proj.project_id).first().group_id
                proj_dict['project_group_name'] =db.query(Group).filter(Group.id == proj_dict['project_group_id']).first().group_name
                project_ls.append(proj_dict)
            return project_ls
        
        else: ##GroupAdmin可以看到所有own group 的project
            logger.info(f"***********Group Admin**************")
            all_project = db.query(Project).filter(Project.group_id==is_group_admin.group_id).all() 
            project_ls = []
            for proj in all_project  :
            #     user_dict = user.model_dump()
                proj_dict = dict()
                proj_dict['project_id'] = proj.project_id
                proj_dict['project_name'] = proj.project_name
                proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == proj.project_id).first()
                proj_dict['project_status'] =proj_status.project_status
                proj_dict['project_statusname']  = status_trans[proj_status.project_status]    
                proj_dict['member_role'] = is_group_admin.member_role #group admin
                proj_dict['project_role'] = 3 #不知道要從哪邊撈，先設3

                if proj_status.updatetime is None:
                    proj_dict['project_time'] =proj_status.createtime
                else:
                    proj_dict['project_time'] =proj_status.updatetime

                proj_dict['project_group_id'] =proj.group_id
                proj_dict['project_group_name'] =db.query(Group).filter(Group.id == proj.group_id).first().group_name
                project_ls.append(proj_dict)
            return project_ls

    else: #SuperAdmin可以看到所有的projecy
        logger.info(f"***********SuperAdmin**************")
        all_project = db.query(Project).filter().all() 
        project_ls = []
        for proj in all_project  :
        #     user_dict = user.model_dump()
            proj_dict = dict()
            proj_dict['project_id'] = proj.project_id
            proj_dict['project_name'] = proj.project_name
            proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == proj.project_id).first()
            proj_dict['project_status'] =proj_status.project_status
            proj_dict['project_statusname']  = status_trans[proj_status.project_status]    
            proj_dict['member_role'] = is_super_admin.member_role #super_admin
            proj_dict['project_role'] = 3 #不知道要從哪邊撈，先設3

            if proj_status.updatetime is None:
                proj_dict['project_time'] =proj_status.createtime
            else:
                proj_dict['project_time'] =proj_status.updatetime


            proj_dict['project_group_id'] =proj.group_id
            proj_dict['project_group_name'] =db.query(Group).filter(Group.id == proj.group_id).first().group_name
            project_ls.append(proj_dict)
        return project_ls

    # data['obj']= all_project

    # return data


@Project_List.get("/list")
def list_projects(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    
    try:
        project_list = get_project_ls(member_id,db)
    except Exception as e:    
        msg = f"Member {useraccount} project list failed: {str(e)}"
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

    msg = f"Member {useraccount} list projects successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, obj=project_list, status=True) ##for check member id
    
    
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
