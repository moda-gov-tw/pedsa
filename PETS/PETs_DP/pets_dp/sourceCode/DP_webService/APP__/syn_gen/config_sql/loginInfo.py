#!/usr/bin/python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os.path


# 20180820
class getConfig:
    def __init__(self, config='/app/app/devp/config/development.ini'):
        self.parser = ConfigParser()
        self.parser.read(config)

    def getLoginHdfs(self):
        keyPath = self.parser.get('hdfs', 'hdfs_keyPath')
        hdfsInfo = dict()

        if (os.path.isfile(keyPath)):
            hdfsInfo['hostname'] = self.parser.get('hdfs', 'hdfs_hostname')
            hdfsInfo['port'] = self.parser.get('hdfs', 'hdfs_port')
            hdfsInfo['user'] = self.parser.get('hdfs', 'hdfs_user')
            hdfsInfo['keyPath'] = keyPath
            return hdfsInfo

        else:
            hdfsInfo['hostname'] = self.parser.get('hdfs', 'hdfs_hostname')
            hdfsInfo['port'] = self.parser.get('hdfs', 'hdfs_port')
            hdfsInfo['user'] = self.parser.get('hdfs', 'hdfs_user')
            hdfsInfo['password'] = self.parser.get('hdfs', 'hdfs_password')
            return hdfsInfo

    def getLoginWebservice(self):
        webInfo = dict()
        webInfo['ip'] = self.parser.get('webservice', 'ip')
        webInfo['port'] = self.parser.get('webservice', 'port')
        webInfo['user'] = self.parser.get('webservice', 'user')
        webInfo['password'] = self.parser.get('webservice', 'password')
        webInfo['sql_type'] = self.parser.get('webservice', 'sql_type')
        return webInfo

    def getLoginMysql(self):
        ip = self.parser.get('webservice', 'ip')
        port = self.parser.get('webservice', 'port')
        user = self.parser.get('webservice', 'user')
        password = self.parser.get('webservice', 'password')
        sql_type = self.parser.get('webservice', 'sql_type')
        print(ip, port, user, password, sql_type)
        return ip, port, user, password, sql_type

    def getImportPath(self,type_):
        # type_ = 'hdfs' or 'local'
        if type_ == 'hdfs':
            importPath = self.parser.get('hdfs', 'hdfs_import_path')

        elif type_ == 'local':
            importPath = self.parser.get('hdfs', 'local_import_path')
        else:
            importPath = self.parser.get('hdfs', 'local_import_path')
        return importPath

    def getExportPath(self,type_):
        # type_ = 'hdfs' or 'local'
        if type_ == 'local':
            exportPath = self.parser.get('hdfs', 'local_export_path')
        else:
            exportPath = self.parser.get('hdfs', 'hdfs_export_path')
        return exportPath

    def getJarFiles(self, jars=None):
        jar_path = self.parser.get('hdfs', 'jar_path')
        jar_files = self.parser.get('hdfs', 'jar_files')
        if jars is None:
            jar_list = [os.path.join(jar_path, jar.strip(' ')+'.jar') for jar in jar_files.split(',')]
        elif '.jar' in jars:
            jar_list = [os.path.join(jar_path, jar.strip(' ')) for jar in jars.split(',')]
        else:
            jar_list = [os.path.join(jar_path, jar.strip(' ') + '.jar') for jar in jars.split(',')]
        return ','.join(jar_list)

    def getSparkCode(self,pyFile):
        spark_code_path = self.parser.get('hdfs', 'spark_code_path')
        return os.path.join(spark_code_path,pyFile)

    def getSparkPath(self):
        spark_path = self.parser.get('hdfs', 'spark_path')
        return spark_path

def getLoginAquila(file_):
    parser = ConfigParser()
    parser.read(file_)
    ip = parser.get('Login_information', 'ip')
    port = parser.get('Login_information', 'port')
    user = parser.get('Login_information', 'user')
    password = parser.get('Login_information', 'password')
    return ip, port, user, password


def getLoginMysql(file_):
    parser = ConfigParser()
    parser.read(file_)
    ip = parser.get('Login_information', 'ip')
    port = parser.get('Login_information', 'port')
    user = parser.get('Login_information', 'user')
    password = parser.get('Login_information', 'password')
    return ip, port, user, password


def getLogin_hd30(file_):
    parser = ConfigParser()
    parser.read(file_)
    hostname = parser.get('Login_information', 'hostname')
    user = parser.get('Login_information', 'user')
    keyPath = parser.get('Login_information', 'keyPath')
    return hostname, user, keyPath