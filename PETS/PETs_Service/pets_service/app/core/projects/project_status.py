from fastapi import Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from logging.config import dictConfig
import logging

from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup, Result_P
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group,get_status,get_status_name



status = APIRouter()

@status.get('/status')
def get_project_status(project_id:int,db:Session = Depends(get_db)):
    checked, proj_sta_ser = get_status(project_id, db)
    if not checked:
        message = str(proj_sta_ser)
        msg = f"get project {project_id} status failed: {message}"
        print(msg)
        result = Result_P(msg=msg, status=-1)
        return _result_wrapper(result, status_code=400)
    elif proj_sta_ser['project_status'] > 9 or proj_sta_ser['project_status'] <0 :
        msg = f"project id {project_id} status error, do not exist project status {proj_sta_ser['project_status']}"
        proj_sta_ser['status'] = proj_sta_ser.pop('project_status')
        result = Result_P(msg=msg, obj=proj_sta_ser, status=-2)
        return _result_wrapper(result, status_code=400)
    else:
        msg = f"get project {project_id} status successful"
        print(msg)
        status_name = get_status_name(proj_sta_ser)
        proj_sta_ser['status_name'] = status_name
        proj_sta_ser['status'] = proj_sta_ser.pop('project_status')
        result = Result_P(msg=msg, obj=proj_sta_ser, status=0)
        return _result_wrapper(result, status_code=200)
    

