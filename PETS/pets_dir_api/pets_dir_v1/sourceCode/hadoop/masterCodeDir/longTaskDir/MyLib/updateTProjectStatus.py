#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
#from pyspark import SparkConf, SparkContext, StorageLevel
#from py4j.protocol import Py4JJavaError
#from pyspark.sql import SQLContext
#from pyspark.sql.functions import col
import logging
import subprocess
from subprocess import check_output

from MyLib.connect_sql import ConnectSQL
#from funniest.logging_tester import _getLogger
#$HADOOP_HOME


import time 

#reload(sys)
#sys.setdefaultencoding('utf-8')

#import codecs
#sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
#sys.stdout.write("Your content....")


########################33
class updateTProjectStatus:
    conn=None
    condisionSampleData ={}
    appID=None
    appName=None

    projId=None
    dbName=None

    Start_Time = None
    Finish_Time = None
    Progress = None

    def __init__(self,project_id = 999,userId=1):
        self.project_id=project_id
        self.userId=userId

        t = time.localtime()
        try:
            conn = ConnectSQL()
            
            self.conn = conn
            self.conn.close()
        except Exception as e:
            print('Connect mysql error: %s', str(e))
            return False
        # insert node status info
        self.condisionSampleData = {
            'project_id': project_id         

        }




    def updateToMysql(self, project_id, project_status, statusname):
        self.project_id = project_id
        
            
        #if(self.Progress =="100%"):
        #    t = time.localtime()
        #    self.Finish_Time=time.strftime("%Y-%m-%d %H:%M:%S", t)

        valueSampleData = {
            'project_id' : project_id,
            'project_status' : project_status,
            'statusname' : statusname,
            'updateMember_Id': self.userId
                              
        }
        # def updateValue(self, dbName, tblName, conditions, setColsValue):
        

        try:
            conn = ConnectSQL()
            self.conn = conn
            
        except Exception as e:
            print('Connect mysql error: %s', str(e))
            raise Exception('Connect mysql error: %s', str(e))
            return False


        resultSampleData = self.conn.updateValueMysql('DeIdService',
                                                 'T_ProjectStatus',
                                                 self.condisionSampleData,
                                                 valueSampleData)
            
        if resultSampleData['result'] == 1:
            #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
            print("---project_id={0}--project_status={1}----(in updateTProjectStatus)-----Update updateTProjectStatus succeed. {2}".format(project_id, project_status,resultSampleData['msg']))
            self.conn.close()
            return True
        else:
            msg = resultSampleData['msg']
            #_logger.debug('insertSampleDataToMysql fail: ' + msg)
            print('-------(in updateTProjectStatus)---------updateTProjectStatus fail: ' + msg)
            return False
            
            
