#!/usr/bin/python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os.path

import base64
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random

import getpass
import io , sys
import re

import random
import string



#from connect_sql import ConnectSQL



# 20180820
class getConfig:
    def __init__(self, config='/app/app/devp/config/development.ini'):
        self.parser = ConfigParser()
        self.parser.read(config)

        self.inputDBPasswd = ""
        self.inputHdfsPasswd = ""

    def setDBPwd(self, passwd_):    
        self.inputDBPasswd = passwd_

    def setHdfsPwd(self, passwd_):    
        self.inputHdfsPasswd = passwd_


    def randomString(self, stringLength=8, oldPasswd=None):


        #tmpStr = self.getPWDFroRandomFile(oldPasswd)
 
        #if (tmpStr == ""):
            #return ""

        letters = string.hexdigits
        #letters = letters.upper()
        return ''.join(random.choice(letters) for i in range(stringLength))
        #return "abc"

    def getPWDFroRandomFile(self, oldPasswd=None):
        #h = SHA256.new()
  
        hash_=""
        for x in os.listdir('/run/secrets'):
            if "digestF_w" in x:
                #print(x)
                x= '/run/secrets/' +x
                with open(x,'r') as fp:
                   hash_ = fp.readline()
                break;
        hash_ = hash_.strip()
        #print(hash_)
        #print(len(hash_))
        #print("-------")
        pwddd=""
        for file_ in os.listdir('/run/secrets'):
            h = SHA256.new()
            h.update(file_)
            resData2 = h.hexdigest() 
            
            resData3 = resData2.upper()
            #print(resData3)
            #print(len(resData3))

            if(resData3 == hash_):
                file_= '/run/secrets/' +file_
                with open(file_,'r') as fp:
                   pwddd = fp.readline()
                   #print(file_)
                   #print(resData3)  
        
        pwddd = pwddd.strip()

        if (oldPasswd != None):
            if(oldPasswd != pwddd):
                pwddd=""
        return pwddd 



    def Sha256(self, toHash): 
        h = SHA256.new()
        #print("---1--")
        #print(toHash)
        #print(len(toHash))
        #print("---2--")
        h.update(toHash)
        resData2 = h.hexdigest() 
        #resData2 = h1.encode('hex')
        resData3 = resData2.upper()
        return resData3.strip()
    
    ##citc, 20200527 add
    def passwordCheck(self, password):
        """
        Verify the strength of 'password'
        Returns a dict indicating the wrong criteria
        A password is considered strong if:
            12 characters length or more
            1 digit or more
            1 uppercase letter or more
            1 lowercase letter or more
        """

        # calculating the length
        length_error = len(password) < 12

        # searching for digits
        digit_error = re.search(r"\d", password) is None

        # searching for uppercase
        uppercase_error = re.search(r"[A-Z]", password) is None

        # searching for lowercase
        lowercase_error = re.search(r"[a-z]", password) is None

        # overall result
        password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error)

        return {
            'password_ok' : password_ok,
            'length_error' : length_error,
            'digit_error' : digit_error,
            'uppercase_error' : uppercase_error,
            'lowercase_error' : lowercase_error
        }


    def updateLoginHdfsToCipher(self, hashValue):
        #tmpString = self.parser.get('hdfs', 'hdfs_password')

        tmpString = hashValue

        self.parser.set("hdfs", "hdfs_password", tmpString)

        with open('/app/app/devp/config/development.ini', 'wb') as fileW:
            self.parser.write(fileW)

        return


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
        print("padChar = "+str(ord(padChar)))

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
                    

    def updateLoginWebserviceToCipher(self, hashValue):
        #tmpString = self.parser.get('webservice', 'password')

        tmpString = hashValue
    

        self.parser.set("webservice", "password", tmpString)

        with open('/app/app/devp/config/development.ini', 'wb') as fileW:
            self.parser.write(fileW)

        return


    def updateLoginWebserviceToCipher(self):
        #tmpString = self.parser.get('webservice', 'password')

        tmpString = self.inputDBPasswd
        tmpString = self.Encrypt(tmpString, self.tmpkkk)


        #citc, 20200529 add
        for x in os.listdir('/run/secrets'):
            if "digestF_" in x:
                #print(x)
                x= '/run/secrets/' +x
                with open(x,'r') as fp:
                   hash_ = fp.readline()
                break;
        hash_ = hash_.strip()
        tmpString = hash_

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

    '''
    try:
        print('start connectToMysql to check project_name in mysql: {}'.format("projName"))
        check_conn = ConnectSQL()
    except Exception as e:
        
        print('connectToMysql fail: ' + str(e))
        
        #return
    '''
    show = sys.argv[1]



    if show == "1":#computing sha2 value of the random file name(the file stroe secret)

        getConfig_ = getConfig()
        fileName = sys.argv[2]
        hashFileName = getConfig_.Sha256(fileName)
        #updateLoginHdfsToCipher(hashFileName)
        #updateLoginWebserviceToCipher(hashFileName)

        print u"{0}".format(hashFileName)
        #print(len(hashFileName))

     
    elif show == "2": #get random file name for storing secret
        getConfig_ = getConfig()
        password = sys.argv[2]
        oldPasswd = sys.argv[3]
        #citc, 

        #print(password)
        #print(oldPasswd)
        

        retDic = getConfig_.passwordCheck(password)
        #print (retDic['password_ok'])
        #print (retDic['length_error'])
        #if(retDic['password_ok'] == False):
            #print("password_not_ok")
        #else
        #fileName = getConfig_.randomString(8, oldPasswd)
        fileName = getConfig_.randomString()
        #key.encode("utf8")
        #print (fileName.encode("utf8"))
        print u"{0}".format(fileName)
        #print u"---{0}---".format("password")
        #print(len(fileName))

    elif show == "3":#get a random file by computing sha2 value of the random file name
                     #matching the value in the digestF_worker
        getConfig_ = getConfig()
        
        pwdd = getConfig_.getPWDFroRandomFile()
        print u"{0}".format(pwdd)
        #print(len(pwdd))




                



    else:
        getConfig_ = getConfig()

        pw1 = getpass.getpass("please input mariaDB user(deidadmin) passwd:")
        #print("input mariaDB admin passwd="+pw1)
        getConfig_.setDBPwd(pw1)       


        getConfig_.updateLoginWebserviceToCipher()



 
