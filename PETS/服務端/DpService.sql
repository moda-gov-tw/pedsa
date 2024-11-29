DROP DATABASE IF EXISTS DpService;
CREATE DATABASE  IF NOT EXISTS `DpService` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `DpService`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 34.81.71.21    Database: DpService
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
-- Table structure for table `T_CeleryStatus`
--

DROP TABLE IF EXISTS `T_CeleryStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_CeleryStatus` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `pro_name` varchar(255) NOT NULL,
  `step` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `return_result` text NOT NULL,
  `log` text NOT NULL,
  `isRead` int(11) DEFAULT 0,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Dept`
--

DROP TABLE IF EXISTS `T_Dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Dept` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(100) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_GANStatus`
--

DROP TABLE IF EXISTS `T_GANStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_GANStatus` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `pro_name` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `jobName` varchar(255) NOT NULL,
  `step` varchar(255) NOT NULL,
  `percentage` int(11) DEFAULT NULL,
  `isRead` int(11) DEFAULT 0,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Member`
--

DROP TABLE IF EXISTS `T_Member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Member` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `useraccount` varchar(100) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `dept_id` int(11) NOT NULL,
  `isAdmin` tinyint(1) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Member`
--

LOCK TABLES `T_Member` WRITE;
/*!40000 ALTER TABLE `T_Member` DISABLE KEYS */;
INSERT INTO `T_Member` VALUES (1,'deidadmin',NULL,'citcw200',NULL,1,1,'2023-12-18 12:53:28',NULL);
/*!40000 ALTER TABLE `T_Member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Pro_DistinctTB`
--

DROP TABLE IF EXISTS `T_Pro_DistinctTB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Pro_DistinctTB` (
  `pdis_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `pro_db` varchar(100) NOT NULL,
  `pro_tb` varchar(100) NOT NULL,
  `pro_col` varchar(100) NOT NULL,
  `pro_discol_count` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`pdis_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Project`
--

DROP TABLE IF EXISTS `T_Project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Project` (
  `project_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(255) NOT NULL,
  `project_cht` varchar(255) DEFAULT NULL,
  `project_desc` longtext DEFAULT NULL,
  `project_path` longtext DEFAULT NULL,
  `export_path` longtext DEFAULT NULL,
  `projectowner_id` int(11) NOT NULL,
  `risk_rdata` varchar(100) DEFAULT NULL,
  `r1_data` varchar(100) DEFAULT NULL,
  `r2_data` varchar(100) DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `ftaskid` int(11) DEFAULT NULL,
  `sectaskid` int(11) DEFAULT NULL,
  `dp_id` int(11) DEFAULT NULL,
  `downloadpath` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_ProjectColumnType`
--

DROP TABLE IF EXISTS `T_ProjectColumnType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_ProjectColumnType` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `pro_name` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `pro_col_en` longtext DEFAULT NULL,
  `pro_col_cht` longtext DEFAULT NULL,
  `tableCount` int(11) DEFAULT NULL,
  `ob_col` longtext DEFAULT NULL,
  `ID_column` longtext DEFAULT NULL,
  `pro_col_en_nunique` longtext DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `selectcol` longtext DEFAULT NULL,
  `selectcolvalue` longtext DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_ProjectGetFolder`
--

DROP TABLE IF EXISTS `T_ProjectGetFolder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_ProjectGetFolder` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `pro_name` varchar(255) NOT NULL,
  `csvdata` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `T_ProjectJobStatus`
--

DROP TABLE IF EXISTS `T_ProjectJobStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_ProjectJobStatus` (
  `pjs_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `project_jobstatus` int(11) NOT NULL,
  `jobname` varchar(255) NOT NULL,
  `job_tb` varchar(255) DEFAULT NULL,
  `jobrule` varchar(255) DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`pjs_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_ProjectSample5Data`
--

DROP TABLE IF EXISTS `T_ProjectSample5Data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_ProjectSample5Data` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `pro_name` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `data` longtext NOT NULL,
  `select_data` longtext DEFAULT NULL,
  `select_colNames` longtext DEFAULT NULL,
  `targetCols` longtext DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_ProjectSampleData`
--

DROP TABLE IF EXISTS `T_ProjectSampleData`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_ProjectSampleData` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `dbname` varchar(255) NOT NULL,
  `tbname` varchar(255) NOT NULL,
  `data` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_ProjectStatus`
--

DROP TABLE IF EXISTS `T_ProjectStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_ProjectStatus` (
  `ps_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `project_status` int(11) NOT NULL,
  `statusname` varchar(255) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`ps_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Project_FinalTable`
--

DROP TABLE IF EXISTS `T_Project_FinalTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Project_FinalTable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(100) NOT NULL,
  `proj_id` int(11) NOT NULL,
  `process` varchar(100) NOT NULL,
  `jobName` varchar(255) NOT NULL,
  `rawTblName` varchar(100) NOT NULL,
  `genTblName` varchar(100) NOT NULL,
  `k_checkTblName` varchar(100) DEFAULT NULL,
  `joinTblName` varchar(100) DEFAULT NULL,
  `unionTblName` varchar(100) DEFAULT NULL,
  `joinUnionSupRate` varchar(100) DEFAULT NULL,
  `joinUnionSupCount` int(11) DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Project_NumStatValue`
--

DROP TABLE IF EXISTS `T_Project_NumStatValue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Project_NumStatValue` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `proj_id` int(11) NOT NULL,
  `proj_db` varchar(100) NOT NULL,
  `proj_table` varchar(100) NOT NULL,
  `statValue` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Project_SampleTable`
--

DROP TABLE IF EXISTS `T_Project_SampleTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Project_SampleTable` (
  `ps_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `pro_db` varchar(100) NOT NULL,
  `pro_tb` varchar(100) NOT NULL,
  `pro_col_en` longtext DEFAULT NULL,
  `pro_col_cht` longtext DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `pro_path` varchar(255) DEFAULT NULL,
  `tableCount` int(11) DEFAULT NULL,
  `tableDisCount` int(11) DEFAULT NULL,
  `minKvalue` int(11) DEFAULT NULL,
  `supRate` varchar(100) DEFAULT NULL,
  `supCount` int(11) DEFAULT NULL,
  `finaltblName` varchar(255) DEFAULT NULL,
  `after_col_en` longtext DEFAULT NULL,
  `after_col_cht` longtext DEFAULT NULL,
  `qi_col` longtext DEFAULT NULL,
  `tablekeycol` longtext DEFAULT NULL,
  `after_col_value` varchar(255) DEFAULT NULL,
  `gen_qi_settingvalue` longtext DEFAULT NULL,
  `warning_col` longtext DEFAULT NULL,
  PRIMARY KEY (`ps_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `T_Project_SparkStatus_Management`
--

DROP TABLE IF EXISTS `T_Project_SparkStatus_Management`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Project_SparkStatus_Management` (
  `pspark_id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` varchar(255) NOT NULL,
  `celery_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `step` varchar(100) DEFAULT NULL,
  `stepstatus` int(1) DEFAULT NULL,
  PRIMARY KEY (`pspark_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_Project_SysStep_Config`
--

DROP TABLE IF EXISTS `T_Project_SysStep_Config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_Project_SysStep_Config` (
  `psys_id` int(11) NOT NULL AUTO_INCREMENT,
  `pro_status` int(11) NOT NULL,
  `pro_status_config` text NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  PRIMARY KEY (`psys_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_SystemSetting`
--

DROP TABLE IF EXISTS `T_SystemSetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_SystemSetting` (
  `sys_id` int(11) NOT NULL AUTO_INCREMENT,
  `kdata` varchar(100) DEFAULT NULL,
  `ldata` varchar(100) DEFAULT NULL,
  `rdata` varchar(100) DEFAULT NULL,
  `dfprojowner` int(255) DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime NOT NULL,
  PRIMARY KEY (`sys_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `T_originTable`
--

DROP TABLE IF EXISTS `T_originTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_originTable` (
  `tbl_id` int(11) NOT NULL AUTO_INCREMENT,
  `tableName` varchar(255) DEFAULT NULL,
  `tableCount` int(11) DEFAULT NULL,
  `sample` longtext DEFAULT NULL,
  `col_en` longtext DEFAULT NULL,
  `col_cht` longtext DEFAULT NULL,
  `project` varchar(255) DEFAULT NULL,
  `member` varchar(255) DEFAULT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`tbl_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `T_utilityResult`
--

DROP TABLE IF EXISTS `T_utilityResult`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `T_utilityResult` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `target_col` varchar(255) NOT NULL,
  `select_csv` varchar(255) NOT NULL,
  `model` varchar(255) NOT NULL,
  `MLresult` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-03-20 21:28:51
