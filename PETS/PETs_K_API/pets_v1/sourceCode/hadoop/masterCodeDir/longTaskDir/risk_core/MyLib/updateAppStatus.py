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


########################33
class updateAppProgress:
    step = None
    div_in_loop = None
    div_cumm = None
    
    #tmp =0

    def __init__(self, lower, upper, div_in_loop, looop_round):
        tmp = (upper-lower)/looop_round
        self.step = tmp/div_in_loop
        self.div_in_loop = div_in_loop
        self.div_cumm = lower
        #self.lower = lower

    def getLoopProgress(self, div_increment):
        tmp = self.div_cumm
        progress = (self.step* div_increment)+self.div_cumm
        tmp = tmp + self.step
        if(div_increment == self.div_in_loop):
            self.div_cumm = progress
            #tmp=self.div_cumm
        progress = int(progress)
        progress_str = str(progress)
        return progress_str    


  
 


########################33
class updateAppStatus:
    conn=None
    condisionSampleData ={}
    appID=None
    appName=None

    projId=None
    dbName=None

    Start_Time = None
    Finish_Time = None
    Progress = None

    def __init__(self,appID_, appName_, dbName_, projId_):
        self.appID=appID_
        self.appName=appName_

        self.projId=projId_
        self.dbName=dbName_

        t = time.localtime()
        #self.Start_Time=time.strftime("%Y-%m-%d %H:%M:%S", t)
        #self.Finish_Time=time.strftime("%Y-%m-%d %H:%M:%S", t)
        self.Progress = "5"
        self.Progress_State = "running"
        try:
            conn = ConnectSQL()
            self.conn = conn
        except Exception as e:
            print('Connect mysql error: %s', str(e))
            return False
        # insert node status info
        self.condisionSampleData = {
            'Application_Id': self.appID,
            'Application_Name': self.appName,
            'proj_id' : self.projId,
            'dbName' : self.dbName

        }




    def updateToMysql(self,appState, progress,progress_state="Running"):

        self.Progress = progress
        self.Progress_State = progress_state

        try:
            conn = ConnectSQL()
            self.conn = conn
        except Exception as e:
            print('Connect mysql error: %s', str(e))
            return False
        
        #if(self.Progress =="100%"):
        #    t = time.localtime()
        #    self.Finish_Time=time.strftime("%Y-%m-%d %H:%M:%S", t)

        valueSampleData = {
           'Application_Id': self.appID,
           'Application_Name': self.appName,
           'proj_id' : self.projId,
           'dbName' : self.dbName,          
           'App_state': appState,
           'Progress': self.Progress,
           'Progress_State': self.Progress_State                      
        }
        # def updateValue(self, dbName, tblName, conditions, setColsValue):
        resultSampleData = self.conn.updateValueMysql('spark_status',
                                                 'appStatus',
                                                 self.condisionSampleData,
                                                 valueSampleData)
        if resultSampleData['result'] == 1:
            #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
            print("Update mysql succeed. {0}".format(resultSampleData['msg']))
        else:
            msg = resultSampleData['msg']
            #_logger.debug('insertSampleDataToMysql fail: ' + msg)
            print('insertNodeStatusToMysql fail: ' + msg)