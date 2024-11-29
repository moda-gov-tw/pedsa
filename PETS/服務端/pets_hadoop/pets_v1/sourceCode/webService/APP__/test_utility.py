
import base64
import unittest
import requests
import json



#config = 'config/development.ini'
#webservice = getConfig(config=config).getLoginWebservice()
#IP = 'http://{}:{}/'.format(webservice['ip'], webservice['port'])
#print("IP:", IP)

IP = 'http://{}:{}/'.format('140.96.111.117', '5088')

class TestFlaskApiUsingRequests(unittest.TestCase):

    '''
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
        for key in response.json().keys():
            print('{}: {}'.format(key, response.json()[key]))
            if key == 'status':
                self.assertEqual(result[key], 1)
            self.assertEqual(result[key] is not None, True)
        self.assertEqual('application_' in result['spark_jobID'], True)



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

        jsonDic_ = {'projID': '1',
                    'projStep': 'export',
                    'projName': 'test_project',
                    'mainInfo': {'tbl_1': {'tblName': 'adult_id_add_data_69755040_18',
                                           'location': 'local'
                                           }
                                 }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            self.assertEqual(jsonDic[key] is not None, True)



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

        jsonDic_ = {'projID': '1',
                    'projStep': 'gen',
                    'projName': 'test_project',
                    'mainInfo': {
                        'tbl_1': {'tblName': 'adult_id_add_data_32294_18',
                                  'colInfo': {'col_1': {'colName': 'age',
                                                        'apiName': 'getGenNumLevel',
                                                        'level': '10'},

                                              'col_2': {'colName': 'workclass',
                                                        'apiName': 'getNogenerlize'},

                                              'col_3': {'colName': 'fnlwgt',
                                                        'apiName': 'getNogenerlize'},

                                              'col_4': {'colName': 'education',
                                                        'apiName': 'getNogenerlize'},

                                              'col_5': {'colName': 'education_num',
                                                        'apiName': 'getNogenerlize'},

                                              'col_6': {'colName': 'marital_status',
                                                        'apiName': 'getGenUdf',
                                                        'userRule': '/app/app/devp/udfRule/marital_status_rule.txt',
                                                        'level': '2'},

                                              'col_7': {'colName': 'occupation',
                                                        'apiName': 'getNogenerlize'},

                                              'col_8': {'colName': 'relationship',
                                                        'apiName': 'getNogenerlize'},

                                              'col_9': {'colName': 'race',
                                                        'apiName': 'getNogenerlize'},

                                              'col_10': {'colName': 'sex',
                                                         'apiName': 'getNogenerlize'},

                                              'col_11': {'colName': 'capital_gain',
                                                         'apiName': 'getGenNumLevel',
                                                         'level': '50'},

                                              'col_12': {'colName': 'capital_loss',
                                                         'apiName': 'getGenNumLevel',
                                                         'level': '100'},

                                              'col_13': {'colName': 'hours_per_week',
                                                         'apiName': 'getGenNumInterval',
                                                         'valueStart': ['1','11','21'],
                                                         'valueEnd': ['10','20','100'],
                                                         'toValue': ['5','15','25']},

                                              'col_14': {'colName': 'country',
                                                         'apiName': 'getNogenerlize'},

                                              'col_15': {'colName': 'class',
                                                         'apiName': 'getNogenerlize'},

                                              'col_16': {'colName': 'ch_address',
                                                         'apiName': 'getGenAddress',
                                                         'level': '5'},

                                              'col_17': {'colName': 'date',
                                                         'apiName': 'getGenDate',
                                                         'level': 'Mo'},

                                              'col_18': {'colName': 'id',
                                                         'apiName': 'getNogenerlize'} ,
                                              }
                                  }
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)


    '''


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

        jsonDic_ = {'projID': '1',
                    'projStep': 'import',
                    'projName': 'test_project',
                    'mainInfo': {
                        'tbl_1': {'tblName': 'adult_id_add_data_69755040_18'}
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)

    '''

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

        jsonDic_ = {'projID': '1',
                    'projStep': 'kchecking',
                    'projName': 'test_project',
                    'jobName': 'job01',
                    'kchecking': 1,
                    'mainInfo': {
                        'joinType': 'inner',
                        'kValue': '10',
                        'publicTableName': 'adult_17438760_18',
                        'dataInfo': [
                            {'QIcols': ['age','race','sex'],
                             'colNames': ['age',
                                          'workclass',
                                          'fnlwgt',
                                          'education',
                                          'education_num',
                                          'marital_status',
                                          'occupation',
                                          'relationship',
                                          'race',
                                          'sex',
                                          'capital_gain',
                                          'capital_loss',
                                          'hours_per_week',
                                          'country',
                                          'class',
                                          'ch_address',
                                          'date'
                                          'rowid'],
                             'tableName': 'adult_17438760_18',
                             'dbName': 'test_project',
                             'keyNames': ['rowid']
                             }
                        ]
                    }
                    }


        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)



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
                    'projName': 'test_project',
                    'jobName': 'job01',
                    'kchecking': 0,
                    'mainInfo':
                        {
                            'joinType': 'inner',
                            'dataInfo':
                                [
                                    {'QIcols': ['pre_age', 'pre_sex', 'pre_race'],
                                     'colNames': ['pre_id', 'pre_age', 'pre_sex', 'pre_race'],
                                     'tableName': 'adult_id_pre2w',
                                     'dbName': 'test_project',
                                     'keyNames': ['pre_id']
                                     },
                                    {'QIcols': ['post_sex', 'post_race', 'post_age'],
                                     'colNames': ['post_id', 'post_sex', 'post_race', 'post_age'],
                                     'tableName': 'adult_id_post2w',
                                     'dbName': 'test_project',
                                     'keyNames': ['post_id']
                                     }
                                ],
                            'publicTableName': 'adult_id_pre2w'
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

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
                    'projName': 'test_project',
                    'jobName': 'job01',
                    'kchecking': 1,
                    'mainInfo':
                        {
                            'joinType': 'full',
                            'dataInfo':
                                [
                                    {'QIcols': ['pre_age', 'pre_sex', 'pre_race'],
                                     'colNames': ['pre_id', 'pre_age', 'pre_sex', 'pre_race'],
                                     'tableName': 'adult_id_pre2w',
                                     'dbName': 'test_project',
                                     'keyNames': ['pre_id']
                                     },
                                    {'QIcols': ['post_sex', 'post_race', 'post_age'],
                                     'colNames': ['post_id', 'post_sex', 'post_race', 'post_age'],
                                     'tableName': 'adult_id_post2w',
                                     'dbName': 'test_project',
                                     'keyNames': ['post_id']
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

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)





    def test_getDistinctData_not_async(self):
        # not async
        url_ = IP + "getDistinctData_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'projID': '1',
                    'projStep': 'distinct',
                    'projName': 'test_project',
                    'jobName': 'job01',
                    'mainInfo':
                        {
                            'colNames': ['race', 'sex', 'age'],
                            'tableName': 'adult_17438760_18',
                            'dbName': 'test_project',
                            'reqFunc': 0
                        }
                    }


        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)




    def test_getDistinctData_async(self):
        """
        userRule: Divorced:Divorced;Never-married:Never-married;Separated:Separated;Widowed:Widowed;Married-civ-spouse:Married-civ-spouse;Married-AF-spouse:Married-AF-spouse;Married-spouse-absent:Married-spouse-absent
        status: 1errMsg:
        projStep: distinct
        sparkAppID: application_1542276527282_0276
        status: 1
        tblName: adult_pre2w
        celeryID: 779fe2f3-cc93-4822-806c-f982bd9e3782
        jobID: job01
        dbName: test_project
        time_async: 30.4788470268
        outTblName: ['test_project_job01_dis_adult_pre2w_pre_race', 'test_project_job01_dis_adult_pre2w_pre_sex']

        :return:
        """
        # async
        url_ = IP + "getDistinctData_async"
        print('--------{}--------'.format(url_))

        jsonDic_ = {'projID': '1',
                    'projStep': 'distinct',
                    'projName': 'taipei_bus',
                    'jobName': 'job01',
                    'mainInfo':
                        {
                            'colNames': ['x','y'],
                            'tableName': 'sup_taipei_bus',
                            'dbName': 'taipei_bus',
                            'reqFunc': 1
                        }
                    }

        data = {"jsonBase64": base64.b64encode(json.dumps(jsonDic_).encode()).decode("utf-8")}
        response = requests.post(url_, json=data)
        result = json.loads(response.text)
        jsonDic = json.loads(base64.b64decode(result['jsonBase64']).decode("utf-8"))

        for key in jsonDic.keys():
            print('{}: {}'.format(key, jsonDic[key]))
            if key == 'status':
                self.assertEqual(jsonDic[key], '1')
            if key != 'errMsg':
                self.assertEqual(jsonDic[key] != '', True)


    '''


if __name__ == "__main__":
    unittest.main()