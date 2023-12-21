#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import app
from app import celery
from flask_redis import FlaskRedis
from celery import states

import time
import base64
from module import getSqlString
from log.logging_tester import _getLogger
from module.base64convert import getJsonParser, encodeDic
from config.ssh_hdfs import ssh_hdfs
from config.loginInfo import getConfig

from config.getSparkStatus import checkSparkStatus


redis_store = FlaskRedis(app)


###itri, for deID (start)######################
@celery.task(bind=True)
def generalization_longTask(self, base64_,nothing):
    """
    base64_: string
    nothing: 1
    """
    with app.app_context():
        ts0 = time.time()

        # Set log.
        global _logger, _vlogger
        _logger = _getLogger('generalization')
        _vlogger = _getLogger('verify__' + 'generalization')


        #decode base64
        jsonAll = getJsonParser(base64_) # return jsons
        _logger.debug(jsonAll)
        _logger.debug("------ userAccount  userId --start-------")
        userAccount = jsonAll['userAccount']
        userId = jsonAll['userId']
        _logger.debug('userAccount: %s',userAccount)
        _logger.debug('userId: %s',userId) 
        _logger.debug("------ userAccount  userId --end-------")

        # Decode base64.
        #jsonAll = getJsonParser(base64_) # Return json
        if isinstance(jsonAll, str):
            errMsg = 'decode_base64_error: %s', jsonAll
            _logger.debug(errMsg)
            self.update_state(state=states.FAILURE, meta={'errMsg': errMsg})
            return

        # Get dbName and tblName
        try:
            projStep = jsonAll['projStep']
            projName = jsonAll['projName']
            projID = jsonAll['projID']
            mainInfo = jsonAll['mainInfo']
        except Exception as e:
            errMsg = 'json_format_error: {}'.format(str(e))
            _logger.debug(errMsg)
            self.update_state(state=states.FAILURE, meta={'errMsg': errMsg})
            return

        _logger.debug('projStep: %s', projStep)
        _logger.debug('projID: %s', projID)
        _logger.debug('dbName: %s', projName)
        _vlogger.debug('projStep: %s', projStep)
        _vlogger.debug('projID: %s', projID)
        _vlogger.debug('dbName: %s', projName)

        ###20200110, citc get node status####################3###################################################
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
            errMsg = '(gen)checkSparkStatus.nodeStatus: ' + str(e)
            print(errMsg)
            self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return     
        ###########################################################################################################        

        # Check if step is generalization
        if projStep != 'gen':
            errMsg = 'celery_gen_error_projStep_is_not_gen'
            _logger.debug(errMsg)
            self.update_state(state='FAIL_CELERY', meta={'errMsg': errMsg})
            return 

        # Collect all udf functions
        udfs = [func for func in dir(getSqlString) if func[:3] == 'get']


        # export
        jarFiles = getConfig().getJarFiles()  # Get all jar file names.
        sparkCode = getConfig().getSparkCode('getGenTbl.py')
        tblColDict = dict()
        doMinMaxCols = dict()
        # Iterate each table
        for tbl in mainInfo:
            genList = ''  # List of all actions on each columns.
            colList = mainInfo[tbl]['col_en'].split(',')
            rawTblName = mainInfo[tbl]['tblName']
            doMinMaxCols[rawTblName] = dict()
            for col_ in mainInfo[tbl]['colInfo']:
                '''
                col_ = col_1,col_2,...
                check json schema of each generalization
                schema = js.colInfoSchema()
                json_ = js.loadJson(mainInfo[tbl]['colInfo'][col_],schema) # return str if error                
                '''

                # check schema
                json_ = mainInfo[tbl]['colInfo'][col_]
                if isinstance(json_, str):
                    errMsg = 'JsonsError_%s', json_
                    _logger.debug(errMsg)
                    self.update_state(state='FAIL_CELERY', meta={'errMsg': errMsg})
                    return

                # Find what action this column is.
                action_ = 'getNogenerlize'
                for function in udfs:
                    if function == json_['apiName']:
                        action_ = function

                # Check if column need to do Min Max boung
                if action_ == 'getGenNumLevelMinMax':
                    min_bound, max_bound = getSqlString.getGenNumLevelMinMax(json_, bound=True)
                    doMinMaxCols[rawTblName][json_['colName']] = "{0},{1}".format(min_bound, max_bound)

                # Get action function
                colSqlAction = getSqlString.__dict__.get(action_)(json_)  # Return sql string
                _logger.debug(colSqlAction)

                # If found celery error, then return
                if colSqlAction[:16] == 'celery_gen_error':
                    errMsg = str(colSqlAction)
                    _logger.debug(errMsg)
                    self.update_state(state='FAIL_CELERY',
                                      meta={'errMsg': errMsg})
                    return

                genList += colSqlAction
                genList += '^'

                colList.pop(colList.index(json_['colName']))

            for colName in colList:
                # for those columns no generalized, append columns name
                genList += colName
                genList += '^'

            genList = genList[:-1]

            _vlogger.debug(genList)

            # Decode genList into base64 for ssh
            genListEncode = base64.b64encode(genList)

            tblColDict[mainInfo[tbl]['tblName']] = genListEncode

        genDictEncode = encodeDic(tblColDict)
        doMinMaxEncode = encodeDic(doMinMaxCols)
        try:
            cmdStr = '''
            spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7}'''.format(jarFiles,
                                                              sparkCode,
                                                              projName,
                                                              genDictEncode,
                                                              doMinMaxEncode,
                                                              projID,
                                                              userAccount,
                                                              userId)
            _logger.debug(cmdStr)
 

            ssh_for_bash = ssh_hdfs()
            stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

        except Exception as e:
            errMsg = 'ssh connect error: {0} You may check login information.'.format(str(e))
            _logger.debug(errMsg)
            self.update_state(state='FAIL_CELERY', meta={'errMsg': errMsg})
            time.sleep(1)
            return

        if 0:
            lines = stdout.readlines()
            for line in lines:
                print(line)

            outList = getSparkAppId_( lines)
            print(outList)
        else:
            ##c. get spark ID, table name##########
            outList = getSparkAppId(self, stdout, True)
            print(outList)

        if len(outList) < 2:
            #appID=app_ID
            appID="9999"
            outTblName="errTable"
            err_ = 'outList_length_error: Except length >= 2, but get lenthgh: {}'.format(len(outList))
            self.update_state(state=states.FAILURE, meta={'sparkAppID':appID, 'outTblName':err_})

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
        #ssh.close() 
        return outList


##2018/03/30, citc recover###############################
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
    meta_ = dict()# python dict
    #meta_['celeryErr']
    while True:
        line = stdout_.readline()
        if line == '':
            break
        #print(line)
        #sys.stdout.write(line)
        #sys.stdout.flush()
        
        ##20180103 add, citc add for error###########
        if "errTable:" in  line:
            errTable_index=line.find('errTable:')
            errReson_=line[errTable_index:].strip('\n')
            _logger.debug('The errReason_ is ' + errReson_)
            _logger.debug('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break
        ##20180103 add, citc add for error (end)#######
        
        #dbName 20180611
        if "spark_gen_dbName_" in  line:
            spark_gen_dbName_index=line.find('spark_gen_dbName_') 
            spark_gen_dbName_=line[spark_gen_dbName_index:][len("spark_gen_dbName_"):].strip('\n')
            _logger.debug('The gen_dbName is ' + spark_gen_dbName_)
            meta_['dbName'] = spark_gen_dbName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_gen_dbName_)
            
        #tblName 20180611
        if "spark_gen_tblName_" in  line:
            spark_gen_tblName_index=line.find('spark_gen_tblName_') 
            spark_gen_tblName_=line[spark_gen_tblName_index:][len("spark_gen_tblName_"):].strip('\n')
            _logger.debug('The gen_tblName is ' + spark_gen_tblName_)
            meta_['tblName'] = spark_gen_tblName_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_gen_tblName_)
            
        if "sc.applicationId:" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:].strip('\n')
            #this gives the app_ID
            _logger.debug('The app ID is ' + app_ID)
            meta_['sparkAppID'] = app_ID
            self.update_state(state="PROGRESS", meta=meta_)
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
        self.update_state(state='FAIL_SPARK', meta=meta_)
        time.sleep(1)

    return outList
