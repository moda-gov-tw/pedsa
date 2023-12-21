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

#from connect_sql import ConnectSQL

def getPWDFroRandomFileDB(passwd):
    #h = SHA256.new()

    hash_=""
    for x in os.listdir('/run/secrets'):
        if "digestF_M" in x:
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

        if(hash_ in resData3):
            file__= '/run/secrets/' +file_
            with open(file__,'r') as fp:
                pwddd = fp.readline()
                pwddd=pwddd.strip()
                if pwddd != passwd:
                    return "password not mating"
            return file_.strip() 
    
    return "no matching file"            


#citc, 20200529 add, get passwd from swarm
def getPWDFroRandomFile(passwd):
    #h = SHA256.new()

    hash_=""
    for x in os.listdir('/run/secrets'):
        if "digestF_H" in x:
            #print(x)
            x= '/run/secrets/' +x
            with open(x,'r') as fp:
               hash_ = fp.readline()
            break;
    hash_ = hash_.strip()
    #print(hash_)
    #print(len(hash_))
    #print("-------")
    #pwddd=""
    for file_ in os.listdir('/run/secrets'):
        h = SHA256.new()
        h.update(file_)
        resData2 = h.hexdigest() 
        
        resData3 = resData2.upper()
        #print(resData3)
        #print(len(resData3))

 
        if(resData3 == hash_):
            file__= '/run/secrets/' +file_
            with open(file__,'r') as fp:
                pwddd = fp.readline()
                pwddd=pwddd.strip()
                if pwddd != passwd:
                    return "password not mating"
            return file_.strip() 
    
    return "no matching file"    

#digestF_Hdfs
#digestF_Maria   

if __name__ == "__main__":
    digestF = sys.argv[1]
    passwd = sys.argv[2]
    tmp = ""

    if "digestF_H" in digestF:
    	tmp = getPWDFroRandomFile(passwd)
        
    else:
    	tmp= getPWDFroRandomFileDB(passwd)
    
    print(tmp)      



