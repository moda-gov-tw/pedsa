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
from app.core.models import Group, Member,MemberGroupRole ,MemberProjectRole , AdminRole, ProjectJobList, Project
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group,user_is_active

Project_jobLogList = APIRouter()

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


def get_jobLogList(member_id, db: Session):
    is_super_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.super_admin.value).first()
    if not is_super_admin: #Groupadmin or user
        is_group_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        if not is_group_admin:
            logger.info("***********project user****get_jobLogList*****")
            # logger.info(f"***********project user{member_id}****get_jobLogList*****")
            all_project = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id).all() 
            jobLogList = []
            for proj in all_project  :
                record = db.query(ProjectJobList).filter(ProjectJobList.project_id == proj.project_id).first()
                if record:
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
                else:
                    pass
            sorted_jobLogList = sorted(jobLogList, key=lambda x: (x['project_eng'], x['createtime']))
            return sorted_jobLogList
        
        else:##GroupAdmin可以看到所有own group 的project
            logger.info("*****************get_jobLogList********")
            all_project = db.query(Project).filter(Project.group_id==is_group_admin.group_id).all() 
            jobLogList = []
            for proj in all_project  :
                record = db.query(ProjectJobList).filter(ProjectJobList.project_id == proj.project_id).first()
                if record:
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
                else:
                    pass

            logger.info("**************get_jobLogList******")
            all_project = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id).all() 
            for proj in all_project  :
                record = db.query(ProjectJobList).filter(ProjectJobList.project_id == proj.project_id).first()
                if record:
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
                else:
                    pass

            merged_dict = {}
            for project in jobLogList:
                project_id = project["project_id"]
                if project_id not in merged_dict:
                    # 若尚未有該 project_id，則直接新增
                    merged_dict[project_id] = project
                else:
                    # If the project_id already exists, update the record and keep
                    if project["project_role"] in [1,2,4,5]:
                        merged_dict[project_id].update(project)

                    # Preserve the original member_role value
                    elif project["member_role"] is not None:
                        merged_dict[project_id]["member_role"] = project["member_role"]
                    
            # 轉換字典為列表，只保留合併後的紀錄
            merged_list = list(merged_dict.values())
            return merged_list

    else: #SuperAdmin可以看到所有的projecy
        logger.info(f"***********SuperAdmin*******get_jobLogList*******")
        all_records = db.query(ProjectJobList).all()
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
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    result = {}
    result['status'] = 1
    result['msg'] = "get job log"
    result['dataInfo'] = get_jobLogList(member_id, db)
    return result
