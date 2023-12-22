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

#dc = {"projName": "app/devp/syn_gen/projAdult/","fileName":"app/devp/syn_gen/data/adult.csv","colNames":["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class"],"keyName":["workclass"]}
#dc = {"projName": "app/devp/project/project_adult/","fileName":"app/devp/project/raw data/adult.csv","colNames":["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class"],"keyName":["workclass"]}
#dc = {"projName": "project_adult_3","fileName":"adult.csv","colNames":["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class"],"keyName":["workclass"]}
#dc = {'projID': 9527, 'projName': 'crime'}

#dc = {'projID': '9527', 'projName': 'crime','fileName':'crime_revised.csv'}

#dc = {'projID': '9517', 'projName': 'crime', 'fileName': 'crime_revised.csv', 'colNames': ['TYPE','HUNDRED_BLOCK','NEIGHBOURHOOD','AAAA'], 'keyName': ['AAAA']}

#dc = {'projID': '9517', 'projName': 'crime', 'fileName': 'crime_revised.csv', 'colNames': ['TYPE','HUNDRED_BLOCK','NEIGHBOURHOOD','AAAA'], 'select_colNames': ['TYPE','HUNDRED_BLOCK','NEIGHBOURHOOD','AAAA','X','Y','YEAR'],'keyName': ['AAAA']}


#for adult:
#dc = {'userID':'jojo','projID': '9517', 'projName': 'adult','PID':'51'}
#dc = {'userID':'JOJO','projID': '9517', 'projName': 'adult','fileName':'adult.csv'}
#dc = {'userID':'JOJO','projID': '9517', 'projName': 'adult', 'fileName': 'adult.csv', 'colNames': ["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class"], 'select_colNames': ["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class","age","fnlwgt","hours_per_week"],'keyName': ['native_country']}

#dc = {'userID':'USER','projID': '2020', 'projName': 'adulttest', 'fileName': 'adulttest.csv'}
#dc = {'userID':'USER','projID': '2020', 'projName': 'adulttest', 'fileName': 'adulttest.csv', 'colNames': ["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class"], 'select_colNames': ["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class","age","fnlwgt","hours_per_week"],'keyName': ['native_country']}

#dc = {'userID':'JOJO','projID': '9517', 'projName': 'adult', 'fileName': 'adult.csv', 'colNames': ["workclass","education","education_num","marital_status","occupation","relationship","race","sex","native_country","class"], 'select_colNames': ['fnlwgt', 'hours_per_week', 'age'],'keyName': ['']}
#for crime:
#dc = {'userID':'JOJO','projID': '9527', 'projName': 'crime'}
#dc = {'userID':'JOJO','projID': '9527', 'projName': 'crime','fileName':'crime_revised.csv'}
#dc = {'userID':'JOJO','projID': '9517', 'projName': 'crime', 'fileName': 'crime_revised.csv', 'colNames': ['TYPE','HUNDRED_BLOCK','NEIGHBOURHOOD','AAAA'], 'select_colNames': ['TYPE','HUNDRED_BLOCK','NEIGHBOURHOOD','AAAA','X','Y','YEAR'],'keyName': ['AAAA']}

#dc =  {'projID': '123', 'userID': 'JOJO', 'projName': 'adult', 'dataName' : ['synthetic_transform_rmhit30.csv']}

dc = {'userID':'1','projID': '1234', 'projName': 'adulttest'}

print("json#### ",json.dumps(dc))
print("type#### ", type(json.dumps(dc)))
#print("type(b)# ", type(dc.encode('utf-8')))
#print('###############ENCODE###############')
enc = encodeDic(dc)

#print('###############DECODE###############')


getJsonParser(enc)


