from fastapi import FastAPI,APIRouter,Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from celery_worker import send_email, celery, join_json, import_json, AES_Decrypt_task
from config.getContainersStatus import checkContainersStatus
from model import User

from logging.config import dictConfig
import logging
from app.core.config  import LogConfig
from config.base64convert import getJsonParser


from app.core.config import LogConfig
from app.database import get_db
from app.core.models import ProjectJoinFunc, Project
from app.core.schemas import ProjectJoinFunct, Projectjoin, Result
from app.core.utils import _result_wrapper


import subprocess
from config.loginInfo import getConfig



dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

import time
import random
import json
import os


monitor = APIRouter()


#@app.get("/tasks")
def read_task(task_id: str):
    task_result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }



@monitor.get("/getcontainersstatus")
def getcontainersStatus():
    logger.info(f"*********** getContainersStatus*********")
    try:
        logger.info(f"test 123")
        checkContainersStatus_ = checkContainersStatus()
        container_dict_ = checkContainersStatus_.getDockerClient()

        logger.info(container_dict_)
        ###logger.info(container_dict_.keys())

        # compare_list = ['pets_syn_web','pets_syn_redis_syn1','pets_syn_nginx','pets_syn_genSyncData_celery','pets_syn_deidweb','pets_dp_web','pets_dp_redis_dp1','pets_dp_genSyncData_celery',
        #                 'pets_dp_differential_privacy','pets_dp_deidweb','PETservice_redis_fastapi','PETservice_flower','PETservice_fastapi','PETservice_celery','PET_join_Hadoop_psqlhms',
        #                 'PET_join_Hadoop_nodemaster','PET_join_Hadoop_MariaDB_nrt','PETWEB_nextjs','PETSWebservice_worker','PETSWebservice_web','PETSWebservice_redis','PETSWebservice_deidweb',
        #                 'PETSWebservice_OpenApi_web','PETSHadoop_psqlhms','PETSHadoop_nodemaster']
        compare_list = ['PETSHadoop_nodemasterK','PETSHadoop_psqlhms','PETSWebservice_OpenApi_web','PETSWebservice_deidweb','PETSWebservice_redis_k','PETSWebservice_web','PETSWebservice_worker',
                        'PET_join_Hadoop_MariaDB_nrt','PET_join_Hadoop_nodemasterJ','PET_join_Hadoop_psqlhmsJ','pets_dp_deidweb','pets_dp_genSyncData_celery','pets_dp_redis_dp1','pets_dp_web',
                        'pets_service_celery','pets_service_fastapi','pets_service_redis_fastapi','pets_syn_deidweb','pets_syn_genSyncData_celery','pets_syn_nginx','pets_syn_redis_syn1','pets_syn_web','pets_web_nextjs']

        remove_list = []  
        for item in container_dict_:
            container = item['container_name'].split('.')[0]

            if container not in compare_list:
                remove_list.append(item.copy())

            if container in compare_list and item['container_status'] == 'running':
                compare_list.remove(container)
            
        # error = 'error'
        # error +=1
        
        for item in remove_list:
            container_dict_.remove(item)
            
        # compare_list = ['pets_dp_web']
        # container_dict_.append({'container_name':'pets_dp_web',
        #                         'container_status': 'error'})

        if compare_list == []:
            # result = Result(msg = f"get {len(container_dict_)} containers status" , status = True , obj = container_dict_)
            result = {
                "status": True,
                'is_connection': True,
                "obj": container_dict_,
                "msg":f"get {len(container_dict_)} containers status"
            }
            return _result_wrapper(result=result,status_code=200)
            
        else:
            # result = Result(msg = f"error containers status {compare_list}" , status = False , obj = container_dict_)
            result =  {
                "status": True,
                'is_connection': False,
                "container_dict": container_dict_,
                "msg":f"error containers status {compare_list}"
            }
            return _result_wrapper(result=result,status_code=200)
           

    

        
    except Exception as e:
        result = Result(msg = f"ERROR: {e}" , status = False)
        return _result_wrapper(result=result,status_code=200)
        # return {
        #     "status": -1,
        #     "msg": f"ERROR: {e}"
        # }


#@app.post("/joindata")
def joindata(joinjson: Projectjoin, db :Session =Depends(get_db)):
    logger.info(f"*********** joinjson: {joinjson}*********")
    try:
        logger.info(type(joinjson))

        member_id = joinjson.member_id
        project_id = joinjson.project_id
        enc_key = joinjson.enc_key
        join_type = joinjson.join_type
        join_func = joinjson.join_func
        project_eng = db.query(Project).filter(Project.project_id == project_id).first().project_eng

        logger.info(f"*********** join_func: {join_func}*********")
        path = getConfig().getImportPath('local')
        ori_path = getConfig().getMovePath('local')
        ori_project_path = os.path.join(ori_path, project_eng)
        logger.info(f"path is {path}")
        logger.info(f"ori_project_path is {ori_project_path}")

        cmd = f'sshpass -p "citcw200@" scp -o StrictHostKeyChecking=no -P 6922 -r {ori_project_path} hadoop@140.96.178.108:{path}'
        logger.info(f"cmd is {cmd}")

        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(proc.stdout)
        logger.info(proc.stderr)

        task = join_json.delay(member_id, project_id, project_eng, enc_key, join_type, join_func)
        # task = join_json.delay(jsonbase64)
        task_id = task.id
        time.sleep(random.randint(5, 10))
        if celery.AsyncResult(task_id).status == "SUCCESS":
            task_result = read_task(task_id)
            return {
                "task_id": task_result["task_id"],
                "task_status": task_result["task_status"],
                "status": 0 ,
                "msg": "",
                "dataInfo": task_result["task_result"],
            }
    except Exception as e:
        return {
            "status": -1,
            "msg": f"ERROR: {e}",
        }
