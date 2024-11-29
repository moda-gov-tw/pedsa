CREATE DATABASE  IF NOT EXISTS `PetsService` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `PetsService`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 34.81.71.21    Database: PetsService
-- ------------------------------------------------------
-- Server version	5.5.5-10.3.21-MariaDB-1:10.3.21+maria~bionic

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `T_Pets_FailedLogin`
--

DROP TABLE IF EXISTS `T_Pets_FailedLogin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_FailedLogin` (
  `member_id` int(11) NOT NULL COMMENT '使用者ID',
  `times` int(11) NOT NULL,
  `last_time` datetime NOT NULL,
  PRIMARY KEY (`member_id`),
  CONSTRAINT `T_Pets_FailedLogin_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_FailedLogin`
--


--
-- Table structure for table `T_Pets_Group`
--

DROP TABLE IF EXISTS `T_Pets_Group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_Group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '機關ID',
  `group_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '機關名稱',
  `group_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '機關代號',
  `project_quota` int(11) DEFAULT NULL COMMENT '機關專案配額',
  `createtime` datetime DEFAULT current_timestamp() COMMENT '建立日期',
  `updatetime` datetime DEFAULT NULL COMMENT '修改日期',
  `createmember_id` int(11) NOT NULL COMMENT '建立使用者ID',
  `updatemember_id` int(11) DEFAULT NULL COMMENT '修改使用者ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_name` (`group_name`),
  UNIQUE KEY `group_type` (`group_type`),
  KEY `ix_T_Pets_Group_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_Group`
--

LOCK TABLES `T_Pets_Group` WRITE;
/*!40000 ALTER TABLE `T_Pets_Group` DISABLE KEYS */;
INSERT INTO `T_Pets_Group` VALUES (1,'system','sys',20,'2024-01-01 00:00:00',NULL,1,NULL);
/*!40000 ALTER TABLE `T_Pets_Group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Pets_HistoryProject`
--

DROP TABLE IF EXISTS `T_Pets_HistoryProject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_HistoryProject` (
  `project_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(255) NOT NULL,
  `project_eng` varchar(255) NOT NULL,
  `project_desc` longtext DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `enc_key` varchar(200) DEFAULT NULL,
  `jointablename` varchar(255) DEFAULT NULL,
  `jointablecount` int(11) DEFAULT NULL,
  `join_func` int(11) DEFAULT NULL,
  `join_func_content` longtext DEFAULT NULL,
  `project_role_content` longtext DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `createMember_Id` int(11) DEFAULT NULL,
  `updateMember_Id` int(11) DEFAULT NULL,
  `aes_col` varchar(255) DEFAULT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `useraccount` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`project_id`),
  KEY `group_id` (`group_id`),
  KEY `createMember_Id` (`createMember_Id`),
  KEY `updateMember_Id` (`updateMember_Id`),
  CONSTRAINT `T_Pets_HistoryProject_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `T_Pets_Group` (`id`),
  CONSTRAINT `T_Pets_HistoryProject_ibfk_2` FOREIGN KEY (`createMember_Id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_HistoryProject_ibfk_3` FOREIGN KEY (`updateMember_Id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_HistoryProject`
--


DROP TABLE IF EXISTS `T_Pets_JobSyslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_JobSyslog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `member_id` int(11) NOT NULL,
  `log_type` int(11) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `jobname` varchar(255) DEFAULT NULL,
  `project_step` varchar(255) DEFAULT NULL,
  `percentage` int(11) DEFAULT NULL,
  `logcontent` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  KEY `member_id` (`member_id`),
  CONSTRAINT `T_Pets_JobSyslog_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `T_Pets_Project` (`project_id`),
  CONSTRAINT `T_Pets_JobSyslog_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;



DROP TABLE IF EXISTS `T_Pets_Member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_Member` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '使用者ID',
  `useraccount` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '使用者帳號',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '使用者姓名',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密碼',
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Email',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_Member`
--

LOCK TABLES `T_Pets_Member` WRITE;
/*!40000 ALTER TABLE `T_Pets_Member` DISABLE KEYS */;
INSERT INTO `T_Pets_Member` VALUES (1,'admin','admin','$2b$12$RD60o4A2ALKAH8a29xIfauJCmoj4U0eIjWYsQO.z2rEq1L44A4k7m','admin@mail.com',1,'2023-10-27 07:38:13','2023-12-14 14:43:28',NULL,1,1,1,'2024-03-11 17:09:09');
/*!40000 ALTER TABLE `T_Pets_Member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Pets_MemberGroupRole`
--

DROP TABLE IF EXISTS `T_Pets_MemberGroupRole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_MemberGroupRole` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_MemberGroupRole`
--

LOCK TABLES `T_Pets_MemberGroupRole` WRITE;
/*!40000 ALTER TABLE `T_Pets_MemberGroupRole` DISABLE KEYS */;
INSERT INTO `T_Pets_MemberGroupRole` VALUES (1,1,1,1,'2023-10-27 07:38:13',NULL,1,NULL);
/*!40000 ALTER TABLE `T_Pets_MemberGroupRole` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Pets_MemberProjectRole`
--

DROP TABLE IF EXISTS `T_Pets_MemberProjectRole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_MemberProjectRole` (
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
  CONSTRAINT `T_Pets_MemberProjectRole_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_MemberProjectRole_ibfk_2` FOREIGN KEY (`createmember_id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_MemberProjectRole_ibfk_3` FOREIGN KEY (`updatemember_id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Pets_Permission`
--

DROP TABLE IF EXISTS `T_Pets_Permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_Permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '權限ID',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '權限名稱',
  `description` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '權限說明',
  PRIMARY KEY (`id`),
  KEY `ix_T_Pets_Permission_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_Permission`
--

LOCK TABLES `T_Pets_Permission` WRITE;
/*!40000 ALTER TABLE `T_Pets_Permission` DISABLE KEYS */;
INSERT INTO `T_Pets_Permission` VALUES (1,'sys_health','系統環境健康度'),(2,'syslog','系統操作記錄'),(3,'create_group','建立機關'),(4,'update_group','修改機關'),(5,'delete_group','刪除機關'),(6,'create_member','建立人員帳號'),(7,'set_admin','設定管理員'),(8,'user_list','人員列表'),(9,'project_control','專案總量管制'),(10,'create_project','建立專案'),(11,'delete_project','刪除專案'),(12,'group_list','機關列表'),(13,'edit_project','編輯專案'),(14,'project_list','專案列表'),(15,'project_setting','查看專案設定'),(16,'reset_project','重設專案'),(17,'reset_status','重設隱私強化參數'),(18,'project_report_dp','查看專案dp結果'),(19,'project_report_k','查看專案k結果'),(20,'project_report_gan','查看專案gan結果'),(21,'download_project_dp','下載隱私強化dp資料'),(22,'download_project_k','下載隱私強化k資料'),(23,'download_project_gan','下載隱私強化gan資料');
/*!40000 ALTER TABLE `T_Pets_Permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Pets_Project`
--

DROP TABLE IF EXISTS `T_Pets_Project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_Project` (
  `project_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(255) NOT NULL,
  `project_eng` varchar(255) NOT NULL,
  `project_desc` longtext DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `enc_key` varchar(200) DEFAULT NULL,
  `join_func` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `createMember_Id` int(11) DEFAULT NULL,
  `updateMember_Id` int(11) DEFAULT NULL,
  `jointablename` varchar(255) DEFAULT NULL,
  `jointablecount` int(11) DEFAULT NULL,
  `aes_col` varchar(255) DEFAULT NULL,
  `join_sampledata` longtext DEFAULT NULL,
  PRIMARY KEY (`project_id`),
  UNIQUE KEY `project_name` (`project_name`),
  UNIQUE KEY `project_eng` (`project_eng`),
  KEY `group_id` (`group_id`),
  KEY `createMember_Id` (`createMember_Id`),
  KEY `updateMember_Id` (`updateMember_Id`),
  CONSTRAINT `T_Pets_Project_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `T_Pets_Group` (`id`),
  CONSTRAINT `T_Pets_Project_ibfk_2` FOREIGN KEY (`createMember_Id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_Project_ibfk_3` FOREIGN KEY (`updateMember_Id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Pets_ProjectJoinFunc`
--

DROP TABLE IF EXISTS `T_Pets_ProjectJoinFunc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_ProjectJoinFunc` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `left_group_id` int(11) NOT NULL,
  `left_dataset` varchar(255) NOT NULL,
  `left_col` varchar(255) NOT NULL,
  `right_group_id` int(11) NOT NULL,
  `right_dataset` varchar(255) NOT NULL,
  `right_col` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `createMember_Id` int(11) NOT NULL,
  `updateMember_Id` int(11) DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `left_group_id` (`left_group_id`),
  KEY `right_group_id` (`right_group_id`),
  KEY `project_id` (`project_id`),
  KEY `createMember_Id` (`createMember_Id`),
  KEY `updateMember_Id` (`updateMember_Id`),
  CONSTRAINT `T_Pets_ProjectJoinFunc_ibfk_1` FOREIGN KEY (`left_group_id`) REFERENCES `T_Pets_Group` (`id`),
  CONSTRAINT `T_Pets_ProjectJoinFunc_ibfk_2` FOREIGN KEY (`right_group_id`) REFERENCES `T_Pets_Group` (`id`),
  CONSTRAINT `T_Pets_ProjectJoinFunc_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `T_Pets_Project` (`project_id`),
  CONSTRAINT `T_Pets_ProjectJoinFunc_ibfk_4` FOREIGN KEY (`createMember_Id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_ProjectJoinFunc_ibfk_5` FOREIGN KEY (`updateMember_Id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Pets_ProjectStatus`
--

DROP TABLE IF EXISTS `T_Pets_ProjectStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_ProjectStatus` (
  `ps_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `project_status` int(11) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `createMember_Id` int(11) NOT NULL,
  `updateMember_Id` int(11) DEFAULT NULL,
  PRIMARY KEY (`ps_id`),
  KEY `project_id` (`project_id`),
  KEY `createMember_Id` (`createMember_Id`),
  KEY `updateMember_Id` (`updateMember_Id`),
  CONSTRAINT `T_Pets_ProjectStatus_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `T_Pets_Project` (`project_id`),
  CONSTRAINT `T_Pets_ProjectStatus_ibfk_2` FOREIGN KEY (`createMember_Id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_ProjectStatus_ibfk_3` FOREIGN KEY (`updateMember_Id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Pets_RolePermission`
--

DROP TABLE IF EXISTS `T_Pets_RolePermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_RolePermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '角色權限對應ID',
  `role_id` int(11) NOT NULL COMMENT '角色ID',
  `permission_id` int(11) NOT NULL COMMENT '權限ID',
  PRIMARY KEY (`id`),
  KEY `permission_id` (`permission_id`),
  KEY `ix_T_Pets_RolePermission_id` (`id`),
  CONSTRAINT `T_Pets_RolePermission_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `T_Pets_Permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Pets_RolePermission`
--

LOCK TABLES `T_Pets_RolePermission` WRITE;
/*!40000 ALTER TABLE `T_Pets_RolePermission` DISABLE KEYS */;
INSERT INTO `T_Pets_RolePermission` VALUES (1,1,1),(2,1,2),(3,1,3),(4,1,4),(5,1,5),(6,1,6),(7,1,7),(8,1,8),(9,1,9),(10,1,10),(11,1,11),(12,1,12),(13,1,13),(14,1,14),(15,1,15),(16,1,16),(17,1,17),(18,1,18),(19,1,19),(20,1,20),(21,1,21),(22,1,22),(23,1,23),(24,2,7),(25,2,8),(26,2,9),(27,2,10),(28,2,14),(29,2,15),(30,2,18),(31,2,19),(32,2,20),(33,3,8),(34,3,10),(35,3,11),(36,3,13),(37,3,14),(38,3,15),(39,3,16),(40,3,17),(41,3,18),(42,3,19),(43,3,20),(44,3,21),(45,3,22),(46,3,23),(47,4,8),(48,4,13),(49,4,14),(50,4,15),(51,4,17),(52,4,18),(53,4,19),(54,4,20),(55,4,21),(56,4,22),(57,4,23),(58,5,14),(59,5,15),(60,5,18),(61,5,19),(62,5,20),(63,3,12);
/*!40000 ALTER TABLE `T_Pets_RolePermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Pets_Syslog`
--

DROP TABLE IF EXISTS `T_Pets_Syslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_Syslog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sysdatetime` datetime DEFAULT current_timestamp() COMMENT '操作時間',
  `useraccount` varchar(100) NOT NULL COMMENT '使用者帳號',
  `log_type` varchar(50) NOT NULL COMMENT 'Log類別',
  `project_name` varchar(255) DEFAULT NULL COMMENT '專案名稱',
  `logcontent` varchar(255) DEFAULT NULL COMMENT 'Log紀錄',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Pets_UtilityResult`
--

DROP TABLE IF EXISTS `T_Pets_UtilityResult`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pets_UtilityResult` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `privacy_type` varchar(10) NOT NULL,
  `target_col` varchar(255) NOT NULL,
  `model` varchar(255) NOT NULL,
  `MLresult` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `createMember_Id` int(11) DEFAULT NULL,
  `updateMember_Id` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `project_id` (`project_id`),
  KEY `createMember_Id` (`createMember_Id`),
  KEY `updateMember_Id` (`updateMember_Id`),
  CONSTRAINT `T_Pets_UtilityResult_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `T_Pets_Project` (`project_id`),
  CONSTRAINT `T_Pets_UtilityResult_ibfk_2` FOREIGN KEY (`createMember_Id`) REFERENCES `T_Pets_Member` (`id`),
  CONSTRAINT `T_Pets_UtilityResult_ibfk_3` FOREIGN KEY (`updateMember_Id`) REFERENCES `T_Pets_Member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Temporary view structure for view `V_Pets_ProjectJobList`
--


DROP View IF EXISTS `PetsService`.`V_Pets_ProjectList`;

create view `PetsService`.`V_Pets_ProjectList` as
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
as projectlist ;

DROP View IF EXISTS `PetsService`.`V_Pets_ProjectJobList`;

create view `PetsService`.`V_Pets_ProjectJobList` as
select tpjs.project_id,tpp.project_name,tpp.project_eng,'主系統' as project_env,tpjs.jobname,
tpjs.percentage,tpjs.logcontent,tpm.useraccount,tpjs.createtime,tpjs.updatetime,
 TIMESTAMPDIFF(SECOND, tpjs.createtime, tpjs.updatetime) as processtime
 from `PetsService`.`T_Pets_JobSyslog` as tpjs
left join `PetsService`.`T_Pets_Project` as tpp on tpjs.project_id = tpp.project_id
left join `PetsService`.`T_Pets_Member` as tpm on tpjs.member_id=tpm.id
union all
select tpp.project_id,tpp.project_name,tpp.project_eng,'K匿名處理' as project_env,
k_app.Application_Name,k_app.Progress,k_app.App_State as logcontent,tpm.useraccount,
k_app.createtime,k_app.updatetime,
 TIMESTAMPDIFF(SECOND, k_app.createtime, k_app.updatetime) as processtime 
from `PetsService`.`T_Pets_Project` as tpp
left join `PetsService`.`T_Pets_Member` as tpm on tpp.createMember_Id=tpm.id
left join `spark_status`.`appStatus` as k_app on tpp.project_eng = k_app.dbName
where k_app.Application_Name is NOT NULL
union ALL
select tpp.project_id,tpp.project_name,tpp.project_eng,'合成資料' as project_env,
syn_gs.jobName,syn_gs.percentage,syn_gs.step as logcontent,tpm.useraccount,
syn_gs.createtime,syn_gs.updatetime,
 TIMESTAMPDIFF(SECOND, syn_gs.createtime, syn_gs.updatetime) as processtime 
from `PetsService`.`T_Pets_Project` as tpp
left join `PetsService`.`T_Pets_Member` as tpm on tpp.createMember_Id=tpm.id
left join `SynService`.`T_GANStatus` as syn_gs on tpp.project_eng =syn_gs.pro_name
where syn_gs.jobName is NOT NULL
union all
select tpp.project_id,tpp.project_name,tpp.project_eng,'差分隱私' as project_env,
dp_ps.statusname as jobname,100 as percentage,dp_ps.statusname as logcontent,tpm.useraccount,
dp_ps.createtime,dp_ps.updatetime,
 TIMESTAMPDIFF(SECOND, dp_ps.createtime, dp_ps.updatetime) as processtime 
from `PetsService`.`T_Pets_Project` as tpp
left join `PetsService`.`T_Pets_Member` as tpm on tpp.createMember_Id=tpm.id
left join `DpService`.`T_Project` as dpp on tpp.project_eng =dpp.project_name
left join `DpService`.`T_ProjectStatus`  as dp_ps on dpp.project_id =dp_ps.project_id
where dp_ps.statusname is NOT NULL;

/*!50001 DROP VIEW IF EXISTS `V_Pets_ProjectList`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `V_Pets_ProjectList` AS SELECT 
 1 AS `row_num`,
 1 AS `project_id`,
 1 AS `project_name`,
 1 AS `project_eng`,
 1 AS `project_desc`,
 1 AS `createtime`,
 1 AS `updatetime`,
 1 AS `enc_key`,
 1 AS `join_func`,
 1 AS `group_id`,
 1 AS `createMember_Id`,
 1 AS `updateMember_Id`,
 1 AS `jointablename`,
 1 AS `jointablecount`,
 1 AS `aes_col`,
 1 AS `join_sampledata`,
 1 AS `project_status`,
 1 AS `project_statusname`,
 1 AS `project_roleid`,
 1 AS `rolemember_id`,
 1 AS `useraccount`,
 1 AS `username`,
 1 AS `project_role`,
 1 AS `project_joinfuncid`,
 1 AS `left_group_id`,
 1 AS `left_dataset`,
 1 AS `left_col`,
 1 AS `right_group_id`,
 1 AS `right_dataset`,
 1 AS `right_col`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `V_Pets_ProjectJobList`
--

/*!50001 DROP VIEW IF EXISTS `V_Pets_ProjectJobList`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `V_Pets_ProjectJobList` AS select row_number() over ( order by `projectjoblist`.`project_id`) AS `row_num`,`projectjoblist`.`project_id` AS `project_id`,`projectjoblist`.`project_name` AS `project_name`,`projectjoblist`.`project_eng` AS `project_eng`,`projectjoblist`.`project_env` AS `project_env`,`projectjoblist`.`jobname` AS `jobname`,`projectjoblist`.`percentage` AS `percentage`,`projectjoblist`.`logcontent` AS `logcontent`,`projectjoblist`.`useraccount` AS `useraccount`,`projectjoblist`.`createtime` AS `createtime`,`projectjoblist`.`updatetime` AS `updatetime`,`projectjoblist`.`processtime` AS `processtime` from (select `tpjs`.`project_id` AS `project_id`,`tpp`.`project_name` AS `project_name`,`tpp`.`project_eng` AS `project_eng`,'主系統' AS `project_env`,`tpjs`.`jobname` AS `jobname`,`tpjs`.`percentage` AS `percentage`,`tpjs`.`logcontent` AS `logcontent`,`tpm`.`useraccount` AS `useraccount`,`tpjs`.`createtime` AS `createtime`,`tpjs`.`updatetime` AS `updatetime`,timestampdiff(SECOND,`tpjs`.`createtime`,`tpjs`.`updatetime`) AS `processtime` from ((`PetsService`.`T_Pets_JobSyslog` `tpjs` left join `PetsService`.`T_Pets_Project` `tpp` on(`tpjs`.`project_id` = `tpp`.`project_id`)) left join `PetsService`.`T_Pets_Member` `tpm` on(`tpjs`.`member_id` = `tpm`.`id`)) union all select `tpp`.`project_id` AS `project_id`,`tpp`.`project_name` AS `project_name`,`tpp`.`project_eng` AS `project_eng`,'K匿名處理' AS `project_env`,`k_app`.`Application_Name` AS `Application_Name`,`k_app`.`Progress` AS `Progress`,`k_app`.`App_State` AS `logcontent`,`tpm`.`useraccount` AS `useraccount`,`k_app`.`createtime` AS `createtime`,`k_app`.`updatetime` AS `updatetime`,timestampdiff(SECOND,`k_app`.`createtime`,`k_app`.`updatetime`) AS `processtime` from ((`PetsService`.`T_Pets_Project` `tpp` left join `PetsService`.`T_Pets_Member` `tpm` on(`tpp`.`createMember_Id` = `tpm`.`id`)) left join `spark_status`.`appStatus` `k_app` on(`tpp`.`project_eng` = `k_app`.`dbName`)) where `k_app`.`Application_Name` is not null union all select `tpp`.`project_id` AS `project_id`,`tpp`.`project_name` AS `project_name`,`tpp`.`project_eng` AS `project_eng`,'合成資料' AS `project_env`,`syn_gs`.`jobName` AS `jobName`,`syn_gs`.`percentage` AS `percentage`,`syn_gs`.`step` AS `logcontent`,`tpm`.`useraccount` AS `useraccount`,`syn_gs`.`createtime` AS `createtime`,`syn_gs`.`updatetime` AS `updatetime`,timestampdiff(SECOND,`syn_gs`.`createtime`,`syn_gs`.`updatetime`) AS `processtime` from ((`PetsService`.`T_Pets_Project` `tpp` left join `PetsService`.`T_Pets_Member` `tpm` on(`tpp`.`createMember_Id` = `tpm`.`id`)) left join `SynService`.`T_GANStatus` `syn_gs` on(`tpp`.`project_eng` = `syn_gs`.`pro_name`)) where `syn_gs`.`jobName` is not null union all select `tpp`.`project_id` AS `project_id`,`tpp`.`project_name` AS `project_name`,`tpp`.`project_eng` AS `project_eng`,'差分隱私' AS `project_env`,`dp_ps`.`statusname` AS `jobname`,100 AS `percentage`,`dp_ps`.`statusname` AS `logcontent`,`tpm`.`useraccount` AS `useraccount`,`dp_ps`.`createtime` AS `createtime`,`dp_ps`.`updatetime` AS `updatetime`,timestampdiff(SECOND,`dp_ps`.`createtime`,`dp_ps`.`updatetime`) AS `processtime` from (((`PetsService`.`T_Pets_Project` `tpp` left join `PetsService`.`T_Pets_Member` `tpm` on(`tpp`.`createMember_Id` = `tpm`.`id`)) left join `DpService`.`T_Project` `dpp` on(`tpp`.`project_eng` = `dpp`.`project_name`)) left join `DpService`.`T_ProjectStatus` `dp_ps` on(`dpp`.`project_id` = `dp_ps`.`project_id`)) where `dp_ps`.`statusname` is not null) `projectjoblist` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `V_Pets_ProjectList`
--

/*!50001 DROP VIEW IF EXISTS `V_Pets_ProjectList`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `V_Pets_ProjectList` AS select `projectlist`.`row_num` AS `row_num`,`projectlist`.`project_id` AS `project_id`,`projectlist`.`project_name` AS `project_name`,`projectlist`.`project_eng` AS `project_eng`,`projectlist`.`project_desc` AS `project_desc`,`projectlist`.`createtime` AS `createtime`,`projectlist`.`updatetime` AS `updatetime`,`projectlist`.`enc_key` AS `enc_key`,`projectlist`.`join_func` AS `join_func`,`projectlist`.`group_id` AS `group_id`,`projectlist`.`createMember_Id` AS `createMember_Id`,`projectlist`.`updateMember_Id` AS `updateMember_Id`,`projectlist`.`jointablename` AS `jointablename`,`projectlist`.`jointablecount` AS `jointablecount`,`projectlist`.`aes_col` AS `aes_col`,`projectlist`.`join_sampledata` AS `join_sampledata`,`projectlist`.`project_status` AS `project_status`,`projectlist`.`project_statusname` AS `project_statusname`,`projectlist`.`project_roleid` AS `project_roleid`,`projectlist`.`rolemember_id` AS `rolemember_id`,`projectlist`.`useraccount` AS `useraccount`,`projectlist`.`username` AS `username`,`projectlist`.`project_role` AS `project_role`,`projectlist`.`project_joinfuncid` AS `project_joinfuncid`,`projectlist`.`left_group_id` AS `left_group_id`,`projectlist`.`left_dataset` AS `left_dataset`,`projectlist`.`left_col` AS `left_col`,`projectlist`.`right_group_id` AS `right_group_id`,`projectlist`.`right_dataset` AS `right_dataset`,`projectlist`.`right_col` AS `right_col` from (select row_number() over ( order by `tp`.`project_id`) AS `row_num`,`tp`.`project_id` AS `project_id`,`tp`.`project_name` AS `project_name`,`tp`.`project_eng` AS `project_eng`,`tp`.`project_desc` AS `project_desc`,`tp`.`createtime` AS `createtime`,`tp`.`updatetime` AS `updatetime`,`tp`.`enc_key` AS `enc_key`,`tp`.`join_func` AS `join_func`,`tp`.`group_id` AS `group_id`,`tp`.`createMember_Id` AS `createMember_Id`,`tp`.`updateMember_Id` AS `updateMember_Id`,`tp`.`jointablename` AS `jointablename`,`tp`.`jointablecount` AS `jointablecount`,`tp`.`aes_col` AS `aes_col`,`tp`.`join_sampledata` AS `join_sampledata`,`tps`.`project_status` AS `project_status`,case `tps`.`project_status` when 0 then '建立專案及設定' when 1 then '資料匯入及鏈結設定檢查' when 2 then '安全資料鏈結處理' when 3 then '安全資料鏈結處理中' when 4 then '隱私安全服務強化處理' when 5 then '產生隱私安全強化資料' when 6 then '感興趣欄位選擇' when 7 then '可用性分析處理中' end AS `project_statusname`,`tpmr`.`id` AS `project_roleid`,`tpmr`.`member_id` AS `rolemember_id`,`tpmr`.`useraccount` AS `useraccount`,`tpmr`.`username` AS `username`,`tpmr`.`project_role` AS `project_role`,`tpjf`.`Id` AS `project_joinfuncid`,`tpjf`.`left_group_id` AS `left_group_id`,`tpjf`.`left_dataset` AS `left_dataset`,`tpjf`.`left_col` AS `left_col`,`tpjf`.`right_group_id` AS `right_group_id`,`tpjf`.`right_dataset` AS `right_dataset`,`tpjf`.`right_col` AS `right_col` from (((`PetsService`.`T_Pets_Project` `tp` join `PetsService`.`T_Pets_ProjectStatus` `tps` on(`tp`.`project_id` = `tps`.`project_id`)) left join (select `tpmr`.`id` AS `id`,`tpmr`.`project_role` AS `project_role`,`tpmr`.`project_id` AS `project_id`,`tpmr`.`member_id` AS `member_id`,`tpmr`.`createtime` AS `createtime`,`tpmr`.`updatetime` AS `updatetime`,`tpmr`.`createmember_id` AS `createmember_id`,`tpmr`.`updatemember_id` AS `updatemember_id`,`tpm`.`useraccount` AS `useraccount`,`tpm`.`username` AS `username` from (`PetsService`.`T_Pets_MemberProjectRole` `tpmr` join `PetsService`.`T_Pets_Member` `tpm` on(`tpmr`.`member_id` = `tpm`.`id`))) `tpmr` on(`tp`.`project_id` = `tpmr`.`project_id`)) left join `PetsService`.`T_Pets_ProjectJoinFunc` `tpjf` on(`tp`.`project_id` = `tpjf`.`project_id`))) `projectlist` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-03-20 21:09:12
