#!/usr/bin/python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os.path

import base64
from Crypto.Cipher import AES
from Crypto import Random

import getpass
import io , sys

#from connect_sql import ConnectSQL



# 20180820
class getConfig:
    def __init__(self, config='/app/app/devp/config/development.ini'):
        self.parser = ConfigParser()
        self.parser.read(config)
        self.tmpkkk = "key1234567890key"
        self.iv = "1234567890123456"
        self.inputDBPasswd = ""
        self.inputHdfsPasswd = ""

    def setDBPwd(self, passwd_):    
        self.inputDBPasswd = passwd_

    def setHdfsPwd(self, passwd_):    
        self.inputHdfsPasswd = passwd_

         

    def Encrypt(self, toEncrypt, key):   

    
        toEncrypt = toEncrypt.encode("utf8")#转换为UTF8编码
        key = key.encode("utf8")
     
        bs = AES.block_size

        print("bs="+str(bs))
        pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)#PKS7
        #iv = "1234567890123456"
        cipher = AES.new(key, AES.MODE_ECB, self.iv)#ECB模式
        
        resData1 = cipher.encrypt(pad(toEncrypt))
     
        resData2 = resData1.encode('hex')
        resData3 = resData2.upper()#全部大寫
     
        return resData3

    def Decrypt(self, toDecryptHexStr, key):   

    
        toDecryptHexStr = toDecryptHexStr.encode("utf8")#转换为UTF8编码
        key = key.encode("utf8")
     
        bs = AES.block_size
        
        #iv = Random.new().read(bs)
        #iv = "1234567890123456"
        cipher = AES.new(key, AES.MODE_ECB, self.iv)
        
        resData1 = cipher.decrypt(toDecryptHexStr.decode('hex'))
        #citc, 20200310 unpadding###########
        tmpString = self.unpadding(resData1)
        #####################################
     
          
        return tmpString    


    def updateLoginHdfsToCipher(self):
        #tmpString = self.parser.get('hdfs', 'hdfs_password')

        tmpString = self.inputHdfsPasswd
        tmpString = self.Encrypt(tmpString, self.tmpkkk)


        self.parser.set("hdfs", "hdfs_password", tmpString)

        with open('/app/app/devp/config/development.ini', 'wb') as fileW:
            self.parser.write(fileW)

        return

    def unpadding(self, toUnpadStr):
        #citc, 20200310 unpadding###########
        tmpString = toUnpadStr
        lenStr = len(tmpString)
        padChar = tmpString[lenStr - 1] 
        # print("padChar = "+str(ord(padChar)))

        len_ = ord(padChar)
        tmpString = tmpString[:-len_]
        #print(tmpString)
        lenStr = len(tmpString)
        #print("lenStr = "+str(lenStr))
        return tmpString
        #####################################


    def updateLoginHdfsToPlain(self):
        tmpString = self.parser.get('hdfs', 'hdfs_password')
        tmpString = self.Decrypt(tmpString, self.tmpkkk)

        #citc, 20200310 unpadding###########
        #tmpString = self.unpadding(tmpString)
        #####################################

        self.parser.set("hdfs", "hdfs_password", tmpString)

        with open('/app/app/devp/config/development.ini', 'wb') as fileW:
            self.parser.write(fileW)

        return    
                    


    def updateLoginWebserviceToCipher(self):
        #tmpString = self.parser.get('webservice', 'password')

        tmpString = self.inputDBPasswd
        tmpString = self.Encrypt(tmpString, self.tmpkkk)


        self.parser.set("webservice", "password", tmpString)

        with open('/app/app/devp/config/development.ini', 'wb') as fileW:
            self.parser.write(fileW)

        return

    def updateLoginWebserviceToPlain(self):
        tmpString = self.parser.get('webservice', 'password')


        #print("in updateLoginWebserviceToPlain tmpString ="+tmpString)
        tmpString = self.Decrypt(tmpString, self.tmpkkk)
        #print("in updateLoginWebserviceToPlain tmpString ="+tmpString)

        #citc, 20200310 unpadding###########
        #tmpString = self.unpadding(tmpString)
        #####################################

        self.parser.set("webservice", "password", tmpString)

        with open('/app/app/devp/config/development.ini', 'wb') as fileW:
            self.parser.write(fileW)

        return        


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
            if(key == None):
                tmpString = self.parser.get('hdfs', 'hdfs_password')

                #print("----len(tmpString)={}".format(len(tmpString)))
                
                if(len(tmpString)==32):
                    tmpString = self.Decrypt(tmpString, self.tmpkkk)
                hdfsInfo['password'] = tmpString    

            else:
                tmpString = self.parser.get('hdfs', 'hdfs_password')
                #print("tmpString="+tmpString)
                tmpString = self.Decrypt(tmpString, self.tmpkkk)

                hdfsInfo['password'] = tmpString

                #encTmpString = self.Encrypt(tmpString, "key1234567890key")
                #print("tmpString="+str(tmpString))
                    
            return hdfsInfo

    def getLoginWebservice(self, key=None):
        webInfo = dict()
        webInfo['ip'] = self.parser.get('webservice', 'ip')
        webInfo['port'] = self.parser.get('webservice', 'port')
        webInfo['user'] = self.parser.get('webservice', 'user')
        if(key == None):
            #webInfo['password'] = self.parser.get('webservice', 'password')
            tmpString = self.parser.get('webservice', 'password')
            if(len(tmpString)==32):
                tmpString = self.Decrypt(tmpString, self.tmpkkk)
    
            webInfo['password'] = tmpString    

        else:
            tmpString = self.parser.get('webservice', 'password')
            #print("tmpString="+tmpString)
            tmpString = self.Decrypt(tmpString, self.tmpkkk)

            webInfo['password'] = tmpString

            #encTmpString = self.Encrypt(tmpString, "key1234567890key")
            #print("tmpString="+str(tmpString))
            
        webInfo['sql_type'] = self.parser.get('webservice', 'sql_type')
        return webInfo

    def getLoginMysql(self, key=None):
        ip = self.parser.get('webservice', 'ip')
        port = self.parser.get('webservice', 'port')
        user = self.parser.get('webservice', 'user')

        #password = self.parser.get('webservice', 'password')
        if(key == None):
            #webInfo['password'] = self.parser.get('webservice', 'password')
            tmpString = self.parser.get('webservice', 'password')
            if(len(tmpString)==32):
                tmpString = self.Decrypt(tmpString, self.tmpkkk)
    
            password = tmpString    

        else:
            tmpString = self.parser.get('webservice', 'password')
            #print("tmpString="+tmpString)
            tmpString = self.Decrypt(tmpString, self.tmpkkk)

            password = tmpString


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


if __name__ == "__main__":

    
    show = sys.argv[1]


    if show == "1":
 
        hdfsInfo = getConfig().getLoginHdfs()
        # print("hdfsInfo['password']="+hdfsInfo['password'])
    else:
        getConfig_ = getConfig()

        pw2 = getpass.getpass("please input hdfs_user (hadoop) passwd:")
        #print("input hdfs passwd="+pw2)

        getConfig_.setHdfsPwd(pw2)
        getConfig_.updateLoginHdfsToCipher()
        
