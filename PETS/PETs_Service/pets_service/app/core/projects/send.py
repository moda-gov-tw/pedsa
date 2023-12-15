from fastapi import FastAPI,APIRouter,Depends

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import SecretStr
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from celery_worker import send_email, celery, join_json, import_json, AES_Decrypt_task
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

import configparser

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")

import time
import random
import json
import os


app = APIRouter()


#@app.get("/tasks")
def read_task(task_id: str):
    task_result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }

#@app.post("/users")
def create_user(user: User):
    task = send_email.delay(user.email)
    task_id = task.id
    time.sleep(random.randint(3, 6))
    task_result = read_task(task_id)
    return {
        "task_id": task_result["task_id"],
        "task_status": task_result["task_status"],
        "task_result": task_result["task_result"],
    }



@app.post("/joindata")
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

        try:
            file_ = '/usr/src/app/config/Hadoop_information.txt'
            config = configparser.ConfigParser()
            config.read(file_)
            join_ip = config.get('Hadoop_information', 'join_ip')
            join_port = config.get('Hadoop_information', 'join_port')
            logger.info(f"join_ip is {join_ip}")
            logger.info(f"join_port is {join_port}")
        except Exception as e:
            logger.debug('to PETs hadoop error : ',str(e))


        # cmd = f'sshpass -p "citcw200@" scp -o StrictHostKeyChecking=no -P 6922 -r {ori_project_path} hadoop@140.96.178.108:{path}'
        cmd = f'sshpass -p "citcw200@" scp -o StrictHostKeyChecking=no -P ' + join_port +' -r ' + ori_project_path+ ' hadoop@'+ join_ip +':' +path
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


@app.post("/comparedata")
def comparedata(project_id:int = 1,db :Session =Depends(get_db)):
    try:
        # catch = getJsonParser(jsonbase64)
        catch = dict()
        catch["project_id"] = project_id
        join_info = db.query(ProjectJoinFunc).filter(ProjectJoinFunc.project_id == catch['project_id']).all()

        if not join_info:
            msg = f"does not have this project {catch['project_id']}"
            logger.error(msg)
            return {
                "msg": msg,
                "status": -1
            }

        project_eng = db.query(Project).filter(Project.project_id == catch['project_id']).first().project_eng
        logger.info(f"*********** project_eng: {project_eng}*********")

        deal_data = []
        for item in join_info:
            deal_data.append(dict(ProjectJoinFunct.model_validate(item)))
        logger.info(f"*********** deal_data: {deal_data}*********")



        data_path = "/usr/src/app/sftp_upload_floder/%s" %(project_eng)
        logger.info(f"*********** data_path: {data_path}*********")

        folder_list = os.listdir(data_path)
        logger.info(f"*********** folder_list: {folder_list}*********")

        folder_csv = []
        for f_csv in folder_list:
            if f_csv.split(".")[-1] == 'csv':
                folder_csv.append(f_csv)

        logger.info(f"*********** folder_csv: {folder_csv}*********")

        folder_json = []
        for f_json in folder_list:
            if f_json.split(".")[-1] == 'json':
                folder_json.append(f_json)

        logger.info(f"*********** folder_json: {folder_json}*********")

        df_to_be_upload = {}
        to_be_compare = {}
        # compare_data_output = {}
        # compare_data_output['status'] = -1
        # compare_data_output['message'] = ""
        importlist = []

        for tblName in folder_json:
            f = open(os.path.join(data_path,tblName))
            read_j = json.load(f)
            to_append = {}

            to_be_compare[read_j['enc_datasetname']] = read_j
            to_append['dataset'] = read_j['enc_datasetname']

            to_append['dataset_count'] = read_j['ds_count']
            logger.info("Dealing with col_setting")
            col_setting = []
            cols = read_j['col_name'].split(',')
            cols_set = read_j['col_setting'].split(',')

            for i in range(len(cols)):
                col_setting_item = {}
                col_setting_item['col'] = cols[i]
                col_setting_item['func'] = cols_set[i]
                col_setting.append(col_setting_item)
            to_append['col_setting'] = col_setting
            logger.info("Dealing with col_setting finish")
            importlist.append(to_append)

        dataInfo = {}
        dataInfo['importlist'] = importlist
        logger.info(f"*********** 1. dataInfo: {dataInfo}*********")


        # if len(folder_csv)!=len(folder_json) :
        #     msg = f"the CSV files are not equal the JSON files"
        #     logger.error(msg)
        #     return {
        #         "msg": msg,
        #         "status": -2,
        #         "dataInfo": dataInfo,
        #     }


        folder_json_name = []
        for j_name in folder_json:
            j_n = j_name.split(".")[0]
            folder_json_name.append(j_n)
        logger.info(f"*********** folder_json_name: {folder_json_name}*********")

        folder_csv_name = []
        for c_name in folder_csv:
            c_n = c_name.split(".")[0]
            folder_csv_name.append(c_n)
        logger.info(f"*********** folder_csv_name: {folder_csv_name}*********")


        for i in range(len(folder_json_name)):
            if folder_json_name[i] not in folder_csv_name:
                msg = f"the CSV files are not equal the JSON files. file name: {folder_json_name[j]} is not a pair "
                logger.error(msg)
                return {
                    "msg": msg,
                    "status": -2,
                    "dataInfo": dataInfo,
                }

        for j in range(len(folder_csv_name)):
            if folder_csv_name[j] not in folder_json_name:
                msg = f"the CSV files are not equal the JSON files. file name: {folder_csv_name[j]} is not a pair "
                logger.error(msg)
                return {
                    "msg": msg,
                    "status": -2,
                    "dataInfo": dataInfo,
                }



        col_str = ""
        tbl_str = ""
        for item in deal_data:
            if item == deal_data[-1]:
                if len(item['left_col'].split(','))>1 and len(item['right_col'].split(','))>1 :
                    new_left_col = item['left_col'].replace(",", "|^")
                    new_right_col = item['right_col'].replace(",", "|^")
                    col_str = col_str + new_left_col + ',' + new_right_col
                    tbl_str = tbl_str + item['left_dataset'] + ',' + item['right_dataset']
                else:
                    col_str = col_str + item['left_col'] + ',' + item['right_col']
                    tbl_str = tbl_str + item['left_dataset'] + ',' + item['right_dataset']
            else:
                if len(item['left_col'].split(','))>1 and len(item['right_col'].split(','))>1 :
                    new_left_col = item['left_col'].replace(",", "|^")
                    new_right_col = item['right_col'].replace(",", "|^")
                    col_str = col_str + new_left_col + ',' + new_right_col+ ','
                    tbl_str = tbl_str + item['left_dataset'] + ',' + item['right_dataset'] + ','
                else:
                    col_str = col_str + item['left_col'] + ',' + item['right_col'] + ','
                    tbl_str = tbl_str + item['left_dataset'] + ',' + item['right_dataset'] + ','


        logger.info(f"*********** col_str: {col_str}*********")
        logger.info(f"*********** tbl_str: {tbl_str}*********")
        tbl_list = list(set(tbl_str.split(",")))

        logger.info(f"*********** tbl_list: {tbl_list}*********")

        DB_table_list = []
        for d in deal_data:
            d_r = d["right_dataset"]
            DB_table_list.append(d_r)
            d_l = d["left_dataset"]
            DB_table_list.append(d_l)
        logger.info(f"*********** DB_table_list: {DB_table_list}*********")
        DB_table_list_set = list(set(DB_table_list))
        logger.info(f"*********** DB_table_list_set: {DB_table_list_set}*********")

        for j in range(len(folder_csv)):
            if folder_csv[j] not in DB_table_list_set:
                msg = f"the CSV files are not equal the DB.  file name: {folder_csv[j] } is not in DB "
                logger.error(msg)
                return {
                    "msg": msg,
                    "status": -2,
                    "dataInfo": dataInfo,
                }

        tables = []
        items = tbl_str.split(',')
        for item in items:
            if item[:-len(".csv")] not in tables:
                tables.append(item[:-len(".csv")])

        logger.info("tables = %s" ,tables)

        df_to_be_upload = {}
        to_be_compare = {}
        compare_data_output = {}
        compare_data_output['status'] = -1
        compare_data_output['message'] = ""
        importlist = []

        for tblName in tables:
            f = open(os.path.join(data_path,tblName+'.json'))
            read_j = json.load(f)
            to_append = {}


            to_be_compare[read_j['enc_datasetname']] = read_j
            to_append['dataset'] = read_j['enc_datasetname']




            to_append['dataset_count'] = read_j['ds_count']
            logger.info("Dealing with col_setting")
            col_setting = []
            cols = read_j['col_name'].split(',')
            cols_set = read_j['col_setting'].split(',')

            for i in range(len(cols)):
                col_setting_item = {}
                col_setting_item['col'] = cols[i]
                col_setting_item['func'] = cols_set[i]
                col_setting.append(col_setting_item)
            to_append['col_setting'] = col_setting
            logger.info("Dealing with col_setting finish")
            importlist.append(to_append)

        dataInfo = {}
        dataInfo['importlist'] = importlist
        tables = tbl_str.split(',')
        columns = col_str.split(',')
        datacompare = []
        logger.info("dealing with datacompare item " )
        logger.info("table = %s" ,tables)
        logger.info("columns = %s" ,columns)
        try:
            for i in range(int(len(tables)/2)):
                logger.info("in for loop")
                datacompare_item = {}
                datacompare_item['dataset'] = tables[2*i] + '*' + tables[2*i+1]
                logger.info("datacompare_item['dataset'] %s" ,datacompare_item['dataset'])
                datacompare_item_col = columns[2*i].replace("|^", ",") + '*' + columns[2*i+1].replace("|^", ",")
                datacompare_item['col'] = datacompare_item_col
                if tables[2*i] in to_be_compare and tables[2*i+1] in to_be_compare :
                    datacompare_item['match'] = 'Y'
                else:
                    datacompare_item['match'] = 'N'
                    datacompare_item['colmatch'] = 'N'

                if  "," not in datacompare_item_col:
                    cols = to_be_compare[tables[2*i]]['col_name'].split(',')
                    cols2 = to_be_compare[tables[2*i+1]]['col_name'].split(',')

                    if columns[2*i] in cols and columns[2*i+1] in cols2:
                        logger.info("to find cols 1 %s",columns[2*i])
                        logger.info("to find cols 1 in  %s",cols)

                        logger.info("to find cols 2 %s",columns[2*i+1])
                        logger.info("to find cols 2 in  %s",cols2)

                        datacompare_item['colmatch'] = 'Y'
                    else:
                        datacompare_item['colmatch'] = 'N'
                else:
                    for c in deal_data:
                        c_r = c["right_col"]
                        c_r = c_r.replace(",", "|^")
                        l_r = c["left_col"]
                        l_r = l_r.replace(",", "|^")
                        if c_r not in columns or l_r not in columns:
                            datacompare_item['colmatch'] = 'N'
                        else:
                            datacompare_item['colmatch'] = 'Y'




                datacompare.append(datacompare_item)
                logger.info("datacompare = %s" ,datacompare)

                dataInfo['datacompare'] = datacompare
                compare_data_output['dataInfo'] = dataInfo
                compare_data_output['status'] = 0
                logger.info("compare_data_output = %s" ,compare_data_output)
                logger.info(f"*********** 2. dataInfo: {dataInfo}*********")


            msg = f"data not in folder"
            for i in range(len(tbl_list)):
                if tbl_list[i] not in folder_csv:
                    msg += ' ' + tbl_list[i]
                    logger.error(msg)
                    return {
                        "msg": msg,
                        "status": -2,
                        "dataInfo": dataInfo,
                    }

        except Exception as e:
            return {
                "msg": f"ERROR: {e}",
                "status": -4,
                "dataInfo": dataInfo,
            }




        return {
            "status": 0 ,
            "msg": "",
            "dataInfo": dataInfo,
        }

        #
        #
        #
        # task = import_json.delay(catch,deal_data)
        # task_id = task.id
        # time.sleep(random.randint(5, 10))
        # if celery.AsyncResult(task_id).status == "SUCCESS":
        #     task_result = read_task(task_id)
        #     return {
        #         "task_id": task_result["task_id"],
        #         "task_status": task_result["task_status"],
        #         "task_result": task_result["task_result"],
        #         "status" : 0,
        #         "deal_data" : deal_data
        #     }

    except Exception as e:
        return {
            "msg": f"ERROR: {e}",
            "status": -2
        }

@app.post("/aesdecrypt")
def aesdecrypt(project_id:int = 5, aes_col:str = 'age_w2_b' ,db :Session =Depends(get_db)):
    try:
        # catch = getJsonParser(jsonbase64)
        catch = dict()
        catch["project_id"] = project_id
        #catch["decrypt_file"] = decrypt_file
        logger.info(f"***********jsonbase64 info{catch}*********")
        logger.info(catch)
        enc_key = db.query(Project).filter(Project.project_id == catch['project_id']).first().enc_key
        # aes_col = db.query(Project).filter(Project.project_id == catch['project_id']).first().aes_col
        project_name = db.query(Project).filter(Project.project_id == project_id).first().project_eng
        #jointablename = db.query(Project).filter(Project.project_id == catch['project_id']).first().jointablename


        logger.info(enc_key)
        logger.info(aes_col)
        #logger.info(jointablename)


        task = AES_Decrypt_task.delay(project_id, project_name, enc_key, aes_col)
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
            "task_status": f"ERROR: {e}",
        }


@app.post("/sample")
def sample(project_id:int = 22,db :Session =Depends(get_db)):
    try:
        catch = dict()
        if project_id == None or project_id is None:
            return {
                "msg": f"project_id is None",
                "status": -1
            }

        catch["project_id"] = project_id
        logger.info(f"***********jsonbase64 info{catch}*********")
        logger.info(catch)
        try:
            join_sampledata = db.query(Project).filter(Project.project_id == catch['project_id']).first().join_sampledata
            project_name = db.query(Project).filter(Project.project_id == catch['project_id']).first().project_name
            project_eng = db.query(Project).filter(Project.project_id == catch['project_id']).first().project_eng
        except Exception as e:
            return {
                "msg": f"project_id  ERROR : {e}",
                "status": -2
            }

        obj={}
        obj["project_id"] = project_id
        obj["project_name"] = project_name
        obj["project_eng"] = project_eng
        obj["join_sampledata"] = join_sampledata

        return {
            "status": 0 ,
            "msg": "",
            "obj": obj,
        }
    except Exception as e:
        return {
            "msg": f"unknow ERROR: {e}",
            "status": -3
        }