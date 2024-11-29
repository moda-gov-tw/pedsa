import time
import random

from celery import Celery
from celery.utils.log import get_task_logger
import base64
import json
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig
from module.base64convert import getJsonParser, encodeDic
import os

from module import getSqlString

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

#20240628:gen_getGenTbl
@celery.task
def gen_getGenTbl_task(project_id: int, project_name: str, member_id: int,useraccount: str,privacy_type: str, mainInfo: dict):
    # try:
    jarfiles = getConfig().getJarFiles()
    sparkCode = getConfig().getSparkCode('gen_getGenTbl.py')
    projName = project_name #"decrypt_output"
    projID = project_id
    project_gen = projName+'_'+privacy_type
    userAccount = useraccount
    userId = member_id

    # Collect all udf functions
    udfs = [func for func in dir(getSqlString) if func[:3] == 'get']

    meta_ = {}
    meta_['dbName'] = project_gen
    tblColDict = dict()
    doMinMaxCols = dict()
    celery_log.info(mainInfo)
    # Iterate each table
    for tbl in mainInfo:
        genList = ''  # List of all actions on each columns.
        colList = mainInfo[tbl]['col_en'].split(',')
        rawTblName = mainInfo[tbl]['tblName']
        doMinMaxCols[rawTblName] = dict()
        
        for col_ in mainInfo[tbl]['colInfo']:
            '''
                col_ = col_1,col_2,...
                check json schema of each generalization
                schema = js.colInfoSchema()
                json_ = js.loadJson(mainInfo[tbl]['colInfo'][col_],schema) # return str if error                
            '''

                # check schema
            json_ = mainInfo[tbl]['colInfo'][col_]
            celery_log.info('############################1')
            celery_log.info(type(json_))
            celery_log.info(json_)
            if isinstance(json_, str):
                errMsg = 'JsonsError_%s', json_
                celery_log.debug(errMsg)
                return {
                    "msg": errMsg
                }
            
            # Find what action this column is.
            action_ = 'getNogenerlize'
            for function in udfs:
                if function == json_['apiName']:
                    action_ = function

            celery_log.info('############################2')
            celery_log.info(type(action_))
            celery_log.info(action_)
            # Check if column need to do Min Max boung
            if action_ == 'getGenNumLevelMinMax':
                min_bound, max_bound = getSqlString.getGenNumLevelMinMax(json_, bound=True)
                doMinMaxCols[rawTblName][json_['colName']] = "{0},{1}".format(min_bound, max_bound)

                # Get action function
            colSqlAction = getSqlString.__dict__.get(action_)(json_)  # Return sql string

            # If found celery error, then return
            if colSqlAction[:16] == 'celery_gen_error':
                errMsg = str(colSqlAction)
                celery_log.debug(errMsg)
                return {
                        "msg": errMsg
                }

            genList += colSqlAction
            genList += '^'

            colList.pop(colList.index(json_['colName']))

        for colName in colList:
            # for those columns no generalized, append columns name
            genList += colName
            genList += '^'

        genList = genList[:-1]

            # Decode genList into base64 for ssh
        genListEncode = base64.b64encode(genList.encode('utf-8')).decode('utf-8')

        tblColDict[mainInfo[tbl]['tblName']] = genListEncode

    celery_log.info('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    genDictEncode = encodeDic(tblColDict).decode('utf-8')
    doMinMaxEncode = encodeDic(doMinMaxCols).decode('utf-8')
    
    celery_log.info(genDictEncode)
    celery_log.info(doMinMaxEncode)
    try:
        cmdStr = '''
            spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7} {8}'''.format(jarfiles,
                                                              sparkCode,
                                                              project_gen,
                                                              genDictEncode,
                                                              doMinMaxEncode,
                                                              projID,                                                                                   userAccount,
                                                              userId,
                                                              privacy_type,
                                                              )
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        celery_log.info(f"stdin is {stdin}")
        celery_log.info(f"stdout is {stdout}")
        celery_log.info(f"stderr is {stderr}")

        return {
                    "project_id": project_id,
                    "project_name": project_gen,
                    "msg": f"cmdStr is {cmdStr}"
            }

    except Exception as e:
        errMsg = 'ssh connect error: ' + str(e)
        celery_log.debug(errMsg)
        return {
                "msg": errMsg
            }
    # except Exception as e:
    #     errMsg = 'gen_getGenTbl error: ' + str(e)
    #     celery_log.debug(errMsg)
    #     return {
    #             "msg": errMsg
    #         }
    
#20240627:gen_import
@celery.task
def gen_import_task(project_id: int, project_name: str, member_id: int,useraccount: str,privacy_type: str, select_cols: str):
    try:
        jarfiles = getConfig().getJarFiles()
        sparkCode = getConfig().getSparkCode('gen_import.py')
        projName = project_name #"decrypt_output"
        projID = project_id
        project_gen = projName+'_'+privacy_type
        userAccount = useraccount
        userId = member_id
        meta_ = {}
        meta_['dbName'] = project_gen
        
        # celery_log.info("-------in----1")
        # get tables in projName
        type_ = 'local'
        serverPath = getConfig().getImportPath(type_)
        filePath = os.path.join(serverPath, project_gen, '*')
        cmdStr = 'stat --format "%n" ' + filePath
        celery_log.info(f"-------in--cmdStr--{cmdStr}")
        ssh_get_tables = ssh_hdfs()
        stdin_, stdout_, stderr_ = ssh_get_tables.callCommand_output(cmdStr)
        # celery_log.info("-------in----2")
        
        # collect server folder
        try:
            input_list = []
            mainInfo = dict()
            for line in stdout_.readlines():
                input_list.append(line.strip('\n'))

            # collect file name
            tables = list()
            for path_ in input_list:
                celery_log.info(f"-------in--path_1--{path_}")
                path, file = os.path.split(path_)
                celery_log.info(f"-------in--path_2--{path}---{file}")
                fileName = file.split('.csv')[0]
                tables.append(fileName)
            for tbl in tables:
                mainInfo[tbl] = {'tblName': tbl}
        except Exception as e:
            errMsg = 'collect_server_folder_error: ' + str(e)
            return errMsg
        # celery_log.info("-------in----3")
        # updat state for response to front
        tables = ';'.join([mainInfo[tbl]['tblName'] for tbl in mainInfo])
        meta_['tblName'] = tables
        importListEncode = base64.b64encode(tables.encode('utf-8')).decode('utf-8')

        selectColsEncode = base64.b64encode(select_cols.encode('utf-8')).decode('utf-8')
        # celery_log.info(f"-------in----4--{importListEncode}")
        try:
            jarfiles = getConfig().getJarFiles()
            path = getConfig().getImportPath('local')
            sparkCode = getConfig().getSparkCode('gen_import.py')

            cmdStr='''
            spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7} {8} {9}'''.format(jarfiles,
                                                                    sparkCode,
                                                                    project_gen,
                                                                    projID,
                                                                    importListEncode,
                                                                    path,
                                                                    userAccount,
                                                                    userId,
                                                                    privacy_type,
                                                                    selectColsEncode)

            ssh_for_bash = ssh_hdfs()
            stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
            celery_log.info(f"stdin is {stdin}")
            celery_log.info(f"stdout is {stdout}")
            celery_log.info(f"stderr is {stderr}")

            return {
                    "project_id": project_id,
                    "project_name": project_gen,
                    "msg": f"cmdStr is {cmdStr}"
                }

        except Exception as e:
            errMsg = 'ssh connect error: ' + str(e)
            celery_log.debug(errMsg)
            return {
                "msg": errMsg
            }
    except Exception as e:
        errMsg = 'gen import error: ' + str(e)
        celery_log.debug(errMsg)
        return {
                "msg": errMsg
            }


#20240627:gen_import
@celery.task
def gen_export_task(project_id: int, project_name: str, finaltblName: str, member_id: int,useraccount: str,privacy_type: str,pro_col_en: str,pro_col_cht: str):
    try:
        projName = project_name #"decrypt_output"
        project_gen = projName+'_'+privacy_type
        projID = project_id

        userAccount = useraccount
        userId = member_id

        try:
            jarfiles = getConfig().getJarFiles()
            path = getConfig().getExportPath('local')
            sparkCode = getConfig().getSparkCode('gen_getExport.py')
            cmdStr='''
            spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7}'''.format(jarfiles,
                                                                  sparkCode,
                                                                  project_gen,
                                                                  finaltblName,
                                                                  path,
                                                                  projID,
                                                                  pro_col_en,
                                                                  pro_col_cht)

            ssh_for_bash = ssh_hdfs()
            stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
            celery_log.info(f"stdin is {stdin}")
            celery_log.info(f"stdout is {stdout}")
            celery_log.info(f"stderr is {stderr}")

            return {
                "project_id": project_id,
                "project_name": project_gen,
                "msg": f"cmdStr is {cmdStr}"
            }

        except Exception as e:
            errMsg = 'ssh connect error: ' + str(e)
            celery_log.debug(errMsg)
            return {
                "msg": errMsg
            }
    except Exception as e:
        errMsg = 'gen import error: ' + str(e)
        celery_log.debug(errMsg)
        return {
            "msg": errMsg
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
