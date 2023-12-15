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
from app.core.models import Group, Member, AdminRole
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup, \
    CreateSyslog
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group, get_active_user, db_insert_syslog, db_query_syslog

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
    checked = check_permissions(member_id, ['create_member'], db)
    if not checked:
        msg = f"Delete user failed: Member {useraccount} does not have create_member permission"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)

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
def list_syslog(decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    useraccount = decode_info['sub']
    list_syslog_ser = db_query_syslog(db)
    msg = f"Member {useraccount} list syslog successful"
    logger.info(msg)
    result = Result(msg=msg, obj=list_syslog_ser, status=True)
    return _result_wrapper(result, status_code=200)
