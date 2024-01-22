import time
import random

from celery import Celery
from celery.utils.log import get_task_logger
import base64
import json
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig
from config.base64convert import getJsonParser, encodeDic
import os


celery = Celery(
    "tasks",
    broker="redis://redis_service_compose:6379/0",
    backend="redis://redis_service_compose:6379/0",
)

celery_log = get_task_logger(__name__)

@celery.task
def send_email(email: str):
    time.sleep(random.randint(1, 4))
    celery_log.info("Email has been sent")
    return {
        "msg": f"Email has been sent to {email}",
        "details": {
            "destination": email,
        },
    }


@celery.task
def join_json(member_id: int, project_id: int, project_eng: str, enc_key: str, join_type: int, join_func: list):
    # base = getJsonParser(j_str)
    #time.sleep(random.randint(1, 4))
    celery_log.info(f"member_id is {member_id}")
    celery_log.info(f"project_id is {project_id}")
    celery_log.info(f"project_id is {project_eng}")
    celery_log.info(f"enc_key is {enc_key}")
    celery_log.info(f"join_type is {join_type}")
    celery_log.info(f"join_func is {join_func}")

    list_str = str(join_func)
    join_func_encoded = base64.b64encode(list_str.encode()).decode()

    try:
        jarfiles = getConfig().getJarFiles()
        path = getConfig().getImportPath('local')
        sparkCode = getConfig().getSparkCode('joinfile.py')
        ex_path = getConfig().getExportPath('local')
        celery_log.info(f"jarfiles is {jarfiles}")
        celery_log.info(f"path is {path}")
        celery_log.info(f"sparkCode is {sparkCode}")
        celery_log.info(f"ex_path is {ex_path}")
        cmdStr='''spark-submit --jars {0} {1} {2} {3} {4} {5} {6}'''.format(jarfiles,
                                                                    sparkCode,
                                                                    member_id,
                                                                    join_type,
                                                                    join_func_encoded,
                                                                    project_eng,
                                                                    project_id)

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        celery_log.info(f"stdin is {stdin}")
        celery_log.info(f"stdout is {stdout}")
        celery_log.info(f"stderr is {stderr}")

        return {
            "member_id": member_id,
            "project_id": project_id,
            "project_name": project_eng,
            "enc_key": enc_key,
            "join_type": join_type,
            "join_func": join_func,
            "msg": f"cmdStr is {cmdStr}"
        }

    except Exception as e:
        errMsg = 'ssh connect error: ' + str(e)
        celery_log.debug(errMsg)
        return {
            "msg": errMsg,

        }


@celery.task
def import_json(i_str: str,join_info: list):
    base = getJsonParser(i_str)
    celery_log.info("JsonParser has been success")
    celery_log.info(f"JsonParser is {base}")
    celery_log.info(f"JoinInfo is {join_info}")

    try:
        jarfiles = getConfig().getJarFiles()
        path = getConfig().getImportPath('local')
        sparkCode = getConfig().getSparkCode('joinfile_import.py')
        ex_path = getConfig().getExportPath('local')
        celery_log.info(f"jarfiles is {jarfiles}")
        celery_log.info(f"path is {path}")
        celery_log.info(f"sparkCode is {sparkCode}")
        celery_log.info(f"ex_path is {ex_path}")
        col_str = ""
        tbl_str = ""

        for item in join_info:
            if item == join_info[-1]:
                col_str = col_str + item['left_col'] + ',' + item['right_col']
                tbl_str = tbl_str + item['left_dataset'] + ',' + item['right_dataset']
            else:
                col_str = col_str + item['left_col'] + ',' + item['right_col'] + ','
                tbl_str = tbl_str + item['left_dataset'] + ',' + item['right_dataset'] +','


        cmdStr='''spark-submit --jars {0} {1} {2} {3} {4} {5} {6}'''.format(jarfiles,
                                                                            sparkCode,
                                                                            i_str,
                                                                            path,
                                                                            ex_path,
                                                                            col_str,
                                                                            tbl_str)

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        celery_log.info(f"stdin is {stdin}")
        celery_log.info(f"stdout is {stdout}")
        celery_log.info(f"stderr is {stderr}")

        return {
            "msg": f"ssh connect success get Json Parser is {base}"
        }

    except Exception as e:
        errMsg = 'ssh connect error: ' + str(e)
        celery_log.debug(errMsg)
        return {
            "msg": errMsg
        }


@celery.task
def AES_Decrypt_task(project_id: int, project_name: str, enc_key: str, aes_col: str):
    # base = getJsonParser(aes_str)
    # celery_log.info("JsonParser has been success")
    # celery_log.info(f"JsonParser is {base}")
    try:
        jarfiles = getConfig().getJarFiles()
        sparkCode = getConfig().getSparkCode('udfAESUID_final_project.py')
        # 資料名稱內容
        tblName = "aaa" # decrypt_file #"w1_adult_id123_enc" #tblName
        # 解密 Key
        key = enc_key #"AAAAAABC0DCB39FE182FAF7CE960A2B0BA63AFEEDC76D8A92AED52938AA06ABA" #key
        sep = ","
        # 解密欄位
        columns_mac = aes_col #"age" #columns_mac
        projName = project_name #"decrypt_output"
        projID = project_id # "999"
        dateHash = "Y"
        onlyHash = "Y" # DO Decrypt
        userId="1"
        userAccount="deidadmin"

        celery_log.info(f"jarfiles is {jarfiles}")
        celery_log.info(f"sparkCode is {sparkCode}")

        cmdStr='''spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}'''.format(
                jarfiles,
                sparkCode,
                tblName,
                key,
                sep,
                columns_mac,
                projName,
                projID,
                dateHash,
                onlyHash,
                userId,
                userAccount
                )


        celery_log.info(f"cmdStr is {cmdStr}")
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

        return {
            "project_id": project_id,
            "project_name": project_name,
            "aes_col": aes_col,
            "msg": f"cmdStr is {cmdStr}"
        }

    except Exception as e:
        errMsg = 'ssh connect error: ' + str(e)
        celery_log.debug(errMsg)
        return {
            "msg": errMsg
        }
