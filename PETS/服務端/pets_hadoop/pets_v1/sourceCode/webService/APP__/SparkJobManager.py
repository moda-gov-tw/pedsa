#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from funniest.logging_tester import _getLogger
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig

#citc, 20181022 add for SSH login into local hadoop cluster
from mylib.loginInfo import getLoginLoacalHadoop

_logger=_getLogger('SparkManager')


def parseStatusResult(stdout_):
    dirDic={'/docker​/':'/docker/citc​', '/home/':'/home/citc', '/data/docker/':'/data/citc','/docker/':'/citc','/home/docker/':'/home/citc'}
    buf = stdout_
    meta_ ={}
    while True:
        line = buf.readline()
        print line
        if line == '':
            break
        #stdout_.write(line)
        # #stdout_.flush()
        

        #overlay
        if("overlay" in line):
            #strList[0]                            strList[-1]
            #overlay         876G  183G  648G  23% /
            strList = line.split()
            

            buff = strList[-1]
            #buff = "/home/docker/overlay2/e699c8d6f2f7b8cb36b64be1a6475fb152b22e9543ef7a85ea1ae668fedf359d/merged"
            dirName = buff
            #print("11")
            if(len(strList[-1])>1):
                #print("109")
                strL = buff.split("overlay2")
                #print("108")
                print("dirName--------------%s"%strL[0])
                dirName = dirDic[strL[0]]

            
            meta_["dirName"] = dirName
            meta_["Size"] = strList[1]
            meta_["Used"] = strList[2]
            meta_["Avail"] = strList[3]
            meta_["usedPercen"] = strList[4] 
            break;

        if("UNHEALTHY" in line):
            #line = " ".join(line.split())
            #line = line.strip(' ')
            strList = line.split()

            #print(strList)
 
            NodeId= strList[0].strip()
            meta_ = parseUnhealthNodeStatusReport(NodeId,meta_ )
            meta_["Node-Id"] = strList[0].strip()
            meta_["Node-State"] = strList[1].strip()
            break;

        if("RUNNING" in line):
            #line = " ".join(line.split())
            #line = line.strip(' ')
            strList = line.split()
            
            #print(strList)
            meta_["Node-Id"] = strList[0].strip()
            meta_["Node-State"] = strList[1].strip() 
            break;   

        
        if(("Application-Id" in  line) or ("Progress" in  line) or ("Start-Time" in  line) \
             or ("Finish-Time" in  line) or ("State" in  line)) and (":" in line):
            print("line-> %s"%line) 

            strList = line.split(':')

            meta_[strList[0].strip()] = strList[1].strip()
            
            #break;
    
    print(meta_)
    return meta_

'''
/docker​ /home /data/docker /docker /home/docker /home/docker​
/docker/citc​ /home/citc /data/citc /citc /home/citc /home/citc​
'''
###citc, 20191126 add###############3
def getSparkNodeDiskStatus():
    #irDic={'/docker​':'/docker/citc​', '/home':'/home/citc', '/data/docker':'/data/citc','/docker':'/citc','/home/docker':'/home/citc'}
    start = time.time()
    meta={}

    try:
        PATH = getConfig().getSparkPath()
        cmdStr = '''
        export PATH={0}

        source .bashrc
        
        df -h
        '''.format(PATH)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        meta = parseStatusResult(stdout)
    except Exception as e:
        _logger.debug(str(e))
        meta['err']=str(e)

    end = time.time()
    print("total time="+str((end - start)))
    return meta







###citc, 20191125 add###############3
#yarn node -status nodemaster:8050 
def parseUnhealthNodeStatusReport(NodeId,meta_):
    start = time.time()
    #meta={}

    try:
        PATH = getConfig().getSparkPath()
        cmdStr = '''
        export PATH={0}

        source .bashrc
        
        yarn node -status {1}
        '''.format(PATH,NodeId)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        #meta = parseStatusResult(stdout)
        buf = stdout
    except Exception as e:
        _logger.debug(str(e))
        meta_['err']=str(e)
    
    while True:
        line = buf.readline()
        #print line
        if line == '':
            break
        #stdout_.write(line)
        # #stdout_.flush()
        

   
        if("Health-Report" in  line) and (":" in line):
            print("line-> %s"%line) 
            strList = line.split(':')
            meta_[strList[0].strip()] = strList[1].strip()

    meta = meta_
    end = time.time()
    print("total time="+str((end - start)))
    return meta



###citc, 20191125 add###############3
def getSparkNodeStatus():
    start = time.time()
    meta={}

    try:
        PATH = getConfig().getSparkPath()
        cmdStr = '''
        export PATH={0}

        source .bashrc
        
        yarn node -list -all
        '''.format(PATH)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        meta = parseStatusResult(stdout)
    except Exception as e:
        _logger.debug(str(e))
        meta['err']=str(e)

    end = time.time()
    print("total time="+str((end - start)))
    return meta


def getSparkJobStatus(applicationID):
    start = time.time()
    meta={}

    try:
        PATH = getConfig().getSparkPath()
        cmdStr = '''
        export PATH={0}

        source .bashrc
        
        yarn application -status {1}
        '''.format(PATH, applicationID)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        meta = parseStatusResult(stdout)
    except Exception as e:
        _logger.debug(str(e))
        meta['err']=str(e)

    end = time.time()
    print("total time="+str((end - start)))
    return meta
    
    
def killSparkJob(applicationID):
    start = time.time()
    meta ={} #dict

    try:
        PATH = getConfig().getSparkPath()
        cmdStr = '''
        export PATH={0}

        source .bashrc

        yarn application -kill {1}
        '''.format(PATH, applicationID)
        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

        while True:
            line = stdout.readline()
            # print line
            if line == '':
                break
            meta['result'] = line.strip()

    except Exception as e:
        _logger.debug(str(e))
        meta['err']=str(e)

    end = time.time()
    print("total time="+str((end - start)))
    return meta    
