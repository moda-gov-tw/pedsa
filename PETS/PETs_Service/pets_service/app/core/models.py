# -*- coding: utf-8 -*-

import enum
from sqlalchemy import Column, Integer, Boolean, DateTime, VARCHAR, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.database import Base
from sqlalchemy.dialects.mysql import LONGTEXT


class Group(Base):
    __tablename__ = "T_Pets_Group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="機關ID")
    group_name = Column(VARCHAR(100), nullable=False, unique=True, comment="機關名稱")
    group_type = Column(VARCHAR(100), nullable=False, unique=True, comment="機關代號")
    project_quota = Column(Integer, nullable=True, comment="機關專案配額")
    createtime = Column(DateTime(timezone=True), server_default=func.now(), comment="建立日期")
    updatetime = Column(DateTime(timezone=True), nullable=True, comment="修改日期")
    createmember_id = Column(Integer, nullable=False, comment="建立使用者ID")
    updatemember_id = Column(Integer, nullable=True, comment="修改使用者ID")


class Member(Base):
    __tablename__ = "T_Pets_Member"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="使用者ID")
    useraccount = Column(VARCHAR(100), nullable=False, unique=True, comment="使用者帳號")
    username = Column(VARCHAR(100), nullable=False, comment="使用者姓名")
    password = Column(VARCHAR(255), nullable=False, comment="密碼")
    email = Column(VARCHAR(255), nullable=True, comment="Email")
    group_id = Column(Integer, ForeignKey(Group.id), nullable=True, comment="機關ID")
    group = relationship(Group, backref="member")
    group_name = association_proxy(target_collection='group', attr='group_name')
    group_type = association_proxy(target_collection='group', attr='group_type')
    createtime = Column(DateTime(timezone=True), server_default=func.now(), comment="建立日期")
    updatetime = Column(DateTime(timezone=True), nullable=True, comment="修改日期")
    createmember_id = Column(Integer, nullable=True, comment="建立使用者ID")
    updatemember_id = Column(Integer, nullable=True, comment="修改使用者ID")
    isactive = Column(Boolean, default=True, comment="帳號是否啟用")
    ischange = Column(Boolean, default=False, comment="密碼是否變更")
    last_time = Column(DateTime(timezone=True), nullable=True, comment="最後登入時間")


class AdminRole(bytes, enum.Enum):
    def __new__(cls, value, alias):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.alias = alias
        return obj

    super_admin = (1, 'super admin')
    group_admin = (2, 'group admin')
    project_admin = (3, 'project admin')


class MemberGroupRole(Base):
    __tablename__ = "T_Pets_MemberGroupRole"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="機關使用者權限ID")
    member_role = Column(Integer, Enum(AdminRole), nullable=False,
                         comment="1:super admin, 2:group admin, 3:project admin")
    group_id = Column(Integer, ForeignKey(Group.id), nullable=True, comment="機關ID")
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False, comment="使用者ID")
    createtime = Column(DateTime(timezone=True), server_default=func.now(), comment="建立日期")
    updatetime = Column(DateTime(timezone=True), nullable=True, comment="修改日期")
    createmember_id = Column(Integer, ForeignKey(Member.id), nullable=False, comment="建立使用者ID")
    updatemember_id = Column(Integer, ForeignKey(Member.id), nullable=True, comment="修改使用者ID")


class ProjectRole(bytes, enum.Enum):
    def __new__(cls, value, alias):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.alias = alias
        return obj

    project_admin = (3, 'project admin')
    project_user = (4, 'project user')
    project_data_provider = (5, 'project data provider')


class MemberProjectRole(Base):
    __tablename__ = "T_Pets_MemberProjectRole"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="專案使用者權限ID")
    project_role = Column(Integer, Enum(ProjectRole), nullable=False,
                          comment="3:project admin, 4:project user, 5:project data provider")
    project_id = Column(Integer, nullable=False, comment="專案ID")
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False, comment="使用者ID")
    createtime = Column(DateTime(timezone=True), server_default=func.now(), comment="建立日期")
    updatetime = Column(DateTime(timezone=True), nullable=True, comment="修改日期")
    createmember_id = Column(Integer, ForeignKey(Member.id), nullable=False, comment="建立使用者ID")
    updatemember_id = Column(Integer, ForeignKey(Member.id), nullable=True, comment="修改使用者ID")


class Permission(Base):
    __tablename__ = "T_Pets_Permission"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="權限ID")
    name = Column(VARCHAR(100), nullable=False, comment="權限名稱")
    description = Column(VARCHAR(100), nullable=False, comment="權限說明")


class RolePermission(Base):
    __tablename__ = "T_Pets_RolePermission"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="角色權限對應ID")
    role_id = Column(Integer, nullable=False, comment="角色ID")
    permission_id = Column(Integer, ForeignKey(Permission.id), nullable=False, comment="權限ID")
    permission = relationship(Permission, backref="rolepermissions")
    permission_name = association_proxy(target_collection='permission', attr='name')


class FailedLogin(Base):
    __tablename__ = "T_Pets_FailedLogin"

    member_id = Column(Integer, ForeignKey(Member.id), primary_key=True, nullable=False, comment="使用者ID")
    times = Column(Integer, default=1, nullable=False)
    last_time = Column(DateTime(timezone=True), nullable=False)


class Project(Base):
    __tablename__ = "T_Pets_Project"
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column( VARCHAR(255), nullable=False)
    project_eng = Column( VARCHAR(255), nullable=False)
    project_desc = Column( VARCHAR(255), nullable=False)
    createtime = Column(DateTime(timezone=True), nullable=False)
    updatetime = Column(DateTime(timezone=True), nullable=False)
    enc_key = Column( VARCHAR(255), nullable=False)
    jointablename = Column( VARCHAR(255), nullable=False)
    join_func = Column(Integer, nullable=True)
    group_id = Column(Integer, ForeignKey(Group.id), nullable=True)
    createMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    updateMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    aes_col = Column( VARCHAR(255), nullable=False)
    jointablecount = Column(Integer, nullable=True)
    join_sampledata = Column( VARCHAR(255), nullable=False)


class ProjectStatus(Base):
    __tablename__ = "T_Pets_ProjectStatus"
    ps_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey(Project.project_id), nullable=True)
    project_status = Column(Integer, nullable=True)
    createtime = Column(DateTime(timezone=True), nullable=False)
    updatetime = Column(DateTime(timezone=True), nullable=False)
    createMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    updateMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)


class ProjectJoinFunc(Base):
    __tablename__ = "T_Pets_ProjectJoinFunc"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    left_group_id = Column(Integer, nullable=True)
    left_dataset = Column( VARCHAR(255), nullable=False)
    left_col = Column( VARCHAR(255), nullable=False)
    right_group_id = Column(Integer, nullable=True)
    right_dataset = Column( VARCHAR(255), nullable=False)
    right_col = Column( VARCHAR(255), nullable=False)
    project_id = Column(Integer,  nullable=True)
    #project_id = Column(Integer, ForeignKey(Project.project_id), nullable=True)
    createMember_Id = Column(Integer,  nullable=True)
    #createMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    updateMember_Id = Column(Integer, nullable=True)
    #updateMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    createtime = Column(DateTime(timezone=True), nullable=False)
    updatetime = Column(DateTime(timezone=True), nullable=False)


class ViewsDetails(Base):
    __tablename__ = "V_Pets_ProjectList"
    row_num = Column(Integer,primary_key=True, nullable=True)
    project_id = Column(Integer, nullable=True)
    project_name = Column( VARCHAR(255), nullable=False)
    project_eng = Column( VARCHAR(255), nullable=False)
    createtime = Column(DateTime(timezone=True), nullable=False)
    updatetime = Column(DateTime(timezone=True), nullable=False)
    enc_key = Column( VARCHAR(255), nullable=False)
    join_func = Column(Integer, nullable=True)
    group_id = Column(Integer, nullable=True)
    createMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    updateMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    jointablename = Column( VARCHAR(255), nullable=False)
    jointablecount = Column(Integer, nullable=False)#Project:T_Pets_Project
    aes_col = Column( VARCHAR(255), nullable=False) #Project:T_Pets_Project
    join_sampledata  = Column(LONGTEXT, nullable=False)
    project_status = Column(Integer, nullable=True)
    project_roleid = Column(Integer, nullable=True) #流水號
    rolemember_id = Column(Integer, nullable=True) #member_id
    project_role = Column(Integer, nullable=True)
    project_joinfuncid = Column(Integer, nullable=True)
    left_group_id = Column(Integer, nullable=True)
    left_dataset = Column( VARCHAR(255), nullable=False)
    left_col = Column( VARCHAR(255), nullable=False)
    right_group_id = Column(Integer, nullable=True)
    right_dataset = Column( VARCHAR(255), nullable=False)
    right_col = Column( VARCHAR(255), nullable=False)
    

class HistoryProject(Base):
    __tablename__ = "T_Pets_HistoryProject"
    project_id = Column(Integer,primary_key=True, nullable=False, autoincrement=True)
    project_name = Column( VARCHAR(255), nullable=False) #Project:T_Pets_Project
    project_eng = Column( VARCHAR(255), nullable=False) #Project:T_Pets_Project
    project_desc = Column( VARCHAR(255), nullable=False) #Project:T_Pets_Project
    createtime = Column(DateTime(timezone=True), nullable=False)
    updatetime = Column(DateTime(timezone=True), nullable=True)
    enc_key = Column( VARCHAR(200), nullable=False) #Project:T_Pets_Project
    jointablename = Column( VARCHAR(255), nullable=False) #Project:T_Pets_Project
    jointablecount = Column(Integer, nullable=False)#Project:T_Pets_Project
    join_func = Column(Integer, nullable=True) #Project:T_Pets_Project
    join_func_content = Column(LONGTEXT, nullable=False)  #ProjectJoinFunc
    project_role_content = Column( LONGTEXT, nullable=False)#MemberProjectRole
    group_id = Column(Integer, nullable=True) #Project:T_Pets_Project
    createMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    updateMember_Id = Column(Integer, ForeignKey(Member.id), nullable=True)
    aes_col = Column( VARCHAR(255), nullable=False) #Project:T_Pets_Project


class UtilityResult(Base):
    __tablename__ = "T_Pets_UtilityResult"
    Id = Column(Integer,primary_key=True, nullable=False, autoincrement=True)
    project_id = Column(Integer, nullable=False)
    privacy_type = Column( VARCHAR(10), nullable=False)
    target_col = Column( VARCHAR(255), nullable=False)
    model = Column( VARCHAR(255), nullable=False)
    MLresult = Column( VARCHAR(255), nullable=False)
    createtime = Column(DateTime(timezone=True), nullable=False)
    updatetime = Column(DateTime(timezone=True), nullable=True)
    createMember_Id = Column(Integer, nullable=True)
    updateMember_Id = Column(Integer, nullable=True)


class Syslog(Base):
    __tablename__ = "T_Pets_Syslog"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    sysdatetime = Column(DateTime(timezone=True), server_default=func.now(), comment="操作時間")
    useraccount = Column(VARCHAR(100), nullable=False, comment="使用者帳號")
    log_type = Column(VARCHAR(50), nullable=False, comment="Log類別")
    project_name = Column(VARCHAR(255), comment="專案名稱")
    logcontent = Column(VARCHAR(255), comment="Log紀錄")

class JobSyslog(Base):
    __tablename__ = "T_Pets_JobSyslog"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    createtime = Column(DateTime(timezone=True))
    updatetime = Column(DateTime(timezone=True))    
    member_id = Column(Integer, nullable=False) #member_id
    log_type = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)
    jobname= Column(VARCHAR(255), nullable=False)
    project_step = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    logcontent  = Column(VARCHAR(255))