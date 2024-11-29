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
    get_user, is_group_owner, get_group,user_is_active
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

from datetime import datetime, timedelta

import os 
runcode = os.system('pip install requests')

import requests
import configparser

from pydantic import (
    BaseModel,
)
from typing import Optional, Union, List
from typing import (
    Dict,
    List,
    Optional,
)  

Project_MultiInsert = APIRouter() ##need to edit

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
    #project_eng: str
    #project_desc: Optional[str] = None
    #enc_key: str
    join_type: int
    #group_id : int
    aes_col: str
    jointablecount:int
    jointablename:str
    #project_role: List[Dict] #List[ProjectRole]
    join_func:List[Dict] #List[Join_func]


## 使用者登入後，從專案列表，選取對應的專案，插入專案所需資訊
@Project_MultiInsert.post("/multiinsert") ##need to edit
def multiinsert_projects(data: DataModelIn=Body(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    logger.info(f"***********insert_multiple projects*************")
    checked=True

    insert_data = data.model_dump()
    project_name = insert_data['project_name']
    join_type = insert_data['join_type']
    join_func = insert_data['join_func']

    logger.info(insert_data)
    logger.info('-----------------')
    #check parameter is null?
    if project_name == '': 
        msg = 'project_name不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  join_type== '':
        msg = 'join_type不能為空值' 
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

    #def更新multi table 資訊 
    Project_join_type = db.query(Project).filter(Project.project_id == project_id).first()
    Project_join_type.aes_col = insert_data['aes_col']
    Project_join_type.jointablecount = insert_data['jointablecount'] #
    Project_join_type.jointablename = insert_data['jointablename']
    Project_join_type.join_func = join_type
    Project_join_type.updatetime = datetime.now()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Member  update multiple table failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)



    # project_id =db.query(Project).order_by(Project.project_id.desc()).first().project_id +1
    try:
        for join_func_id in join_func:
            l_group_id = join_func_id['left_datasetname'].split('_')[0]
            r_group_id = join_func_id['right_datasetname'].split('_')[0]
            logger.info(join_func_id)
            db_ProjectJoinFunc = ProjectJoinFunc()
            db_ProjectJoinFunc.left_group_id = db.query(Group).filter(Group.group_type == l_group_id).first().id
            db_ProjectJoinFunc.left_dataset = join_func_id['left_datasetname']
            db_ProjectJoinFunc.left_col= join_func_id['left_col']
            db_ProjectJoinFunc.right_group_id = db.query(Group).filter(Group.group_type == r_group_id).first().id
            db_ProjectJoinFunc.right_dataset= join_func_id['right_datasetname']
            db_ProjectJoinFunc.right_col= join_func_id['right_col']
            db_ProjectJoinFunc.project_id = project_id
            db_ProjectJoinFunc.createtime = datetime.now()
            db_ProjectJoinFunc.createMember_Id  = member_id
            db.add(db_ProjectJoinFunc)
            db.commit()
    except Exception as e:
        # check_result = del_api(project_id)
        db.rollback()
        msg = f"Member insert join_func table fail: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


    try: #要寫狀態嗎?
        db_ProjectStatus = db.query(ProjectStatus).filter_by(project_id=project_id).first()
        if db_ProjectStatus:
            db_ProjectStatus.project_status = 1
            db_ProjectStatus.createtime = datetime.now()
            db_ProjectStatus.createMember_Id = member_id
        else:
            db_ProjectStatus = ProjectStatus()
            db_ProjectStatus.project_id = project_id
            db_ProjectStatus.project_status = 1
            db_ProjectStatus.createtime = datetime.now()
            db_ProjectStatus.createMember_Id = member_id
            db.add(db_ProjectStatus)
        db.commit()
    except Exception as e:
        # check_result = del_api(project_id)
        db.rollback()
        msg = f"Member insert project_status table fail: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    
    
    msg = f"Member  insert_multi_project_information successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
