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


#self.conn.doSqlCommand (sqlStr)#######################33
class updateTProjectSampleAvgRisk:
    conn=None
    condisionSampleData ={}
    appID=None
    appName=None

    projId=None
    dbName=None

    Start_Time = None
    Finish_Time = None
    Progress = None

    def __init__(self,project_id = 999):
        self.project_id=project_id
        

        t = time.localtime()
        try:
            conn = ConnectSQL()
            
            self.conn = conn
        except Exception as e:
            print('Connect mysql error: %s', str(e))
            return False
        # insert node status info
        self.condisionSampleData = {
            'project_id': project_id         

        }



    def selectT1(self):
        sqlStr = "Select T1  from DeIdService.T_Project_SampleTable where Project_id="+self.project_id
        retMsg = self.conn.doSqlCommand (sqlStr)

        return retMsg

    def selectT2(self):
        sqlStr = "Select T2 from DeIdService.T_Project_SampleTable where Project_id="+self.project_id
        retMsg = self.conn.doSqlCommand (sqlStr)

        return retMsg    




    #def updateToMysql(self, project_id, k_risk, max_t):
    def updateToMysql(self,  k_risk, max_t):
        print("=========self.project_id---------{}".format(self.project_id))
        
            
        #if(self.Progress =="100%"):
        #    t = time.localtime()
        #    self.Finish_Time=time.strftime("%Y-%m-%d %H:%M:%S", t)
        project_id = self.project_id
        valueSampleData = {
            'project_id' : project_id,
            'k_risk' : k_risk,
            'max_t' : max_t
                              
        }
        # def updateValue(self, dbName, tblName, conditions, setColsValue):
        resultSampleData = self.conn.updateValueMysql('DeIdService',
                                                 'T_Project_SampleTable',
                                                 self.condisionSampleData,
                                                 valueSampleData)
        if resultSampleData['result'] == 1:
            #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
            print("-------(in updateTProjectStatus)-----Update mysql succeed. {0}".format(resultSampleData['msg']))
        else:
            msg = resultSampleData['msg']
            #_logger.debug('insertSampleDataToMysql fail: ' + msg)
            print('-------(in updateTProjectStatus)---------insertNodeStatusToMysql fail: ' + msg)