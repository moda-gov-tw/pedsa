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
import random
import string
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

Project_Save = APIRouter() ##need to edit

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
    project_name: str #專案名稱
    project_eng: str #專案資料夾
    project_desc: Optional[str] = None
    enc_key: str #金鑰
    #join_type: int
    group_id : int
    #aes_col: str
    #jointablecount:int
    #jointablename:str
    project_role: List[Dict] #List[ProjectRole]
    #join_func:List[Dict] #List[Join_func]
    issingle: int #1:單一資料集;0:multi dataset 

def generate_key_code():
    # 隨機選擇一個大寫字母作為第一個字元
    first_char = random.choice(string.ascii_uppercase)
    # 剩下的 4 個字元為隨機數字或大寫字母
    remaining_digits = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return first_char + remaining_digits

def generate_unique_key_code(existing_codes):
    while True:
        key_code = generate_key_code()
        if key_code not in existing_codes:
            return key_code

## 使用者登入後，從專案列表，選取對應的專案，插入專案所需資訊
@Project_Save.post("/projectsave") ##need to edit
def save_projects(data: DataModelIn=Body(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    logger.info(f"***********insert_projects*************")
    checked=True

    insert_data = data.model_dump()
    project_name = insert_data['project_name']
    project_eng = insert_data['project_eng']
    project_desc = insert_data['project_desc']
    enc_key = insert_data['enc_key']
    # join_type = insert_data['join_type']
    group_id = insert_data['group_id']
    project_role = insert_data['project_role']
    # join_func = insert_data['join_func']
    issingle = insert_data['issingle']

    logger.info(insert_data)
    logger.info('-----------------')
    #check parameter is null?
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
    # elif  join_type== '':
    #     msg = 'join_type不能為空值' 
    #     logger.error(msg)
    #     result = Result(msg=msg, status=False)
    #     return _result_wrapper(result, status_code=400)
    elif  group_id== '':
        msg = 'group_id不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    elif  project_role== '':
        msg = 'project_role不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    # elif  join_func== '':
    #     msg = 'join_func不能為空值' 
    #     logger.error(msg)
    #     result = Result(msg=msg, status=False)
    #     return _result_wrapper(result, status_code=400)
    elif  issingle== '':
        msg = 'issingle不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    try:
        #先 insert T_Pets_Project
        db_Project = Project()
        #db_Project.project_id = db.query(Project).order_by(Project.project_id.desc()).first().project_id +1 
        db_Project.project_name = project_name
        db_Project.project_eng = insert_data['project_eng']
        db_Project.project_desc = insert_data['project_desc']
        db_Project.createtime = datetime.now()
        db_Project.enc_key = insert_data['enc_key']
        # db_Project.join_func =  insert_data['join_type']
        db_Project.createMember_Id = member_id 
        db_Project.group_id = insert_data['group_id'] #
        # db_Project.aes_col = insert_data['aes_col']
        # db_Project.jointablecount = insert_data['jointablecount'] #
        # db_Project.jointablename = insert_data['jointablename']
        db_Project.issingle = insert_data['issingle']
        db.add(db_Project)
        db.commit()        
    except Exception as e:
        db.rollback()
        msg = f"Member insert Project table fail: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    project_id = db.query(Project).filter(Project.project_name == project_name).first().project_id

    try:
        for project_role_id in project_role:
            # logger.info(project_role_id)
            db_MemberProjectRole = MemberProjectRole()
            db_MemberProjectRole.project_role = project_role_id['member_role']
            db_MemberProjectRole.project_id = project_id
            db_MemberProjectRole.member_id = project_role_id['member_id']
            db_MemberProjectRole.createtime = datetime.now()
            db_MemberProjectRole.createmember_id = member_id

            #產生key_code，但不能重複
            all_key_code = db.query(MemberProjectRole).filter().all()
            db_MemberProjectRole.key_code = generate_unique_key_code(all_key_code)

            db.add(db_MemberProjectRole)
            db.commit()
    except Exception as e:
        # check_result = del_api(project_id)
        db.rollback()
        msg = f"Member insert project_role table fail: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    try:
        db_ProjectStatus = ProjectStatus()
        db_ProjectStatus.project_id = project_id
        db_ProjectStatus.project_status = 0
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
    
    msg = f"Member save_project_information successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
