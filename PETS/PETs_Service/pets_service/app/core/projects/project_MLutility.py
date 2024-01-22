# -*- coding: utf-8 -*-
from fastapi import Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from logging.config import dictConfig
import logging

import configparser

from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole,ViewsDetails
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

import base64
import json
import subprocess


Project_MLutility = APIRouter() ##need to edit

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

security = HTTPBearer(description="HTTP Bearer token scheme")


@Project_MLutility.post("/mlutility")
def mlutility(project_id:int, member_id:int, project_name:str, privacy_type:str, target_cols:str):
    config_file = '/usr/src/app/config/Hadoop_information.txt'
    config = configparser.ConfigParser()
    config.read(config_file)
    ip = config.get('Hadoop_information', 'host_ip')
    #ip = '34.81.71.21' #'34.80.229.221'
    port = '5088'
    logger.info("----------------------Project_MLutility----------------------")
    input_ = {}
    input_['projID'] = project_id
    input_['userID'] = member_id
    input_['projName'] = project_name
    input_['privacyType'] = privacy_type
    input_['targetCols'] = [col.strip() for col in target_cols.split(',')]

    # Convert dictionary to JSON string
    json_string = json.dumps(input_)
    # Encode JSON string to base64
    base64_encoded = base64.b64encode(json_string.encode()).decode()

    curl_command = 'curl -H "Content-Type: application/json" -X POST -d \'{"jsonBase64":"'+base64_encoded+'"}\' "http://'+ip+':'+port+'/PETs_MLutility_async"'
    logger.info(curl_command)

    # Run the cURL command using subprocess
    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get the output
    stdout, stderr = process.communicate()

    stdout_str = stdout.decode().replace('\n', '').replace('\\"', '"')
    stdout_dict = json.loads(stdout_str)

    result = {}
    if stdout_dict['celeryId']!="":
        result['status'] = 1
        result['msg'] = 'PETs_MLutility is operating'
        result['obj'] = stdout_dict
    else:
        result['status'] = -1
        result['msg'] = 'PETs_MLutility error'
        result['obj'] = stdout_dict

    return result