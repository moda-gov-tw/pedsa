#!/usr/bin/python
# -*- coding: utf-8 -*-

from config.connect_sql import ConnectSQL


def main():


    # Connect mysql
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False

    # Insert to table
    '''
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    colsValue = {
        'project_id': '1',
        'pro_db': 'test_import_all',
        'pro_tb': 'adult_id_post2w',
        'pro_col_en': 'col_0,col_1,col_2,col_3,col_4,col_5,col_6,col_7,col_8,col_9,\
                       col_10,col_11,col_12,col_13,col_14,col_15',
        'pro_col_cht': 'post_id,post_age,post_workclass,post_fnlwgt,post_education,\
                   post_education_num,post_marital_status,post_occupation,\
                   post_relationship,post_race,post_sex,post_capital_gain,\
                   post_capital_loss,post_hours_per_week,post_country,post_class'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_Project'
    colsValue = {
        'project_name': 'demo1',
        'project_path': '/home/deid/citc/sourceCode/hadoop/data/input/',
        'export_path': '/home/deid/citc/sourceCode/hadoop/data/output/',
        'projectowner_id': '124'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_originTable'
    colsValue = {
        'tableName': 'unittest_project1_file1',
        'tableCount': '155',
        'sample': 'aaa^bbb%',
        'col_en': 'c_1,c_2',
        'col_cht': 'col1,col2'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_Member'
    colsValue = {
        'useraccount': 'unittest',
        'username': '155',
        'sample': 'aaa^bbb%',
        'col_en': 'c_1,c_2',
        'col_cht': 'col1,col2'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    colsValue = {
        'project_id': 11,
        'pro_db': 11,
        'pro_tb': 11,
        'pro_col_en': 11,
        'pro_col_cht': 11,
        'pro_path': 11,
        'tableCount': 1,
        'tableDisCount': 'NULL',
        'minKvalue': 'NULL',
        'supRate': 'NULL',
    }
    result = conn.insertValue(db, tbl, colsValue, True)    
    '''




    # Delete value
    '''
    db = 'DeIdService'
    tbl = 'T_Dept'
    colsValue = {
        'dept_name': 'NCHC'
    }
    result = conn.deleteValue(db, tbl, colsValue)
    '''

    '''   
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    sqlCommand = """
    DELETE FROM {}.{}
    WHERE ps_id<159
    AND pro_db='myfone'
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    '''    

    '''
    db = 'DeIdService'
    tbl = 'T_originTable'
    sqlCommand = """
    DELETE FROM {}.{}
    WHERE tableCount>1
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)

    '''




    # alter
    '''
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    sqlCommand = """
    ALTER TABLE {}.{}
    MODIFY COLUMN pro_col_en LONGTEXT;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    sqlCommand = """
    ALTER TABLE {}.{}
    ADD COLUMN  gen_qi_settingvalue VARCHAR(255);
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)    
    '''



    '''
    db = 'DeIdService'
    tbl = 'T_Project_SparkStatus_Management'
    sqlCommand = """
    ALTER TABLE {}.{}
    ADD COLUMN stepstatus int(1);
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_originTable'
    sqlCommand = """
    ALTER TABLE {}.{}
    ADD COLUMN tbl_id int(11) NOT NULL auto_increment PRIMARY KEY;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_originTable'
    sqlCommand = """
    ALTER TABLE {}.{}
    ADD COLUMN user varchar(255)
    ADD COLUMN project varchar(255);
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    '''



    # select
    '''
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    sqlCommand = """
    SELECT pro_col_en,pro_col_cht
    FROM {}.{}
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)

    colCompare = dict()

    pro_col_en = [col.strip(' ') for col in result['msg'][0]['pro_col_en'].split(',')]
    pro_col_cht = [col.strip(' ') for col in result['msg'][0]['pro_col_cht'].split(',')]

    for i in range(len(pro_col_en)):
        colCompare[pro_col_en[i]] = pro_col_cht[i]

    from mylib.base64convert import getJsonParser, encodeDic
    tmp = encodeDic(colCompare)
    #tmp = base64.b64encode(json.dumps(colCompare).encode()).decode("utf-8")

    tmp2 = getJsonParser(tmp)
    #tmp2 = base64.b64decode(tmp).decode("utf-8")
    print(99999999999999999999)
    '''


    '''

    db = 'key_db'
    tbl = 'T_Dept'
    sqlCommand = """
    select * from {}.{};
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    print(result['msg'][0]['dept_name'])
    '''

    '''
    db = 'DeIdService'
    tbl = 'T_Member'
    sqlCommand = """
    select * from {}.{}
    WHERE username='bruce1';
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    print(result)
    print(type(result['msg']))
    print(type(result['result']))
    print(len(result['msg']) == 0)
    '''


    #Create
    '''
    db = 'DeIdService'
    sqlCommand = """
    CREATE TABLE {0}.T_originTable (
        tableName VARCHAR(255),
        tableCount INT(11),
        sample LONGTEXT,
        col_en LONGTEXT,
        col_cht LONGTEXT,
        createtime DATETIME,
        updatetime DATETIME,
        tbl_id int(11) NOT NULL auto_increment PRIMARY KEY
    );
    """.format(db)
    result = conn.doSqlCommand(sqlCommand)
    print(result)
    '''

    #Update
    '''
    db = 'DeIdService'
    tbl = 'T_originTable'
    conditions = {
        'tableName': 'unittest_project1_file1',
        'tableCount': '155',
        'sample': 'aaa^bbb%',
        'col_en': 'c_1,c_2',
        'col_cht': 'col1,col2'
    }

    setColsValue = {
        'tableName': 'unittest_project1_file1',
        'tableCount': '155',
        'sample': 'aaa^bbb%',
        'col_en': 'c_1,c_2',
        'col_cht': 'col1,col2',
        'createtime': 'NOW()'
    }
    result = conn.updateValue(db, tbl, conditions, setColsValue)
    '''

    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    conditions = {
        'pro_tb': 'mac_adult_id',
    }

    setColsValue = {
        'after_col_en': 'c_3537_0,c_3537_1,c_3537_2,c_3537_3,c_3537_4,c_3537_5,c_3537_6,c_3537_7,c_3537_8,c_3537_9,c_3537_10,c_3537_11,c_3537_12,c_3537_13,c_3537_14,c_3537_15',
        'after_col_cht': 'id,age,workclass,fnlwgt,education,education_num,marital_status,occupation,relationship,race,sex,capital_gain,capital_loss,hours_per_week,country,class',
        'qi_col': 'fnlwgt-2,race-1,sex-1,hours_per_week-2',
        'after_col_value': '4,3,3,2,4,4,4,4,4,1,1,4,4,2,4,4',
        'tablekeycol': 'age,workclass',
        'gen_qi_settingvalue': 'udfMacUID_adult_id*4,0,0,4*?,0,0,?'
    }
    result = conn.updateValue(db, tbl, conditions, setColsValue)





    if result['result'] == 1:
        print(result['msg'])
    else:
        print('mysql fail:' + result['msg'])
        return False

if __name__ == "__main__":
    main()

