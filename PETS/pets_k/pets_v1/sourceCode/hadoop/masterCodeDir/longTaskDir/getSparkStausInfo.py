#!/usr/bin/python
# -*- coding: utf-8 -*-

#from pyspark import SparkConf, SparkContext, StorageLevel
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

########################33


def updateToMysql(nodeID, status,HealthReport):
    try:
        conn = ConnectSQL()
    except Exception as e:
        print('Connect mysql error: %s', str(e))
        return False
    # insert node status info
    condisionSampleData = {
        'Node_Id': nodeID

    }

    valueSampleData = {
        'Node_Id': nodeID,
        'Node_state': status,
        'Health_Report': HealthReport

    }
    # def updateValue(self, dbName, tblName, conditions, setColsValue):
    resultSampleData = conn.updateValueMysql('spark_status',
                                             'nodeStatus',
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        #_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
        print("Update mysql succeed. {0}".format(resultSampleData['msg']))
    else:
        msg = resultSampleData['msg']
        #_logger.debug('insertSampleDataToMysql fail: ' + msg)
        print('insertNodeStatusToMysql fail: ' + msg)



def parseStatusResult(subprocess):
 
    meta_ ={}
    while True:
        
        line = subprocess.stdout.readline()
        #print("type(line) is %s"%type(line))
        line= str(line)
        #print (line)
        if line == '' and sparkCommand.poll() is not None:
            break
        #sys.stdout.write(line)
        #sys.stdout.flush()
        #stdout_.write(line)
        # #stdout_.flush()

        
        if("UNHEALTHY" in line):
            #line = " ".join(line.split())
            #line = line.strip(' ')
            line = line.strip('b')
            #print(line.strip('\''))
            line =line.strip('\'')
            strList = line.split()

            #print(strList)
 
            NodeId= strList[0].strip()
            #meta_ = parseUnhealthNodeStatusReport(NodeId,meta_ )
            meta_["Node-Id"] = strList[0].strip().strip('\\t')
            meta_["Node-State"] = strList[1].strip().strip('\\t')
            break;

        if("RUNNING" in line):
            #line = " ".join(line.split())
            #line = line.strip(' ')
            #print("==1==")
            #print(line)
            #print(line.strip('b'))
            line = line.strip('b')
            #print(line.strip('\''))
            line =line.strip('\'')
            #print("==1==")
            strList = line.split()
            #strList = strList[0].split("b")
            #print("====")
            #print(strList)
            #print("====")
            meta_["Node-Id"] = strList[0].strip().strip('\\t')
            meta_["Node-State"] = strList[1].strip().strip('\\t')
            #updateToMysql(nodeID, status,HealthReport)
            break;   

        
    return meta_

def parseSingleNodeStatus(subprocess,meta_):
 
    #meta_ ={}
    while True:
        
        line = subprocess.stdout.readline()
        #print("type(line) is %s"%type(line))
        line= str(line)
        #print (line)
        if line == '' and sparkCommand.poll() is not None:
            break

        #Health-Report :
        if(("Health-Report" in  line) or ("Application-Id" in  line) or ("Progress" in  line) or ("Start-Time" in  line) \
             or ("Finish-Time" in  line) or ("State_1" in  line)) and (":" in line):
            print("line-> %s"%line) 
            line = line.strip('b')
            #print(line.strip('\''))
            line =line.strip('\'')
            line = line.strip('n')
            strList = line.split(':')
            print("strList[1].strip()=%s"%strList[1].strip())

            meta_[strList[0].strip().lstrip('\\t')] = strList[1].strip().strip('\\t')
            print(strList[0])
            print(strList[0].strip().strip('\\t'))
            print("meta_=%s"%meta_)
            break;
    #updateToMysql(meta_["Node-Id"] , meta_["Node-State"],meta_["Health-Report"])    
    #print(meta_)
    return meta_




def getSparkNodeStatus():
    
    #print('in hadoop getSparkStatus')
    meta_={}
    #print('in hadoop getSparkStatus1')
    #yarnCommand=os.path.join(os.environ.get("HADOOP_HOME"),"bin","yarn")
    #print('in hadoop getSparkStatus2')
    
    #20191209, citc mark. could not get HADOOP_HOME, using ssh remote call 
    #yarnCommandList=[yarnCommand,'node','-list','-all']
    
    yarnCommandList=['/home/hadoop/hadoop/bin/yarn','node','-list','-all']
    #print('in hadoop getSparkStatus2')
    #print (yarnCommandList)
    
    #out = check_output(yarnCommandList)
    
    #print(out)
    #print(type(out))
    #print("====================")
    getSparkNodeStatus=subprocess.Popen(yarnCommandList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 
    #getSparkNodeStatus
    meta_ = parseStatusResult(getSparkNodeStatus)
    
    #get heathy report
    #UNHEALTHY
    if(meta_['Node-State'] == 'UNHEALTHY'):
        #yarn node -status nodemaster:8050
        yarnCommandList=['/home/hadoop/hadoop/bin/yarn','node','-status']
        yarnCommandList.append(meta_['Node-Id'])
        print (meta_['Node-Id'])
        print ("yarnCommandList = %s"%yarnCommandList)
        getSparkNodeStatus=subprocess.Popen(yarnCommandList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        parseSingleNodeStatus(getSparkNodeStatus, meta_)  
    else:
        meta_["Health-Report"]="test20191209"          
        
        
    updateToMysql(meta_["Node-Id"] , meta_["Node-State"],meta_["Health-Report"])
    return meta_
    

if __name__ == "__main__":
    #global _logger
    #NAME="getSparkStatusInfo"
    #_logger=_getLogger(NAME)
    # command from celery:
    #'spark-submit --jars gen.jar longTaskDir/getGenTbl.py '+projName+' '+tblName
    '''
    projName = sys.argv[1] #str #projName = dbName
    projID = sys.argv[2] #str #projName = dbName
    base64_ = sys.argv[3] #str
    path_ = sys.argv[4]  # str
    print('########')
    print(projName)
    print(projID)
    print(base64_)
    print(path_)
    print('#############')
    '''
    meta_ = getSparkNodeStatus()
    print (meta_)
