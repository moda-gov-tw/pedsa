-- MySQL dump 10.17  Distrib 10.3.21-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: DpService
-- ------------------------------------------------------
-- Server version	10.3.21-MariaDB-1:10.3.21+maria~bionic

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `T_CeleryStatus`
--

DROP DATABASE IF EXISTS DpService;
CREATE DATABASE  IF NOT EXISTS `DpService` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `DpService`;

DROP TABLE IF EXISTS `T_CeleryStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=152 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_CeleryStatus`
--

LOCK TABLES `T_CeleryStatus` WRITE;
/*!40000 ALTER TABLE `T_CeleryStatus` DISABLE KEYS */;
INSERT INTO `T_CeleryStatus` VALUES (144,'1',84,'test07181','createFolder','','Mission Complete','WyIvYXBwL2FwcC9kZXZwL0FQSS9sb2dnaW5nX3NldHRpbmcucHk6MTM6IFlBTUxMb2FkV2FybmluZzogY2FsbGluZyB5YW1sLmxvYWQoKSB3aXRob3V0IExvYWRlcj0uLi4gaXMgZGVwcmVjYXRlZCwgYXMgdGhlIGRlZmF1bHQgTG9hZGVyIGlzIHVuc2FmZS4gUGxlYXNlIHJlYWQgaHR0cHM6Ly9tc2cucHl5YW1sLm9yZy9sb2FkIGZvciBmdWxsIGRldGFpbHMuXG4iLCAiICBjb25maWcgPSB5YW1sLmxvYWQoZilcbiJd',0,'2024-07-19 09:23:05',NULL),(145,'1',84,'test07181','DP','test07181_inner.csv','','WyIvYXBwL2FwcC9kZXZwL3N5bl9nZW4vbG9nZ2luZ19zZXR0aW5nLnB5OjEzOiBZQU1MTG9hZFdhcm5pbmc6IGNhbGxpbmcgeWFtbC5sb2FkKCkgd2l0aG91dCBMb2FkZXI9Li4uIGlzIGRlcHJlY2F0ZWQsIGFzIHRoZSBkZWZhdWx0IExvYWRlciBpcyB1bnNhZmUuIFBsZWFzZSByZWFkIGh0dHBzOi8vbXNnLnB5eWFtbC5vcmcvbG9hZCBmb3IgZnVsbCBkZXRhaWxzLlxuIiwgIiAgY29uZmlnID0geWFtbC5sb2FkKGYpXG4iLCAiXG4iLCAiV0FSTklORzogYXB0IGRvZXMgbm90IGhhdmUgYSBzdGFibGUgQ0xJIGludGVyZmFjZS4gVXNlIHdpdGggY2F1dGlvbiBpbiBzY3JpcHRzLlxuIiwgIlxuIl0=',0,'2024-07-19 09:27:03',NULL),(146,'1',84,'test07181','MLutility','test07181_inner.csv',',statistic,Mission Complete','WyIvYXBwL2FwcC9kZXZwL0FQSS9sb2dnaW5nX3NldHRpbmcucHk6MTM6IFlBTUxMb2FkV2FybmluZzogY2FsbGluZyB5YW1sLmxvYWQoKSB3aXRob3V0IExvYWRlcj0uLi4gaXMgZGVwcmVjYXRlZCwgYXMgdGhlIGRlZmF1bHQgTG9hZGVyIGlzIHVuc2FmZS4gUGxlYXNlIHJlYWQgaHR0cHM6Ly9tc2cucHl5YW1sLm9yZy9sb2FkIGZvciBmdWxsIGRldGFpbHMuXG4iLCAiICBjb25maWcgPSB5YW1sLmxvYWQoZilcbiIsICItLS0gTG9nZ2luZyBlcnJvciAtLS1cbiIsICJUcmFjZWJhY2sgKG1vc3QgcmVjZW50IGNhbGwgbGFzdCk6XG4iLCAiICBGaWxlIFwiL3Vzci9saWIvcHl0aG9uMy42L2xvZ2dpbmcvaGFuZGxlcnMucHlcIiwgbGluZSA3MSwgaW4gZW1pdFxuIiwgIiAgICBpZiBzZWxmLnNob3VsZFJvbGxvdmVyKHJlY29yZCk6XG4iLCAiICBGaWxlIFwiL3Vzci9saWIvcHl0aG9uMy42L2xvZ2dpbmcvaGFuZGxlcnMucHlcIiwgbGluZSAxODcsIGluIHNob3VsZFJvbGxvdmVyXG4iLCAiICAgIG1zZyA9IFwiJXNcXG5cIiAlIHNlbGYuZm9ybWF0KHJlY29yZClcbiIsICIgIEZpbGUgXCIvdXNyL2xpYi9weXRob24zLjYvbG9nZ2luZy9fX2luaXRfXy5weVwiLCBsaW5lIDg0MCwgaW4gZm9ybWF0XG4iLCAiICAgIHJldHVybiBmbXQuZm9ybWF0KHJlY29yZClcbiIsICIgIEZpbGUgXCIvdXNyL2xpYi9weXRob24zLjYvbG9nZ2luZy9fX2luaXRfXy5weVwiLCBsaW5lIDU3NywgaW4gZm9ybWF0XG4iLCAiICAgIHJlY29yZC5tZXNzYWdlID0gcmVjb3JkLmdldE1lc3NhZ2UoKVxuIiwgIiAgRmlsZSBcIi91c3IvbGliL3B5dGhvbjMuNi9sb2dnaW5nL19faW5pdF9fLnB5XCIsIGxpbmUgMzM4LCBpbiBnZXRNZXNzYWdlXG4iLCAiICAgIG1zZyA9IG1zZyAlIHNlbGYuYXJnc1xuIiwgIlR5cGVFcnJvcjogbm90IGFsbCBhcmd1bWVudHMgY29udmVydGVkIGR1cmluZyBzdHJpbmcgZm9ybWF0dGluZ1xuIiwgIkNhbGwgc3RhY2s6XG4iLCAiICBGaWxlIFwiL2FwcC9hcHAvZGV2cC9BUEkvc3RhdGlzdGljVXRpbGl0eS5weVwiLCBsaW5lIDM2NiwgaW4gPG1vZHVsZT5cbiIsICIgICAgbWFpbigpXG4iLCAiICBGaWxlIFwiL2FwcC9hcHAvZGV2cC9BUEkvc3RhdGlzdGljVXRpbGl0eS5weVwiLCBsaW5lIDI4MywgaW4gbWFpblxuIiwgIiAgICBfdmxvZ2dlci5kZWJ1ZyhcIiMjIyMjIyMjIyMjIyMjUkFXRElSLCBcIixkZi5oZWFkKDIpLnRvX2RpY3Qob3JpZW50PSdyZWNvcmRzJykpXG4iLCAiTWVzc2FnZTogJyMjIyMjIyMjIyMjIyMjUkFXRElSLCAnXG4iLCAiQXJndW1lbnRzOiAoW3snd29ya2NsYXNzX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiAnU3RhdGUtZ292JywgJ21hcml0YWxfc3RhdHVzX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiAnTmV2ZXItbWFycmllZCcsICdvY2N1cGF0aW9uX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiAnQWRtLWNsZXJpY2FsJ30sIHsnd29ya2NsYXNzX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiAnU2VsZi1lbXAtbm90LWluYycsICdtYXJpdGFsX3N0YXR1c19zeXNfcGVyc29uYWxfZmluYW5jaWFsJzogJ01hcnJpZWQtY2l2LXNwb3VzZScsICdvY2N1cGF0aW9uX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiAnRXhlYy1tYW5hZ2VyaWFsJ31dLClcbiIsICItLS0gTG9nZ2luZyBlcnJvciAtLS1cbiIsICJUcmFjZWJhY2sgKG1vc3QgcmVjZW50IGNhbGwgbGFzdCk6XG4iLCAiICBGaWxlIFwiL3Vzci9saWIvcHl0aG9uMy42L2xvZ2dpbmcvX19pbml0X18ucHlcIiwgbGluZSA5OTQsIGluIGVtaXRcbiIsICIgICAgbXNnID0gc2VsZi5mb3JtYXQocmVjb3JkKVxuIiwgIiAgRmlsZSBcIi91c3IvbGliL3B5dGhvbjMuNi9sb2dnaW5nL19faW5pdF9fLnB5XCIsIGxpbmUgODQwLCBpbiBmb3JtYXRcbiIsICIgICAgcmV0dXJuIGZtdC5mb3JtYXQocmVjb3JkKVxuIiwgIiAgRmlsZSBcIi91c3IvbGliL3B5dGhvbjMuNi9sb2dnaW5nL19faW5pdF9fLnB5XCIsIGxpbmUgNTc3LCBpbiBmb3JtYXRcbiIsICIgICAgcmVjb3JkLm1lc3NhZ2UgPSByZWNvcmQuZ2V0TWVzc2FnZSgpXG4iLCAiICBGaWxlIFwiL3Vzci9saWIvcHl0aG9uMy42L2xvZ2dpbmcvX19pbml0X18ucHlcIiwgbGluZSAzMzgsIGluIGdldE1lc3NhZ2VcbiIsICIgICAgbXNnID0gbXNnICUgc2VsZi5hcmdzXG4iLCAiVHlwZUVycm9yOiBub3QgYWxsIGFyZ3VtZW50cyBjb252ZXJ0ZWQgZHVyaW5nIHN0cmluZyBmb3JtYXR0aW5nXG4iLCAiQ2FsbCBzdGFjazpcbiIsICIgIEZpbGUgXCIvYXBwL2FwcC9kZXZwL0FQSS9zdGF0aXN0aWNVdGlsaXR5LnB5XCIsIGxpbmUgMzY2LCBpbiA8bW9kdWxlPlxuIiwgIiAgICBtYWluKClcbiIsICIgIEZpbGUgXCIvYXBwL2FwcC9kZXZwL0FQSS9zdGF0aXN0aWNVdGlsaXR5LnB5XCIsIGxpbmUgMjgzLCBpbiBtYWluXG4iLCAiICAgIF92bG9nZ2VyLmRlYnVnKFwiIyMjIyMjIyMjIyMjIyNSQVdESVIsIFwiLGRmLmhlYWQoMikudG9fZGljdChvcmllbnQ9J3JlY29yZHMnKSlcbiIsICJNZXNzYWdlOiAnIyMjIyMjIyMjIyMjIyNSQVdESVIsICdcbiIsICJBcmd1bWVudHM6IChbeyd3b3JrY2xhc3Nfc3lzX3BlcnNvbmFsX2ZpbmFuY2lhbCc6ICdTdGF0ZS1nb3YnLCAnbWFyaXRhbF9zdGF0dXNfc3lzX3BlcnNvbmFsX2ZpbmFuY2lhbCc6ICdOZXZlci1tYXJyaWVkJywgJ29jY3VwYXRpb25fc3lzX3BlcnNvbmFsX2ZpbmFuY2lhbCc6ICdBZG0tY2xlcmljYWwnfSwgeyd3b3JrY2xhc3Nfc3lzX3BlcnNvbmFsX2ZpbmFuY2lhbCc6ICdTZWxmLWVtcC1ub3QtaW5jJywgJ21hcml0YWxfc3RhdHVzX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiAnTWFycmllZC1jaXYtc3BvdXNlJywgJ29jY3VwYXRpb25fc3lzX3BlcnNvbmFsX2ZpbmFuY2lhbCc6ICdFeGVjLW1hbmFnZXJpYWwnfV0sKVxuIl0=',0,'2024-07-19 09:27:18',NULL),(147,'1',85,'test08091','createFolder','','Mission Complete','WyIvYXBwL2FwcC9kZXZwL0FQSS9sb2dnaW5nX3NldHRpbmcucHk6MTM6IFlBTUxMb2FkV2FybmluZzogY2FsbGluZyB5YW1sLmxvYWQoKSB3aXRob3V0IExvYWRlcj0uLi4gaXMgZGVwcmVjYXRlZCwgYXMgdGhlIGRlZmF1bHQgTG9hZGVyIGlzIHVuc2FmZS4gUGxlYXNlIHJlYWQgaHR0cHM6Ly9tc2cucHl5YW1sLm9yZy9sb2FkIGZvciBmdWxsIGRldGFpbHMuXG4iLCAiICBjb25maWcgPSB5YW1sLmxvYWQoZilcbiJd',0,'2024-08-09 20:33:35',NULL),(148,'1',85,'test08091','DP','test08091_single.csv','','WyIvYXBwL2FwcC9kZXZwL3N5bl9nZW4vbG9nZ2luZ19zZXR0aW5nLnB5OjEzOiBZQU1MTG9hZFdhcm5pbmc6IGNhbGxpbmcgeWFtbC5sb2FkKCkgd2l0aG91dCBMb2FkZXI9Li4uIGlzIGRlcHJlY2F0ZWQsIGFzIHRoZSBkZWZhdWx0IExvYWRlciBpcyB1bnNhZmUuIFBsZWFzZSByZWFkIGh0dHBzOi8vbXNnLnB5eWFtbC5vcmcvbG9hZCBmb3IgZnVsbCBkZXRhaWxzLlxuIiwgIiAgY29uZmlnID0geWFtbC5sb2FkKGYpXG4iLCAiXG4iLCAiV0FSTklORzogYXB0IGRvZXMgbm90IGhhdmUgYSBzdGFibGUgQ0xJIGludGVyZmFjZS4gVXNlIHdpdGggY2F1dGlvbiBpbiBzY3JpcHRzLlxuIiwgIlxuIiwgImRlYmNvbmY6IHVuYWJsZSB0byBpbml0aWFsaXplIGZyb250ZW5kOiBEaWFsb2dcbiIsICJkZWJjb25mOiAoVEVSTSBpcyBub3Qgc2V0LCBzbyB0aGUgZGlhbG9nIGZyb250ZW5kIGlzIG5vdCB1c2FibGUuKVxuIiwgImRlYmNvbmY6IGZhbGxpbmcgYmFjayB0byBmcm9udGVuZDogUmVhZGxpbmVcbiIsICJkZWJjb25mOiB1bmFibGUgdG8gaW5pdGlhbGl6ZSBmcm9udGVuZDogUmVhZGxpbmVcbiIsICJkZWJjb25mOiAoVGhpcyBmcm9udGVuZCByZXF1aXJlcyBhIGNvbnRyb2xsaW5nIHR0eS4pXG4iLCAiZGViY29uZjogZmFsbGluZyBiYWNrIHRvIGZyb250ZW5kOiBUZWxldHlwZVxuIiwgImRwa2ctcHJlY29uZmlndXJlOiB1bmFibGUgdG8gcmUtb3BlbiBzdGRpbjogXG4iLCAiV2FybmluZzogUGVybWFuZW50bHkgYWRkZWQgJzE2OC4xNy44LjI1MicgKEVDRFNBKSB0byB0aGUgbGlzdCBvZiBrbm93biBob3N0cy5cclxuIl0=',0,'2024-08-14 13:36:50',NULL),(149,'1',86,'test08151','createFolder','','Mission Complete','WyIvYXBwL2FwcC9kZXZwL0FQSS9sb2dnaW5nX3NldHRpbmcucHk6MTM6IFlBTUxMb2FkV2FybmluZzogY2FsbGluZyB5YW1sLmxvYWQoKSB3aXRob3V0IExvYWRlcj0uLi4gaXMgZGVwcmVjYXRlZCwgYXMgdGhlIGRlZmF1bHQgTG9hZGVyIGlzIHVuc2FmZS4gUGxlYXNlIHJlYWQgaHR0cHM6Ly9tc2cucHl5YW1sLm9yZy9sb2FkIGZvciBmdWxsIGRldGFpbHMuXG4iLCAiICBjb25maWcgPSB5YW1sLmxvYWQoZilcbiJd',0,'2024-08-15 08:21:49',NULL),(150,'1',86,'test08151','DP','test08151_single.csv','','WyIvYXBwL2FwcC9kZXZwL3N5bl9nZW4vbG9nZ2luZ19zZXR0aW5nLnB5OjEzOiBZQU1MTG9hZFdhcm5pbmc6IGNhbGxpbmcgeWFtbC5sb2FkKCkgd2l0aG91dCBMb2FkZXI9Li4uIGlzIGRlcHJlY2F0ZWQsIGFzIHRoZSBkZWZhdWx0IExvYWRlciBpcyB1bnNhZmUuIFBsZWFzZSByZWFkIGh0dHBzOi8vbXNnLnB5eWFtbC5vcmcvbG9hZCBmb3IgZnVsbCBkZXRhaWxzLlxuIiwgIiAgY29uZmlnID0geWFtbC5sb2FkKGYpXG4iLCAiXG4iLCAiV0FSTklORzogYXB0IGRvZXMgbm90IGhhdmUgYSBzdGFibGUgQ0xJIGludGVyZmFjZS4gVXNlIHdpdGggY2F1dGlvbiBpbiBzY3JpcHRzLlxuIiwgIlxuIl0=',0,'2024-08-15 08:28:43',NULL),(151,'1',87,'test08191','createFolder','','Mission Complete','WyIvYXBwL2FwcC9kZXZwL0FQSS9sb2dnaW5nX3NldHRpbmcucHk6MTM6IFlBTUxMb2FkV2FybmluZzogY2FsbGluZyB5YW1sLmxvYWQoKSB3aXRob3V0IExvYWRlcj0uLi4gaXMgZGVwcmVjYXRlZCwgYXMgdGhlIGRlZmF1bHQgTG9hZGVyIGlzIHVuc2FmZS4gUGxlYXNlIHJlYWQgaHR0cHM6Ly9tc2cucHl5YW1sLm9yZy9sb2FkIGZvciBmdWxsIGRldGFpbHMuXG4iLCAiICBjb25maWcgPSB5YW1sLmxvYWQoZilcbiJd',0,'2024-08-19 18:57:02',NULL);
/*!40000 ALTER TABLE `T_CeleryStatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Dept`
--

DROP TABLE IF EXISTS `T_Dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `T_Dept` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(100) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Dept`
--

LOCK TABLES `T_Dept` WRITE;
/*!40000 ALTER TABLE `T_Dept` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Dept` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_GANStatus`
--

DROP TABLE IF EXISTS `T_GANStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_GANStatus`
--

LOCK TABLES `T_GANStatus` WRITE;
/*!40000 ALTER TABLE `T_GANStatus` DISABLE KEYS */;
INSERT INTO `T_GANStatus` VALUES (141,'1',84,'test07181','test07181_inner.csv','Preview','finish',100,0,'2024-07-19 09:23:05','2024-07-19 09:23:13'),(142,'1',84,'test07181','test07181_inner.csv','utility','finish',100,0,'2024-07-19 09:27:17','2024-07-19 09:27:18'),(143,'1',85,'test08091','test08091_single.csv','Preview','finish',100,0,'2024-08-09 20:33:35','2024-08-09 20:33:42'),(144,'1',85,'test08091','test08091_single.csv','utility','finish',100,0,'2024-08-14 13:37:03','2024-08-14 13:37:03'),(146,'1',86,'test08151','test08151_single.csv','utility','finish',100,0,'2024-08-15 08:29:21','2024-08-15 08:29:21'),(147,'1',87,'test08191','test08191_single.csv','Preview','Initial',0,0,'2024-08-19 18:57:02',NULL);
/*!40000 ALTER TABLE `T_GANStatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Member`
--

DROP TABLE IF EXISTS `T_Member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
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
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_Pro_DistinctTB`
--

LOCK TABLES `T_Pro_DistinctTB` WRITE;
/*!40000 ALTER TABLE `T_Pro_DistinctTB` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Pro_DistinctTB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Project`
--

DROP TABLE IF EXISTS `T_Project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  `dp_report_data` longtext DEFAULT NULL,
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_Project`
--

LOCK TABLES `T_Project` WRITE;
/*!40000 ALTER TABLE `T_Project` DISABLE KEYS */;
INSERT INTO `T_Project` VALUES (84,'test07181','test07181','test07181','test07181','test07181',1,NULL,NULL,NULL,'2024-07-19 09:22:53','2024-07-19 09:27:00',NULL,NULL,NULL,NULL,'[]'),(85,'test08091','test08091','test08091','test08091','test08091',1,NULL,NULL,NULL,'2024-08-09 20:33:34','2024-08-14 13:36:50',NULL,NULL,NULL,NULL,'[]'),(86,'test08151','test08151','test08151','test08151','test08151',1,NULL,NULL,NULL,'2024-08-15 08:21:48','2024-08-15 08:28:42',NULL,NULL,NULL,NULL,'[]'),(87,'test08191','test08191','test08191','test08191','test08191',1,NULL,NULL,NULL,'2024-08-19 18:57:02',NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `T_Project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_ProjectColumnType`
--

DROP TABLE IF EXISTS `T_ProjectColumnType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  `corr_col` longtext DEFAULT NULL,
  `choose_corr_col` longtext DEFAULT NULL,
  `epsilon` double DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_ProjectColumnType`
--

LOCK TABLES `T_ProjectColumnType` WRITE;
/*!40000 ALTER TABLE `T_ProjectColumnType` DISABLE KEYS */;
INSERT INTO `T_ProjectColumnType` VALUES (73,'1',84,'test07181','test07181_inner.csv','SEQN_sys_personal_financial,workclass_sys_personal_financial,marital_status_sys_personal_financial,occupation_sys_personal_financial,capital_gain_sys_personal_financial,capital_loss_sys_personal_financial,hours_per_week_sys_personal_financial,income_sys_personal_financial,age_sys_personal_info,fnlwgt_sys_personal_info,education_sys_personal_info,education_num_sys_personal_info,relationship_sys_personal_info,race_sys_personal_info,sex_sys_personal_info,native_country_sys_personal_info','workclass_sys_personal_financial,marital_status_sys_personal_financial,occupation_sys_personal_financial,capital_gain_sys_personal_financial,capital_loss_sys_personal_financial,hours_per_week_sys_personal_financial,income_sys_personal_financial,age_sys_personal_info,fnlwgt_sys_personal_info,education_sys_personal_info,education_num_sys_personal_info,relationship_sys_personal_info,race_sys_personal_info,sex_sys_personal_info,native_country_sys_personal_info',48842,'workclass_sys_personal_financial,marital_status_sys_personal_financial,occupation_sys_personal_financial','SEQN_sys_personal_financial','9,7,15,123,99,96,2,74,28523,16,16,6,5,2,42','2024-07-19 09:23:13','2024-07-19 09:24:39','workclass_sys_personal_financial,marital_status_sys_personal_financial,occupation_sys_personal_financial','C,C,C','workclass_sys_personal_financial^marital_status_sys_personal_financial','workclass_sys_personal_financial^marital_status_sys_personal_financial',100),(74,'1',85,'test08091','test08091_single.csv','EmployeID_sys_TP_3000,ID_sys_TP_3000,Name_sys_TP_3000,DoB_sys_TP_3000,PhoneNumber_sys_TP_3000,Email_sys_TP_3000,Sex_sys_TP_3000,Address_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000,NoOfChildren_sys_TP_3000,AddtionalIncome_sys_TP_3000,IncomePerMonth_sys_TP_3000,PoliticalSpectrum_sys_TP_3000,RandomCode_sys_TP_3000','Name_sys_TP_3000,Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000,NoOfChildren_sys_TP_3000,PoliticalSpectrum_sys_TP_3000',3000,'Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000','EmployeID_sys_TP_3000,ID_sys_TP_3000,DoB_sys_TP_3000,PhoneNumber_sys_TP_3000,Email_sys_TP_3000,Address_sys_TP_3000,AddtionalIncome_sys_TP_3000,IncomePerMonth_sys_TP_3000,RandomCode_sys_TP_3000','2230,2,3,56,31,3','2024-08-09 20:33:42','2024-08-14 13:36:46','Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000','C,C,C','Sex_sys_TP_3000^MaritalStatus_sys_TP_3000','Sex_sys_TP_3000^MaritalStatus_sys_TP_3000^Height_sys_TP_3000',100),(75,'1',86,'test08151','test08151_single.csv','EmployeID_sys_TP_3000,ID_sys_TP_3000,Name_sys_TP_3000,DoB_sys_TP_3000,PhoneNumber_sys_TP_3000,Email_sys_TP_3000,Sex_sys_TP_3000,Address_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000,NoOfChildren_sys_TP_3000,AddtionalIncome_sys_TP_3000,IncomePerMonth_sys_TP_3000,PoliticalSpectrum_sys_TP_3000,RandomCode_sys_TP_3000','Name_sys_TP_3000,Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000,NoOfChildren_sys_TP_3000,PoliticalSpectrum_sys_TP_3000',3000,'Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,NoOfChildren_sys_TP_3000','EmployeID_sys_TP_3000,ID_sys_TP_3000,DoB_sys_TP_3000,PhoneNumber_sys_TP_3000,Email_sys_TP_3000,Address_sys_TP_3000,AddtionalIncome_sys_TP_3000,IncomePerMonth_sys_TP_3000,RandomCode_sys_TP_3000','2230,2,3,56,31,3','2024-08-15 08:21:57','2024-08-15 08:28:38','Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,NoOfChildren_sys_TP_3000','C,C,C','Sex_sys_TP_3000^MaritalStatus_sys_TP_3000','Sex_sys_TP_3000^MaritalStatus_sys_TP_3000^NoOfChildren_sys_TP_3000',100);
/*!40000 ALTER TABLE `T_ProjectColumnType` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_ProjectGetFolder`
--

DROP TABLE IF EXISTS `T_ProjectGetFolder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `T_ProjectGetFolder` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `pro_name` varchar(255) NOT NULL,
  `csvdata` longtext NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_ProjectGetFolder`
--

LOCK TABLES `T_ProjectGetFolder` WRITE;
/*!40000 ALTER TABLE `T_ProjectGetFolder` DISABLE KEYS */;
INSERT INTO `T_ProjectGetFolder` VALUES (1,'1',3,'adult','Cannot find the folder named as same as projName.','2024-04-01 05:42:58','2024-04-01 05:43:15');
/*!40000 ALTER TABLE `T_ProjectGetFolder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_ProjectJobStatus`
--

DROP TABLE IF EXISTS `T_ProjectJobStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_ProjectJobStatus`
--

LOCK TABLES `T_ProjectJobStatus` WRITE;
/*!40000 ALTER TABLE `T_ProjectJobStatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_ProjectJobStatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_ProjectSample5Data`
--

DROP TABLE IF EXISTS `T_ProjectSample5Data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_ProjectSample5Data`
--

LOCK TABLES `T_ProjectSample5Data` WRITE;
/*!40000 ALTER TABLE `T_ProjectSample5Data` DISABLE KEYS */;
INSERT INTO `T_ProjectSample5Data` VALUES (73,'1',84,'test07181','test07181_inner.csv','[{\"workclass_sys_personal_financial\":\"State-gov\",\"marital_status_sys_personal_financial\":\"Never-married\",\"occupation_sys_personal_financial\":\"Adm-clerical\",\"capital_gain_sys_personal_financial\":2174,\"capital_loss_sys_personal_financial\":0,\"hours_per_week_sys_personal_financial\":40,\"income_sys_personal_financial\":\"<=28000\",\"age_sys_personal_info\":39,\"fnlwgt_sys_personal_info\":77516,\"education_sys_personal_info\":\"Bachelors\",\"education_num_sys_personal_info\":13,\"relationship_sys_personal_info\":\"Not-in-family\",\"race_sys_personal_info\":\"White\",\"sex_sys_personal_info\":\"Male\",\"native_country_sys_personal_info\":\"United-States\"},{\"workclass_sys_personal_financial\":\"Self-emp-not-inc\",\"marital_status_sys_personal_financial\":\"Married-civ-spouse\",\"occupation_sys_personal_financial\":\"Exec-managerial\",\"capital_gain_sys_personal_financial\":0,\"capital_loss_sys_personal_financial\":0,\"hours_per_week_sys_personal_financial\":13,\"income_sys_personal_financial\":\"<=28000\",\"age_sys_personal_info\":50,\"fnlwgt_sys_personal_info\":83311,\"education_sys_personal_info\":\"Bachelors\",\"education_num_sys_personal_info\":13,\"relationship_sys_personal_info\":\"Husband\",\"race_sys_personal_info\":\"White\",\"sex_sys_personal_info\":\"Male\",\"native_country_sys_personal_info\":\"United-States\"},{\"workclass_sys_personal_financial\":\"Private\",\"marital_status_sys_personal_financial\":\"Divorced\",\"occupation_sys_personal_financial\":\"Handlers-cleaners\",\"capital_gain_sys_personal_financial\":0,\"capital_loss_sys_personal_financial\":0,\"hours_per_week_sys_personal_financial\":40,\"income_sys_personal_financial\":\"<=28000\",\"age_sys_personal_info\":38,\"fnlwgt_sys_personal_info\":215646,\"education_sys_personal_info\":\"HS-grad\",\"education_num_sys_personal_info\":9,\"relationship_sys_personal_info\":\"Not-in-family\",\"race_sys_personal_info\":\"White\",\"sex_sys_personal_info\":\"Male\",\"native_country_sys_personal_info\":\"United-States\"},{\"workclass_sys_personal_financial\":\"Private\",\"marital_status_sys_personal_financial\":\"Married-civ-spouse\",\"occupation_sys_personal_financial\":\"Handlers-cleaners\",\"capital_gain_sys_personal_financial\":0,\"capital_loss_sys_personal_financial\":0,\"hours_per_week_sys_personal_financial\":40,\"income_sys_personal_financial\":\"<=28000\",\"age_sys_personal_info\":53,\"fnlwgt_sys_personal_info\":234721,\"education_sys_personal_info\":\"11th\",\"education_num_sys_personal_info\":7,\"relationship_sys_personal_info\":\"Husband\",\"race_sys_personal_info\":\"Black\",\"sex_sys_personal_info\":\"Male\",\"native_country_sys_personal_info\":\"United-States\"},{\"workclass_sys_personal_financial\":\"Private\",\"marital_status_sys_personal_financial\":\"Married-civ-spouse\",\"occupation_sys_personal_financial\":\"Prof-specialty\",\"capital_gain_sys_personal_financial\":0,\"capital_loss_sys_personal_financial\":0,\"hours_per_week_sys_personal_financial\":40,\"income_sys_personal_financial\":\"<=28000\",\"age_sys_personal_info\":28,\"fnlwgt_sys_personal_info\":338409,\"education_sys_personal_info\":\"Bachelors\",\"education_num_sys_personal_info\":13,\"relationship_sys_personal_info\":\"Wife\",\"race_sys_personal_info\":\"Black\",\"sex_sys_personal_info\":\"Female\",\"native_country_sys_personal_info\":\"Cuba\"}]',NULL,'workclass_sys_personal_financial,marital_status_sys_personal_financial,occupation_sys_personal_financial','workclass_sys_personal_financial','2024-07-19 09:23:13','2024-07-19 09:27:17'),(74,'1',85,'test08091','test08091_single.csv','[{\"Name_sys_TP_3000\":\"王羽\",\"Sex_sys_TP_3000\":\"女\",\"MaritalStatus_sys_TP_3000\":\"未提供\",\"Height_sys_TP_3000\":180,\"NoOfChildren_sys_TP_3000\":20,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"},{\"Name_sys_TP_3000\":\"鄒冠廷\",\"Sex_sys_TP_3000\":\"男\",\"MaritalStatus_sys_TP_3000\":\"未婚\",\"Height_sys_TP_3000\":200,\"NoOfChildren_sys_TP_3000\":5,\"PoliticalSpectrum_sys_TP_3000\":\"泛綠\"},{\"Name_sys_TP_3000\":\"李家瑜\",\"Sex_sys_TP_3000\":\"女\",\"MaritalStatus_sys_TP_3000\":\"未提供\",\"Height_sys_TP_3000\":199,\"NoOfChildren_sys_TP_3000\":1,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"},{\"Name_sys_TP_3000\":\"葛龍\",\"Sex_sys_TP_3000\":\"女\",\"MaritalStatus_sys_TP_3000\":\"未婚\",\"Height_sys_TP_3000\":155,\"NoOfChildren_sys_TP_3000\":25,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"},{\"Name_sys_TP_3000\":\"朱沖\",\"Sex_sys_TP_3000\":\"男\",\"MaritalStatus_sys_TP_3000\":\"已婚\",\"Height_sys_TP_3000\":156,\"NoOfChildren_sys_TP_3000\":28,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"}]',NULL,'Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,Height_sys_TP_3000','Height_sys_TP_3000','2024-08-09 20:33:42','2024-08-14 13:37:02'),(75,'1',86,'test08151','test08151_single.csv','[{\"Name_sys_TP_3000\":\"王羽\",\"Sex_sys_TP_3000\":\"女\",\"MaritalStatus_sys_TP_3000\":\"未提供\",\"Height_sys_TP_3000\":180,\"NoOfChildren_sys_TP_3000\":20,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"},{\"Name_sys_TP_3000\":\"鄒冠廷\",\"Sex_sys_TP_3000\":\"男\",\"MaritalStatus_sys_TP_3000\":\"未婚\",\"Height_sys_TP_3000\":200,\"NoOfChildren_sys_TP_3000\":5,\"PoliticalSpectrum_sys_TP_3000\":\"泛綠\"},{\"Name_sys_TP_3000\":\"李家瑜\",\"Sex_sys_TP_3000\":\"女\",\"MaritalStatus_sys_TP_3000\":\"未提供\",\"Height_sys_TP_3000\":199,\"NoOfChildren_sys_TP_3000\":1,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"},{\"Name_sys_TP_3000\":\"葛龍\",\"Sex_sys_TP_3000\":\"女\",\"MaritalStatus_sys_TP_3000\":\"未婚\",\"Height_sys_TP_3000\":155,\"NoOfChildren_sys_TP_3000\":25,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"},{\"Name_sys_TP_3000\":\"朱沖\",\"Sex_sys_TP_3000\":\"男\",\"MaritalStatus_sys_TP_3000\":\"已婚\",\"Height_sys_TP_3000\":156,\"NoOfChildren_sys_TP_3000\":28,\"PoliticalSpectrum_sys_TP_3000\":\"泛藍\"}]',NULL,'Sex_sys_TP_3000,MaritalStatus_sys_TP_3000,NoOfChildren_sys_TP_3000','NoOfChildren_sys_TP_3000','2024-08-15 08:21:57','2024-08-15 08:29:20');
/*!40000 ALTER TABLE `T_ProjectSample5Data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_ProjectSampleData`
--

DROP TABLE IF EXISTS `T_ProjectSampleData`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_ProjectSampleData`
--

LOCK TABLES `T_ProjectSampleData` WRITE;
/*!40000 ALTER TABLE `T_ProjectSampleData` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_ProjectSampleData` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_ProjectStatus`
--

DROP TABLE IF EXISTS `T_ProjectStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `T_ProjectStatus` (
  `ps_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `project_status` int(11) NOT NULL,
  `statusname` varchar(255) NOT NULL,
  `createtime` datetime NOT NULL,
  `updatetime` datetime DEFAULT NULL,
  PRIMARY KEY (`ps_id`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_ProjectStatus`
--

LOCK TABLES `T_ProjectStatus` WRITE;
/*!40000 ALTER TABLE `T_ProjectStatus` DISABLE KEYS */;
INSERT INTO `T_ProjectStatus` VALUES (82,84,8,'資料相似度報表','2024-07-19 09:23:04','2024-07-19 09:27:18'),(83,85,8,'資料相似度報表','2024-08-09 20:33:35','2024-08-14 13:37:03'),(84,86,8,'資料相似度報表','2024-08-15 08:21:49','2024-08-15 08:29:21'),(85,87,2,'資料匯入中','2024-08-19 18:57:02','2024-08-19 18:57:02');
/*!40000 ALTER TABLE `T_ProjectStatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Project_FinalTable`
--

DROP TABLE IF EXISTS `T_Project_FinalTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_Project_FinalTable`
--

LOCK TABLES `T_Project_FinalTable` WRITE;
/*!40000 ALTER TABLE `T_Project_FinalTable` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Project_FinalTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Project_NumStatValue`
--

DROP TABLE IF EXISTS `T_Project_NumStatValue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_Project_NumStatValue`
--

LOCK TABLES `T_Project_NumStatValue` WRITE;
/*!40000 ALTER TABLE `T_Project_NumStatValue` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Project_NumStatValue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Project_SampleTable`
--

DROP TABLE IF EXISTS `T_Project_SampleTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_Project_SampleTable`
--

LOCK TABLES `T_Project_SampleTable` WRITE;
/*!40000 ALTER TABLE `T_Project_SampleTable` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Project_SampleTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Project_SparkStatus_Management`
--

DROP TABLE IF EXISTS `T_Project_SparkStatus_Management`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_Project_SparkStatus_Management`
--

LOCK TABLES `T_Project_SparkStatus_Management` WRITE;
/*!40000 ALTER TABLE `T_Project_SparkStatus_Management` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Project_SparkStatus_Management` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_Project_SysStep_Config`
--

DROP TABLE IF EXISTS `T_Project_SysStep_Config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_Project_SysStep_Config`
--

LOCK TABLES `T_Project_SysStep_Config` WRITE;
/*!40000 ALTER TABLE `T_Project_SysStep_Config` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_Project_SysStep_Config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_SystemSetting`
--

DROP TABLE IF EXISTS `T_SystemSetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_SystemSetting`
--

LOCK TABLES `T_SystemSetting` WRITE;
/*!40000 ALTER TABLE `T_SystemSetting` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_SystemSetting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_originTable`
--

DROP TABLE IF EXISTS `T_originTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Dumping data for table `T_originTable`
--

LOCK TABLES `T_originTable` WRITE;
/*!40000 ALTER TABLE `T_originTable` DISABLE KEYS */;
/*!40000 ALTER TABLE `T_originTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `T_utilityResult`
--

DROP TABLE IF EXISTS `T_utilityResult`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `T_utilityResult`
--

LOCK TABLES `T_utilityResult` WRITE;
/*!40000 ALTER TABLE `T_utilityResult` DISABLE KEYS */;
INSERT INTO `T_utilityResult` VALUES (96,84,'workclass_sys_personal_financial','DP_test07181_inner.csv','statistic','eydyYXcgZGF0YSc6IHsnd29ya2NsYXNzX3N5c19wZXJzb25hbF9maW5hbmNpYWwnOiB7J3R5cGUnOiAnY2F0ZWdvcnknLCAndmFsdWUnOiB7J1ByaXZhdGUnOiAzMzkwNiwgJ1NlbGYtZW1wLW5vdC1pbmMnOiAzODYyLCAnTG9jYWwtZ292JzogMzEzNiwgJz8nOiAyNzk5LCAnU3RhdGUtZ292JzogMTk4MSwgJ290aGVycyc6IDMxNTh9fX0sICdzeW4uIGRhdGEnOiB7J3dvcmtjbGFzc19zeXNfcGVyc29uYWxfZmluYW5jaWFsJzogeyd0eXBlJzogJ2NhdGVnb3J5JywgJ3ZhbHVlJzogeydQcml2YXRlJzogMzM5MDYsICdTZWxmLWVtcC1ub3QtaW5jJzogMzg2MiwgJ0xvY2FsLWdvdic6IDMxMzYsICc/JzogMjc5OSwgJ1N0YXRlLWdvdic6IDE5ODEsICdvdGhlcnMnOiAzMTU4fX19fQ==','2024-07-19 09:27:18',NULL),(97,85,'Height_sys_TP_3000','DP_df_preview.csv','statistic','eydyYXcgZGF0YSc6IHsnSGVpZ2h0X3N5c19UUF8zMDAwJzogeyd0eXBlJzogJ2NhdGVnb3J5JywgJ3ZhbHVlJzogeycxNTYnOiA2NywgJzE4Nyc6IDY2LCAnMTg0JzogNjYsICcxNTknOiA2NSwgJzE1Myc6IDY0fX19LCAnc3luLiBkYXRhJzogeydIZWlnaHRfc3lzX1RQXzMwMDAnOiB7J3R5cGUnOiAnY2F0ZWdvcnknLCAndmFsdWUnOiB7JzE1Nic6IDY3LCAnMTg3JzogNjYsICcxODQnOiA2NiwgJzE1OSc6IDY1LCAnMTUzJzogNjR9fX19','2024-08-14 13:37:03',NULL),(98,86,'NoOfChildren_sys_TP_3000','DP_df_preview.csv','statistic','eydyYXcgZGF0YSc6IHsnTm9PZkNoaWxkcmVuX3N5c19UUF8zMDAwJzogeyd0eXBlJzogJ2NhdGVnb3J5JywgJ3ZhbHVlJzogeyczMCc6IDExOSwgJzEzJzogMTE3LCAnMjknOiAxMTIsICc1JzogMTA2LCAnMTYnOiAxMDZ9fX0sICdzeW4uIGRhdGEnOiB7J05vT2ZDaGlsZHJlbl9zeXNfVFBfMzAwMCc6IHsndHlwZSc6ICdjYXRlZ29yeScsICd2YWx1ZSc6IHsnMzAnOiAxMTksICcxMyc6IDExNywgJzI5JzogMTEyLCAnNSc6IDEwNiwgJzE2JzogMTA2fX19fQ==','2024-08-15 08:29:21',NULL);
/*!40000 ALTER TABLE `T_utilityResult` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-20 14:03:01
