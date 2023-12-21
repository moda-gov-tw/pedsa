#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser 
import os.path

# 20180820
class getConfig():

	def __init__(self):

		self.config = ConfigParser.ConfigParser()
		self.config.read('/app/app/devp/config/development.ini')

	def getLoginHdfs(self):
		keyPath = self.config.get('hdfs', 'hdfs_keyPath')
		hdfsInfo = {}

		if (os.path.isfile(keyPath)):
			hdfsInfo['hostname'] = self.config.get('hdfs', 'hdfs_hostname') 
			hdfsInfo['user'] = self.config.get('hdfs', 'hdfs_user')
			hdfsInfo['keyPath'] = keyPath
			return hdfsInfo

		else:
			hdfsInfo['hostname']  = self.config.get('hdfs', 'hdfs_hostname') 
			hdfsInfo['port']  = self.config.get('hdfs', 'hdfs_port')
			hdfsInfo['user']  = self.config.get('hdfs', 'hdfs_user')
			hdfsInfo['password']  = self.config.get('hdfs', 'hdfs_password')
			return hdfsInfo


	'''
	def getLoginAquila(self):
		config = ConfigParser.ConfigParser()
		config.read(file_)
		ip = self.config.get('Login_information', 'ip') 
		port = self.config.get('Login_information', 'port')
		user = self.config.get('Login_information', 'user')
		password = self.config.get('Login_information', 'password')
		return ip, port, user, password
	'''

	def getLoginMysql(self):
		ip = self.config.get('webservice', 'mysql_ip') 
		port = self.config.get('webservice', 'mysql_port')
		user = self.config.get('webservice', 'mysql_user')
		password = self.config.get('webservice', 'mysql_password')
		return ip, port, user, password

	'''
	def getLogin_hd30(self):
		hostname = self.config.get('hdfs', 'hdfs_hostname') 
		user = self.config.get('hdfs', 'hdfs_user')
		keyPath = self.config.get('hdfs', 'hdfs_keyPath')
		return hostname, user, keyPath
	'''

	def getImportPath(self,type_):
		# type_ = 'hdfs' or 'local'
		if type_ == 'hdfs':
			importPath = self.config.get('hdfs', 'hdfs_import_path') 
		return importPath

	def getExportPath(self,type_):
		# type_ = 'hdfs' or 'local'
		if type_ == 'local':
			exportPath = self.config.get('hdfs', 'local_export_path') 
		return exportPath

	def getJarFiles(self):
		jar_path = self.config.get('hdfs', 'jar_path')
		jar_files = self.config.get('hdfs', 'jar_files')
		jar_list = [os.path.join(jar_path,jar.strip(' ')+'.jar') for jar in jar_files.split(',')]
		jarFiles = ','.join(jar_list)
		return jarFiles

	def getSparkCode(self,pyFile):
		spark_code_path = self.config.get('hdfs', 'spark_code_path')
		return os.path.join(spark_code_path,pyFile)



def getLoginAquila(file_):
	config = configcarser.ConfigParser()
	config.read(file_)
	ip = config.get('Login_information', 'ip') 
	port = config.get('Login_information', 'port')
	user = config.get('Login_information', 'user')
	password = config.get('Login_information', 'password')
	return ip, port, user, password


def getLoginMysql(file_):
	config = configparser.ConfigParser()
	config.read(file_)
	ip = config.get('Login_information', 'ip') 
	port = config.get('Login_information', 'port')
	user = config.get('Login_information', 'user')
	password = config.get('Login_information', 'password')
	return ip, port, user, password

def getLogin_hd30(file_):
	config = configparser.ConfigParser()
	config.read(file_)
	hostname = config.get('Login_information', 'hostname') 
	user = config.get('Login_information', 'user')
	keyPath = config.get('Login_information', 'keyPath')
	return hostname, user, keyPath