#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import re
import base64
import os
from app import app
from app import celery
from flask_redis import FlaskRedis
from celery import states
from log.logging_tester import _getLogger
from module.base64convert import getJsonParser
from module.JsonSchema import getImportSchema,loadJson
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig
from config.connect_sql import ConnectSQL

from config.getSparkStatus import checkSparkStatus

import sys
reload(sys)
sys.setdefaultencoding('utf8')


redis_store = FlaskRedis(app)


###itri, for deID (start)######################
@celery.task(bind=True)
def removeprojectdata_longTask(self, base64_,nothing):
    """
    base64_: string
    nothing: 1
    """

    projName=""
    with app.app_context():
        ts0 = time.time()

        global _logger,_vlogger
        _logger=_getLogger('removeprojectdata')
        _vlogger=_getLogger('verify__' + 'removeprojectdata')

        #decode base64
        #jsonAll = getJsonParser(base64_) # return jsons
        
        #decode base64
        jsonAll = getJsonParser(base64_) # return jsons
        _logger.debug(jsonAll)
        _logger.debug("------ userAccount  userId --start-------")
        userAccount = jsonAll['userAccount']
        userId = jsonAll['userId']
        _logger.debug('userAccount: %s',userAccount)
        _logger.debug('userId: %s',userId) 
        _logger.debug("------ userAccount  userId --end-------")
        

        if isinstance(jsonAll,str):
            errMsg = 'decode_base64_error: %s',jsonAll
            _logger.debug(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return

        # get dbName and tblName
        try:
            #jsonDic_ = {"proj_name": "t1_porj"}, base64 string: eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9
            #curl: curl -H 'Content-Type: application/json' -X POST "http://140.96.81.155:5915/rm_T_Project_DataByProjNameB64" 
            # -d '{"jsonBase64": "eyJwcm9qX25hbWUiOiAidDFfcG9yaiJ9"}'
            #projStep = jsonAll['projStep']
            projName = jsonAll['proj_name']
                  
            #citc, 20200621 fir debug
            #projName = "2QDataMarketDeId"

            #projID = jsonAll['projID']
            _logger.debug("------remove proj by Name ---start-------"+projName)
            #_logger.debug(projStep)
            _logger.debug(projName)
            #_logger.debug(projID)

            _logger.debug("------remove proj by Name---end-------")



            #mainInfo = jsonAll['mainInfo']
        except Exception as e:
            errMsg = 'json_format_error: {}'.format(str(e))
            _logger.debug(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return
        meta_ = {}
        self.update_state(state="PROGRESS", meta=meta_)

  
        #_logger.debug('projStep: %s',projStep)
        _logger.debug('dbName: %s',projName)
        #_vlogger.debug('projStep: %s',projStep)
        _vlogger.debug('dbName: %s',projName)


        ###20191206, citc get node status####################3###################################################
        checkSparkStatus_ = checkSparkStatus()
        meta_ = checkSparkStatus_.nodeStatus()
        try:
            if(meta_['Node-State']=='UNHEALTHY'):
                #{'Health-Report': '1/1 local-dirs are bad', 'Node-State': 'UNHEALTHY', 'Node-Id': 'nodemaster:8050'}
                respStr='sparkNpde:{0}, status is {1}, report: {2}'.format(meta_['Node-Id'],
                                                                  meta_['Node-State'],
                                                                  meta_['Health-Report'])
                #errMsg = 'g_getImport: {} tblName not found'.format(tbl)
                _logger.debug(respStr)
                self.update_state(state="FAIL_CELERY", meta={'errMsg':respStr})
                return

        except Exception as e:
            errMsg = '(removeProject_Data)checkSparkStatus.nodeStatus: ' + str(e)
            print(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return     
        ###########################################################################################################
        
        try:
        ################
            #def getSparkCode(self,pyFile):
                #spark_code_path = self.parser.get('hdfs', 'spark_code_path')
                #return os.path.join(spark_code_path,pyFile)
            #in developement.ini, 
            #spark_path = /home/hadoop/hive/bin:/home/hadoop/spark/bin:/home/hadoop/spark/    

            sparkCode = getConfig().getSparkCode('remove_T_Project_Data.py')
            dateTime = "0-0-0___"+projName
            cmdStr = 'spark-submit {0} {1} {2} {3}'.format(sparkCode,dateTime,userAccount,userId) #dateTime is "0-0-0___"+projName, here
            print("============spark-submit==1==============")
            _logger.debug(cmdStr)
            print (cmdStr)
            print("============spark-submit==2==============")
            ssh_for_bash = ssh_hdfs()
            stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
        
            buf = stdout
        ##########
        except Exception as e:
            errMsg = 'ssh connect error: ' + str(e)
            _logger.debug(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return


        if 0:
            lines = stdout.readlines()

            for line in lines:
                print(line)

            outList = getSparkAppId_( lines)
            print(outList)
        else:
            ##c. get spark ID, table name##########
            outList = getSparkAppId(self, stdout, projName, True)
            print("outList---1-----------------")
            print(outList)
            print("outList---2-----------------")


        if len(outList) < 8:
            #appID=app_ID
            appID="9999"
            err_ = 'outList_length_error: Except length >= 8, but get lenthgh: {}'.format(len(outList))
            errMsg = err_

            

            self.update_state(state="ICL_FAILURE", meta={'sparkAppID': appID,'errMsg':errMsg})
            return errMsg

        else:
            appID=outList[1]
            outTblName=outList[0]

        ts1 = time.time()
        print(ts1-ts0)
        ##d. close ssh section##########
        return outList


##2018/03/30, citc recover###############################
def getSparkAppId(self, stdout_, projName_, viewSparkProcess_):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')
    ######################33
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #sparkCommand = subprocess
    #sparkCommand=subprocess.Popen(submitSparkList,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # Poll process for new output until finished
    viewSparkProcess = viewSparkProcess_
    meta_= dict()

    doneList = []
    tmp_data_path = ''
    tmp_header_en_path = ''
    tmp_header_ch_path = ''

    while True:
        line = stdout_.readline()
        if line == '':
            break
        print(line)

        #ICL, retain here
        ##20180103 add, citc add for error###########
        if "errTable:" in  line:
            errTable_index=line.find('errTable:')
            errReson_=line[errTable_index:].strip('\n')
            _logger.debug('The errReason_ is ' + errReson_)
            _logger.debug('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            meta_['sparkAppID'] = '9999'
            _logger.debug(errReson_)
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break
   
        
        #20220831 deleteMariaDataByProjectId
        #print('deleteMariaDataByProjectId return id = {}, id=1 is ok'.format(ret))
        #deleteMariaDataByProjectId return id = 1, id=1 is ok
        #                                        , id=1 is ok\n
        #
        if "deleteMariaDataByProjectId return id =" in  line:
            tmpLen = len('deleteMariaDataByProjectId return id = ')
            tmpLen_deleteMariaDataByProjectId_idx = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            deleteMariaDataByProjectId_Result=line[tmpLen_deleteMariaDataByProjectId_idx:tmpLen_deleteMariaDataByProjectId_idx+1]
            meta_['deleteMariaDataByProjectId_Result'] = deleteMariaDataByProjectId_Result
            outList.append(deleteMariaDataByProjectId_Result)

            _logger.debug("deleteMariaDataByProjectId_Result result is {}".format(deleteMariaDataByProjectId_Result))


        #20220831 rmLocalHostDir 0
        #print('rmLocalHostDir_Result intput retDict = {}'.format(retDict["rmLocalHostDir_inputResult"]))
        ###print('rmLocalHostDir_Result output retDict = {}'.format(retDict["rmLocalHostDir_outputResult"]))
        ###print('rmLocalHostDir_Result dataMac output retDict = {}'.format(retDict["rmLocalHostDir_dataMac_outputResult"]))
        if "rmLocalHostDir_Result intput retDict =" in  line:
            tmpLen = len('rmLocalHostDir_Result intput retDict = ')
            tmpLen_rmLocalHostByTime_idx = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            rmLocalHostDir_Result=line[tmpLen_rmLocalHostByTime_idx:]
            meta_['rmLocalHostDir_input_Result'] = rmLocalHostDir_Result
            outList.append(rmLocalHostDir_Result)

            _logger.debug('rmLocalHostDir_input_Result result is ' + rmLocalHostDir_Result)


        #20220831 rmLocalHostDir 1
        ###print('rmLocalHostDir_Result intput retDict = {}'.format(retDict["rmLocalHostDir_inputResult"]))
        #print('rmLocalHostDir_Result output retDict = {}'.format(retDict["rmLocalHostDir_outputResult"]))
        ###print('rmLocalHostDir_Result dataMac output retDict = {}'.format(retDict["rmLocalHostDir_dataMac_outputResult"]))
        if "rmLocalHostDir_Result output retDict =" in  line:
            tmpLen = len('rmLocalHostDir_Result output retDict = ')
            tmpLen_rmLocalHostByTime_idx = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            rmLocalHostDir_Result=line[tmpLen_rmLocalHostByTime_idx:]
            meta_['rmLocalHostDir_output_Result'] = rmLocalHostDir_Result
            outList.append(rmLocalHostDir_Result)

            _logger.debug('rmLocalHostDir_output_Result result is ' + rmLocalHostDir_Result)
        
        #20220831 rmLocalHostDir 2
        ###print('rmLocalHostDir_Result intput retDict = {}'.format(retDict["rmLocalHostDir_inputResult"]))
        ###print('rmLocalHostDir_Result output retDict = {}'.format(retDict["rmLocalHostDir_outputResult"]))
        #print('rmLocalHostDir_Result dataMac output retDict = {}'.format(retDict["rmLocalHostDir_dataMac_outputResult"]))
        if "rmLocalHostDir_Result dataMac output retDict =" in  line:
            tmpLen = len('rmLocalHostDir_Result dataMac output retDict = ')
            tmpLen_rmLocalHostByTime_idx = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            rmLocalHostDir_Result=line[tmpLen_rmLocalHostByTime_idx:]
            meta_['rmLocalHostDir_dataMac_output_Result'] = rmLocalHostDir_Result
            outList.append(rmLocalHostDir_Result)

            _logger.debug('rmLocalHostDir_dataMac_output_Result result is ' + rmLocalHostDir_Result)    
   

        #print('rmHdfsDirByTime input retDict = {}'.format(resultDic["rm_projName_input"]))
        if "rmHdfsDirByTime input retDict =" in  line:
            tmpLen = len('rmHdfsDirByTime input retDict = ')
            tmpLen_rmHdfsDirByTime_input_idx = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            rmHdfsDirByTime_inputResult=line[tmpLen_rmHdfsDirByTime_input_idx:]
            meta_['rmHdfsDir_input_Result'] = rmHdfsDirByTime_inputResult
            outList.append(rmHdfsDirByTime_inputResult)

            _logger.debug('rmHdfsDir_input_Result result is ' + rmHdfsDirByTime_inputResult)


        #print('rmHdfsDirByTime output retDict = {}'.format(resultDic["rm_projName_out"]))
        if "rmHdfsDirByTime output retDict =" in  line:
            tmpLen = len('rmHdfsDirByTime output retDict = ')
            tmpLen_rmHdfsDirByTime_output_idx = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            rmHdfsDirByTime_outputResult=line[tmpLen_rmHdfsDirByTime_output_idx:]
            meta_['rmHdfsDir_output_Result'] = rmHdfsDirByTime_outputResult
            outList.append(rmHdfsDirByTime_outputResult)

            _logger.debug('rmHdfsDir_output_Result result is ' + rmHdfsDirByTime_outputResult)


        #print('dropHiveDBByTime_T_ProjectDataFilter retDict = {}'.format(resultDic[dataBaseName]))
        if "dropHiveDBByTime_T_ProjectDataFilter retDict =" in  line:
            tmpLen = len('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            tmpLen_hiveResult_index = tmpLen
            #hiveResult_index=line.find('dropHiveDBByTime_T_ProjectDataFilter retDict = ')
            hiveResult=line[tmpLen_hiveResult_index:]
            meta_['dropHiveTblResult'] = hiveResult
            outList.append(hiveResult)

            _logger.debug('dropHiveDBByTime_T_ProjectDataFilter result is ' + hiveResult)
            #_logger.debug('The toDoList are ' + ';'.join(toDoList))



        #'rmPorjectName': u'data by proj name--DB_list_ = t1_porj\n',
        #_logger.debug("---for rm data by proj name--DB_list_ = {}".format(DB_list_[0]))
        '''
        if "for rm data by proj name" in  line:
            tmpLen = len('---for rm data by proj name--DB_list_ = ')
            DB_list_index = tmpLen+1
            rmPorjectName=line[DB_list_index:]
            meta_['rmPorjectName'] = rmPorjectName
            outList.append(rmPorjectName)
            #rmPorjectName is data by proj name--DB_list_ = t1_porj
            _logger.debug('rmPorjectName is ' + rmPorjectName)
        '''

        #==removeProject end==
        if "==removeProject end==" in  line:
            _logger.debug('success :' + line)
            print('success :' + line)
            self.update_state(state="ICL_END", meta=meta_)
            time.sleep(5)
            break;  
        #==removeProject end==
        if "END end" in  line:
            _logger.debug('success :' + line)
            print('success1 :' + line)
            self.update_state(state="ICL_END", meta=meta_)
            time.sleep(5)
            break;                  

        if "sc.applicationId:" in  line:
            #self.update_state(state="ICL_START", meta=meta_)
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            _logger.debug('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            meta_['dbName'] = projName_
            #projName_
            self.update_state(state="ICL_START", meta=meta_)
            #self.update_state(state="PROGRESS", meta=meta_)
            #self.update_state(state="PROGRESS", meta={'progress': app_ID})
            outList.append(app_ID)
            #return outList
            if not viewSparkProcess:
                break

    print('#####meta_######')
    print(len(meta_))
    print(meta_)


    ##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
        self.update_state(state='FAIL_CELERY', meta=meta_)
        # Celery status from SparkError to SUCCESS, which changing too fast to get Info. from flask.
        # Therefore, set time lag 5 sec to get Info. in flask.
        time.sleep(5)
    else:
        self.update_state(state="PROGRESS", meta=meta_)

    return outList

