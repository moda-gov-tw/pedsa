#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser 
import os.path



#import sys
#import codecs
#sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

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
			
			#citc, 20220301
			#hdfsInfo['password']  = self.config.get('hdfs', 'hdfs_password')
			hdfsInfo['password'] = getPWDFroRandomFileDB("hadoop_file")
			return hdfsInfo


	

	def getLoginMysql(self):
		ip = self.config.get('webservice', 'mysql_ip') 
		port = self.config.get('webservice', 'mysql_port')
		user = self.config.get('webservice', 'mysql_user')
		#citc, 20220301
		#password = self.config.get('webservice', 'mysql_password')
		password = getPWDFroRandomFileDB("maria_file")
		return ip, port, user, password

	

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




#citc, 20220301 modified
#############################################
#citc, 20200529 add, get passwd from swarm
##############################################
def getPWDFroRandomFileDB(rand_file_name):

    hash_=""
    for x in os.listdir('/run/secrets'):
        if rand_file_name in x:
            print(x)
            print(len(x))
            x= '/run/secrets/' +x
            print(x)
            print(len(x))
            with open(x,'r') as fp:
               hash_ = fp.read()
            break;
    hash_ = hash_.strip()
    print(hash_)
    print(len(hash_))
    print("-------")
 
    
    return hash_ 


##citc hadoop get mysql info############################
#file_ = /home/hadoop/proj_/longTaskDir/login_mysql.txt#
#in connect_sql.py######################################
def getLoginMysql(file_):
    print("in getLoginMysql (nodemaster)")
    config = configparser.ConfigParser()
    config.read(file_)
    ip = config.get('Login_information', 'ip') 
    port = config.get('Login_information', 'port')
    user = config.get('Login_information', 'user')
    #password = config.get('Login_information', 'password')
    password = getPWDFroRandomFileDB("maria_file")
    print(user)
    print(password)

    print("leave getLoginMysql")
    return ip, port, user, password

def getLogin_hd30(file_):
	config = configparser.ConfigParser()
	config.read(file_)
	hostname = config.get('Login_information', 'hostname') 
	user = config.get('Login_information', 'user')
	keyPath = config.get('Login_information', 'keyPath')
	return hostname, user, keyPath

if __name__ == "__main__":

	#ret = Sha256("63Fc3bC1")
	#print(ret)

	pwd = getPWDFroRandomFileDB()
	print(pwd)
