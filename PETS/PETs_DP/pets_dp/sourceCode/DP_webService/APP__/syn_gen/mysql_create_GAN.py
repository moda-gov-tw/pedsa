from MyLib.connect_sql import ConnectSQL 

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

def flushPrivileges(conn):
    # Create Database;
    sqlCommand = """
    FLUSH PRIVILEGES;
    """
    result = conn.doSqlCommand(sqlCommand)
    return result

def createDB_SynService(conn):
    # Create Database;
    db = 'SynService'
    sqlCommand = """
    CREATE DATABASE IF NOT EXISTS {0} DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
    """.format(db)
    result = conn.doSqlCommand(sqlCommand)
    return result

def createTbl_T_GANStatus(conn):
    db = 'SynService'
    tbl = 'T_GANStatus'
    sqlCommand = """
    CREATE TABLE IF NOT EXISTS {0}.{1} (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        jobName VARCHAR(255) NOT NULL,
        step VARCHAR(255) NOT NULL,
        percentage INT(11) ,
        isRead INT(11) DEFAULT 0,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    """.format(db, tbl)
    result = conn.doSqlCommand(sqlCommand)
    return result