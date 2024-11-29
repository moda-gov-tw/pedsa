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
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group


projects = APIRouter()
from app.core.projects.project_MLstop import Project_MLstop
from app.core.projects.project_selectcol import Project_selectcol 
from app.core.projects.projects_Save import Project_Save
from app.core.projects.projects_MultiInsert import Project_MultiInsert
from app.core.projects.projects_SingleInsert import Project_SingleInsert
from app.core.projects.projects_ProjMemGroupId import Project_ProjMemGroupId
from app.core.projects.projects_UpdateNew import Project_UpdateNew

from app.core.projects.projects_CheckProjEn import Project_CheckProjEn
from app.core.projects.projects_CheckProjCht import Project_CheckProjCht
from app.core.projects.projects_CheckGpProjNum import Project_CheckGpProjnum
from app.core.projects.projects_listHistory import Project_listHistory
from app.core.projects.projects_list import Project_List #Import此類別的.py裡宣告的router
from app.core.projects.projects_reset import Project_Reset #Import此類別的.py裡宣告的router
from app.core.projects.projects_detail import Project_Detail #Import此類別的.py裡宣告的router
from app.core.projects.projects_insert import Project_Insert #Import此類別的.py裡宣告的router
from app.core.projects.projects_update import Project_Update #Import此類別的.py裡宣告的router
from app.core.projects.projects_delete import Project_Delete #Import此類別的.py裡宣告的router
from app.core.projects.project_MLutility import Project_MLutility #Import此類別的.py裡宣告的router
from app.core.projects.project_utilityReport import Project_utilityReport #Import此類別的.py裡宣告的router
from app.core.projects.project_utilityReportList import Project_utilityReportList #Import此類別的.py裡宣告的router
from app.core.projects.project_jobLogList import Project_jobLogList #Import此類別的.py裡宣告的router

from app.core.projects.genkey import gen #Import此類別的.py裡宣告的router
from app.core.projects.project_status import status #Import此類別的.py裡宣告的router
from app.core.projects.project_status_update import Update_status #Import此類別的.py裡宣告的router
from app.core.projects.join import join #Import此類別的.py裡宣告的router
from app.core.projects.send import app
from app.core.projects.monitorContainers import monitor

from app.core.projects.gen_Import import gen_Import
from app.core.projects.gen_getGenTbl import gen_getGenTbl
from app.core.projects.gen_getExport import gen_getExport 
from app.core.projects.gen_integration import gen_Integration

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

#將所有router串並加上prefix
projects.include_router(Project_MLstop,prefix='/projects')
projects.include_router(Project_selectcol,prefix='/projects')
projects.include_router(Project_Save,prefix='/projects')
projects.include_router(Project_MultiInsert,prefix='/projects')
projects.include_router(Project_SingleInsert,prefix='/projects')
projects.include_router(Project_ProjMemGroupId,prefix='/projects')
projects.include_router(Project_UpdateNew,prefix='/projects')

projects.include_router(Project_CheckProjEn,prefix='/projects')
projects.include_router(Project_CheckProjCht,prefix='/projects')
projects.include_router(Project_CheckGpProjnum,prefix='/projects')
projects.include_router(Project_listHistory,prefix='/projects')
projects.include_router(Project_List,prefix='/projects')
projects.include_router(Project_Reset,prefix='/projects')
projects.include_router(Project_Detail,prefix='/projects')
projects.include_router(gen,prefix='/projects')
projects.include_router(status,prefix='/projects')
projects.include_router(Update_status,prefix='/projects')
projects.include_router(join,prefix='/projects')
projects.include_router(app,prefix='/projects')
projects.include_router(Project_Update,prefix='/projects')
projects.include_router(Project_Insert,prefix='/projects')
projects.include_router(Project_Delete,prefix='/projects')
projects.include_router(Project_MLutility,prefix='/projects')
projects.include_router(Project_utilityReport,prefix='/projects')
projects.include_router(Project_utilityReportList,prefix='/projects')
projects.include_router(Project_jobLogList,prefix='/projects')
projects.include_router(monitor,prefix='/projects')
projects.include_router(gen_Import,prefix='/projects')
projects.include_router(gen_getGenTbl,prefix='/projects')
projects.include_router(gen_getExport,prefix='/projects')
projects.include_router(gen_Integration,prefix='/projects')
