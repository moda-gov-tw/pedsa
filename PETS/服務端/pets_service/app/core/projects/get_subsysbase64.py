from config.loginInfo import getConfig
from config.MyLib.connect_sql import ConnectSQL

import base64
import json

def getJsonParser(jsonBase64__):
    if jsonBase64__ is None:
        return 'input error! getJsonParser input is None!'
    # decode base64
    try:
        de_b64 = base64.b64decode(jsonBase64__)
    except Exception as err:
        return 'decode base64 error! - %s:%s' % (type(err).__name__, err)
    # json parser
    try:
        jsonDic__ = json.loads(de_b64)
        print("Before getJsonParser: ")
        print(jsonBase64__)
        print("After getJsonParser result: ")
        print(jsonDic__)
    except Exception as err:
        return 'json parser error! - %s:%s' % (type(err).__name__, err)
    return jsonDic__


def encodeDic(dictionary__):
    if dictionary__ is None:
        return 'input error! encodeDictionary input is None!'
    try:
        print("Before encodeDic: ")
        print(dictionary__)
        jsonBase64__ = base64.b64encode(json.dumps(dictionary__).encode('utf-8'))
        print("After encodeDic result: ")
        print(jsonBase64__)
    except Exception as err:
        return 'encode error! - %s:%s' % (type(err).__name__, err)

    return jsonBase64__


def get_info_fromdb(syn_pid):
    sqlStr = f"SELECT pro_name, file_name, ob_col FROM SynService.T_ProjectColumnType WHERE project_id = '{syn_pid}'"
    try:
        check_conn = ConnectSQL()
        resultSampleData = check_conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            pro_name = resultSampleData['fetchall'][0].get('pro_name')
            file_name =resultSampleData['fetchall'][0].get('file_name')
            ob_col =resultSampleData['fetchall'][0].get('ob_col')
            return pro_name, file_name, ob_col
        else:
            print('fetch DataToMysql fail')
            check_conn.close()
            return None, None, None
    except Exception as e:
            print('errTable: get select cols from table fail. {0}'.format(str(e)))
            return None, None, None

def get_select_colNames(syn_pid):
    sqlStr = f"SELECT select_colNames FROM SynService.T_ProjectSample5Data WHERE project_id = '{syn_pid}'"
    try:
        check_conn = ConnectSQL()
        resultSampleData = check_conn.doSqlCommand(sqlStr)
        if resultSampleData['result'] == 1:
            select_colNames = resultSampleData['fetchall'][0].get('select_colNames')
            return select_colNames
        else:
            print('fetch DataToMysql fail')
            check_conn.close()
            return None
    except Exception as e:
            print('errTable: get select cols from table fail. {0}'.format(str(e)))
            return None
    
def syn_base64(syn_pid):
    curl_compose= dict()
    curl_compose['userID'] = str(1)
    curl_compose['projID'] = str(syn_pid)
    pro_name, file_name, ob_col  =  get_info_fromdb(syn_pid)
    curl_compose['projName'] = pro_name
    curl_compose['fileName'] = file_name
    curl_compose['colNames'] = ob_col.split(',')
    curl_compose['select_colNames'] =  get_select_colNames(syn_pid).split(',')
    curl_compose['keyName']=['']

    enc = encodeDic(curl_compose)
    if isinstance(enc, bytes):
        enc = enc.decode('utf-8')  # 將 bytes 轉換為 UTF-8 編碼的字串
    return enc
    




##
# test_dict = {'userID': '1',
#  'projID': '149', #sys_pid
#  'projName': 'gen_0827_syn', #T_ProjectColumnType pro_name
#  'fileName': 'gen_0827_syn_single.csv', #T_ProjectColumnType file_name
#  'colNames': ['race_moi_personal_info_sys_gen_0628',
#               'sex_moi_personal_info_sys_gen_0628',
#               'marital_status_mof_personal_financial_sys_gen_0628',
#               'income_mof_personal_financial_sys_gen_0628'], #T_ProjectColumnType ob_col
#  'select_colNames': ['age_moi_personal_info_sys_gen_0628',
#                      'fnlwgt_moi_personal_info_sys_gen_0628',
#                      'race_moi_personal_info_sys_gen_0628',
#                      'sex_moi_personal_info_sys_gen_0628',
#                      'marital_status_mof_personal_financial_sys_gen_0628',
#                      'hours_per_week_mof_personal_financial_sys_gen_0628'
#                      ,'income_mof_personal_financial_sys_gen_0628'], #T_ProjectSample5Data select_colNames
#  'keyName': ['']}
##