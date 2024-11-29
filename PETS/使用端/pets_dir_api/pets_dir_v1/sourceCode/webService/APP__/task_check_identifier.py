#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import app
from app import celery
from flask_redis import FlaskRedis
import time
import re
from config.ssh_hdfs import ssh_hdfs
from log.logging_tester import _getLogger
from config.loginInfo import getConfig
import paramiko



from config.connect_sql import ConnectSQL

redis_store = FlaskRedis(app)

###itri, for Mac (start)###################### 
@celery.task(bind=True)
def multiplehash_longTask(self, identifier_code):
    # with app.app_context():

        # Set log.
    global _logger, _vlogger
    _logger=_getLogger('mac')
    _vlogger=_getLogger('verify__' + 'mac')
    print("################################################")
    ts0 = time.time()

    try:
        jarfiles = getConfig().getJarFiles()
        path = getConfig().getImportPath('local')
        sparkCode = getConfig().getSparkCode('check_identifier.py')
        


        cmdStr='''spark-submit --jars {0} {1} {2}'''.format(jarfiles,sparkCode,'\"'+identifier_code+'\"')

 
        print(cmdStr)
        ssh_for_bash = ssh_hdfs()
        print(cmdStr)
        _logger.debug(cmdStr)
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        print(stdout)
        print(stderr)
    except Exception as e:
        print("************************************************")
        errMsg = 'ssh connect error: ' + str(e)
        print(errMsg)
        _logger.debug(errMsg)
        self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
        return

        if 0:
            lines = stdout.readlines()
            print(lines)
            print(stderr.readlines())


            for line in lines:
                print(line)

            outList = getSparkAppId_( lines)
            print(outList)
        else:
            ##c. get spark ID, table name##########
            outList = getSparkAppId(self, stdout, False)
            print(outList)

        #self.update_state(self.request.id, state="PROGRESS", meta={'progress': 90})
        #time.sleep(1)

        if len(outList) < 2:
            #appID=app_ID
            appID="9999"
            outTblName="errTable"
        else:
            appID=outList[1]
            outTblName=outList[0]
        print(outTblName)
        print(len(outTblName))
        outTblName = outTblName[:-1]
        appID=appID[:-1]


        ts1 = time.time()
        print(ts1-ts0)
        ##d. close ssh section##########
        return outList


def getColoumnsFromMysql(projName, tblOutput, conn):
    # query columns name
    colCompare = dict()

    sqlCommand = """
    SELECT pro_col_en,pro_col_cht
    FROM {0}.{1}
    WHERE pro_db='{2}'
    AND finaltblName='{3}'
    """.format('DeIdService', 'T_Project_SampleTable', projName, tblOutput)

    _logger.debug(sqlCommand)

    result = conn.doSqlCommand(sqlCommand)
    _logger.debug(result)

    if len(result['fetchall']) == 0:
        errMsg = 'Can not find finaltblName: {}'.format(tblOutput)
        _logger.debug(errMsg)
        return colCompare

    pro_col_en = [col.strip(' ') for col in result['fetchall'][0]['pro_col_en'].split(',')]
    pro_col_cht = [col.strip(' ') for col in result['fetchall'][0]['pro_col_cht'].split(',')]

    for i in range(len(pro_col_en)):
        colCompare[pro_col_en[i]] = pro_col_cht[i]
    _logger.debug(colCompare)
    return colCompare

def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    meta_={}# python dict
    while True:
        line = stdout_.readline()
        #print(line)
        #print("##########line#################")
        if line == '':
            break
        print(line)
        #sys.stdout.write(line)
        #sys.stdout.flush()

        ##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_')
            errReson_=line[kTable_index:]
            _logger.debug('The errReson_ is ' + errReson_)
            print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;


        if "sc.applicationId:" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            _logger.debug('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
#            self.update_state(state="PROGRESS", meta={'progress': app_ID})
            self.update_state(state="PROGRESS", meta=meta_)
            outList.append(app_ID)
            #if not viewSparkProcess:
            #   break
    print('#####meta_######')
    print(len(meta_))
    print(meta_)

#############################################################
    ##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
        self.update_state(state="FAIL", meta=meta_)
    else:
        self.update_state(state="PROGRESS", meta=meta_)
    ##20180103 add, citc add for error (end)###########

    if 0:
        output = sparkCommand.communicate()[0]
        exitCode = sparkCommand.returncode

        if (exitCode == 0):
            #return output
            pass
        else:
            print(exitCode)
            print(output)

            #raise subprocess.ProcessException(command, exitCode, output)
    #print(len(outList))
#    return outList
########################33
##(end, 2018/03/30)###################

#####################################################################

    return outList


#2018/03/26, citc
def getSparkAppId_( lines):
    app_ID=9999
    outList=[]
    print('in getSparkAppId_')
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    meta_={}# python dict
    #while True:
    for line in lines:


        ##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_')
            errReson_=line[kTable_index:]
            print('The errReson_ is ' + errReson_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;
        ##20180103 add, citc add for error (end)#######

 
        #if "local-" in  line: application_
        if "application_" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            print('The app ID is ' + app_ID)
            meta_['jobID'] = app_ID
            #self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)

    print('#####meta_######')
    print("meta len ="+str(len(meta_)))
    print(meta_)
    print('#####meta_ (end)######')


    return outList
    ########################33
