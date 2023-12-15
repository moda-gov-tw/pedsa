#!/usr/bin/python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os.path

import base64

#20220301, citc add
#############################################
#citc, 20200529 create, get passwd from swarm
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


# 20180820
class getConfig:
    def __init__(self, config='/usr/src/app/config/development.ini'):
        self.parser = ConfigParser()
        self.parser.read(config)
        self.tmpkkk = "key1234567890key"



 

    def getLoginHdfs(self, key=None):
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

            #20220301, citc modified
            hdfsInfo['password'] = self.parser.get('hdfs', 'hdfs_password')
            #hdfsInfo['password'] = getPWDFroRandomFileDB("hadoop_file")

                    
            return hdfsInfo

    def getLoginWebservice(self, key=None):
        webInfo = dict()
        webInfo['ip'] = self.parser.get('webservice', 'ip')
        webInfo['port'] = self.parser.get('webservice', 'port')
        webInfo['user'] = self.parser.get('webservice', 'user')
        ##20220301, citc modified
        #webInfo['password'] = self.parser.get('webservice', 'password') 
        webInfo['password']  = getPWDFroRandomFileDB("maria_file")
         
            
        webInfo['sql_type'] = self.parser.get('webservice', 'sql_type')
        return webInfo

    def getLoginMysql(self, key=None):
        ip = self.parser.get('webservice', 'ip')
        port = self.parser.get('webservice', 'port')
        user = self.parser.get('webservice', 'user')

        #password = self.parser.get('webservice', 'password')
        password = getPWDFroRandomFileDB("maria_file")

        sql_type = self.parser.get('webservice', 'sql_type')
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

    def getMovePath(self,type_):
        # type_ = 'hdfs' or 'local'
        if type_ == 'local':
            importPath = self.parser.get('hdfs', 'pet_path')

        elif type_ == 'hdfs':
            importPath = self.parser.get('hdfs', 'pet_hadoop_path')
        else:
            importPath = self.parser.get('hdfs', 'pet_hadoop_path')
        return importPath

    def getImportMacPath(self,type_):
        # type_ = 'hdfs' or 'local'
        if type_ == 'hdfs':
            importPath = self.parser.get('hdfs', 'hdfs_import_path')

        elif type_ == 'local':
            importPath = self.parser.get('hdfs', 'local_mac_import_path')
        else:
            importPath = self.parser.get('hdfs', 'local_mac_import_path')
        return importPath

    def getExportPath(self,type_):
        # type_ = 'hdfs' or 'local'
        if type_ == 'local':
            exportPath = self.parser.get('hdfs', 'local_export_path')
        elif type_ == 'mac':
            exportPath = self.parser.get('hdfs', 'local_mac_export_path')            
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

    def getOpenAPI(self, host_name):
        web_ip = self.parser.get('openapi', 'web_ip')
        web_port = self.parser.get('openapi', 'web_port')
        flask_ip = self.parser.get('openapi', 'flask_ip')
        flask_port = self.parser.get('openapi', 'flask_port')
        #hsm_key = self.parser.get('openapi', 'hsm_key')
        hsm_url = self.parser.get('openapi', host_name)
        hsm_key = self.parser.get('openapi', host_name+"_key")
        return web_ip,web_port,flask_ip,flask_port,hsm_key,hsm_url

    def getOpenAPI_withoutHostName(self):
        web_ip = self.parser.get('openapi', 'web_ip')
        web_port = self.parser.get('openapi', 'web_port')
        flask_ip = self.parser.get('openapi', 'flask_ip')
        flask_port = self.parser.get('openapi', 'flask_port')
        return web_ip,web_port,flask_ip,flask_port
        
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


if __name__ == "__main__":


    #getConfig().updateLoginWebserviceToCipher()
    #getConfig().updateLoginWebserviceToPlain()

    webInfo= getConfig().getLoginWebservice()
    print("webInfo['password'] = "+webInfo['password'])

    hdfsInfo = getConfig().getLoginHdfs()
    print("hdfsInfo['password']="+hdfsInfo['password'])
    #hdfsInfo = getConfig().getLoginHdfs("key")
    #print("decry")
    #print(hdfsInfo['password'])
    #getConfig().updateLoginHdfsToPlain()
    #hdfsInfo = getConfig().getLoginHdfs()


    #print(hdfsInfo['password'])
    tmpString = hdfsInfo['password']
    lenStr = len(tmpString)
    print("lenStr = "+str(lenStr))

    ip, port, user, password, sql_type = getConfig().getLoginMysql()
    print("password="+password)


    '''
    getConfig().updateLoginHdfsToCipher()

    hdfsInfo = getConfig().getLoginHdfs()
    print(hdfsInfo['password'])
    
    hdfsInfo = getConfig().getLoginHdfs("key")
    print("decry")
    print(hdfsInfo['password'])
    getConfig().updateLoginHdfsToCipher("key1234567890key")
    '''