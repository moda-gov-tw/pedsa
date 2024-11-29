import base64
import unittest
import requests
import json



#config = 'config/development.ini'
#webservice = getConfig(config=config).getLoginWebservice()
#IP = 'http://{}:{}/'.format(webservice['ip'], webservice['port'])
#print("IP:", IP)
IP = 'http://{}:{}/'.format('172.28.1.3', '5088')


def logBase64(url_, dict_, result):

    with open('/app/app/devp/log/logBase64.txt', 'a') as file:
        file.write(url_)
        file.write('\n')
        file.write('test api:')
        file.write('\n')
        file.write(json.dumps(dict_))
        file.write('\n')
        file.write('return:')
        file.write('\n')
        file.write(json.dumps(result))
        file.write('\n')
        file.write('\n')
        file.write('\n')



class TestFlaskApiUsingRequests(unittest.TestCase):

    
    '''  
    def test_hello_world__(self):
        url_ = IP + "hello_world_"
        print('--------{}--------'.format(url_))

        response = requests.get(url_)
        msg = 'This page has been seen'
        self.assertEqual(msg in response.text, True)

    
    def test_uidEnc_async(self):
        """
        Except return:

        time_async: 29.0947639942
        spark_jobID: application_1542276527282_0284
        kTable: udfEncTable_test
        celeyId: e382b158-e2e4-422e-a401-57d8ae97d997
        """

        url_ = IP + "uidEnc_async"
        print('--------{}--------'.format(url_))

        data = {
                "dbName": "test_project",
                "tableName": "adult_id",
                "colNames": ["id", "age"]
                }
        response = requests.post(url_, json=data)
        result = json.loads(response.text)

        logBase64(url_, data, result)

        for key in response.json().keys():
            print('{}: {}'.format(key, response.json()[key]))
            if key == 'status':
                self.assertEqual(result[key], 1)
            self.assertEqual(result[key] is not None, True)
        self.assertEqual('application_' in result['spark_jobID'], True)

    '''

    def test_getServerFolder(self):
        """
        Except return:

        /root/data/input/test_project/adult
        /root/data/input/test_project/adult_id
        /root/data/input/test_project/adult_post2w
        /root/data/input/test_project/adult_pre2w
        /root/data/input/youbike/youbike10512_sample
        """
        url_ = IP + "getServerFolder"
        print('--------{}--------'.format(url_))
        """
        jsonDic_ = {'projID': '1',
                   'projStep': 'getServerFolder',
                   'projName': '2QDataMarketDeid'}
        """
        """
        jsonDic_ = {'projID': '7',
                   'projStep': 'getServerFolder',
                   'projName': '2QDataMarketDeid'}
        """

        jsonDic_ = {'projName': '2QDataMarketDeId',
'projStep': 'getServerFolder',
'projID': '7'}


        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        #data = {"jsonBase64": "eyJwcm9qTmFtZSI6IjJRRGF0YU1hcmtldERlSWQiLCJwcm9qU3RlcCI6ImdldFNlcnZlckZvbGRlciIsInByb2pJRCI6IjcifQ=="}

        response = requests.post(url_, json=data)

        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)
        print(jsonDic)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], 1)
            self.assertEqual(jsonDic[key] is not None, True)



    def test_getSparkJobStatusB64(self):
        """
        Except return:

        Application-Id: application_1542276527282_0051
        Finish-Time: 1545010828953
        Start-Time: 1545010807032
        State: FINISHED
        Final-State: SUCCEEDED
        Progress: 100%
        """
        url_ = IP + "getSparkJobStatusB64"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'applicationID': 'application_1545643130154_0004'}

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], 1)
            self.assertEqual(jsonDic[key] is not None, True)



    def test_killSparkJobB64(self):
        """
        Except return:

        result: Application application_1542276527282_0051 has already finished
        """
        url_ = IP + "killSparkJobB64"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'applicationID': 'application_1542276527282_0313'}

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], 1)
            self.assertEqual(jsonDic[key] is not None, True)


    def test_park_task(self):
        url_ = IP + "park_task" + "/220228b2-276c-49f1-b86d-d3e601a189b2"
        print('--------{}--------'.format(url_))
        response = requests.get(url_)
        result = json.loads(response.text)

        self.assertEqual(result['state'] is not None, True)
      

    def test_ExportFile(self):
        """
        Except return:

        errMsg:
        projStep: export
        status: 1
        tblName: adult,adult_id
        celeryID: 3c0c3714-65f3-4f73-acd8-8d82f4eef9a0
        dbName: test_project
        time_async: 0.0186121463776
        """
        url_ = IP + "ExportFile"
        print('--------{}--------'.format(url_))

        jsonDic_ = {"projID": "1",
                    "projStep": "export",
                    "projName": "2QDataMarketDeId",
                    "mainInfo": {"tbl_1": {"pro_tb": "mac_adult_id",
                                           "finaltblName": "g_mac_adult_id_k_job01",
                                           "location": "local"
                                           }
                                 }
                    }
        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1', jsonDic['errMsg'])
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True, jsonDic['errMsg'])



    def test_checkTemplete(self):
        """
        Except return:

        userRule: Divorced:Divorced;Never-married:Never-married;Separated:Separated;Widowed:Widowed;Married-civ-spouse:Married-civ-spouse;Married-AF-spouse:Married-AF-spouse;Married-spouse-absent:Married-spouse-absent
        status: 1
        """

        url_ = IP + "checkTemplete"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'mainInfo': {'userRule': '/app/app/devp/udfRule/2qdatamarketdeid/mac_adult_id/marital_status_rule.txt'}}

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(str(jsonDic[key]), '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True, jsonDic['errMsg'])

 

    def test_Generalization_async(self):
        """
        Except return:

        sparkAppID: application_1542276527282_0286
        tblName: df_table__
        outTblName: default_gen_df_table__
        dbName: test_project
        time_async: 27.7051579952
        status: 1
        errMsg:
        celeryID: 5f97fbc7-7dff-4590-907c-e817d138600c
        projStep: gen
        """

        # in HIVE: default.df_table__  is adult data set
        # [c0,c1,...c14] = [age,workclass,fnlwgt,education,education_num,marital_status,occupation,
        # relationship,race,sex,capital_gain,capital_loss,hours_per_week,country,class]

        url_ = IP + "Generalization_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {"projID": "1",
                    "projStep": "gen",
                    "projName": "2QDataMarketDeId",
                    "mainInfo": {
                        "tbl_1": {"tblName": "mac_adult_id",
                                  "col_en": "c_2771_0,c_2771_1,c_2771_2,c_2771_3,c_2771_4,c_2771_5,c_2771_6,c_2771_7,c_2771_8,c_2771_9,c_2771_10,c_2771_11,c_2771_12,c_2771_13,c_2771_14,c_2771_15",
                                  "colInfo": {
                                              "col_1": {"colName": "c_2771_1",
                                                        "apiName": "getGenNumLevel",
                                                        "userRule": "10"},

                                              "col_6": {"colName": "c_2771_6",
                                                        "apiName": "getGenUdf",
                                                        "userRule": "/app/app/devp/udfRule/2qdatamarketdeid/mac_adult_id/marital_status_rule.txt"},

                                              "col_11": {"colName": "c_2771_11",
                                                         "apiName": "getGenNumLevel",
                                                         "userRule": "50"},

                                              "col_12": {"colName": "c_2771_12",
                                                         "apiName": "getGenNumLevel",
                                                         "userRule": "100"},

                                              "col_13": {"colName": "c_2771_13",
                                                         "apiName": "getGenNumInterval",
                                                         "userRule": "1_10_5^11_20_15^21_100_25"}
                                              }
                                  }
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)


    def test_ImportFile(self):
        """
        Except return:

        dbName: test_project
        sparkAppID: application_1542276527282_0285
        projStep: import
        celeryID: 368a4acb-fe94-4ed1-8bf9-0cdd1afffde3
        errMsg:
        tblNames: adult_pre2w;adult_post2w;adult
        time_async: 27.9285020828
        status: 1
        """
        url_ = IP + "ImportFile"
        print('--------{}--------'.format(url_))

        """ old version
        jsonDic_ = {'projID': '1',
                    'projStep': 'import',
                    'projName': 'test_project',
                    'mainInfo': {
                        'tbl_1': {'tblName': 'adult'},
                        'tbl_2': {'tblName': 'adult_id_pre2w'},
                        'tbl_3': {'tblName': 'adult_id_post2w'},
                        'tbl_4': {'tblName': 'adult_id'},
                        }
                    }
        """

        jsonDic_ = {"projID": "1",
                    "projStep": "import",
                    "projName": "2QDataMarketDeId"
                    }
        """
        jsonDic_ = {'projID': '7',
                    'projStep': 'import',
                    'projName': 'myfone'
                    }
        """

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)


    def test_kchecking_async(self):
        """
        Except return:

        status: 1
        celeryID: d79953a3-b1ef-4eac-a843-5ee263a608c6
        sparkAppID: application_1542276527282_0274
        tblName:  adult_id
        projStep: kchecking
        errMsg:
        dbName:  test_project
        finaltblName: test_project_job01_kchecking_adult_id_final
        time_async: 32.4258031845
        state: PROGRESS
        """
        url_ = IP + "kchecking_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {"projID": "1",
                    "projStep": "kchecking",
                    "projName": "2QDataMarketDeId",
                    "jobName": "job01",
                    "kchecking": 1,
                    "mainInfo": {
                        "joinType": "inner",
                        "kValue": "50",
                        "publicTableName": "2QDataMarketDeid_gen_udfMacUID_adult_id",
                        "dataInfo": [
                            {"QIcols": ["c_2737_10", "c_2737_1", "c_2737_9", "c_2737_6"],
                             "colNames": ["c_2737_1",
                                          "c_2737_2",
                                          "c_2737_3",
                                          "c_2737_4",
                                          "c_2737_5",
                                          "c_2737_6",
                                          "c_2737_7",
                                          "c_2737_8",
                                          "c_2737_9",
                                          "c_2737_10",
                                          "c_2737_11",
                                          "c_2737_12",
                                          "c_2737_13",
                                          "c_2737_14",
                                          "c_2737_15",
                                          "c_2737_0"],
                             "tableName": "2QDataMarketDeid_gen_udfMacUID_adult_id",
                             "dbName": "2QDataMarketDeId",
                             "keyNames": ["c_2737_0"]
                             }
                        ]
                    }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)
 
    '''
    def test_getJoinData_async_k0(self):
        """
        Except return:

        tblName: ['adult_pre2w', 'adult_post2w']
        dbName: ['test_project', 'test_project']
        jobID: job01
        time_async: 29.8481900692
        celeryID: 54b3fd3c-ef22-4d3a-b94f-d0fd2c62331c
        outTblName: test_project_job01_ijT_adult_pre2w_adult_post2w
        projStep: join
        status: 1
        sparkAppID: application_1542276527282_0287
        errMsg:
        """

        # inner, kchecking=0
        url_ = IP + "getJoinData_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'projID': '1',
                    'projStep': 'join',
                    'projName': 'test_import_all',
                    'jobName': 'job01',
                    'kchecking': 0,
                    'mainInfo':
                        {
                            'joinType': 'inner',
                            'dataInfo':
                                [
                                    {'QIcols': ['adult_id_pre2w_col_1', 'adult_id_pre2w_col_10', 'adult_id_pre2w_col_9'],
                                     'colNames': ['adult_id_pre2w_col_0', 'adult_id_pre2w_col_1', 'adult_id_pre2w_col_10', 'adult_id_pre2w_col_9'],
                                     'tableName': 'adult_id_pre2w',
                                     'dbName': 'test_import_all',
                                     'keyNames': ['adult_id_pre2w_col_0']
                                     },
                                    {'QIcols': ['adult_id_post2w_col_10', 'adult_id_post2w_col_9', 'adult_id_post2w_col_1'],
                                     'colNames': ['adult_id_post2w_col_0', 'adult_id_post2w_col_10', 'adult_id_post2w_col_9', 'adult_id_post2w_col_1'],
                                     'tableName': 'adult_id_post2w',
                                     'dbName': 'test_import_all',
                                     'keyNames': ['adult_id_post2w_col_0']
                                     }
                                ],
                            'publicTableName': 'adult_id_pre2w'
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)
    

    def test_getJoinData_async_k1(self):
        """
        Except return

        tblName: ['adult_pre2w', 'adult_post2w']
        status: 1
        jobID: job01
        errMsg:
        dbName: ['test_project', 'test_project']
        sparkAppID: application_1542276527282_0288
        outTblName: test_project_job01_fjT_adult_pre2w_adult_post2w
        time_async: 29.5258789062
        projStep: join
        celeryID: 5f1b11d2-5eb9-47b3-b937-07cfc82afc95
        """
        # full, kchecking=1
        url_ = IP + "getJoinData_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'projID': '1',
                    'projStep': 'join',
                    'projName': 'test_import_all',
                    'jobName': 'job01',
                    'kchecking': 1,
                    'mainInfo':
                        {
                            'joinType': 'full',
                            'dataInfo':
                                [
                                    {'QIcols': ['adult_id_pre2w_col_1', 'adult_id_pre2w_col_10', 'adult_id_pre2w_col_9'],
                                     'colNames': ['adult_id_pre2w_col_0', 'adult_id_pre2w_col_1', 'adult_id_pre2w_col_10', 'adult_id_pre2w_col_9'],
                                     'tableName': 'adult_id_pre2w',
                                     'dbName': 'test_import_all',
                                     'keyNames': ['adult_id_pre2w_col_0']
                                     },
                                    {'QIcols': ['adult_id_post2w_col_10', 'adult_id_post2w_col_9', 'adult_id_post2w_col_1'],
                                     'colNames': ['adult_id_post2w_col_0', 'adult_id_post2w_col_10', 'adult_id_post2w_col_9', 'adult_id_post2w_col_1'],
                                     'tableName': 'adult_id_post2w',
                                     'dbName': 'test_import_all',
                                     'keyNames': ['adult_id_post2w_col_0']
                                     }
                                ],
                            'kValue': '200',
                            'publicTableName': 'adult_id_pre2w'
                        }
                    }


        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)    
    '''


    def test_getDistinctData_not_async(self):
        # not async
        url_ = IP + "getDistinctData_async"
        print('--------{}--------'.format(url_))

        """
        jsonDic_ = {'projID': '1',
                    'projStep': 'distinct',
                    'projName': 'myfone',
                    'jobName': 'job01',
                    'mainInfo':
                        {
                            'colNames': ['c_1857_4', 'c_1857_5', 'c_1857_6'],
                            'tableName': 'udfmacuid_myphone_3',
                            'dbName': 'myfone',
                            'reqFunc': 0
                        }
                    }
        """
        jsonDic_ = {'projID': '1',
                    'projStep': 'distinct',
                    'projName': '2qdatamarketdeid',
                    'jobName': 'job02',
                    'mainInfo':
                        {
                            'origColNames':['race','country'],
                            'colNames':['c_6037_9','c_6037_14'],
                            'tableName':'udfmacuid_adult_id',
                            'dbName':'2qdatamarketdeid',
                            'reqFunc':0
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)
   
    def test_getDistinctData_async(self):
        """
        Except return:
      
        projStep: distinct
        sparkAppID: application_1542276527282_0276
        status: 1
        tblName: adult_pre2w
        celeryID: 779fe2f3-cc93-4822-806c-f982bd9e3782
        jobID: job01
        dbName: test_project
        time_async: 30.4788470268
        outTblName: ['test_project_job01_dis_adult_pre2w_pre_race', 'test_project_job01_dis_adult_pre2w_pre_sex']
        """
        # asyn
        url_ = IP + "getDistinctData_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'projID': '1',
                    'projStep': 'distinct',
                    'projName': 'test_import_all',
                    'jobName': 'job02',
                    'mainInfo':
                        {
                            'origColNames':['race','country'],
                            'colNames':['c_0827_8','c_0827_13'],
                            'tableName':'adult',
                            'dbName':'test_import_all',
                            'reqFunc':0
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        logBase64(url_, data, result)

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)

if __name__ == "__main__":
    unittest.main()                                                                                                                   
