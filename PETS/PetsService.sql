DROP DATABASE IF EXISTS PetsService;
CREATE DATABASE PetsService DEFAULT CHARSET utf8 COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS `T_Pets_Group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '機關ID',
  `group_name` varchar(100) NOT NULL COMMENT '機關名稱',
  `group_type` varchar(100) NOT NULL COMMENT '機關代號',
  `project_quota` int(11) DEFAULT NULL COMMENT '機關專案配額',
  `createtime` datetime DEFAULT current_timestamp() COMMENT '建立日期',
  `updatetime` datetime DEFAULT NULL COMMENT '修改日期',
  `createmember_id` int(11) NOT NULL COMMENT '建立使用者ID',
  `updatemember_id` int(11) DEFAULT NULL COMMENT '修改使用者ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_name` (`group_name`),
  UNIQUE KEY `group_type` (`group_type`),
  KEY `ix_T_Pets_Group_id` (`id`)
)  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 取消選取資料匯出。

-- 傾印  資料表 testuser.T_Pets_Member 結構
CREATE TABLE IF NOT EXISTS `T_Pets_Member` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '使用者ID',
  `useraccount` varchar(100) NOT NULL COMMENT '使用者帳號',
  `username` varchar(100) NOT NULL COMMENT '使用者姓名',
  `password` varchar(255) NOT NULL COMMENT '密碼',
  `email` varchar(255) DEFAULT NULL COMMENT 'Email',
  `group_id` int(11) DEFAULT NULL COMMENT '機關ID',
  `createtime` datetime DEFAULT current_timestamp() COMMENT '建立日期',
  `updatetime` datetime DEFAULT NULL COMMENT '修改日期',
  `createmember_id` int(11) DEFAULT NULL COMMENT '建立使用者ID',
  `updatemember_id` int(11) DEFAULT NULL COMMENT '修改使用者ID',
  `isactive` tinyint(1) DEFAULT NULL COMMENT '帳號是否啟用',
  `ischange` tinyint(1) DEFAULT NULL COMMENT '密碼是否變更',
  `last_time` datetime DEFAULT NULL COMMENT '最後登入時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `useraccount` (`useraccount`),
  KEY `group_id` (`group_id`),
  KEY `ix_T_Pets_Member_id` (`id`),
  CONSTRAINT `T_Pets_Member_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `T_Pets_Group` (`id`)
)  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 取消選取資料匯出。

-- 傾印  資料表 testuser.T_Pets_MemberGroupRole 結構
CREATE TABLE IF NOT EXISTS `T_Pets_MemberGroupRole` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '機關使用者權限ID',
  `member_role` int(11) NOT NULL COMMENT '1:super admin, 2:group admin',
  `group_id` int(11) DEFAULT NULL COMMENT '機關ID',
  `member_id` int(11) NOT NULL COMMENT '使用者ID',
  `createtime` datetime DEFAULT current_timestamp() COMMENT '建立日期',
  `updatetime` datetime DEFAULT NULL COMMENT '修改日期',
  `createmember_id` int(11) NOT NULL COMMENT '建立使用者ID',
  `updatemember_id` int(11) DEFAULT NULL COMMENT '修改使用者ID',
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  KEY `member_id` (`member_id`),
  KEY `createmember_id` (`createmember_id`),
  KEY `updatemember_id` (`updatemember_id`),
  KEY `ix_T_Pets_MemberGroupRole_id` (`id`),
  CONSTRAINT `T_Pets_MemberGroupRole_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `T_Pets_Group` (`id`),
  CONSTRAINT `T_Pets_MemberGroupRole_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_MemberGroupRole_ibfk_3` FOREIGN KEY (`createmember_id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_MemberGroupRole_ibfk_4` FOREIGN KEY (`updatemember_id`) REFERENCES `T_Pets_Member` (`id`)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 取消選取資料匯出。
CREATE TABLE IF NOT EXISTS `PetsService`.`T_Pets_Project` (
    project_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL UNIQUE,
    project_eng VARCHAR(255) NOT NULL UNIQUE,
    project_desc LONGTEXT,
    createtime DATETIME NOT NULL,
    updatetime DATETIME,
    enc_key VARCHAR(200),
    jointablename VARCHAR(255),
    jointablecount int,
    aes_col VARCHAR(255),
    join_func INT,
    group_id INT(11),
    createMember_Id INT(11),
    updateMember_Id INT(11),
    FOREIGN KEY(group_id) REFERENCES T_Pets_Group(id),
    FOREIGN KEY(createMember_Id) REFERENCES T_Pets_Member(id),
    FOREIGN KEY(updateMember_Id) REFERENCES T_Pets_Member(id)

) DEFAULT CHARSET=utf8;


CREATE TABLE  IF NOT EXISTS `PetsService`.`T_Pets_UtilityResult` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  privacy_type varchar(10) NOT NULL,
  `dbName` varchar(255) NOT NULL,
  `deIdTbl` varchar(255) NOT NULL,
  `target_col` varchar(255) NOT NULL,
  `model` varchar(255) NOT NULL,
  `MLresult` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `createMember_Id` int(11) DEFAULT NULL,
  `updateMember_Id` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  FOREIGN KEY(project_id) REFERENCES T_Pets_Project(project_id),
   FOREIGN KEY(createMember_Id) REFERENCES T_Pets_Member(id),
    FOREIGN KEY(updateMember_Id) REFERENCES T_Pets_Member(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

-- 傾印  資料表 testuser.T_Pets_MemberProjectRole 結構
CREATE TABLE IF NOT EXISTS `T_Pets_MemberProjectRole` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '專案使用者權限ID',
  `project_role` int(11) NOT NULL COMMENT '1:project admin, 2:project user, 3:project data provider',
  `project_id` int(11) NOT NULL COMMENT '專案ID',
  `member_id` int(11) NOT NULL COMMENT '使用者ID',
  `createtime` datetime DEFAULT current_timestamp() COMMENT '建立日期',
  `updatetime` datetime DEFAULT NULL COMMENT '修改日期',
  `createmember_id` int(11) NOT NULL COMMENT '建立使用者ID',
  `updatemember_id` int(11) DEFAULT NULL COMMENT '修改使用者ID',
  PRIMARY KEY (`id`),
  KEY `member_id` (`member_id`),
  KEY `createmember_id` (`createmember_id`),
  KEY `updatemember_id` (`updatemember_id`),
  KEY `ix_T_Pets_MemberProjectRole_id` (`id`),
  FOREIGN KEY(project_id) REFERENCES T_Pets_Project(project_id),
  CONSTRAINT `T_Pets_MemberProjectRole_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_MemberProjectRole_ibfk_2` FOREIGN KEY (`createmember_id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_MemberProjectRole_ibfk_3` FOREIGN KEY (`updatemember_id`) REFERENCES `T_Pets_Member` (`id`)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 取消選取資料匯出。

-- 傾印  資料表 testuser.T_Pets_Permission 結構
CREATE TABLE IF NOT EXISTS `T_Pets_Permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '權限ID',
  `name` varchar(100) NOT NULL COMMENT '權限名稱',
  `description` varchar(100) NOT NULL COMMENT '權限說明',
  PRIMARY KEY (`id`),
  KEY `ix_T_Pets_Permission_id` (`id`)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 取消選取資料匯出。

-- 傾印  資料表 testuser.T_Pets_RolePermission 結構
CREATE TABLE IF NOT EXISTS `T_Pets_RolePermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '角色權限對應ID',
  `role_id` int(11) NOT NULL COMMENT '角色ID',
  `permission_id` int(11) NOT NULL COMMENT '權限ID',
  PRIMARY KEY (`id`),
  KEY `permission_id` (`permission_id`),
  KEY `ix_T_Pets_RolePermission_id` (`id`),
  CONSTRAINT `T_Pets_RolePermission_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `T_Pets_Permission` (`id`)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `PetsService`.`T_Pets_ProjectJoinFunc` (
        Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        left_group_id int NOT NULL,
        left_dataset varchar(255) NOT NULL,
        left_col varchar(255) NOT NULL,
        right_group_id int NOT NULL,
        right_dataset varchar(255) NOT NULL,
        right_col varchar(255) NOT NULL,
        project_id int NOT NULL,
        createMember_Id int not null,
        updateMember_Id int,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        FOREIGN KEY(left_group_id) REFERENCES T_Pets_Group(id),
        FOREIGN KEY(right_group_id) REFERENCES T_Pets_Group(id),
        FOREIGN KEY(project_id) REFERENCES T_Pets_Project(project_id),
        FOREIGN KEY(createMember_Id) REFERENCES T_Pets_Member(id),
        FOREIGN KEY(updateMember_Id) REFERENCES T_Pets_Member(id)
    ) DEFAULT CHARSET=utf8;

    


    CREATE TABLE IF NOT EXISTS `PetsService`.`T_Pets_ProjectStatus` (
        ps_id INT(11) NOT NULL auto_increment PRIMARY KEY,
        project_id INT(11) NOT NULL,
        project_status INT(11) NOT NULL,
        createtime DATETIME NOT NULL,
        updatetime DATETIME,
        createMember_Id int not null,
        updateMember_Id int,
        FOREIGN KEY(project_id) REFERENCES T_Pets_Project(project_id),
        FOREIGN KEY(createMember_Id) REFERENCES T_Pets_Member(id),
        FOREIGN KEY(updateMember_Id) REFERENCES T_Pets_Member(id)
    ) DEFAULT CHARSET=utf8;

 CREATE TABLE IF NOT EXISTS `PetsService`.`T_Pets_Syslog` (
        id INT(11) NOT NULL auto_increment PRIMARY KEY,
    sysdatetime DATETIME DEFAULT current_timestamp,
    useraccount VARCHAR(100) NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    project_name VARCHAR(255),
    logcontent VARCHAR(255)
    ) DEFAULT CHARSET=utf8;

 CREATE TABLE IF NOT EXISTS `PetsService`.`T_Pets_JobSyslog` (
        id INT(11) NOT NULL auto_increment PRIMARY KEY,
        starttime DATETIME NOT NULL,
        endtime DATETIME ,
        member_id INT(11) NOT NULL,
        log_type INT(11) NOT NULL,
        project_id int,
        jobname varchar(255),
        project_step varchar(255),
        percentage int,
        logcontent varchar(255),
        FOREIGN KEY(project_id) REFERENCES T_Pets_Project(project_id),
        FOREIGN KEY(member_id) REFERENCES T_Pets_Member(id)
    ) DEFAULT CHARSET=utf8;




CREATE TABLE IF NOT EXISTS `PetsService`.`T_Pets_HistoryProject` (
    project_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL ,
    project_eng VARCHAR(255) NOT NULL ,
    project_desc LONGTEXT,
    createtime DATETIME NOT NULL,
    updatetime DATETIME,
    enc_key VARCHAR(200),
    jointablename VARCHAR(255),
    jointablecount int,
    join_func INT,
    join_func_content longtext,
    project_role_content longtext,
    group_id INT(11),
    createMember_Id INT(11),
    updateMember_Id INT(11),
    FOREIGN KEY(group_id) REFERENCES T_Pets_Group(id),
    FOREIGN KEY(createMember_Id) REFERENCES T_Pets_Member(id),
    FOREIGN KEY(updateMember_Id) REFERENCES T_Pets_Member(id)
 
) DEFAULT CHARSET=utf8;


Alter view `PetsService`.`V_Pets_ProjectList` as
select * from (select row_number() over(order by tp.project_id) as row_num,tp.*,tps.project_status,
case tps.project_status when 0 then '建立專案及設定' 
when 1 then '資料匯入及鏈結設定檢查' when 2 then '安全資料鏈結處理' when 3 then '安全資料鏈結處理中' 
when 4 then '隱私安全服務強化處理' when 5 then '產生隱私安全強化資料' when 6 then '感興趣欄位選擇' 
when 7 then '可用性分析處理中'end as project_statusname,
tpmr.id as project_roleid,tpmr.member_id as rolemember_id,tpmr.useraccount,tpmr.username,tpmr.project_role,
tpjf.id as project_joinfuncid,tpjf.left_group_id,tpjf.left_dataset,tpjf.left_col,tpjf.right_group_id,tpjf.right_dataset,tpjf.right_col
from `PetsService`.`T_Pets_Project` as tp
inner join `PetsService`.`T_Pets_ProjectStatus` as tps on tp.project_id = tps.project_id
left join (select tpmr.*,tpm.useraccount,tpm.username from `PetsService`.`T_Pets_MemberProjectRole` as tpmr
inner join `PetsService`.`T_Pets_Member` as tpm on tpmr.member_id = tpm.id ) as tpmr on tp.project_id = tpmr.project_id
left join  `PetsService`.`T_Pets_ProjectJoinFunc` as tpjf on tp.project_id = tpjf.project_id )
as projectlist 
