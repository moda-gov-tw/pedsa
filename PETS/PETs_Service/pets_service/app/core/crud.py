# -*- coding: utf-8 -*-

from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.models import Permission, RolePermission, AdminRole, ProjectRole, Member, MemberGroupRole, FailedLogin,\
    MemberProjectRole, Group, ProjectStatus, Syslog
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase,ProjectStatusBase, GetProjectStatusBase, \
    CreateSyslog, ShowSyslog, ListSyslog
from app.core.config import settings
from app.core.utils import gen_default_password, check_password_rule


def db_create_default_permissions_if_not_exists(db):
    perms = {
        "sys_health": "系統環境健康度", "syslog": "系統操作記錄", "create_group": "建立機關", "update_group": "修改機關",
        "delete_group": "刪除機關", "create_member": "建立人員帳號", "set_admin": "設定管理員", "user_list": "人員列表",
        "project_control": "專案總量管制", "create_project": "建立專案", "delete_project": "刪除專案", "group_list": "機關列表",
        "edit_project": "編輯專案", "project_list": "專案列表", "project_setting": "查看專案設定", "reset_project": "重設專案",
        "reset_status": "重設隱私強化參數", "project_report_dp": "查看專案dp結果", "project_report_k": "查看專案k結果",
        "project_report_gan": "查看專案gan結果", "download_project_dp": "下載隱私強化dp資料",
        "download_project_k": "下載隱私強化k資料", "download_project_gan": "下載隱私強化gan資料"
    }

    add_list = []
    for k in perms:
        per = db.query(Permission).filter(Permission.name == k).first()
        if not per:
            add_list.append(Permission(name=k, description=perms[k]))

    if not add_list:
        return True, "Default permission has been add"

    try:
        db.add_all(add_list)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, "Add all default permissions"


def db_create_default_super_admin_permissions_if_not_exists(db):
    all_perms = db.query(Permission).filter().all()

    super_admin_perms = []
    for per in all_perms:
        has_per = db.query(RolePermission).filter(RolePermission.role_id == AdminRole.super_admin.value,
                                                  RolePermission.permission_id == per.id).first()
        if not has_per:
            super_admin_perms.append(RolePermission(role_id=AdminRole.super_admin.value, permission_id=per.id))

    if not super_admin_perms:
        return True, f"Default {AdminRole.super_admin.alias} permission has been add"

    try:
        db.add_all(super_admin_perms)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Add all {AdminRole.super_admin.alias} permissions"


def db_create_default_group_admin_permissions_if_not_exists(db):
    perms_list = ['set_admin', 'user_list', 'project_control', 'create_project','project_list', 'project_setting',
                  'project_report_dp', 'project_report_k', 'project_report_gan']
    perms = db.query(Permission).filter(Permission.name.in_(perms_list)).all()

    group_admin_perms = []
    for per in perms:
        has_per = db.query(RolePermission).filter(RolePermission.role_id == AdminRole.group_admin.value,
                                                  RolePermission.permission_id == per.id).first()
        if not has_per:
            group_admin_perms.append(RolePermission(role_id=AdminRole.group_admin.value, permission_id=per.id))

    if not group_admin_perms:
        return True, f"Default {AdminRole.group_admin.alias} permission has been add"

    try:
        db.add_all(group_admin_perms)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Add all {AdminRole.group_admin.alias} permissions"


def db_create_default_project_admin_permissions_if_not_exists(db):
    perms_list = ['user_list', 'create_project', 'delete_project', 'project_list', 'project_setting', 'edit_project',
                  'reset_project', 'reset_status', 'project_report_dp', 'project_report_k', 'project_report_gan',
                  'download_project_dp', 'download_project_k', 'download_project_gan','group_list']

    perms = db.query(Permission).filter(Permission.name.in_(perms_list)).all()

    project_admin_perms = []
    for per in perms:
        has_per = db.query(RolePermission).filter(RolePermission.role_id == ProjectRole.project_admin.value,
                                                  RolePermission.permission_id == per.id).first()
        if not has_per:
            project_admin_perms.append(RolePermission(role_id=ProjectRole.project_admin.value, permission_id=per.id))

    if not project_admin_perms:
        return True, f"Default {ProjectRole.project_admin.alias} permission has been add"

    try:
        db.add_all(project_admin_perms)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Add all {ProjectRole.project_admin.alias} permissions"


def db_create_default_project_user_permissions_if_not_exists(db):
    perms_list = ['user_list', 'project_list', 'project_setting', 'edit_project', 'reset_status', 'project_report_dp',
                  'project_report_k', 'project_report_gan', 'download_project_dp', 'download_project_k',
                  'download_project_gan']

    perms = db.query(Permission).filter(Permission.name.in_(perms_list)).all()

    project_user_perms = []
    for per in perms:
        has_per = db.query(RolePermission).filter(RolePermission.role_id == ProjectRole.project_user.value,
                                                  RolePermission.permission_id == per.id).first()
        if not has_per:
            project_user_perms.append(RolePermission(role_id=ProjectRole.project_user.value, permission_id=per.id))

    if not project_user_perms:
        return True, f"Default {ProjectRole.project_user.alias} permission has been add"

    try:
        db.add_all(project_user_perms)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Add all {ProjectRole.project_user.alias} permissions"


def db_create_default_project_data_provider_permissions_if_not_exists(db):
    perms_list = ['project_list', 'project_setting', 'project_report_dp', 'project_report_k', 'project_report_gan']

    perms = db.query(Permission).filter(Permission.name.in_(perms_list)).all()

    project_data_provider_perms = []
    for per in perms:
        has_per = db.query(RolePermission).filter(RolePermission.role_id == ProjectRole.project_data_provider.value,
                                                  RolePermission.permission_id == per.id).first()
        if not has_per:
            project_data_provider_perms.append(RolePermission(role_id=ProjectRole.project_data_provider.value,
                                                              permission_id=per.id))

    if not project_data_provider_perms:
        return True, f"Default {ProjectRole.project_data_provider.alias} permission has been add"

    try:
        db.add_all(project_data_provider_perms)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Add all {ProjectRole.project_data_provider.alias} permissions"


def db_create_admin_user_if_not_exists(db):
    admin_user = db.query(Member).filter(Member.useraccount == settings.DEFAULT_USER).first()
    if admin_user:
        return True, "Default admin user has exists"

    hash_password = bcrypt.hash(settings.DEFAULT_PASSWORD)
    admin_ser = CreateMember(useraccount=settings.DEFAULT_USER, username=settings.DEFAULT_USER, password=hash_password,
                             ischange=True)
    db_user = Member(**admin_ser.model_dump())
    try:
        db.add(db_user)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, "Create default admin user successful"


def db_create_default_role_if_not_exists(db):
    admin_user = db.query(Member).filter(Member.useraccount == settings.DEFAULT_USER).first()
    if not admin_user:
        return False, "Default admin user has not been create"

    super_role = db.query(MemberGroupRole).filter(MemberGroupRole.member_role == AdminRole.super_admin.value,
                                                  MemberGroupRole.member_id == admin_user.id).first()
    if super_role:
        return True, f"User admin {AdminRole.super_admin.alias} role has been set"

    super_role_ser = CreateMemberGroup(member_role=AdminRole.super_admin.value, member_id=admin_user.id,
                                       createmember_id=admin_user.id)
    db_super_role = MemberGroupRole(**super_role_ser.model_dump())
    try:
        db.add(db_super_role)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, "Create default admin role successful"


def user_login(useraccount, password, db: Session):
    member = db.query(Member).filter(Member.useraccount == useraccount).first()
    if not member:
        return False, 'no member exist'
    if not member.isactive:
        return False, 'member is inactive'
    time_limit = {'days': settings.ACCOUNT_LOCKOUT_DURATION}
    if is_idle_account(member, time_limit, db):
        return False, 'this account has been idle too long'
    if not db_check_failed_login(member.id, db):
        return False, 'failed login over three times'
    if not bcrypt.verify(password, member.password):
        db_create_failed_login(member.id, db)
        return False, 'account or password wrong'
    db_delete_failed_login(member.id, db)
    return True, 'login pass'


def is_idle_account(member, time_limit, db: Session):
    last_login_time = member.last_time
    if not last_login_time:
        return False
    now = datetime.now()
    expired_time = last_login_time + timedelta(**time_limit)

    if now > expired_time:
        member.isactive = False
        db.commit()
        return True
    return False


def db_check_failed_login(member_id, db: Session):
    failed_login = db.query(FailedLogin).filter(FailedLogin.member_id == member_id).first()
    if not failed_login:
        return True

    now = datetime.now()
    expired_time = failed_login.last_time + timedelta(minutes=15)

    if now > expired_time:
        db.delete(failed_login)
        db.commit()
        return True

    if failed_login.times < 3:
        return True
    return False


def db_create_failed_login(member_id, db: Session):
    failed_login = db.query(FailedLogin).filter(FailedLogin.member_id == member_id).first()
    if not failed_login:
        failed_login_ser = FailedLoginBase(member_id=member_id, last_time=datetime.now())
        db_failed_login = FailedLogin(**failed_login_ser.model_dump())
        db.add(db_failed_login)
        db.commit()
        return True
    if failed_login.times < 3:
        failed_login.times += 1
        failed_login.last_time = datetime.now()
        db.commit()
    return True


def db_delete_failed_login(member_id, db: Session):
    failed_login = db.query(FailedLogin).filter(FailedLogin.member_id == member_id).first()
    if not failed_login:
        return True
    db.delete(failed_login)
    db.commit()
    return True


def gen_jwt_token(account, db: Session):
    JWT_ALGORITHM = settings.JWT_ALGORITHM
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY

    member = db.query(Member).filter(Member.useraccount == account).first()
    role = get_role(member.id, db)
    now_time = datetime.now()
    expires_delta = now_time + timedelta(hours=24)
    to_encode = {"exp": expires_delta, "sub": member.useraccount, "member_id": member.id, "username": member.username}
    to_encode.update(role)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    member.last_time = now_time
    db.commit()
    return member.id, encoded_jwt


def get_role(member_id, db: Session):
    role = {}
    super_admin_data = get_admin_role(member_id, AdminRole.super_admin.value, db)
    group_admin_data = get_admin_role(member_id, AdminRole.group_admin.value, db)
    project_admin_data = get_project_role(member_id, ProjectRole.project_admin.value, db)
    project_user_data = get_project_role(member_id, ProjectRole.project_user.value, db)
    project_data_provider = get_project_role(member_id, ProjectRole.project_data_provider.value, db)
    role.update({"role": {AdminRole.super_admin.name: super_admin_data}})
    role["role"][AdminRole.group_admin.name] = group_admin_data
    role["role"][ProjectRole.project_admin.name] = project_admin_data
    role["role"][ProjectRole.project_user.name] = project_user_data
    role["role"][ProjectRole.project_data_provider.name] = project_data_provider
    return role


def get_admin_role(member_id, admin_role_id, db: Session):
    admin_data = {}
    admin_role = db.query(MemberGroupRole).filter(MemberGroupRole.member_role == admin_role_id,
                                                  MemberGroupRole.member_id == member_id).first()
    if not admin_role:
        return admin_data

    admin_data = MemberGroupBase.model_validate(admin_role)
    return dict(admin_data)


def get_project_role(member_id, role_id, db: Session):
    data = {}
    roles = db.query(MemberProjectRole).filter(MemberProjectRole.project_role == role_id,
                                               MemberProjectRole.member_id == member_id)
    if not roles:
        return data

    for role in roles:
        data[role.project_id] = dict(MemberProjectBase.model_validate(role))
    return data


def check_permissions(member_id: int, permissions: list, db: Session):
    admin_role = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id)
    user_role = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id)
    role_id = set()

    for admin in admin_role:
        role_id.add(admin.member_role)

    for user in user_role:
        role_id.add(user.project_role)

    db_permissions = db.query(RolePermission).filter(RolePermission.role_id.in_(role_id))
    full_check_permissions = set()
    for perm in db_permissions:
        full_check_permissions.add(perm.permission_name)
    check_data = set(permissions)
    return check_data.issubset(full_check_permissions)


def get_all_group(db: Session):
    db_groups = db.query(Group).filter().all()
    group_list_ser = dict(GroupList.model_validate(db_groups))
    return group_list_ser


def db_update_group(group_id: int, updatemember_id: int, modify_group: UpdateGroup, db: Session):
    db_group = db.query(Group).filter(Group.id == group_id)
    if not db_group:
        return False, f"Group {group_id} not exist"

    modify_group_data = modify_group.model_dump(exclude_unset=True)
    modify_group_data['updatemember_id'] = updatemember_id
    modify_group_data['updatetime'] = datetime.now()
    try:
        db_group.update(modify_group_data)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    db_group = db.query(Group).filter(Group.id == group_id).first()
    group_ser = dict(GroupBase.model_validate(db_group))
    return True, group_ser


def db_delete_group(group_id: int, db: Session):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        return False, f"Group {group_id} not exist"

    try:
        db.delete(db_group)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Delete group {group_id} successful"


def get_all_user(group_id, db: Session):
    if not group_id:
        db_users = db.query(Member).filter().all()
    else:
        db_users = db.query(Member).filter(Member.group_id == group_id).all()
    user_list_ser = dict(MemberList.model_validate(db_users))
    user_list = user_list_ser['root']
    users_data = []
    for user in user_list:
        user_dict = user.model_dump()
        member_id = user_dict['id']
        role = get_role(member_id, db)
        user_dict.update(role)
        users_data.append(user_dict)
    return users_data


def get_active_user(db: Session):
    db_users = db.query(Member).filter(Member.isactive == True, Member.ischange == True).all()
    user_list_ser = dict(MemberList.model_validate(db_users))
    user_list = user_list_ser['root']
    users_data = []
    for user in user_list:
        user_dict = user.model_dump()
        member_id = user_dict['id']
        role = get_role(member_id, db)
        user_dict.update(role)
        users_data.append(user_dict)
    return users_data


def user_change_password(member_id, password, new_password_1, new_password_2, db: Session):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return False, 'no member exist'

    if new_password_1 != new_password_2:
        return False, 'new password not match'

    checked, message = check_password_rule(new_password_1)
    if not checked:
        return False, message

    if not bcrypt.verify(password, member.password):
        return False, 'password was wrong'

    member.password = bcrypt.hash(new_password_1)
    member.updatetime = datetime.now()
    member.updatemember_id = member_id
    member.ischange = True
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Update password successful"


def db_delete_member(delete_member_id, db: Session):
    member = db.query(Member).filter(Member.id == delete_member_id).first()
    if not member:
        return False, 'no member exist'

    try:
        db.delete(member)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"Delete member {delete_member_id} successful"


def db_update_member(update_member_id: int, updatemember_id: int, update_member: UpdateMember, db: Session):
    member = db.query(Member).filter(Member.id == update_member_id)
    if not member:
        return False, 'no member exist'

    update_member_data = update_member.model_dump(exclude_unset=True)
    update_member_data['updatemember_id'] = updatemember_id
    update_member_data['updatetime'] = datetime.now()

    try:
        member.update(update_member_data)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    db_member = db.query(Member).filter(Member.id == update_member_id).first()
    member_ser = dict(MemberBase.model_validate(db_member))
    return True, member_ser


def admin_change_user_password(member_id, updatemember_id, db: Session):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return False, 'no member exist'

    new_password = gen_default_password()
    member.password = bcrypt.hash(new_password)
    member.updatetime = datetime.now()
    member.updatemember_id = updatemember_id
    member.ischange = False
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    db_delete_failed_login(member_id, db)
    return True, new_password


def db_update_member_status(member_id, updatemember_id, status, db: Session):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return False, 'no member exist'

    member.isactive = status
    member.updatetime = datetime.now()
    member.updatemember_id = updatemember_id
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, "update member status successful"


def is_group_admin(member_id, db: Session):
    group_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
    if not group_admin:
        return False
    return True


def is_super_admin(member_id, db: Session):
    super_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.super_admin.value).first()
    if not super_admin:
        return False
    return True


def is_group_owner(member_id, group_id, db: Session):
    group_owner = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.group_id == group_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
    if not group_owner:
        return False
    return True


def get_group_users(member_id, db: Session):
    group_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
    group_id = group_admin.group_id
    return get_all_user(group_id, db)


def db_set_admin_role(insert_role_data, db: Session):
    create_role = CreateMemberGroup(**insert_role_data)
    db_create_role = MemberGroupRole(**create_role.model_dump())
    try:
        db.add(db_create_role)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    db.refresh(db_create_role)
    create_role_ser = dict(CreateMemberGroup.model_validate(db_create_role))
    return True, create_role_ser


def db_delete_admin_role(role_id, member_id, db: Session):
    db_role = db.query(MemberGroupRole).filter(MemberGroupRole.id == role_id).first()
    if not db_role:
        return False, 'no admin role exist'
    member_role = db_role.member_role

    if member_role in [1, 2, 3] and is_super_admin(member_id, db):
        pass
    elif member_role == 3 and is_group_admin(member_id, db):
        pass
    else:
        msg = f"member do not have permission"
        return False, msg

    try:
        db.delete(db_role)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    return True, f"delete role {role_id} successful"


def get_user(member_id, db: Session):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return False, 'no member exist'

    user_ser = dict(MemberBase.model_validate(member))
    role = get_role(member_id, db)
    user_ser.update(role)
    return True, user_ser


def get_group(group_id, db: Session):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        return False, 'no group exist'

    group_ser = dict(GroupBase.model_validate(db_group))
    return True, group_ser


def get_status(project_id, db: Session):
    db_proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).first()
    if not db_proj_status:
        return False, str(ProjectStatus.project_id)+ ' no proj exist'

    proj_sta_ser = dict(GetProjectStatusBase.model_validate(db_proj_status))
    return True, proj_sta_ser


def get_status_name(project_status):
    proj_dict = { 0:'建立專案及設定',
                    1 :'資料匯入及鏈結設定檢查',
                    2 :'安全資料鏈結處理',
                    3 :'安全資料鏈結處理中',
                    4 :'安全資料鏈結處理已完成',
                    5 :'隱私安全服務強化處理',
                    6 :'產生安全強化資料',
                    7 :'感興趣欄位選擇',
                    8 :'可用性分析處理中',
                    9 :'查看可用性分析報表',
                    90 : '安全資料鏈結錯誤',
                    91 : '可用性分析錯誤',
                    92:'資料匯入錯誤'
                    }
    if project_status['project_status'] in proj_dict.keys():
        return proj_dict[project_status['project_status']]
    else:
        return 'Key_Error'


def db_update_project_status(project_id: int, modify_status: int, db: Session):
    db_proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id)

    if not db_proj_status:
        return False, f"Project {project_id} not exist"

    modify_status_data = {}
    modify_status_data['project_status'] = modify_status
    # modify_status_data = modify_status.model_dump(exclude_unset=True)
    # modify_status_data['project_status'] = modify_status['project_status']
    # modify_status_data['updatemember_id'] = member_id
    modify_status_data['updatetime'] = datetime.now()   
    try:
        if get_status_name(modify_status_data) == 'Key_Error':
            return False, f"Key {modify_status} Error"
        else:
            db_proj_status.update(modify_status_data)
            db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    db_proj_status = db.query(ProjectStatus).filter(ProjectStatus.project_id == project_id).first()
    update_project_ser = dict(ProjectStatusBase.model_validate(db_proj_status))
    return True, update_project_ser


def db_insert_syslog(create_syslog: CreateSyslog, db: Session):
    db_syslog = Syslog(**create_syslog.model_dump(exclude_unset=True))
    try:
        db.add(db_syslog)
        db.commit()
    except Exception as e:
        db.rollback()
        return False, str(e)
    db.refresh(db_syslog)
    syslog_ser = dict(ShowSyslog.model_validate(db_syslog))
    return True, syslog_ser


def db_query_syslog(db: Session):
    db_syslog_list = db.query(Syslog).order_by(Syslog.sysdatetime.desc()).all()
    list_syslog_ser = ListSyslog.model_validate(db_syslog_list).model_dump()
    return list_syslog_ser
