# -*- coding: utf-8 -*-
from fastapi import Body, Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from logging.config import dictConfig
import logging
import json
from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole,ViewsDetails,ProjectJoinFunc,HistoryProject,JobSyslog
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

from datetime import datetime, timedelta

import os
runcode = os.system('pip install requests')

import requests
import configparser 
import subprocess

from pydantic import (
    BaseModel,
)
from typing import Optional, Union, List
from typing import (
    Dict,
    List,
    Optional,
)  

Project_Delete = APIRouter() ##need to edit

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
def check_k_pid_api(project_name):
    print('********check_k_api*******')
    file_ = '/usr/src/app/app/core/projects/delete_config.txt'
    config = configparser.ConfigParser()
    config.read(file_)
    k_web_ip = config.get('delete_config', 'k_web_ip') 
    k_web_port = config.get('delete_config', 'k_web_port') 
    try:
        response = dict()
        Project_para = { "project_name": project_name}
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*', 'Connection': 'keep-alive'}
        response_get = requests.get("https://"+k_web_ip+":"+k_web_port+"/api/WebAPI/k_checkstatus", params=Project_para, verify=False)
        print(response_get.url)
        response_dic = response_get.json()
        #print("response_get: ",response_dic[0])
        response['status'] = response_dic[0].get('status') #0:fail, 1:sucess
        response['project_id'] = response_dic[0].get('obj').get('project_id')
        return(response)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        print(response)
        return(response)

def check_syn_pid_api(project_name):
    print('********check_syn_api*******')
    file_ = '/usr/src/app/app/core/projects/delete_config.txt'
    config = configparser.ConfigParser()
    config.read(file_)
    syn_web_ip = config.get('delete_config', 'syn_web_ip') 
    syn_web_port = config.get('delete_config', 'syn_web_port') 
    try:
        response = dict()
        Project_para = { "project_name": project_name}
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*', 'Connection': 'keep-alive'}
        response_get = requests.get("http://"+syn_web_ip+":"+syn_web_port+"/api/WebAPI/syn_checkstatus", params=Project_para, verify=False)
        print(response_get.url)
        response_dic = response_get.json()
        #print("response_get: ",response_dic[0])
        response['status'] = response_dic[0].get('status') #0:fail, 1:sucess
        response['project_id'] = response_dic[0].get('obj').get('project_id')
        return(response)
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        print(response)
        return(response)

def del_k_api(project_id):
    print('********del_k_api*******')
    file_ = '/usr/src/app/app/core/projects/delete_config.txt'
    config = configparser.ConfigParser()
    config.read(file_)
    k_web_ip = config.get('delete_config', 'k_web_ip') 
    k_web_port = config.get('delete_config', 'k_web_port') 

    try:
        response = dict()
        delProject_para = { "project_id": project_id}
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*', 'Connection': 'keep-alive'}
        response_get = requests.get("https://"+k_web_ip+":"+k_web_port+"/api/WebAPI/DeleteProject", params=delProject_para, verify=False)
        print(response_get.url)
        response_dic = response_get.json()
        #print("response_get: ",response_dic)
        response['Delete_k_Project_flag']=response_dic
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        print(response)
        #log_time.printLog(errMsg)
        #return make_response(jsonify(response))

    return(response)



def del_syn_api(project_id):
    file_ = '/usr/src/app/app/core/projects/delete_config.txt'
    config = configparser.ConfigParser()
    config.read(file_)
    syn_web_ip = config.get('delete_config', 'syn_web_ip') 
    syn_web_port = config.get('delete_config', 'syn_web_port')  

    print('*******del_syn_api*******')
    try:
        response = dict()
        delProject_para = { "project_id": project_id}
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*', 'Connection': 'keep-alive'}
        response_get = requests.get("http://"+syn_web_ip+":"+syn_web_port+"/api/WebAPI/DeleteProject", params=delProject_para, verify=False)
        print(response_get.url)
        response_dic = response_get.json()
        #print("response_get: ",response_dic)
        response['Delete_syn_Project_flag']=response_dic
    except Exception as e:
        response = dict()
        errMsg = 'request_error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        print(response)

    return(response)

def delete_folder(project_name):
    file_ = '/usr/src/app/app/core/projects/delete_config.txt'
    config = configparser.ConfigParser()
    config.read(file_)

    ip = config.get('delete_config', 'ip')
    port = config.get('delete_config', 'port')
    user = config.get('delete_config', 'user')
    passwd = config.get('delete_config', 'passwd')

    # 34.81.71.21 final_project:
    #data:chmod 777 -R?
    pets_hadoop_in = config.get('delete_config', 'pets_hadoop_in')
    pets_hadoop_out = config.get('delete_config', 'pets_hadoop_out')
    pets_final_k_in = config.get('delete_config', 'pets_final_k_in')
    pets_final_k_out = config.get('delete_config', 'pets_final_k_out')
    pets_final_syn_in = config.get('delete_config', 'pets_final_syn_in')
    pets_final_syn_out =config.get('delete_config', 'pets_final_syn_out')
    pets_download_enc = config.get('delete_config', 'pets_download_enc')
    pets_upload =config.get('delete_config', 'pets_upload')
    user_upload_folder = config.get('delete_config', 'user_upload_folder')
    folderForSynthetic = config.get('delete_config', 'folderForSynthetic')

    pets_hadoop_in_dir = f'{pets_hadoop_in}{project_name}'
    pets_hadoop_out_dir = f'{pets_hadoop_out}{project_name}'
    pets_final_k_in_dir = f'{pets_final_k_in}{project_name}'
    pets_final_k_out_dir = f'{pets_final_k_out}{project_name}'
    pets_final_syn_in_dir = f'{pets_final_syn_in}{project_name}'
    pets_final_syn_out_dir = f'{pets_final_syn_out}{project_name}'
    pets_download_enc_dir = f'{pets_download_enc}{project_name}'
    pets_upload_dir = f'{pets_upload}{project_name}'
    user_upload_folder_dir = f'{user_upload_folder}{project_name}'
    folderForSynthetic_dir = f'{folderForSynthetic}{project_name}'

    delete_dirs = [pets_hadoop_in_dir, pets_hadoop_out_dir, pets_final_k_in_dir, 
    pets_final_k_out_dir, pets_final_syn_in_dir, pets_final_syn_out_dir,
    pets_download_enc_dir, pets_upload_dir, user_upload_folder_dir,folderForSynthetic_dir ]

    try:
        for exec_cmd in delete_dirs:
            cmd = 'sshpass -p \"'+passwd+'\" ssh -o StrictHostKeyChecking=no -p 22 '+user+'@'+ip+ ' sudo chown -R ubuntu:ubuntu '+exec_cmd+'/'
            runcode = os.system(cmd)
            logger.info(f'==============delete_folder===={cmd}==========')
            rm_cmd = f'sshpass -p "{passwd}" ssh -o StrictHostKeyChecking=no -p {port} {user}@{ip} rm -r  {exec_cmd}'
            proc = subprocess.Popen(rm_cmd, shell=True,stdout=subprocess.PIPE)
            logger.info(f'==============delete_folder===={exec_cmd}==========')
        return True
    except Exception as e:
        msg = f"delete project failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

## 使用者登入後，從專案列表，選取對應的專案，插入專案所需資訊
@Project_Delete.post("/delete") ##need to edit
def delete_projects(project_id: int = Form(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    logger.info(f"***********delete_projects*************")
    checked=True

    try:
        #用PID去串project
        db_HistoryProject = HistoryProject()
        #db_HistoryProject.project_id = project_id
        db_HistoryProject.project_name = db.query(Project).filter(Project.project_id == project_id).first().project_name
        db_HistoryProject.project_eng =  db.query(Project).filter(Project.project_id == project_id).first().project_eng
        db_HistoryProject.project_desc = db.query(Project).filter(Project.project_id == project_id).first().project_desc
        db_HistoryProject.createtime = datetime.now()
        db_HistoryProject.enc_key = db.query(Project).filter(Project.project_id == project_id).first().enc_key
        db_HistoryProject.jointablename  = db.query(Project).filter(Project.project_id == project_id).first().jointablename
        db_HistoryProject.jointablecount = db.query(Project).filter(Project.project_id == project_id).first().jointablecount
        db_HistoryProject.join_func = db.query(Project).filter(Project.project_id == project_id).first().join_func
    
        join_func_content_all= db.query(ProjectJoinFunc).filter(ProjectJoinFunc.project_id == project_id).all()
        join_func_content = dict()
        i = 0
        for row in join_func_content_all:
            join_func_content[str(i)] = dict()
            join_func_content[str(i)]['left_group_id'] = row.left_group_id
            join_func_content[str(i)]['left_dataset'] = row.left_dataset
            join_func_content[str(i)]['left_col'] = row.left_col
            join_func_content[str(i)]['right_group_id'] = row.right_group_id
            join_func_content[str(i)]['right_dataset'] = row.right_dataset
            join_func_content[str(i)]['right_col'] = row.right_col
            i= i+1

        db_HistoryProject.join_func_content = json.dumps(join_func_content)

        MemberProjectRole_all= db.query(MemberProjectRole).filter(MemberProjectRole.project_id == project_id).all()
        project_role_content = dict()
        i = 0
        for row in MemberProjectRole_all:
            project_role_content[str(i)] = dict()
            project_role_content[str(i)]['project_role'] = row.project_role
            project_role_content[str(i)]['member_id'] = row.member_id
            project_role_content[str(i)]['createmember_id'] = row.createmember_id
            project_role_content[str(i)]['updatemember_id'] = row.updatemember_id
            # project_role_content[str(i)]['createtime'] = row.createtime
            # project_role_content[str(i)]['updatetime'] = row.updatetime
            i= i+1

        db_HistoryProject.project_role_content = json.dumps(project_role_content)


        db_HistoryProject.group_id = db.query(Project).filter(Project.project_id == project_id).first().group_id
        db_HistoryProject.createMember_Id = member_id
        db_HistoryProject.aes_col = db.query(Project).filter(Project.project_id == project_id).first().aes_col
        db.add(db_HistoryProject)
        db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Member {useraccount} delete project {project_id} failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    #delete records==pid
    try:
        db_JobSyslog = db.query(JobSyslog).filter(JobSyslog.project_id == project_id).all() 
        for row in db_JobSyslog:
            db.delete(row)
            db.commit() 

        db_join_func_content= db.query(ProjectJoinFunc).filter(ProjectJoinFunc.project_id == project_id).all() 
        for row in db_join_func_content:
            db.delete(row)
            db.commit() 

        db_MemberProjectRole = db.query(MemberProjectRole).filter(MemberProjectRole.project_id == project_id).all() 
        for row in db_MemberProjectRole:
            db.delete(row)
            db.commit() 
        
        db_ProjectStatus = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).all() 
        for row in db_ProjectStatus:
            db.delete(row)
            db.commit() 

        db_Project= db.query(Project).filter(Project.project_id == project_id).all() 
        for row in db_Project:
            db.delete(row) 
            db.commit()       
    except Exception as e:
        db.rollback()
        msg = f"Member {useraccount} delete project {project_id} failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} delete_projects {project_id} successful (History)"
    logger.info(msg)

    project_name = db_HistoryProject.project_eng

    obj=dict()
    check_result = check_k_pid_api(project_name)
    if check_result['status'] == 1:
        project_id_k = check_result['project_id']
        result_k = del_k_api(project_id_k)
        print(result_k)
        obj['Delete_k_Project_flag'] = result_k['Delete_k_Project_flag']
    else:
        obj['Delete_k_Project_flag']=False

    check_result = check_syn_pid_api(project_name)
    if check_result['status'] == 1:
        project_id_syn = check_result['project_id']
        result_syn = del_syn_api(project_id_syn)
        print(result_syn)
        obj['Delete_syn_Project_flag']=result_syn['Delete_syn_Project_flag']
    else:
        obj['Delete_syn_Project_flag']=False

    result_del = delete_folder(project_name)
    print(result_del)
    obj['Delete_folder_flag']=result_del

    result = Result(msg=msg, MemberID=member_id, status=checked, obj=obj)
    #result = Result(msg=msg, MemberID=member_id, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
