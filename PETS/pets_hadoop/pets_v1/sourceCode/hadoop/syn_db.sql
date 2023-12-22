
    DROP DATABASE IF EXISTS SynService;
    CREATE DATABASE SynService DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
    


    #1
    CREATE TABLE SynService.T_Dept (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    #2
    CREATE TABLE SynService.T_Member (
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
    

    #3
    CREATE TABLE SynService.T_Pro_DistinctTB (
        pdis_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        pro_db VARCHAR(100) NOT NULL,
        pro_tb VARCHAR(100) NOT NULL,
        pro_col VARCHAR(100) NOT NULL,
        pro_discol_count LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    #4
    CREATE TABLE SynService.T_Project (
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
    

    #5
    CREATE TABLE SynService.T_ProjectJobStatus (
        pjs_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_jobstatus INT(11) NOT NULL,
        jobname VARCHAR(255) NOT NULL,
        job_tb VARCHAR(255),
        jobrule VARCHAR(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    #6
    CREATE TABLE SynService.T_ProjectSampleData (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        dbname VARCHAR(255) NOT NULL,
        tbname VARCHAR(255) NOT NULL,
        data LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    #7
    CREATE TABLE SynService.T_ProjectStatus (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_status INT(11) NOT NULL,
        statusname VARCHAR(255) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    #8
    CREATE TABLE SynService.T_Project_SampleTable (
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
    

    #9
    CREATE TABLE SynService.T_Project_SparkStatus_Management (
        pspark_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        app_id VARCHAR(255) NOT NULL,
        celery_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        step VARCHAR(100),
        stepstatus int(1)
    ) DEFAULT CHARSET=utf8;
    

    #10
    CREATE TABLE SynService.T_Project_SysStep_Config (
        psys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        pro_status INT(11) NOT NULL,
        pro_status_config TEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        project_id int(11) NOT NULL
    ) DEFAULT CHARSET=utf8;
    

    #11
    CREATE TABLE SynService.T_SystemSetting (
        sys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        kdata VARCHAR(100),
        ldata VARCHAR(100),
        rdata VARCHAR(100),
        dfprojowner INT(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME NOT NULL
    ) DEFAULT CHARSET=utf8;
    

    #12
    CREATE TABLE SynService.T_originTable (
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
    

    #13
    CREATE TABLE SynService.T_Project_NumStatValue (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        proj_id INT(11) NOT NULL,
        proj_db VARCHAR(100) NOT NULL,
        proj_table VARCHAR(100) NOT NULL,
        statValue LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    
    #14: Data generation
    CREATE TABLE SynService.T_ProjectGetFolder (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        csvdata LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    #15
    CREATE TABLE SynService.T_ProjectSample5Data (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        data LONGTEXT NOT NULL,
        select_data LONGTEXT,
        select_colNames LONGTEXT ,
        targetCols LONGTEXT ,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    #16
    CREATE TABLE SynService.T_ProjectColumnType (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        pro_col_en LONGTEXT,
        pro_col_cht LONGTEXT,
        tableCount INT(11),
        ob_col LONGTEXT,
        ID_column LONGTEXT,
        pro_col_en_nunique LONGTEXT,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    #17
    CREATE TABLE SynService.T_CeleryStatus (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        step VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        return_result TEXT NOT NULL,
        log TEXT NOT NULL,
        isRead INT(11) DEFAULT 0,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    #18
    CREATE TABLE SynService.T_GANStatus (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        jobName VARCHAR(255) NOT NULL,
        step VARCHAR(255) NOT NULL,
        percentage INT(11),
        isRead INT(11) DEFAULT 0,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    #19
    CREATE TABLE SynService.T_utilityResult (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        target_col VARCHAR(255) NOT NULL,
        select_csv VARCHAR(255) NOT NULL,
        model VARCHAR(255) NOT NULL,
        MLresult LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;

    #DROP TABLE IF EXISTS key_db.products;
    DROP DATABASE IF EXISTS key_db;
    CREATE DATABASE key_db DEFAULT CHARSET utf8 COLLATE utf8_general_ci;

    #DROP TABLE IF EXISTS key_db.products;
    
    CREATE TABLE key_db.products (
      id int(11) NOT NULL AUTO_INCREMENT,
      school_tag varchar(50) NOT NULL,
      key_enc varchar(200) DEFAULT NULL,
      PRIMARY KEY (id)
    ) DEFAULT CHARSET=utf8;

    DROP USER IF EXISTS 'deidadmin'@'%';

    CREATE USER 'deidadmin'@'%' IDENTIFIED BY 'citcw200';

    DROP USER IF EXISTS 'keyadmin'@'%';

    CREATE USER 'keyadmin'@'%' IDENTIFIED BY 'citcw200';
    


    GRANT ALL PRIVILEGES ON SynService.* to 'deidadmin'@'%' IDENTIFIED BY 'citcw200' WITH GRANT OPTION;
    


    GRANT ALL PRIVILEGES ON key_db.* to 'keyadmin'@'%';
    


    UPDATE mysql.user SET select_priv='Y',
    insert_priv='Y',
    update_priv='Y',
    delete_priv='Y',
    create_priv='Y',
    drop_priv='Y',
    reload_priv='Y',
    grant_priv='Y',
    alter_priv='Y' WHERE user='deidadmin';
    


    UPDATE mysql.user SET select_priv='Y',
    insert_priv='Y',
    update_priv='Y',
    delete_priv='Y',
    create_priv='Y',
    drop_priv='Y',
    reload_priv='Y',
    grant_priv='Y',
    alter_priv='Y' WHERE user='keyadmin';
    


    FLUSH PRIVILEGES;
    
INSERT INTO key_db.products VALUES (1,'ntut','Bar12345Bar12345Bar12345Bar12345');

INSERT INTO SynService.T_Member (dept_id,useraccount,isAdmin,password,createtime) VALUES ('1','deidadmin','1','citcw200',now());

INSERT INTO SynService.T_Project (projectowner_id,project_path,project_cht,project_name,export_path,createtime) VALUES ('1','/home/deid/citc/sourceCode/hadoop/data/input/','2QDataMarketDeId','2QDataMarketDeId','/home/deid/citc/sourceCode/hadoop/data/output/',now());

INSERT INTO SynService.T_ProjectStatus (statusname,project_id,project_status,createtime) VALUES ('資料專案開啟','1','0',now());


    CREATE TABLE SynService.T_Project_FinalTable (
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
    

