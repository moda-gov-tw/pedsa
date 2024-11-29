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
from app.core.models import Group, Member, AdminRole, MemberGroupRole, Project,ProjectStatus,MemberProjectRole,ViewsDetails
from app.core.schemas import Result, CreateGroup, GroupBase, UpdateGroup, CreateMember, UpdateMember, InsertAdminGroup
from app.core.utils import _result_wrapper, decode_jwt_token, gen_default_password
from app.core.crud import user_login, gen_jwt_token, check_permissions, get_all_group, db_update_group, db_delete_group, \
    get_all_user, user_change_password, db_delete_member, db_update_member, admin_change_user_password, \
    db_update_member_status, is_group_admin, get_group_users, is_super_admin, db_set_admin_role, db_delete_admin_role, \
    get_user, is_group_owner, get_group,user_is_active
from app.core.schemas import CreateMember, CreateMemberGroup, FailedLoginBase, MemberGroupBase, MemberProjectBase,\
    GroupList, UpdateGroup, MemberList, UpdateMember, MemberBase, GroupBase #, ProjectList

Project_Detail = APIRouter() ##need to edit

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


from typing import Optional, Union, List
def get_project_detail(member_id, project_id, db: Session):
    logger.info(f"***********//////////////////////////{member_id, project_id}**************")
    #fix statusname by Bruce; PEI;
    status_trans={ 0:'建立專案及設定',
                    1 :'資料匯入及鏈結設定檢查',
                    2 :'安全資料鏈結處理',
                    3 :'安全資料鏈結處理中',
                    4 :'安全資料鏈結處理已完成',
                    5 :'隱私安全服務強化處理',
                    6 :'產生安全強化資料',
                    7 :'感興趣欄位選擇',
                    8 :'可用性分析處理中',
                    9 :'查看可用性分析報表',
                    90:'安全資料鏈結錯誤',
                    91:'可用性分析錯誤',
                    92:'資料匯入錯誤'
                    }
    is_super_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.super_admin.value).first()
    if not is_super_admin: #Groupadmin or user
        is_group_admin = db.query(MemberGroupRole).filter(MemberGroupRole.member_id == member_id,
                                                   MemberGroupRole.member_role == AdminRole.group_admin.value).first()
        if not is_group_admin: # user
            logger.info(f"***********project user{member_id}*********")
            user_get_project = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id,
                                                             MemberProjectRole.project_id == project_id).first() 
            if not user_get_project:
                msg = f"Project_Detail failed: The user {member_id} does not have this project {project_id}"
                logger.error(msg)
                return False,  msg
            
            proj_dict = dict()
            proj_dict['project_id'] = project_id
            proj_dict['project_name'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().project_name
            proj_dict['project_eng'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().project_eng
            proj_dict['enc_key'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().enc_key
            proj_dict['join_type'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().join_func
            proj_dict['jointablename'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().jointablename
            proj_dict['jointablecount'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().jointablecount
            proj_dict['aes_col'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().aes_col
            proj_dict['join_sampledata'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().join_sampledata         
            proj_dict['issingle'] =db.query(Project).filter(Project.project_id == project_id).first().issingle
            proj_dict['single_dataset'] =db.query(Project).filter(Project.project_id == project_id).first().single_dataset
            all_records = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).all() 
            join_func = []
            for proj in all_records:
                join_dict= dict()
                join_dict['id'] = proj.project_joinfuncid
                join_dict['project_id'] = proj.project_id
                join_dict['left_group_id'] = proj.left_group_id
                join_dict['left_datasetname'] = proj.left_dataset
                join_dict['left_col'] = proj.left_col
                join_dict['right_group_id'] = proj.right_group_id
                join_dict['right_datasetname'] = proj.right_dataset
                join_dict['right_col'] = proj.right_col  
                join_func.append(join_dict)          
            join_func_dedu = [dict(t) for t in set([tuple(d.items()) for d in join_func])]
            #join_func_dedu:依照id進行排序
            join_func_dedu = sorted(join_func_dedu, key=lambda x: x["id"])
            proj_dict['join_func'] = join_func_dedu

            project_role  = []
            for proj in all_records:
                join_dict= dict()
                join_dict['id'] = proj.project_roleid
                join_dict['project_id'] = proj.project_id
                join_dict['project_role'] = proj.project_role
                join_dict['member_id'] = proj.rolemember_id
                join_dict['key_code'] =db.query(MemberProjectRole).filter( MemberProjectRole.project_id == proj.project_id, MemberProjectRole.member_id == proj.rolemember_id).first().key_code
                project_role.append(join_dict)            
            project_role_dedu = [dict(t) for t in set([tuple(d.items()) for d in project_role])]
            #project_role_dedu:依照id進行排序
            project_role_dedu = sorted(project_role_dedu, key=lambda x: x["id"])
            proj_dict['project_role'] = project_role_dedu
            return True, proj_dict

        
        else: ##GroupAdmin可以看到所有own group 的project
            logger.info(f"***********Group Admin**************")
            user_get_gp_project = db.query(Project).filter(Project.group_id==is_group_admin.group_id,
                                                   Project.project_id == project_id).first()
            user_get_project = db.query(MemberProjectRole).filter(MemberProjectRole.member_id == member_id,
                                                             MemberProjectRole.project_id == project_id).first()
            if not user_get_gp_project and not user_get_project:
                msg = f"Project_Detail failed: The user {member_id} does not have this project {project_id}"
                logger.error(msg)
                return False,  msg 
            
            proj_dict = dict()
            proj_dict['project_id'] = project_id
            proj_dict['project_name'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().project_name
            proj_dict['project_eng'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().project_eng
            proj_dict['enc_key'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().enc_key
            proj_dict['join_type'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().join_func
            proj_dict['jointablename'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().jointablename
            proj_dict['jointablecount'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().jointablecount
            proj_dict['aes_col'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().aes_col
            proj_dict['join_sampledata'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().join_sampledata         
            proj_dict['issingle'] =db.query(Project).filter(Project.project_id == project_id).first().issingle
            proj_dict['single_dataset'] =db.query(Project).filter(Project.project_id == project_id).first().single_dataset
            all_records = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).all() 
            join_func = []
            for proj in all_records:
                join_dict= dict()
                join_dict['id'] = proj.project_joinfuncid
                join_dict['project_id'] = proj.project_id
                join_dict['left_group_id'] = proj.left_group_id
                join_dict['left_datasetname'] = proj.left_dataset
                join_dict['left_col'] = proj.left_col
                join_dict['right_group_id'] = proj.right_group_id
                join_dict['right_datasetname'] = proj.right_dataset
                join_dict['right_col'] = proj.right_col  
                join_func.append(join_dict)          
            join_func_dedu = [dict(t) for t in set([tuple(d.items()) for d in join_func])]
            #join_func_dedu:依照id進行排序
            join_func_dedu = sorted(join_func_dedu, key=lambda x: x["id"])
            proj_dict['join_func'] = join_func_dedu

            project_role  = []
            for proj in all_records:
                join_dict= dict()
                join_dict['id'] = proj.project_roleid
                join_dict['project_id'] = proj.project_id
                join_dict['project_role'] = proj.project_role
                join_dict['member_id'] = proj.rolemember_id
                join_dict['key_code'] =db.query(MemberProjectRole).filter( MemberProjectRole.project_id == proj.project_id, MemberProjectRole.member_id == proj.rolemember_id).first().key_code
                project_role.append(join_dict)            
            project_role_dedu = [dict(t) for t in set([tuple(d.items()) for d in project_role])]
            #project_role_dedu:依照id進行排序
            project_role_dedu = sorted(project_role_dedu, key=lambda x: x["id"])
            proj_dict['project_role'] = project_role_dedu
            return True, proj_dict

    else: #SuperAdmin可以看到所有的projecy
        logger.info(f"***********SuperAdmin**************")
        user_get_project = db.query(Project).filter(Project.project_id == project_id).first() 
        if not user_get_project:
            msg = f"Project_detail failed: The user {member_id} does not have this project {project_id}"
            logger.error(msg)
            return False,  msg  
        
        proj_dict = dict()
        proj_dict['project_id'] = project_id
        proj_dict['project_name'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().project_name
        proj_dict['project_eng'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().project_eng
        proj_dict['enc_key'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().enc_key
        proj_dict['join_type'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().join_func
        proj_dict['jointablename'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().jointablename
        proj_dict['jointablecount'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().jointablecount
        proj_dict['aes_col'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().aes_col
        proj_dict['join_sampledata'] = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).first().join_sampledata      
        proj_dict['issingle'] =db.query(Project).filter(Project.project_id == project_id).first().issingle
        proj_dict['single_dataset'] =db.query(Project).filter(Project.project_id == project_id).first().single_dataset
        all_records = db.query(ViewsDetails).filter(ViewsDetails.project_id == project_id).all() 
        join_func = []
        for proj in all_records:
            join_dict= dict()
            join_dict['id'] = proj.project_joinfuncid
            join_dict['project_id'] = proj.project_id
            join_dict['left_group_id'] = proj.left_group_id
            join_dict['left_datasetname'] = proj.left_dataset
            join_dict['left_col'] = proj.left_col
            join_dict['right_group_id'] = proj.right_group_id
            join_dict['right_datasetname'] = proj.right_dataset
            join_dict['right_col'] = proj.right_col  
            join_func.append(join_dict)          
        join_func_dedu = [dict(t) for t in set([tuple(d.items()) for d in join_func])]

        #依照id進行排序
        join_func_dedu = sorted(join_func_dedu, key=lambda x: x["id"])

        proj_dict['join_func'] = join_func_dedu
        

        project_role  = []
        for proj in all_records:
            join_dict= dict()
            join_dict['id'] = proj.project_roleid
            join_dict['project_id'] = proj.project_id
            join_dict['project_role'] = proj.project_role
            join_dict['member_id'] = proj.rolemember_id
            join_dict['key_code'] =db.query(MemberProjectRole).filter( MemberProjectRole.project_id == proj.project_id, MemberProjectRole.member_id == proj.rolemember_id).first().key_code
            project_role.append(join_dict)            
        project_role_dedu = [dict(t) for t in set([tuple(d.items()) for d in project_role])]
        #project_role_dedu:依照id進行排序
        project_role_dedu = sorted(project_role_dedu, key=lambda x: x["id"])
        proj_dict['project_role'] = project_role_dedu

        return True, proj_dict


## 使用者登入後，從專案列表，選取對應的專案，想要看專案裡的資訊
@Project_Detail.post("/detail") ##need to edit
def detail_projects(project_id: int = Form(), decode_info: dict = Depends(verify_token), db: Session = Depends(get_db)):
    member_id = decode_info['member_id'] #從token找到who are u == 'member_id'
    useraccount = decode_info['sub']
    checked, msg = user_is_active(member_id,db)
    if not checked:
        msg = "User has been suspended."
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)
    logger.info(f"***********Project_Detail*************")
    try:
        checked, project_detail = get_project_detail(member_id, project_id, db)
    except Exception as e:    
        checked, msg = f"Member {useraccount} project list failed: {str(e)}"
        logger.error(msg)
        result = Result(msg=msg, status=False)
        return _result_wrapper(result, status_code=400)


    msg = f"Member {useraccount} view project detail successful"
    logger.info(msg)
    
    result = Result(msg=msg, MemberID=member_id, obj=project_detail, status=checked) ##for check member id
    #result = Result(msg=msg, obj=project_list, status=True) ##should be
    return _result_wrapper(result, status_code=200)
