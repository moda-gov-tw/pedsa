
  
    DROP DATABASE IF EXISTS DeIdService;
    CREATE DATABASE DeIdService DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
    


    CREATE TABLE DeIdService.T_Dept (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_Member (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        useraccount VARCHAR(100) NOT NULL,
        username VARCHAR(100),
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        dept_id INT(11) NOT NULL,
        isAdmin tinyint(1) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
	isChange tinyint(1) not null
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_Pro_DistinctTB (
        pdis_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        pro_db VARCHAR(100) NOT NULL,
        pro_tb VARCHAR(100) NOT NULL,
        pro_col VARCHAR(100) NOT NULL,
        pro_discol_count LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_Project (
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
    


    CREATE TABLE DeIdService.T_ProjectJobStatus (
        pjs_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_jobstatus INT(11) NOT NULL,
        jobname VARCHAR(255) NOT NULL,
        job_tb VARCHAR(255),
        jobrule VARCHAR(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    

    #kdata, distinctCount : 20200224 Jade
    CREATE TABLE DeIdService.T_ProjectSampleData (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        dbname VARCHAR(255) NOT NULL,
        tbname VARCHAR(255) NOT NULL,
        data LONGTEXT NOT NULL,
        kdata LONGTEXT,
        distinctCount LONGTEXT,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_ProjectStatus (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_status INT(11) NOT NULL,
        statusname VARCHAR(255) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_Project_SampleTable (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        pro_db VARCHAR(100) NOT NULL,
        pro_tb VARCHAR(100) NOT NULL,
        pro_col_en LONGTEXT,
        pro_col_cht LONGTEXT,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        dataconfig VARCHAR(255),
        pro_path VARCHAR(255),
        tableCount_before INT(11),   
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
        after_col_value LONGTEXT,
        gen_qi_settingvalue LONGTEXT,
        warning_col LONGTEXT,
        isqi varchar(1),
        tableCountFinal int(11),
        tableDisCountFinal int(11),
        target_col varchar(100)
    ) DEFAULT CHARSET=utf8;


    CREATE TABLE DeIdService.T_utilityResult (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        dbName VARCHAR(255) NOT NULL,
        deIdTbl VARCHAR(255) NOT NULL,
        target_col VARCHAR(255) NOT NULL,       
        model VARCHAR(255) NOT NULL,
        MLresult LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;

    CREATE TABLE DeIdService.T_Project_RiskTable (
        id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_name VARCHAR(255) NOT NULL,
        dbname VARCHAR(255) NOT NULL,
        tblname VARCHAR(255) NOT NULL,
        r1 VARCHAR(100),
        r2 VARCHAR(100),
        r3 VARCHAR(100),
        r4 VARCHAR(100),
        r5 VARCHAR(100),
        rs1 VARCHAR(100),
        rs2 VARCHAR(100),
        rs3 VARCHAR(100),
        rs4 VARCHAR(100),
        rs5 VARCHAR(100),
        createtime DATETIME DEFAULT now(),
        updatetime DATETIME DEFAULT now() ON UPDATE now()
    ) DEFAULT CHARSET=utf8;


    
    
    #ALTER TABLE DeIdService.T_Project_SampleTable add COLUMN isqi varchar(1); 
    #ALTER TABLE DeIdService.T_Project_SampleTable add COLUMN tableCountFinal int(11); 
    #ALTER TABLE DeIdService.T_Project_SampleTable add COLUMN tableDisCountFinal int(11); 
    #ALTER Table DeIdService.T_Project_SampleTable add COLUMN target_col varchar(100); 

    CREATE TABLE DeIdService.T_Project_SparkStatus_Management (
        pspark_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        app_id VARCHAR(255) NOT NULL,
        celery_id VARCHAR(255) NOT NULL,
        project_id INT(11) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        step VARCHAR(100),
        stepstatus int(1)
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_Project_SysStep_Config (
        psys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        pro_status INT(11) NOT NULL,
        pro_status_config TEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        project_id int(11) NOT NULL
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_SystemSetting (
        sys_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        kdata VARCHAR(100),
        ldata VARCHAR(100),
        rdata VARCHAR(100),
        dfprojowner INT(255),
        createtime DATETIME NOT NULL,
        updatetime DATETIME NOT NULL
    ) DEFAULT CHARSET=utf8;
    


    CREATE TABLE DeIdService.T_originTable (
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
    


    CREATE TABLE DeIdService.T_Project_NumStatValue (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        proj_id INT(11) NOT NULL,
        proj_db VARCHAR(100) NOT NULL,
        proj_table VARCHAR(100) NOT NULL,
        statValue LONGTEXT NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME
    ) DEFAULT CHARSET=utf8;
    
    
    #20200317###############
    CREATE TABLE DeIdService.T_GroupMember (
        Id INT(11) NOT NULL auto_increment PRIMARY KEY,
        Member_Id INT(11) NOT NULL,
        Group_Id INT(11) NOT NULL,
        CreateMember INT(11) NOT NULL,
        createtime DATETIME NOT NULL
    ) DEFAULT CHARSET=utf8;

    #2020/12/17#for tar-tai ####
    CREATE TABLE DeIdService.T_ProjectDataFilter (
        id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_name VARCHAR(255),
        pdf_data LONGTEXT,
        pdf_item LONGTEXT,
        pdf_config LONGTEXT,
        createtime DATETIME NOT NULL
    ) DEFAULT CHARSET=utf8;

    insert into DeIdService.T_Dept(dept_name,createtime)value('ITRI_CITC',now());  

    insert into DeIdService.T_Member(useraccount,username,password,dept_id,isAdmin,createtime,isChange)value('deidadmin','deidadmin','26e7a2b13ab39e1b8b70b41a3be4e7dd',(select id from DeIdService.T_Dept where dept_name='ITRI_CITC'),1,now(),0);
    ###########################################
    

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
    


    GRANT ALL PRIVILEGES ON DeIdService.* to 'deidadmin'@'%' IDENTIFIED BY 'citcw200' WITH GRANT OPTION;
    


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

INSERT INTO DeIdService.T_Project (projectowner_id,project_path,project_cht,project_name,export_path,createtime) VALUES ('1','/home/deid/citc/sourceCode/hadoop/data/input/','2QDataMarketDeId','2QDataMarketDeId','/home/deid/citc/sourceCode/hadoop/data/output/',now());

INSERT INTO DeIdService.T_ProjectStatus (statusname,project_id,project_status,createtime) VALUES ('è³æ?å°æ??å?','1','0',now());


    CREATE TABLE DeIdService.T_Project_FinalTable (
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


    ALTER TABLE DeIdService.T_Project_FinalTable MODIFY genTblName varchar(100) NULL;
    


    
    #####20191127 created#########################
    DROP DATABASE IF EXISTS spark_status;
    CREATE DATABASE spark_status DEFAULT CHARSET utf8 COLLATE utf8_general_ci;


    CREATE TABLE spark_status.nodeStatus (
      id int(11) NOT NULL AUTO_INCREMENT,
      Node_Id varchar(50) NOT NULL,
      Node_State varchar(50) NOT NULL,
      Health_Report varchar(200) DEFAULT NULL,
      createtime DATETIME NOT NULL,
      updatetime DATETIME,
      PRIMARY KEY (id)
    ) DEFAULT CHARSET=utf8;

    CREATE TABLE spark_status.appStatus (
      id int(11) NOT NULL AUTO_INCREMENT,
      Application_Id varchar(50) NOT NULL,
      Application_Name varchar(50) NOT NULL,
      App_State varchar(150) NOT NULL,
      Progress varchar(30) DEFAULT NULL,
      Progress_State varchar(30) DEFAULT NULL,
      proj_id INT(11),
      dbName VARCHAR(255),
      createtime DATETIME NOT NULL,
      updatetime DATETIME,
      PRIMARY KEY (id)
    ) DEFAULT CHARSET=utf8;

    ALTER USER 'root'@'localhost' IDENTIFIEd BY 'citcw200';
    FLUSH PRIVILEGES;
    
    #20200311, add
    Alter table `spark_status`.`appStatus` add column isRead int(11);
    #20200314, add
    Alter table `spark_status`.`appStatus` add column createMember_Id int(11);
    Alter table `spark_status`.`appStatus` add column updateMember_Id int(11);

    #ALTER Table spark_status.appStatus add COLUMN proj_id INT(11);
    #ALTER Table spark_status.appStatus add COLUMN dbName VARCHAR(255);


    #ALTER TABLE spark_status.appStatus  DROP proj_id;
    #ALTER TABLE spark_status.appStatus  DROP dbName;

    #ALTER TABLE spark_status.appStatus MODIFY proj_id INT(200) DEFAULT 1;
    #ALTER TABLE spark_status.appStatus MODIFY dbName varchar(255) DEFAULT '1';

    ## 20200327 add by Jade
    ALTER Table `DeIdService`.`T_Project_SampleTable` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_SampleTable` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_ProjectJobStatus` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_ProjectJobStatus` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_RiskTable` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_RiskTable` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_originTable` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_originTable` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_ProjectSampleData` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_ProjectSampleData` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Pro_DistinctTB` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Pro_DistinctTB` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_FinalTable` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_FinalTable` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_NumStatValue` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_NumStatValue` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_utilityResult` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_utilityResult` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_SysStep_Config` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_SysStep_Config` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_SparkStatus_Management` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_SparkStatus_Management` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_SystemSetting` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_SystemSetting` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Dept` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_Dept` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_ProjectStatus` add COLUMN createMember_Id int(11);
    ALTER Table `DeIdService`.`T_ProjectStatus` add COLUMN updateMember_Id int(11);
    ALTER Table `DeIdService`.`T_Project_SampleTable` add COLUMN kdata_col_en longtext;
    ALTER Table `DeIdService`.`T_Project_SampleTable` add COLUMN gen_col_en longtext;
    ALTER Table `DeIdService`.`T_ProjectSampleData` add COLUMN gen_data longtext;
    ALTER Table `DeIdService`.`T_ProjectSampleData` add COLUMN gen_discount longtext;
    ALTER TABLE `DeIdService`.`T_Project_SampleTable` add COLUMN kdata_col_datatype longtext;
    ALTER TABLE `DeIdService`.`T_Project_SampleTable` add COLUMN k_risk varchar(100);
    ALTER TABLE `DeIdService`.`T_Project_SampleTable` add COLUMN T1 DECIMAL(5,5);
    ALTER TABLE `DeIdService`.`T_Project_SampleTable` add COLUMN T2 DECIMAL(5,5);
    ALTER TABLE `DeIdService`.`T_Project_SampleTable` add COLUMN r_value DECIMAL(5,5);
    ALTER TABLE `DeIdService`.`T_Project_SampleTable` add COLUMN max_t DECIMAL(5,5);
