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

from datetime import datetime, timedelta

Project_Reset = APIRouter()

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



def ResetProject(member_id, project_id, db: Session):
    logger.info(f"***********//////////////////////////{member_id, project_id}**************")
    status_trans={ 0:'建立專案及設定',
                    1 :'資料匯入及鏈結設定檢查',
                    2 :'安全資料鏈結處理',
                    3 :'安全資料鏈結處理中',
                    4 :'安全資料鏈結處理已完成',
                    5 :'隱私安全服務強化處理',
                    6 :'產生安全強化資料',
                    7 :'感興趣欄位選擇',
                    8 :'可用性分析處理中',
                    9 :'查看可用性分析報表',
                    90:'安全資料鏈結錯誤',
                    91:'可用性分析錯誤',
                    92:'資料匯入錯誤'
                    }
    
    is_super_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.super_admin.value).first()
    if not is_super_admin: #Groupadmin or user
        is_group_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        if not is_group_admin: #user
            logger.info(f"***********project user{member_id}*********")
            user_get_project = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id,
                                                             MemberProjectRole.project_id == project_id).first() 
            if not user_get_project:
                msg = f"Project_Reset failed: The user {member_id} does not have this project {project_id}"
                logger.error(msg)
                return False,  msg           

            proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).first()
            tmp_status =proj_status.project_status
            tmp_project_status  = status_trans[tmp_status]
            #def更新狀態
            proj_status.project_status = 1
            proj_status.updatetime = datetime.now()
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                return False, str(e)
            msg = f"project {project_id}，從{tmp_project_status}狀態到設定專案 "
            return True,  msg  

    
        else: ##GroupAdmin可以看到所有own group 的project
            logger.info(f"***********Group Admin**************")
            user_get_project = db.query(Project).filter(Project.group_id==is_group_admin.group_id,
                                                   Project.project_id == project_id).first()
            if not user_get_project:
                msg = f"Project_Reset failed: The user {member_id} does not have this project {project_id}"
                logger.error(msg)
                return False,  msg           

            proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).first()
            tmp_status =proj_status.project_status
            tmp_project_status  = status_trans[tmp_status]  
            #def更新狀態
            proj_status.project_status = 1
            proj_status.updatetime = datetime.now()
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                return False, str(e)
            msg = f"project {project_id}，從{tmp_project_status}狀態到設定專案 "
            return True,  msg  

    else: #SuperAdmin可以看到所有的project
        logger.info(f"***********SuperAdmin**************")

        user_get_project = db.query(Project).filter(Project.project_id == project_id).first() 
        if not user_get_project:
            msg = f"Project_Reset failed: The user {member_id} does not have this project {project_id}"
            logger.error(msg)
            return False,  msg           
        proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).first()
        tmp_status =proj_status.project_status
        tmp_project_status  = status_trans[tmp_status]  

        #def更新狀態
        proj_status.project_status = 1
        proj_status.updatetime = datetime.now()
        try:
            # proj_status.update(proj_status)
            db.commit()
        except Exception as e:
            db.rollback()
            return False, str(e)
        msg = f"project {project_id}，從{tmp_project_status}狀態到設定專案 "
        return True,  msg 

@Project_Reset.put("/reset")
def reset_project(project_id: int = Form(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):

    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']

    try:
        checked, _ser = ResetProject(member_id, project_id, db)
    except Exception as e:    
        msg = f"Member {useraccount} Project_Reset failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    
    if not checked:
        logger.error(_ser)
        result = Result(msg=_ser, status=False)
        return _result_wrapper(result, status_code=400)

    logger.info(_ser)
    result = Result(msg=_ser, status=True) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
