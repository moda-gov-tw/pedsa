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
from app.core.schemas import ProjectJoinFunct, Projectjoin

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



@monitor.post("/getcontainersstatus")
def getcontainersStatus():
    logger.info(f"*********** getContainersStatus*********")
    try:
        logger.info(f"test 123")
        checkContainersStatus_ = checkContainersStatus()
        container_dict_ = checkContainersStatus_.getDockerClient()

        logger.info(container_dict_)
        ###logger.info(container_dict_.keys())

        return {
            "status": 1,
            "container_dict": container_dict_,
            "msg":f"get {len(container_dict_)} containers status"
        }
    

        
    except Exception as e:
        return {
            "status": -1,
            "msg": f"ERROR: {e}"
        }


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
