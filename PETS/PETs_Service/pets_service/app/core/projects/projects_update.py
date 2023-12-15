# -*- coding: utf-8 -*-
from fastapi import Body, Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from logging.config import dictConfig
import logging

from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole,ViewsDetails,ProjectJoinFunc
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

from datetime import datetime, timedelta

from pydantic import (
    BaseModel,
)
from typing import Optional, Union, List
from typing import (
    Dict,
    List,
    Optional,
)  

Project_Update = APIRouter() ##need to edit

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

class ProjectRole(BaseModel):
    member_id: int
    group_id: int
    member_role: int

class Join_func(BaseModel):
    left_datasetname: str
    left_col: str
    right_datasetname: str
    right_col: str

class DataModelIn(BaseModel):
    project_name: str
    project_eng: str
    project_desc: Optional[str] = None
    enc_key: str
    join_type: int
    project_role: List[Dict] #List[ProjectRole]
    join_func:List[Dict] #List[Join_func]
    # @model_validator(mode='before')
    # @classmethod
    # def validate_to_json(cls, value):
    #     if isinstance(value, str):
    #         return cls(**json.loads(value))
    #     return value

## 使用者登入後，從專案列表，選取對應的專案，更新專案所需資訊
@Project_Update.put("/update") ##need to edit
def update_projects(data: DataModelIn=Body(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    logger.info(f"***********update_projects*************")
    checked=True

    insert_data = data.model_dump()
    project_name = insert_data['project_name']
    project_role = insert_data['project_role']
    join_func = insert_data['join_func']
    join_type = insert_data['join_type']
    project_eng = insert_data['project_eng']
    project_desc = insert_data['project_desc']
    enc_key = insert_data['enc_key']
 
    if project_name == '': 
        msg = 'project_name不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  project_eng== '':
        msg = 'project_eng不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  project_desc== '':
        msg = 'project_desc不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  enc_key== '':
        msg = 'enc_key不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  join_type== '':
        msg = 'join_type不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  project_role== '':
        msg = 'project_role不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  join_func== '':
        msg = 'join_func不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


    #check join group?
    for join_func_id in join_func:
        try:
            l_group_id_check = join_func_id['left_datasetname'].split('_')[0]
            left_group_id = db.query(Group).filter(Group.group_type == l_group_id_check).first().id
        except Exception as e:
            msg = f'查無群 {l_group_id_check}，資料集前贅字元不符合規則' 
            logger.error(msg)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)
        try:
            r_group_id_check = join_func_id['right_datasetname'].split('_')[0]
            right_group_id = db.query(Group).filter(Group.group_type == r_group_id_check).first().id
        except Exception as e:    
            msg = f'查無群 {r_group_id_check}，資料集前贅字元不符合規則' 
            logger.error(msg)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)


    project_id = db.query(Project).filter(Project.project_name == project_name).first().project_id
            
    #def更新 Project_join_type       
    Project_join_type = db.query(Project).filter(Project.project_id == project_id).first()
    #tmp_status =proj_status.project_status
    #tmp_project_status  = status_trans[tmp_status]
    #def更新狀態
    Project_join_type.join_func = join_type
    Project_join_type.updatetime = datetime.now()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Member {useraccount} update join_type failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    #先delete，filter，再update，commit
    ProjectJoinFunc_tmp = db.query(ProjectJoinFunc).filter(ProjectJoinFunc.project_id == project_id).first()
    ProjectJoinFunc_createtime = ProjectJoinFunc_tmp.createtime
    ProjectJoinFunc_createMember_Id = ProjectJoinFunc_tmp.createMember_Id
    db_ProjectJoinFunc = db.query(ProjectJoinFunc).filter(ProjectJoinFunc.project_id == project_id).all() 
    
    for row in db_ProjectJoinFunc:
        db.delete(row)
    
    try:
        for join_func_id in join_func:
            l_group_id = join_func_id['left_datasetname'].split('_')[0]
            r_group_id = join_func_id['right_datasetname'].split('_')[0]
            db_ProjectJoinFunc = ProjectJoinFunc()
            db_ProjectJoinFunc.left_group_id = db.query(Group).filter(Group.group_type == l_group_id).first().id
            db_ProjectJoinFunc.left_dataset = join_func_id['left_datasetname']
            db_ProjectJoinFunc.left_col= join_func_id['left_col']
            db_ProjectJoinFunc.right_group_id = db.query(Group).filter(Group.group_type == r_group_id).first().id
            db_ProjectJoinFunc.right_dataset= join_func_id['right_datasetname']
            db_ProjectJoinFunc.right_col= join_func_id['right_col']
            db_ProjectJoinFunc.project_id = project_id
            db_ProjectJoinFunc.createtime = ProjectJoinFunc_createtime #datetime.now()
            db_ProjectJoinFunc.createMember_Id  = ProjectJoinFunc_createMember_Id#member_id
            db_ProjectJoinFunc.updatetime = datetime.now()
            db_ProjectJoinFunc.updateMember_Id = member_id
            db.add(db_ProjectJoinFunc)
            db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Member {useraccount} update join_func failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    
    #先delete，filter，再update，commit
    MemberProjectRole_tmp = db.query(MemberProjectRole).filter(MemberProjectRole.project_id == project_id).first()
    MemberProjectRole_createtime = MemberProjectRole_tmp.createtime
    MemberProjectRole_createMember_id = MemberProjectRole_tmp.createmember_id
    db_MemberProjectRole = db.query(MemberProjectRole).filter(MemberProjectRole.project_id == project_id).all() 
    for row in db_MemberProjectRole:
        db.delete(row)
    try:
        for project_role_id in project_role:
            # logger.info(project_role_id)
            db_MemberProjectRole = MemberProjectRole()
            db_MemberProjectRole.project_role = project_role_id['member_role']
            db_MemberProjectRole.project_id = project_id
            db_MemberProjectRole.member_id = project_role_id['member_id']
            db_MemberProjectRole.createtime = MemberProjectRole_createtime
            db_MemberProjectRole.createmember_id = MemberProjectRole_createMember_id
            db_MemberProjectRole.updatetime = datetime.now()
            db_MemberProjectRole.updatemember_id = member_id

            db.add(db_MemberProjectRole)
            db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Member {useraccount} update project_role failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


    msg = f"Member {useraccount} update_projects successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)

