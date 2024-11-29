# -*- coding: utf-8 -*-
from fastapi import Form, Depends, APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from logging.config import dictConfig
import logging

from app.core.config import LogConfig
from app.database import get_db
from app.core.models import Group, Member, AdminRole,FailedLogin, FilePermission
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup, \
    CreateSyslog
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group, get_active_user, db_insert_syslog, db_query_syslog,db_check_member_reference_table_data_exist, \
    db_delete_failed_login,user_is_active, compare ,file_info, get_permission_string
from app.core.projects.monitorContainers import monitor

import os,stat
from stat import *
import subprocess
from sqlalchemy import text

router = APIRouter()

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


@router.get("/")
def hello_world():
    return {"Hello": "World!"}


@router.post("/login")
def login(account: str = Form(), password: SecretStr = Form(), db: Session = Depends(get_db)):
    checked, msg = user_login(account, password.get_secret_value(), db)
    if not checked:
        error_msg = f"Useraccount {account} logging failed: {msg}"
        logger.error(error_msg)
        result = Result(msg=error_msg, status=False)
        return _result_wrapper(result, status_code=400)

    try:
        member_id, jwt_token = gen_jwt_token(account, db)
    except Exception as e:
        error_msg = f"Useraccount {account} gen JWT token failed: {str(e)}"
        logger.error(error_msg)
        result = Result(msg=error_msg, status=False)
        return _result_wrapper(result, status_code=400)
    logger.info(f"Useraccount {account} logging successful")
    result = Result(msg=msg, status=True, obj={"member_id": member_id, "token": jwt_token})
    return _result_wrapper(result, status_code=200)


@router.post("/groups/insert", tags=['group'])
def create_group(group: CreateGroup, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['create_group'], db)
    if not checked:
        msg = f"Create group failed: Member {useraccount} does not have create_group permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    db_group = Group(**group.model_dump(), createmember_id=member_id)
    try:
        db.add(db_group)
        db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Create group failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    db.refresh(db_group)
    group_ser = dict(GroupBase.model_validate(db_group))
    msg = f"Member {useraccount} create group {db_group.group_name} successful"
    logger.info(msg)
    result = Result(msg=msg, obj=group_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/groups/all", tags=['group'])
def list_group(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['group_list'], db)
    if not checked:
        msg = f"List group failed: Member {useraccount} does not have group_list permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    group_list_ser = get_all_group(db)
    msg = f"Member {useraccount} list group successful"
    logger.info(msg)
    result = Result(msg=msg, obj=group_list_ser['root'], status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/groups/users", tags=['group'])
def list_group_user(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = is_group_admin(member_id, db)
    useraccount = decode_info['sub']
    if not checked:
        msg = f"Member {useraccount} list group user failed: Member {useraccount} is not group admin"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    user_list_ser = get_group_users(member_id, db)
    msg = f"Member {useraccount} list group user successful"
    logger.info(msg)
    result = Result(msg=msg, obj=user_list_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/groups/{group_id}", tags=['group'])
def get_group_info(group_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    if is_group_owner(member_id, group_id, db) or check_permissions(member_id, ['group_list'], db):
        checked, group_ser = get_group(group_id, db)
        if not checked:
            message = str(group_ser)
            msg = f"Member {useraccount} get group {group_id} info failed: {message}"
            logger.error(msg)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

        msg = f"Member {useraccount} get group {group_id} info successful"
        logger.info(msg)
        result = Result(msg=msg, obj=group_ser, status=True)
        return _result_wrapper(result, status_code=200)
    else:
        msg = f"Member {useraccount} get group {group_id} info failed: " +\
              "member does not have group_list permission or not group owner"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


@router.put("/groups/update/{group_id}", tags=['group'])
def update_group(group_id: int, modify_group: UpdateGroup, decode_info: dict = Depends(verify_token),
                 db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['update_group'], db)
    if not checked:
        msg = f"Member {useraccount} update group failed: Member {useraccount} does not have update_group permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, group_ser = db_update_group(group_id, member_id, modify_group, db)
    if not checked:
        msg = f"Member {useraccount} update group {group_id} failed: {group_ser}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} update group {group_id} successful"
    logger.info(msg)
    result = Result(msg=msg, obj=group_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.delete("/groups/delete/{group_id}", tags=['group'])
def delete_group(group_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['delete_group'], db)
    if not checked:
        msg = f"Member {useraccount} update delete failed: Member {useraccount} does not have delete_group permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, message = db_delete_group(group_id, db)
    if not checked:
        msg = f"Member {useraccount} delete group {group_id} failed: {message}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} delete group {group_id} successful"
    logger.info(msg)
    result = Result(msg=msg, status=True)
    return _result_wrapper(result, status_code=200)


@router.post("/users/insert", tags=['user'])
def create_user(create_member: CreateMember, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['create_member'], db)
    if not checked:
        msg = f"Member {useraccount} insert user failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    password = gen_default_password()
    hash_password = bcrypt.hash(password)
    create_member_data = create_member.model_dump()
    create_member_data['password'] = hash_password
    create_member_data['createmember_id'] = member_id
    db_user = Member(**create_member_data)

    try:
        db.add(db_user)
        db.commit()
    except Exception as e:
        db.rollback()
        msg = f"Member {useraccount} insert user failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    db.refresh(db_user)
    result_data = {'member_id': db_user.id, 'default_password': password}
    msg = f"Member {useraccount} insert user successful"
    logger.info(msg)
    result = Result(msg=msg, obj=result_data, status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/users/all", tags=['user'])
def list_user(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['user_list'], db)
    if not checked:
        msg = f"List user failed: Member {useraccount} does not have user_list permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    user_list = get_all_user(group_id=None, db=db)
    msg = f"Member {useraccount} list user successful"
    logger.info(msg)
    result = Result(msg=msg, obj=user_list, status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/users/active", tags=['user'])
def list_active_user(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['user_list'], db)
    if not checked:
        msg = f"List active user failed: Member {useraccount} does not have user_list permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    user_list = get_active_user(db=db)
    msg = f"Member {useraccount} list active user successful"
    logger.info(msg)
    result = Result(msg=msg, obj=user_list, status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/users/{member_id}", tags=['user'])
def get_user_info(member_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    jwt_member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(jwt_member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    if jwt_member_id == member_id or check_permissions(jwt_member_id, ['user_list'], db):
        checked, user_ser = get_user(member_id, db)
        if not checked:
            message = str(user_ser)
            msg = f"Member {useraccount} get user {member_id} info failed: {message}"
            logger.error(msg)
            result = Result(msg=msg, status=False)
            return _result_wrapper(result, status_code=400)

        msg = f"Member {useraccount} get user {member_id} info successful"
        logger.info(msg)
        result = Result(msg=msg, obj=user_ser, status=True)
        return _result_wrapper(result, status_code=200)
    else:
        msg = f"Member {useraccount} get user {member_id} info failed: user does not permission or owner"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


@router.put("/users/uppwd", tags=['user'])
def change_password(password: SecretStr = Form(), new_password_1: SecretStr = Form(), new_password_2: SecretStr = Form(),
                    decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked, msg = user_change_password(member_id, password.get_secret_value(), new_password_1.get_secret_value(),
                                        new_password_2.get_secret_value(), db)
    if not checked:
        msg = f"Member {useraccount} change password failed: {msg}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} change password successful"
    logger.info(msg)
    result = Result(msg=msg, status=True)
    return _result_wrapper(result, status_code=200)


@router.delete("/users/delete/{delete_member_id}", tags=['user'])
def delete_user(delete_member_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['create_member'], db)
    if not checked:
        msg = f"Delete user failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    
    refer_info = db_check_member_reference_table_data_exist(delete_member_id,db)
    logger.info('refer info :' + str(refer_info))
        
    if len(refer_info) == 1 and refer_info[0]['table_name'] == FailedLogin.__tablename__:
        db_delete_failed_login(delete_member_id,db)

    checked, message = db_delete_member(delete_member_id, db)
    if not checked:
        msg = f"Member {useraccount} delete member {delete_member_id} failed: {message}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} delete member {delete_member_id} successful"
    logger.info(msg)
    result = Result(msg=msg, status=True)
    return _result_wrapper(result, status_code=200)


@router.put("/users/update/{update_member_id}", tags=['user'])
def update_user(update_member_id: int, update_member: UpdateMember, decode_info: dict = Depends(verify_token),
                db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['create_member'], db)
    if not checked:
        msg = f"Update user failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, member_ser = db_update_member(update_member_id, member_id, update_member, db)
    if not checked:
        msg = f"Member {useraccount} update user {update_member_id} failed: {member_ser}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} update member {update_member_id} successful"
    logger.info(msg)
    result = Result(msg=msg, obj=member_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.put("/users/admin/uppwd", tags=['user'])
def admin_change_password(member_id: int = Form(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    updatemember_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(updatemember_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(updatemember_id, ['create_member'], db)
    if not checked:
        msg = f"Update user password failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, new_password = admin_change_user_password(member_id, updatemember_id, db)
    if not checked:
        message = new_password
        msg = f"Member {useraccount} change password failed: {message}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    result_data = {"member_id": member_id, "new_password": new_password}
    msg = f"Member {useraccount} change member {member_id} password successful"
    logger.info(msg)
    result = Result(msg=msg, obj=result_data, status=True)
    return _result_wrapper(result, status_code=200)


@router.put("/users/deactivate/{member_id}", tags=['user'])
def deactivate_user(member_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    updatemember_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(updatemember_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(updatemember_id, ['create_member'], db)
    if not checked:
        msg = f"Deactivate user failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, msg = db_update_member_status(member_id, updatemember_id, False, db)
    if not checked:
        msg = f"Member {useraccount} deactivate user {member_id} failed: {msg}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} deactivate member {member_id} successful"
    logger.info(msg)
    result = Result(msg=msg, status=True)
    return _result_wrapper(result, status_code=200)


@router.put("/users/activate/{member_id}", tags=['user'])
def activate_user(member_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    updatemember_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(updatemember_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(updatemember_id, ['create_member'], db)
    if not checked:
        msg = f"Activate user failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, msg = db_update_member_status(member_id, updatemember_id, True, db)
    if not checked:
        msg = f"Member {useraccount} activate user {member_id} failed: {msg}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} activate member {member_id} successful"
    logger.info(msg)
    result = Result(msg=msg, status=True)
    return _result_wrapper(result, status_code=200)


@router.post("/roles/set_admin", tags=['role'])
def set_admin_role(insert_admin_role: InsertAdminGroup, decode_info: dict = Depends(verify_token),
                   db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['set_admin'], db)
    if not checked:
        msg = f"Set admin role failed: Member {useraccount} does not have set_admin permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    insert_role_data = insert_admin_role.model_dump()
    member_role = AdminRole[insert_role_data['role_name']].value
    if member_role in [1, 2, 3] and is_super_admin(member_id, db):
        pass
    elif member_role == 3 and is_group_admin(member_id, db):
        pass
    else:
        msg = f"Set admin role failed: Member {useraccount} does not have set {insert_role_data['role_name']} permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    insert_role_data["member_role"] = member_role
    insert_role_data["createmember_id"] = member_id
    checked, admin_role_ser = db_set_admin_role(insert_role_data, db)
    if not checked:
        message = str(admin_role_ser)
        msg = f"Member {useraccount} set {insert_role_data['role_name']} role failed: {message}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} set member {insert_role_data['member_id']} {insert_role_data['role_name']} successful"
    logger.info(msg)
    result = Result(msg=msg, obj=admin_role_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.delete("/roles/delete_admin/{role_id}", tags=['role'])
def delete_admin_role(role_id: int, decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id']
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked = check_permissions(member_id, ['set_admin'], db)
    if not checked:
        msg = f"Delete role failed: Member {useraccount} does not have set_admin permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    checked, message = db_delete_admin_role(role_id, member_id, db)
    if not checked:
        msg = f"Member {useraccount} delete role {role_id} failed: {message}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} delete role {role_id} successful"
    logger.info(msg)
    result = Result(msg=msg, status=True)
    return _result_wrapper(result, status_code=200)


@router.post("/sys/insert", tags=['sys'])
def insert_syslog(create_syslog: CreateSyslog, decode_info: dict = Depends(verify_token),
                   db: Session = Depends(get_db)):
    useraccount = decode_info['sub']
    member_id = decode_info['member_id']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    checked, syslog_ser = db_insert_syslog(create_syslog, db)
    if not checked:
        msg = f"Member {useraccount} insert syslog failed: {syslog_ser}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

    msg = f"Member {useraccount} insert syslog successful"
    logger.info(msg)
    result = Result(msg=msg, obj=syslog_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.get("/sys/syslog", tags=['sys'])
def list_syslog(starttime: datetime = None, endtime: datetime = None, decode_info: dict = Depends(verify_token),
                db: Session = Depends(get_db)):
    useraccount = decode_info['sub']
    member_id = decode_info['member_id']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    if not starttime:
        endtime = datetime.now()
        starttime = endtime - timedelta(days=30)
    elif not endtime:
        endtime = datetime.now()
    list_syslog_ser = db_query_syslog(starttime, endtime, db)
    msg = f"Member {useraccount} list syslog successful"
    logger.info(msg)
    result = Result(msg=msg, obj=list_syslog_ser, status=True)
    return _result_wrapper(result, status_code=200)


@router.get('/sys/file_permssion/{path:path}', tags = ['sys'])
def get_permission(path:str,db:Session = Depends(get_db)):
    if not os.path.exists(path):
        msg = 'Directory not found'
        result = Result(msg = msg , status=False)
        return _result_wrapper(result,status_code=400)
    # if not os.path.isdir(path):
        # raise HTTPException(status_code=400, detail="Path is not a directory")
    try:
        directory_structure = []
        info = os.stat(path)
        directory_structure.append(file_info(info,folder_name=path))
        if  os.path.isdir(path):
            for entry in os.scandir(path):
                directory_structure.append(file_info(entry,path))
        msg = 'Get permission success'
        output = {"path": path, "directory_structure": directory_structure.copy()}
        result = Result(msg = msg , status = True , obj = output)
        return _result_wrapper(result, status_code=200)
    except Exception as e:
        msg = f"file permission error:{str(e)}"
        result = Result(msg = msg , status=False)
        return _result_wrapper(result,status_code=400)




@router.get('/sys/permssion_compare/',tags = ['sys'])
def compare_permission(db:Session = Depends(get_db)):
    # if not os.path.exists(path):
    #     msg = 'Directory not found'
    #     result = Result(msg = msg , status=False)
    #     return _result_wrapper(result,status_code=400)
    # if not os.path.isdir(path):
    #     raise HTTPException(status_code=400, detail="Path is not a directory")
    try:
        directory_structure = []
        path_list = [
                    # '/usr/src/app/app/core/',
                    # '/usr/src/app/app/core/schemas.py',
                    # '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/MariaDBdata/',
                    '/usr/src/app/mount_folder/pets_service/sftp_upload_folder/',
                    '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/data/',
                    '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/',
                    '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre/',
                    '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirN/',
                    '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirD/',
                    '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/MariaDBdata/',
                    '/usr/src/app/mount_folder/pets_dp/pets_dp/sourceCode/DP_webService/APP__/export_fordp/',
                    '/usr/src/app/mount_folder/pets_dp/pets_dp/sourceCode/DP_webService/APP__/folderForSynthetic/',
                    '/usr/src/app/mount_folder/pets_dp/pets_dp/sourceCode/DP_webService/APP__/user_upload_folder/',
                    '/usr/src/app/mount_folder/pets_syn/pets_syn/sourceCode/webService/APP__/folderForSynthetic/',
                    '/usr/src/app/mount_folder/pets_syn/pets_syn/sourceCode/webService/APP__/user_upload_folder/',
                    '/usr/src/app/mount_folder/pets_syn/pets_syn/sourceCode/webService/APP__/PETs_data/',
                    '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/data/',
                    '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre/',
                    '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/masterDirN/',
                    '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/masterDirD/',
                    '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/ssh_conf/',
                    '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/spark_conf/',
                    '/usr/src/app/mount_folder/pets_web/download_folder/',
                    '/usr/src/app/mount_folder/pets_web/download_folder/dec/k/',
                    '/usr/src/app/mount_folder/pets_web/download_folder/enc/k/',
                    '/usr/src/app/mount_folder/pets_web/download_folder/enc/dp/',
                    '/usr/src/app/mount_folder/pets_web/download_folder/enc/syn/',
                     ]

        if path_list == []:
            msg = 'Directory not found'
            result = Result(msg = msg , status=True)
            return _result_wrapper(result,status_code=400)
        not_match = []
        match_data = []
        for p in path_list:
            data = db.query(FilePermission).filter(FilePermission.folder_name == p).first()
            info = os.stat(p)
            directory_structure = file_info(info,folder_name=p)
            output = compare(data,directory_structure)
            if output != 'match':
                not_match.append(output)
            else:
                match_data.append(directory_structure)
        
        # error = 'error'
        # error +=1
        # line = path.split('/')
        # if path.endswith('/'):
        #     filename = line[-2]
        # else:
        #     filename = line[-1]
        # data = db.query(FilePermission).filter(FilePermission.file_name == filename).first()
        # info = os.stat(path)
        # directory_structure.append(file_info(info,name=path))
        # lookup_permission = directory_structure[0]['permissions']
        # not_match = compare(data.permissions,lookup_permission)

    except Exception as e:
        msg = f"compare permission error:{str(e)} data={str(data)}"
        # result = Result(msg = msg , status=False)
        result = {
            "msg":msg,
            "status":True,
            "is_match":True,
            "obj" :[]
        }
        return _result_wrapper(result,status_code=200)
    
    if not_match != []:
        msg = 'Not match,' + ';'.join(not_match) 
        # result = Result(msg = msg , status = False)
        result = {
            "msg":msg,
            "status":True,
            "is_match":True,
            "obj" :[]
        }
        return _result_wrapper(result, status_code=200)
    else:
        msg = 'Permission match'
        for i in range(len(match_data)):
            match_data[i]['is_match'] = True
        # result = Result(msg = msg , status=True,obj = match_data)
        result = {
            "msg":msg,
            "status":True,
            "is_match":True,
            "obj": match_data
        }
        return _result_wrapper(result,status_code=200)



@router.get('/sys/check_db/',tags = ['sys'])
def db_check(db:Session = Depends(get_db)):
    try:
        nonexist_table = []
        table_dict = {'DeIdService': ['T_Dept', 'T_GroupMember', 'T_Member', 'T_originTable', 'T_Project', 'T_ProjectDataFilter', 'T_ProjectJobStatus', 'T_ProjectSampleData', 
                                      'T_ProjectStatus', 'T_Project_FinalTable', 'T_Project_NumStatValue', 'T_Project_RiskTable', 'T_Project_SampleTable', 'T_Project_SparkStatus_Management', 
                                      'T_Project_SysStep_Config', 'T_Pro_DistinctTB', 'T_SystemSetting', 'T_utilityResult'], 
                      'DpService': ['T_CeleryStatus', 'T_Dept', 'T_GANStatus', 'T_Member', 'T_originTable', 'T_Project', 'T_ProjectColumnType', 'T_ProjectGetFolder', 'T_ProjectJobStatus', 
                                    'T_ProjectSample5Data', 'T_ProjectSampleData', 'T_ProjectStatus', 'T_Project_FinalTable', 'T_Project_NumStatValue', 'T_Project_SampleTable', 'T_Project_SparkStatus_Management', 
                                    'T_Project_SysStep_Config', 'T_Pro_DistinctTB', 'T_SystemSetting', 'T_utilityResult'], 
                      'PetsService': ['T_Pets_FailedLogin', 'T_Pets_folder_Permission', 'T_Pets_Group', 'T_Pets_HistoryProject', 'T_Pets_JobSyslog', 'T_Pets_Member', 'T_Pets_MemberGroupRole', 
                                      'T_Pets_MemberProjectRole', 'T_Pets_Permission', 'T_Pets_Project', 'T_Pets_ProjectJoinFunc', 'T_Pets_ProjectStatus', 'T_Pets_RolePermission', 'T_Pets_Syslog', 
                                      'T_Pets_UtilityResult', 'T_Pets_UtilityResult', 'T_Pets_UtilityResult'], 
                      'spark_status': ['appStatus', 'nodeStatus'], 
                      'SynService': ['T_CeleryStatus', 'T_Dept', 'T_GANStatus', 'T_Group', 'T_GroupMember', 'T_Member', 'T_originTable', 'T_Project', 'T_ProjectColumnType', 'T_ProjectGetFolder', 
                                     'T_ProjectJobStatus', 'T_ProjectSample5Data', 'T_ProjectSampleData', 'T_ProjectStatus', 'T_Project_FinalTable', 'T_Project_JoinMember', 'T_Project_NumStatValue', 
                                     'T_Project_SampleTable', 'T_Project_SparkStatus_Management', 'T_Project_SysStep_Config', 'T_Pro_DistinctTB', 'T_SystemSetting', 'T_utilityResult']}
        
        # table_dict['SynService'].append('test_error')
        
        for key in table_dict.keys():
            for table_name in table_dict[key]:
                query = text(f"""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = '{key}' AND TABLE_NAME = '{table_name}';
                """)

                result = db.execute(query).fetchone()
                
                if not result:
                    nonexist_table.append({key:table_name})

        
        if nonexist_table != []:
            msg = f'db_error : table {nonexist_table} do not exist'
            result = {
                "msg":msg,
                "status":True,
                "is_ready":False,
                "obj" :[]
            }

            return _result_wrapper(result,status_code=200)

        else:
            msg = f'DB is ready'
            result = {
                "msg":msg,
                "status":True,
                "is_ready":True,
                "obj" :[table_dict]
            }
            return _result_wrapper(result,status_code=200)
    
    except Exception as e:
        msg = f'db_error : {str(e)}'
        result = {
            "msg":msg,
            "status":False,
            "obj" :[]
        }
        return _result_wrapper(result,status_code=200)
    
    
        





@router.put('/sys/add_permission/',tags = ['sys'])
def Add_permission(db:Session = Depends(get_db)):
    # if not os.path.exists(path):
    #     msg = 'Directory not found'
    #     result = Result(msg = msg , status=False)
    #     return _result_wrapper(result,status_code=400)
    # if not os.path.isdir(path):
    #     raise HTTPException(status_code=400, detail="Path is not a directory")
    try:
        # directory_structure = []
        path_list = [
                     #'/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/MariaDBdata/',
                     '/usr/src/app/mount_folder/pets_service/sftp_upload_folder/',
                     '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/data/',
                     '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/',
                     '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre/',
                     '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirN/',
                     '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirD/',
                     '/usr/src/app/mount_folder/pets_hadoop/pets_v1/sourceCode/hadoop/MariaDBdata/',
                     '/usr/src/app/mount_folder/pets_dp/pets_dp/sourceCode/DP_webService/APP__/export_fordp/',
                     '/usr/src/app/mount_folder/pets_dp/pets_dp/sourceCode/DP_webService/APP__/folderForSynthetic/',
                     '/usr/src/app/mount_folder/pets_dp/pets_dp/sourceCode/DP_webService/APP__/user_upload_folder/',
                     '/usr/src/app/mount_folder/pets_syn/pets_syn/sourceCode/webService/APP__/folderForSynthetic/',
                     '/usr/src/app/mount_folder/pets_syn/pets_syn/sourceCode/webService/APP__/user_upload_folder/',
                     '/usr/src/app/mount_folder/pets_syn/pets_syn/sourceCode/webService/APP__/PETs_data/',
                     '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/data/',
                     '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre/',
                     '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/masterDirN/',
                     '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/masterDirD/',
                     '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/ssh_conf/',
                     '/usr/src/app/mount_folder/pets_k/pets_v1/sourceCode/hadoop/spark_conf/',
                     '/usr/src/app/mount_folder/pets_web/download_folder/',
                     '/usr/src/app/mount_folder/pets_web/download_folder/dec/k/',
                     '/usr/src/app/mount_folder/pets_web/download_folder/enc/k/',
                     '/usr/src/app/mount_folder/pets_web/download_folder/enc/dp/',
                     '/usr/src/app/mount_folder/pets_web/download_folder/enc/syn/',
                     ]
        # path_list = ['/usr/src/app/app/core/',
        #              '/usr/src/app/app/core/schemas.py']
        # path_list = ['/usr/src/app/app/core/crud.py']
        if path_list == []:
            msg = 'Directory not found'
            result = Result(msg = msg , status=False)
            return _result_wrapper(result,status_code=400)
        not_match = []
        err = ''
        for p in path_list:
            err += 'file = ' + p + ' '
            info = os.stat(p)
            directory_structure = file_info(info,folder_name=p)
            data = FilePermission()
            data.folder_name = directory_structure['folder_name']
            data.permissions = directory_structure['permissions']
            data.group = directory_structure['group']
            data.owner = directory_structure['owner']
            data.is_directory = directory_structure['is_directory']
            err+= 'info = ' +str(info) + '  '
            db.add(data)
            db.commit()
        

    except Exception as e:
        msg = f"add permission error:{str(e)}  err = {err}"
        result = Result(msg = msg , status=False)
        return _result_wrapper(result,status_code=400)
    
    if not_match != []:
        msg = 'Not match,' + ';'.join(not_match) 
        result = Result(msg = msg , status = False)
        return _result_wrapper(result, status_code=200)
    else:
        msg = 'add Permission success'

        result = Result(msg = msg , status=True)
        return _result_wrapper(result,status_code=200)

router.include_router(monitor,prefix = '/sys',tags = ['sys'])