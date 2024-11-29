#!/usr/bin/python
# -*- coding: utf-8 -*-
from config.connect_sql import ConnectSQL
from configparser import ConfigParser
import os.path

class getConfig():
	def __init__(self):
		self.config = ConfigParser()
		self.config.read('/app/app/devp/config/development.ini')
	def getLoginMysql(self):
		password = self.config.get('webservice', 'password')
		return password

def createUser_deidadmin(conn):
    # Create Database;
    sqlCommand = """
    CREATE USER 'deidadmin'@'%' IDENTIFIED BY 'citcw200';
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def update_deidadmin(conn):
    # Create Database;
    sqlCommand = """
    UPDATE mysql.user SET select_priv='Y',
    insert_priv='Y',
    update_priv='Y',
    delete_priv='Y',
    create_priv='Y',
    drop_priv='Y',
    reload_priv='Y',
    grant_priv='Y',
    alter_priv='Y' WHERE user='deidadmin';
    """
    result = conn.doSqlCommand(sqlCommand)
    return result


def createDB_DeIdService(conn):
    # Create Database;
    db = 'DeIdService'
    sqlCommand = """
    CREATE DATABASE {0} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
    """.format(db)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createDB_key_db(conn):
    # Create Database;
    db = 'key_db'
    sqlCommand = """
    CREATE DATABASE {0} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
    """.format(db)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Dept(conn):
    db = 'DeIdService'
    tbl = 'T_Dept'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Member(conn):
    db = 'DeIdService'
    tbl = 'T_Member'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        useraccount VARCHAR(100) NOT NULL,
        username VARCHAR(100),
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        dept_id INT(11) NOT NULL,
        isAdmin tinyint(1) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Pro_DistinctTB(conn):
    db = 'DeIdService'
    tbl = 'T_Pro_DistinctTB'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        pdis_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        pro_db VARCHAR(100) NOT NULL,
        pro_tb VARCHAR(100) NOT NULL,
        pro_col VARCHAR(100) NOT NULL,
        pro_discol_count LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Project(conn):
    db = 'DeIdService'
    tbl = 'T_Project'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        project_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_name VARCHAR(255) NOT NULL,
        project_cht VARCHAR(255),
        project_desc LONGTEXT,
        project_path LONGTEXT NULL,
        export_path LONGTEXT NULL, 
        projectowner_id INT(11) NOT NULL,
        risk_rdata VARCHAR(100),
        r1_data VARCHAR(100),
        r2_data VARCHAR(100),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_ProjectJobStatus(conn):
    db = 'DeIdService'
    tbl = 'T_ProjectJobStatus'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        pjs_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_jobstatus INT(11) NOT NULL,
        jobname VARCHAR(255) NOT NULL,
        job_tb VARCHAR(255),
        jobrule VARCHAR(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_ProjectSampleData(conn):
    db = 'DeIdService'
    tbl = 'T_ProjectSampleData'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        dbname VARCHAR(255) NOT NULL,
        tbname VARCHAR(255) NOT NULL,
        data LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_ProjectStatus(conn):
    db = 'DeIdService'
    tbl = 'T_ProjectStatus'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_status INT(11) NOT NULL,
        statusname VARCHAR(255) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Project_SampleTable(conn):
    db = 'DeIdService'
    tbl = 'T_Project_SampleTable'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        pro_db VARCHAR(100) NOT NULL,
        pro_tb VARCHAR(100) NOT NULL,
        pro_col_en LONGTEXT,
        pro_col_cht LONGTEXT,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        pro_path VARCHAR(255),   
        tableCount INT(11),
        tableDisCount INT(11),
        minKvalue INT(11),
        supRate VARCHAR(100), 
        supCount INT(11),
        finaltblName VARCHAR(255),
        after_col_en LONGTEXT,
        after_col_cht LONGTEXT,
        qi_col LONGTEXT,
        tablekeycol LONGTEXT,
        after_col_value VARCHAR(255),
        gen_qi_settingvalue LONGTEXT,
        warning_col LONGTEXT
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Project_SparkStatus_Management(conn):
    db = 'DeIdService'
    tbl = 'T_Project_SparkStatus_Management'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        pspark_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        app_id VARCHAR(255) NOT NULL,
        celery_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        step VARCHAR(100),
        stepstatus int(1)
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Project_SysStep_Config(conn):
    db = 'DeIdService'
    tbl = 'T_Project_SysStep_Config'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        psys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        pro_status INT(11) NOT NULL,
        pro_status_config TEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        project_id int(11) NOT NULL
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_SystemSetting(conn):
    db = 'DeIdService'
    tbl = 'T_SystemSetting'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        sys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        kdata VARCHAR(100),
        ldata VARCHAR(100),
        rdata VARCHAR(100),
        dfprojowner INT(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME NOT NULL
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_originTable(conn):
    db = 'DeIdService'
    tbl = 'T_originTable'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        tbl_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        tableName VARCHAR(255),
        tableCount INT(11),
        sample LONGTEXT,
        col_en LONGTEXT,
        col_cht LONGTEXT,
        project VARCHAR(255),
        member VARCHAR(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Project_NumStatValue(conn):
    db = 'DeIdService'
    tbl = 'T_Project_NumStatValue'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        proj_id INT(11) NOT NULL,
        proj_db VARCHAR(100) NOT NULL,
        proj_table VARCHAR(100) NOT NULL,
        statValue LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_Project_FinalTable(conn):
    db = 'DeIdService'
    tbl = 'T_Project_FinalTable'
    sqlCommand = """
    CREATE TABLE {0}.{1} (
        id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user VARCHAR(100) NOT NULL,
        proj_id INT(11) NOT NULL,
        process VARCHAR(100) NOT NULL,
        jobName VARCHAR(255) NOT NULL,
        rawTblName VARCHAR(100) NOT NULL,
        genTblName VARCHAR(100) NOT NULL,
        k_checkTblName VARCHAR(100),
        joinTblName VARCHAR(100),
        unionTblName VARCHAR(100),
        joinUnionSupRate VARCHAR(100),
        joinUnionSupCount INT(11),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createUser_keyadmin(conn):
    # Create Database;
    sqlCommand = """
    CREATE USER 'keyadmin'@'%' IDENTIFIED BY 'citcw200';
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def setPrivileges_deidadmin(conn):
    # Create Database;
    sqlCommand = """
    GRANT ALL PRIVILEGES ON DeIdService.* to 'deidadmin'@'%';
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def setPrivileges_keyadmin(conn):
    # Create Database;
    sqlCommand = """
    GRANT ALL PRIVILEGES ON key_db.* to 'keyadmin'@'%';
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def update_keyadmin(conn):
    # Create Database;
    sqlCommand = """
    UPDATE mysql.user SET select_priv='Y',
    insert_priv='Y',
    update_priv='Y',
    delete_priv='Y',
    create_priv='Y',
    drop_priv='Y',
    reload_priv='Y',
    grant_priv='Y',
    alter_priv='Y' WHERE user='keyadmin';
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def flushPrivileges(conn):
    # Create Database;
    sqlCommand = """
    FLUSH PRIVILEGES;
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def insert_T_Member(conn):
    db = 'DeIdService'
    tbl = 'T_Member'
    pwd = str(getConfig().getLoginMysql())
    colsValue = {
        'useraccount': 'deidadmin',
        'password': pwd,
        'dept_id': '1',
        'isAdmin': '1'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    return result

def insert_T_Project(conn):
    db = 'DeIdService'
    tbl = 'T_Project'
    colsValue = {
        'project_name': '2QDataMarketDeId',
        'project_cht': '2QDataMarketDeId',
        'project_path': '/home/deid/citc/sourceCode/hadoop/data/input/',
        'export_path': '/home/deid/citc/sourceCode/hadoop/data/output/',
        'projectowner_id': '1'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    return result

def insert_T_ProjectStatus(conn):
    db = 'DeIdService'
    tbl = 'T_ProjectStatus'
    colsValue = {
        'project_id': '1',
        'project_status': '0',
        'statusname': '資料專案開啟'
    }
    result = conn.insertValue(db, tbl, colsValue, True)
    return result

def logBase64(sqlStr):
    with open('/app/app/devp/log/createMysqlLog.txt', 'a') as file:
        file.write(sqlStr)
        file.write('\n')
        file.write('\n')


def main():
    '''

    :return:
    '''
    pwd = str(getConfig().getLoginMysql())
    # Connect mysql
    try:
        conn_ = ConnectSQL(user_input='root', pwd_input=pwd)
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False


    stepDict = {
        '0': createDB_DeIdService(conn_),
        '1': createTbl_T_Dept(conn_),
        '2': createTbl_T_Member(conn_),
        '3': createTbl_T_Pro_DistinctTB(conn_),
        '4': createTbl_T_Project(conn_),
        '5': createTbl_T_ProjectJobStatus(conn_),
        '6': createTbl_T_ProjectSampleData(conn_),
        '7': createTbl_T_ProjectStatus(conn_),
        '8': createTbl_T_Project_SampleTable(conn_),
        '9': createTbl_T_Project_SparkStatus_Management(conn_),
        '10': createTbl_T_Project_SysStep_Config(conn_),
        '11': createTbl_T_SystemSetting(conn_),
        '12': createTbl_T_originTable(conn_),
        '13': createTbl_T_Project_NumStatValue(conn_),
        '14': createDB_key_db(conn_),
        '15': createUser_deidadmin(conn_),
        '16': createUser_keyadmin(conn_),
        '17': setPrivileges_deidadmin(conn_),
        '18': setPrivileges_keyadmin(conn_),
        '19': update_deidadmin(conn_),
        '20': update_keyadmin(conn_),
        '21': flushPrivileges(conn_),
        '22': insert_T_Member(conn_),
        '23': insert_T_Project(conn_),
        '24': insert_T_ProjectStatus(conn_),
        '25': createTbl_T_Project_FinalTable(conn_)
    }

    for i in range(len(stepDict)):
        print(i)
        try:
            result = stepDict[str(i)]
            if result['result'] == 1:
                logBase64(result['msg'])
            else:
                print('mysql fail:' + result['msg'])
                #return False
        except:
            pass

if __name__ == "__main__":
    main()

