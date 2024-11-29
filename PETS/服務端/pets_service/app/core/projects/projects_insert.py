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

Project_Insert = APIRouter() ##need to edit

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

# def del_api(project_id):
#     logger.info('********del_pets_api*******')
#     file_ = '/usr/src/app/app/core/projects/delete_config.txt'
#     config = configparser.ConfigParser()
#     config.read(file_)
#     pets_ip = config.get('delete_config', 'pets_ip') 
#     pets_port = config.get('delete_config', 'pets_port') 

#     delProject_para = { "project_id": project_id}
#     response_get = requests.post("http://"+pets_ip+":"+pets_port+"/projects/delete", params=delProject_para, verify=False)
#     logger.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
#     logger.info(response_get.url)

#     try:
#         response = dict()
#         delProject_para = { "project_id": project_id}
#         #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*', 'Connection': 'keep-alive'}
#         response_get = requests.post("http://"+pets_ip+":"+pets_port+"/projects/delete", params=delProject_para, verify=False)
#         logger.info('********del_pets_api*******')
#         logger.info(response_get.url)
#         response_dic = response_get.json()
#         #print("response_get: ",response_dic)
#         response['Delete_Project_flag']=response_dic
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         print(response)
#         #log_time.printLog(errMsg)
#         #return make_response(jsonify(response))
#     return(response)

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
    group_id : int
    aes_col: str
    jointablecount:int
    jointablename:str
    project_role: List[Dict] #List[ProjectRole]
    join_func:List[Dict] #List[Join_func]
    # @model_validator(mode='before')
    # @classmethod
    # def validate_to_json(cls, value):
    #     if isinstance(value, str):
    #         return cls(**json.loads(value))
    #     return value

## 使用者登入後，從專案列表，選取對應的專案，插入專案所需資訊
@Project_Insert.post("/insert") ##need to edit
def insert_projects(data: DataModelIn=Body(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
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
    join_type = insert_data['join_type']
    group_id = insert_data['group_id']
    project_role = insert_data['project_role']
    join_func = insert_data['join_func']

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
    elif  join_type== '':
        msg = 'join_type不能為空值' 
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
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

    try:
        #先 insert T_Pets_Project
        db_Project = Project()
        #db_Project.project_id = db.query(Project).order_by(Project.project_id.desc()).first().project_id +1 
        db_Project.project_name = project_name
        db_Project.project_eng = insert_data['project_eng']
        db_Project.project_desc = insert_data['project_desc']
        db_Project.createtime = datetime.now()
        db_Project.enc_key = insert_data['enc_key']
        db_Project.join_func =  insert_data['join_type']
        db_Project.createMember_Id = member_id 
        db_Project.group_id = insert_data['group_id'] #
        db_Project.aes_col = insert_data['aes_col']
        db_Project.jointablecount = insert_data['jointablecount'] #
        db_Project.jointablename = insert_data['jointablename']

        db.add(db_Project)
        db.commit()        
    except Exception as e:
        db.rollback()
        msg = f"Member insert Project table fail: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)




    project_id = db.query(Project).filter(Project.project_name == project_name).first().project_id

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


    try:
        for project_role_id in project_role:
            # logger.info(project_role_id)
            db_MemberProjectRole = MemberProjectRole()
            db_MemberProjectRole.project_role = project_role_id['member_role']
            db_MemberProjectRole.project_id = project_id
            db_MemberProjectRole.member_id = project_role_id['member_id']
            db_MemberProjectRole.createtime = datetime.now()
            db_MemberProjectRole.createmember_id = member_id
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
    
    # try:
    #     db.add(db_Project)
    #     db.add(db_ProjectJoinFunc)
    #     db.add(db_MemberProjectRole)
    #     db.add(db_ProjectStatus)
    #     db.commit()
    # except Exception as e:
    #     db.rollback()
    #     msg = f"Member insert projects failed###: {str(e)}"
    #     logger.error(msg)
    #     result = Result(msg=msg, status=False)
    #     return _result_wrapper(result, status_code=400)
    
    msg = f"Member  insert_projects successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
