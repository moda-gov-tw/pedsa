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
from app.core.models import Group, Member, AdminRole, UtilityResult, Project
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group

import base64
import json

Project_utilityReport = APIRouter()

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

security = HTTPBearer(description="HTTP Bearer token scheme")


def get_report(project_id_, privacy_type_, data_, db_):

    MLmodelList = ['XGBoost', 'Random Forest', 'Logistic Regression']
    all_records = db_.query(UtilityResult).filter(UtilityResult.project_id == project_id_, UtilityResult.privacy_type == privacy_type_, UtilityResult.model == data_).all()
    
    report = []
    
    for record in all_records:
        MLresult_byTargetCol = {} #{'colName':'A', 'result':[]}
        MLresult_byTargetCol['colName'] = record.target_col
        MLresult_byTargetCol['result'] = [] #[score_dict, score_dict, score_dict]
        MLresult_byTargetCol['utilitylevel'] = record.utilitylevel
        MLresult_base64 = record.MLresult
        # Decode base64 to JSON string
        MLresult_json_string = base64.b64decode(MLresult_base64).decode()
        # Convert JSON string to dictionary
        MLresult_dict = json.loads(MLresult_json_string)
       
        for model in MLmodelList:
            score_dict = {} #{'model':'XGBoost', 'Training Score':78.7, 'Validation Score':70.9}
            score_dict['model'] = model
            score_dict['Training Score'] = MLresult_dict[model]['Training Score']
            score_dict['Validation Score'] = MLresult_dict[model]['Validation Score']
            MLresult_byTargetCol['result'].append(score_dict)

        report.append(MLresult_byTargetCol)

    return report


@Project_utilityReport.get("/utilityreport")
def utilityreport(project_id:int, privacy_type:str, db:Session = Depends(get_db)):
    result = {}
    result['status'] = 1
    result['msg'] = "get ML utility report"

    obj = {}
    obj['project_id'] = project_id

    #判斷專案是否存在
    try:
        obj['project_name'] = db.query(Project).filter(Project.project_id == project_id).first().project_name
    except:
        result = {}
        result['status'] = -1
        result['msg'] = "project id {} doesn't exist".format(project_id)
        return result
    
    #若專案存在，撈取報表
    obj['privacy_type'] = privacy_type
    obj['rawData'] = get_report(project_id, privacy_type, 'raw/raw', db)
    obj['privacyData'] = get_report(project_id, privacy_type, 'privacy/privacy', db)

    if privacy_type == 'syn' or privacy_type == 'dp':
        obj['privacyrawData'] = get_report(project_id, privacy_type, 'privacy/raw', db)
    result['obj'] = obj

    return result


    
    
