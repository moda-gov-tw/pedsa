# -*- coding: utf-8 -*-

from pydantic import BaseModel, RootModel, field_validator, Field
from pydantic_core.core_schema import FieldValidationInfo
from typing import Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.models import AdminRole, MemberGroupRole, Member

# db = next(get_db())


class CreateMember(BaseModel):
    useraccount: str
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    group_id: Optional[int] = None
    ischange: Optional[bool] = False

    class Config:
        from_attributes = True


class CreateMemberGroup(BaseModel):
    member_role: int
    group_id: Optional[int] = None
    member_id: int
    createmember_id: int

    class Config:
        from_attributes = True


class InsertAdminGroup(BaseModel):
    role_name: str
    group_id: Optional[int] = None
    member_id: int


class Result(BaseModel):
    msg: str
    status: bool = False
    obj: Union[list, dict] = []


class FailedLoginBase(BaseModel):
    member_id: int
    times: int = 1
    last_time: datetime

    class Config:
        from_attributes = True


class MemberGroupBase(BaseModel):
    id: int
    member_role: int
    group_id: Optional[int] = None
    createmember_id: int
    updatemember_id: Optional[int] = None

    class Config:
        from_attributes = True


class MemberProjectBase(BaseModel):
    id: int
    project_role: int
    project_id: int
    createmember_id: int
    updatemember_id: Optional[int] = None

    class Config:
        from_attributes = True


class CreateGroup(BaseModel):
    group_name: str
    group_type: str
    project_quota: int = 20

    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    id: int
    group_name: str
    group_type: str
    project_quota: int
    createtime: datetime
    updatetime: Optional[datetime] = None
    createmember_id: int
    updatemember_id: Optional[int] = None
    owner_username: Optional[str] = Field(default=None, validate_default=True)
    owner_email: Optional[str] = Field(default=None, validate_default=True)

    class Config:
        from_attributes = True

    @field_validator("owner_username", mode='before')
    @classmethod
    def get_owner_username(cls, v: bool, info: FieldValidationInfo):
        db = next(get_db())
        group_id = info.data['id']
        group_admin = db.query(MemberGroupRole).filter(
            MemberGroupRole.group_id == group_id, MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        if not group_admin:
            db.close()
            return None
        owner = db.query(Member).filter(Member.id == group_admin.member_id).first()
        if not owner:
            db.close()
            return None
        owner_username = owner.username
        db.close()
        if not owner_username:
            return None
        return owner_username

    @field_validator("owner_email", mode='before')
    @classmethod
    def get_owner_email(cls, v: bool, info: FieldValidationInfo):
        db = next(get_db())
        group_id = info.data['id']
        group_admin = db.query(MemberGroupRole).filter(
            MemberGroupRole.group_id == group_id, MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        if not group_admin:
            db.close()
            return None
        owner = db.query(Member).filter(Member.id == group_admin.member_id).first()
        if not owner:
            db.close()
            return None
        owner_mail = owner.email
        db.close()
        if not owner_mail:
            return None
        return owner_mail


class GroupList(RootModel):
    root: List[GroupBase]


class UpdateGroup(BaseModel):
    group_name: Optional[str] = None
    project_quota: Optional[int] = None

    class Config:
        from_attributes = True


class MemberBase(BaseModel):
    id: int
    useraccount: str
    username: str
    email: Union[str, None]
    group_id: Union[int, None]
    group_name: Union[str, None]
    group_type: Union[str, None]
    createtime: datetime
    updatetime: Union[datetime, None]
    createmember_id: Union[int, None]
    updatemember_id: Union[int, None]
    isactive: bool
    ischange: bool
    is_super_admin: Optional[bool] = Field(default=None, validate_default=True)
    is_group_admin: Optional[bool] = Field(default=None, validate_default=True)
    is_project_admin: Optional[dict] = Field(default=None, validate_default=True)

    @field_validator("is_super_admin", mode='before')
    @classmethod
    def check_is_super_admin(cls, v: bool, info: FieldValidationInfo):
        db = next(get_db())
        member_id = info.data['id']
        is_super_admin = db.query(MemberGroupRole).filter(
            MemberGroupRole.member_id == member_id, MemberGroupRole.member_role == AdminRole.super_admin.value).first()
        db.close()
        if not is_super_admin:
            return False
        return True

    @field_validator("is_group_admin", mode='before')
    @classmethod
    def check_is_group_admin(cls, v: bool, info: FieldValidationInfo):
        db = next(get_db())
        member_id = info.data['id']
        is_group_admin = db.query(MemberGroupRole).filter(
            MemberGroupRole.member_id == member_id,
            MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        db.close()
        if not is_group_admin:
            return False
        return True

    @field_validator("is_project_admin", mode='before')
    @classmethod
    def check_is_project_admin(cls, v: dict, info: FieldValidationInfo):
        db = next(get_db())
        result = {'status': False}
        member_id = info.data['id']
        is_project_admin = db.query(MemberGroupRole).filter(
            MemberGroupRole.member_id == member_id,
            MemberGroupRole.member_role == AdminRole.project_admin.value).first()
        db.close()
        if not is_project_admin:
            return result
        result['status'] = True
        result['id'] = is_project_admin.id
        result['group_id'] = is_project_admin.group_id
        result['member_role'] = is_project_admin.member_role
        return result

    class Config:
        from_attributes = True


class MemberList(RootModel):
    root: List[MemberBase]


class UpdateMember(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    group_id: Optional[int] = None

    class Config:
        from_attributes = True


class ProjectStatusBase(BaseModel):
    ps_id:int
    project_id: int
    project_status: int
    createtime: datetime
    updatetime: Optional[datetime] = None
    createMember_Id: int
    updateMember_Id: Optional[int] = None

    class Config:
        from_attributes = True


class GetProjectStatusBase(BaseModel):
    project_status: int

    class Config:
        from_attributes = True


class Result_P(BaseModel):
    status: int = -2
    msg: str = "unknown error"
    obj: Union[list, dict] = []


class ProjectJoinFunct(BaseModel):
    id: int
    left_group_id: int
    left_dataset: str
    left_col: str
    right_group_id: int
    right_dataset: str
    right_col: str
    project_id: int
    createtime: datetime
    updatetime: Optional[datetime] = None
    createMember_Id: int
    updateMember_Id: Optional[int] = None
    

    class Config:
        from_attributes = True


class JoinFunc(BaseModel):
    left_dataset: str# = Field(default=None, examples=["w2_b.csv"])
    left_col: str# = Field(default=None, examples=["id"])
    right_dataset: str# = Field(default=None, examples=["w3_c.csv"])
    right_col: str# = Field(default=None, examples=["id"])

    class Config:
        from_attributes = True

class YarnApplication(BaseModel):
    yarn_application: str# = Field(default=None, examples=["w2_b.csv"])

    class Config:
        from_attributes = True        


class Projectjoin(BaseModel):
    member_id: int = Field(default=None, examples=[1])
    project_id: int = Field(default=None, examples=[5])
    enc_key: str = Field(default=None, examples=["AAAAAABC0DCB39FE182FAF7CE960A2B0BA63AFEEDC76D8A92AED52938AA06ABA"])
    join_type: int = Field(default=None, examples=[1])
    join_func: Union[list, dict] = None

    class Config:
        from_attributes = True


class CreateSyslog(BaseModel):
    useraccount: str
    log_type: str
    project_name: Optional[str] = None
    logcontent: str

    class Config:
        from_attributes = True


class ShowSyslog(BaseModel):
    id: int
    sysdatetime: datetime
    useraccount: str
    log_type: str
    project_name: Optional[str] = None
    logcontent: str

    class Config:
        from_attributes = True


class ListSyslog(RootModel):
    root: List[ShowSyslog]
