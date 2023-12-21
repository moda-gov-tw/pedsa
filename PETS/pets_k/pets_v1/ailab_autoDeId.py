import requests
import datetime
import time

prodesc='test in api'
flask_ip='140.96.178.108'
flask_port='5997'

for i in range(1,6):
    try:
        AutoDeIdAsync_para = {
              "columns_mac": "id",
              "configName": "test_0829.json",
              "dataHash": "yes",
              "hashTableName": "test_0829",
              "hashkey": "AAAAAABC0DCB39FE182FAF7CE960A2B0BA63AFEEDC76D8A92AED52938AA06ABA",
              "p_dsname": "tt_0901_autoDeId_%s" %(i),
              "pname": "tt_0901_autoDeId_%s" %(i),
              "prodesc": "describe: DeId-project with hash on adult dataset.",
              "sep": ",",
              "powner": "1",
              "projName": "tt_0901_autoDeId_%s" %(i),
              "onlyHash": "Y"
            }
        print('AutoDeIdAsync_para: ', AutoDeIdAsync_para)           
        response_AutoDeId = requests.post("https://"+flask_ip+":"+flask_port+"/DeIdAsyncAES", json=AutoDeIdAsync_para,timeout=None, verify=False)
        response_dic = response_AutoDeId.json()
        print("response_AutoDeId JSON: ",response_dic)
        time.sleep(5)
    except Exception as e:
        print('response_AutoDeId Error: ',e)
