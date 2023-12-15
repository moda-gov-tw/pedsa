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


#20200212, added for check node status (MariaDB, spark_status.nodeStatus)#
from config.getSparkStatus import checkSparkStatus
##########################################################################



from config.connect_sql import ConnectSQL

redis_store = FlaskRedis(app)

###itri, for deID (start)######################


@celery.task(bind=True)
def kchecking_longTask(self, base64_,nothing):
    """
    base64_: string
    nothing: 1
    """
    with app.app_context():

        # Set log.
        global _logger, _vlogger
        _logger=_getLogger('kchecking')
        _vlogger=_getLogger('verify__' + 'kchecking')
        ts0 = time.time()

        ###20200212, citc get node status####################3###################################################
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


        
        sparkCode = getConfig().getSparkCode('getKchecking_one.py')
        cmdStr = '''
        spark-submit {} {} '''.format(sparkCode, base64_)

        _vlogger.debug("20200220_cmdStr1:"+cmdStr)
        _logger.debug("20200220_cmdStr2:"+cmdStr)
        #_logger.debug(cmdStr)

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)


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



def kchecking4join_longTask(self, base64_,dbName,tb_name_):
    """
    base64_: string
    nothing: 1
    """
#    with app.app_context():

    global _logger, _vlogger
    _logger = _getLogger('kchecking4join')
    _vlogger = _getLogger('verify__' + 'kchecking4join')

    ts0 = time.time()

    sparkCode = getConfig().getSparkCode('getKchecking.py')
    cmdStr = '''
    spark-submit {} {} {} {}'''.format(sparkCode, base64_, dbName, tb_name_)

    _vlogger.debug(cmdStr)
    _logger.debug(cmdStr)

    ssh_for_bash = ssh_hdfs()
    stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)

####################################################################


    if 0:
        lines = stdout.readlines()
        print(lines)
        print(stderr.readlines())
        #ssh.close()

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


def getColoumnsFromMysql(projID, tblOutput, conn):
    # query columns name
    colCompare = dict()

    sqlCommand = """
    SELECT pro_col_en,pro_col_cht
    FROM {0}.{1}
    WHERE project_id='{2}'
    AND finaltblName='{3}'
    """.format('DeIdService', 'T_Project_SampleTable', projID, tblOutput)

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
        ##20180103 add, citc add for error (end)#######

        #kTable_
        if "k-value" in  line:
            kTable_index=line.find('k-value')
            kTable_=line[kTable_index:]
            _logger.debug('The k-value is ' + kTable_)
            print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)

        if "tb_name_" in  line:
            spark_tblname_index=line.find('tb_name_')
            spark_tblname_ =line[spark_tblname_index+10:]
            _logger.debug('The spark_tblname_ is ' + spark_tblname_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['tblName'] = spark_tblname_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_tblname_)

        if "projID___" in  line:
            spark_dbname_index=line.find('projID___')
            #spark_dbname_ =line[spark_dbname_index+10:]
            spark_dbname_ =line[spark_dbname_index+11:]
            _logger.debug('The spark_dbname_ is ' + spark_dbname_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['projID'] = spark_dbname_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_dbname_)


        if "dbName___" in  line:
            spark_dbname_index=line.find('dbName___')
            #spark_dbname_ =line[spark_dbname_index+10:]
            spark_dbname_ =line[spark_dbname_index+11:]
            _logger.debug('The spark_dbname_ is ' + spark_dbname_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['dbName'] = spark_dbname_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_dbname_)


        if "df_count" in  line:
            spark_df_count_index=line.find('df_count')
            spark_df_count_=line[spark_df_count_index+9:]
            _logger.debug('The df_count is ' + spark_df_count_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['dfcount'] = spark_df_count_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_df_count_)


        #citc 20200221 modified, form minKvalue to ___minKvalue___
        if "___minKvalue___" in  line:
            spark_kvalue_index=line.find('___minKvalue___')
            spark_kvalue_ =line[spark_kvalue_index+16:]
            _logger.debug('The min k-value is ' + spark_kvalue_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kvalue'] = spark_kvalue_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_kvalue_)


        if "supCount" in  line:
            spark_supCount_index=line.find('supCount')
            spark_supCount_ =line[spark_supCount_index+9:]
            _logger.debug('The spark_supCount_ is ' + spark_supCount_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['sup_count'] = spark_supCount_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_supCount_)

        if "supRate" in  line:
            spark_supRate_index=line.find('supRate')
            spark_supRate_ =line[spark_supRate_index+8:]
            _logger.debug('The spark_supRate_ is ' + spark_supRate_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['sup_rate'] = spark_supRate_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_supRate_)

        if "warningCols:" in line:
            warningCols_index = line.find('warningCols:')
            warningCols = line[warningCols_index:][len("warningCols:"):].strip('\n')
            #colsStr, countStr = warningCols.split('*')
            #warningColsList = colsStr.split(',')
            #warningCountList = countStr.split(',')
            #
            #try:
            #    your_conn = ConnectSQL()
            #except Exception as e:
            #    _logger.debug('connection fail: ' + str(e))
            #    break
            #
            #pID = meta_['projID'].strip('\n')
            #tbl = meta_['tblName'].strip('\n')
            #colCompare = getColoumnsFromMysql(pID, tbl, your_conn)
            #if colCompare:
            #    for col in colCompare:
            #        if col in warningColsList:
            #            warningColsList[warningColsList.index(col)] = colCompare[col]
            #
            #    warningColsFinal = ','.join(warningColsList) + '*' + ','.join(warningCountList)
            #    _logger.debug('The warning columns are ' + warningColsFinal)
            #    meta_['warningCols'] = warningColsFinal
            #    outList.append(warningColsFinal)
            #else:
            #    _logger.debug('warningCols fail: Can not find record where db={0} and tbl={1}'.format(db, tbl))
            #    break
            try:
                colsStr, countStr = warningCols.split('*')
                warningColsList = colsStr.split(',')
                warningCountList = countStr.split(',')

                try:
                    your_conn = ConnectSQL()
                except Exception as e:
                    _logger.debug('connection fail: ' + str(e))
                    break

                pID = meta_['projID'].strip('\n')
                tbl = meta_['tblName'].strip('\n')
                colCompare = getColoumnsFromMysql(pID, tbl, your_conn)
                if colCompare:
                    for col in colCompare:
                        if col in warningColsList:
                            warningColsList[warningColsList.index(col)] = colCompare[col]

                    warningColsFinal = ','.join(warningColsList) + '*' + ','.join(warningCountList)
                    _logger.debug('The warning columns are ' + warningColsFinal)
                    meta_['warningCols'] = warningColsFinal
                    outList.append(warningColsFinal)
                else:
                    _logger.debug('warningCols fail: Can not find record where db={0} and tbl={1}'.format(db, tbl))
                    break
            except:
                warningColsFinal = ''
                _logger.debug('The warning columns are ' + warningColsFinal)
                meta_['warningCols'] = warningColsFinal
                outList.append(warningColsFinal)



        if "distinct_count" in  line:
            _logger.debug("find it")
            spark_distinct_count_index=line.find('distinct_count')
            spark_distinct_count_ =line[spark_distinct_count_index+15:]
            _logger.debug('The spark_finish_data_distinct_count_ is ' + spark_distinct_count_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['distinct_count'] = spark_distinct_count_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_distinct_count_)



            # Connect to Mysql (update: 20190102)
            if len(spark_distinct_count_) > 1:
                
                try:
                    your_conn = ConnectSQL()
                except Exception as e:
                    print('connection fail: ' + str(e))                
                


                dbName = "DeIdService"
                tblName = "T_Project_SampleTable"
                '''
                colsValue = {
                    'project_id': 4,
                    'pro_db': str(meta_['dbName'][:-1]),  # 'new_0730',      #varchar(100)
                    'pro_tb': str(meta_['finaltblName'][:-1])  # 'sample_0730'      #varchar(100)
                }

                _logger.debug(your_conn.insertValue(dbName, tblName, colsValue))
                '''

                # get input table name
                tblInput = str(meta_['tblName'][:-1])
                tblFinal = str(meta_['finaltblName'][:-1])
                #m = re.search("gen_(.*)_final", tblInput)
                m = re.search("g_(.*)", tblInput)
                if m:
                    tblRaw = m.group(1)


                conditions = {
                    #       'project_id':4,      #int
                    'pro_db': str(meta_['dbName'][:-1]),  # 'adult',      #varchar(100)
                    'pro_tb': tblRaw
                    #'pro_tb': str(meta_['finaltblName'][:-1])  # 'youbike10512_sample'      #varchar(100)
                }

                setColsValue = {
                    'tableCount': int(meta_['dfcount'][:-1]),  # int
                    'minKvalue': int(meta_['kvalue'][:-1]),  # intq
                    'supRate': "%f" % (float(meta_['sup_rate'][:-1]) * 100) + "%",  # varchar(100)
                    'tableDisCount': int(meta_['distinct_count'][:-1]),  # varchar(100)
                    #'supRate': "%f" % (float(meta_['sup_rate'][:-1]) * 100) + "%",  # varchar(100)
                    'supCount': int(meta_['sup_count'][:-1]),  # int
                    'finaltblName': tblFinal,  # str
                    'warning_col' : meta_['warningCols']
                }

                _logger.debug(your_conn.updateValue(dbName, tblName, conditions, setColsValue))
                your_conn.close()
                break


        if "final_tb_name" in  line:
            spark_finaltblname_index=line.find('final_tb_name')
            spark_finaltblname_ =line[spark_finaltblname_index+15:]
            _logger.debug('The spark_finaltblname_ is ' + spark_finaltblname_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['finaltblName'] = spark_finaltblname_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(spark_finaltblname_)

            """
            # Connect to Mysql (update: 20190102)
            if len(spark_finaltblname_) > 1:
                try:
                    your_conn = ConnectSQL()
                except Exception as e:
                    print('connection fail: ' + str(e))

                dbName = "DeIdService"
                tblName = "T_Project_SampleTable"
                '''
                colsValue = {
                    'project_id': 4,
                    'pro_db': str(meta_['dbName'][:-1]),  # 'new_0730',      #varchar(100)
                    'pro_tb': str(meta_['finaltblName'][:-1])  # 'sample_0730'      #varchar(100)
                }

                _logger.debug(your_conn.insertValue(dbName, tblName, colsValue))
                '''

                # get input table name
                tblInput = str(meta_['tblName'][:-1])
                tblFinal = str(meta_['finaltblName'][:-1])
                _logger.debug(999999999999999999)
                _logger.debug(tblFinal)
                _logger.debug(len(tblFinal))
                _logger.debug(meta_)
                #m = re.search("gen_(.*)_final", tblInput)
                m = re.search("gen_(.*)", tblInput)
                if m:
                    tblRaw = m.group(1)

                conditions = {
                    #       'project_id':4,      #int
                    'pro_db': str(meta_['dbName'][:-1]),  # 'adult',      #varchar(100)
                    'pro_tb': tblRaw
                    #'pro_tb': str(meta_['finaltblName'][:-1])  # 'youbike10512_sample'      #varchar(100)
                }

                setColsValue = {
                    'tableCount': int(meta_['dfcount'][:-1]),  # int
                    'minKvalue': int(meta_['kvalue'][:-1]),  # intq
                    'supRate': "%f" % (float(meta_['sup_rate'][:-1]) * 100) + "%",  # varchar(100)
                    #'supRate': "%f" % (float(meta_['sup_rate'][:-1]) * 100) + "%",  # varchar(100)
                    'supCount': int(meta_['sup_count'][:-1]),  # int
                    'finaltblName': tblFinal  # str
                }

                _logger.debug(your_conn.updateValue(dbName, tblName, conditions, setColsValue))
                your_conn.close()
                break
            """

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

        #kTable_
        if "kTable_" in  line:
            kTable_index=line.find('kTable_')
            kTable_=line[kTable_index:]
            print('The kTable_ is ' + kTable_)
            #print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['kTable'] = kTable_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(kTable_)

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
