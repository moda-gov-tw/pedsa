

GRANT ALL PRIVILEGES ON DpService.* TO 'deidadmin'@'%';
FLUSH PRIVILEGES;

    CREATE TABLE DpService.T_Dept (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    CREATE TABLE DpService.T_Member (
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
    

    CREATE TABLE DpService.T_Pro_DistinctTB (
        pdis_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        pro_db VARCHAR(100) NOT NULL,
        pro_tb VARCHAR(100) NOT NULL,
        pro_col VARCHAR(100) NOT NULL,
        pro_discol_count LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    CREATE TABLE DpService.T_Project (
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
    

    CREATE TABLE DpService.T_ProjectJobStatus (
        pjs_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_jobstatus INT(11) NOT NULL,
        jobname VARCHAR(255) NOT NULL,
        job_tb VARCHAR(255),
        jobrule VARCHAR(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DpService.T_ProjectSampleData (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        dbname VARCHAR(255) NOT NULL,
        tbname VARCHAR(255) NOT NULL,
        data LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DpService.T_ProjectStatus (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_status INT(11) NOT NULL,
        statusname VARCHAR(255) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    CREATE TABLE DpService.T_Project_SampleTable (
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
    

    CREATE TABLE DpService.T_Project_SparkStatus_Management (
        pspark_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        app_id VARCHAR(255) NOT NULL,
        celery_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        step VARCHAR(100),
        stepstatus int(1)
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DpService.T_Project_SysStep_Config (
        psys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        pro_status INT(11) NOT NULL,
        pro_status_config TEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        project_id int(11) NOT NULL
    ) DEFAULT CHARSET=utf8;
    

    CREATE TABLE DpService.T_SystemSetting (
        sys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        kdata VARCHAR(100),
        ldata VARCHAR(100),
        rdata VARCHAR(100),
        dfprojowner INT(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME NOT NULL
    ) DEFAULT CHARSET=utf8;
    

    CREATE TABLE DpService.T_originTable (
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
    

    CREATE TABLE DpService.T_Project_NumStatValue (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        proj_id INT(11) NOT NULL,
        proj_db VARCHAR(100) NOT NULL,
        proj_table VARCHAR(100) NOT NULL,
        statValue LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    
    CREATE TABLE DpService.T_ProjectGetFolder (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        pro_name VARCHAR(255) NOT NULL,
        csvdata LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
   



    CREATE TABLE DpService.T_ProjectSample5Data (
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
 
    CREATE TABLE DpService.T_ProjectColumnType (
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
  
    CREATE TABLE DpService.T_CeleryStatus (
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

    CREATE TABLE DpService.T_GANStatus (
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
  
    CREATE TABLE DpService.T_utilityResult (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        target_col VARCHAR(255) NOT NULL,
        select_csv VARCHAR(255) NOT NULL,
        model VARCHAR(255) NOT NULL,
        MLresult LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;

    
INSERT INTO DpService.T_Member (dept_id,useraccount,isAdmin,password,createtime) VALUES ('1','deidadmin','1','citcw200',now());

INSERT INTO DpService.T_Project (projectowner_id,project_path,project_cht,project_name,export_path,createtime) VALUES ('1','/home/deid/citc/sourceCode/hadoop/data/input/','2QDataMarketDeId','2QDataMarketDeId','/home/deid/citc/sourceCode/hadoop/data/output/',now());

INSERT INTO DpService.T_ProjectStatus (statusname,project_id,project_status,createtime) VALUES ('資料專案開啟','1','0',now());


    CREATE TABLE DpService.T_Project_FinalTable (
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
    

